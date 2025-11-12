# Smart Campus ID Security System - Phase 2: Advanced Security Features
# St. Lawrence University - Cybersecurity Club
# Enhanced Flask Web Application with Authentication & Advanced Security

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import mysql.connector
from datetime import datetime, timedelta
import secrets
import hashlib
import json
from functools import wraps
import logging
from auth import (
    security_manager, require_auth, require_api_auth, 
    log_security_event, policy_engine, ROLES
)

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# Enhanced logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('security.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',  # Change to your MySQL username
    'password': '',  # Change to your MySQL password
    'database': 'smart_campus_security',
    'autocommit': True
}

def get_db_connection():
    """Create and return database connection"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        logger.error(f"Database connection error: {err}")
        return None

def enhanced_log_access_attempt(student_id, card_id, location_id, access_type, granted=True, 
                              denial_reason=None, risk_assessment=None):
    """Enhanced access logging with risk assessment"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Calculate risk score if not provided
        if not risk_assessment:
            risk_assessment = policy_engine.assess_access_risk(student_id, location_id)
        
        # Log to access_logs table
        query = """
            INSERT INTO access_logs (student_id, card_id, location_id, access_type, 
                                   access_granted, denial_reason, ip_address, user_agent,
                                   risk_score, requires_review)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(query, (
            student_id, card_id, location_id, access_type,
            granted, denial_reason, 
            request.remote_addr if request else 'simulation',
            request.headers.get('User-Agent') if request else 'virtual_scanner',
            risk_assessment['risk_score'],
            risk_assessment['requires_additional_auth']
        ))
        
        access_log_id = cursor.lastrowid
        
        # Log to risk_assessments table
        risk_query = """
            INSERT INTO risk_assessments (student_id, location_id, access_time, risk_score, 
                                        risk_level, risk_factors, action_taken)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(risk_query, (
            student_id, location_id, datetime.now(),
            risk_assessment['risk_score'],
            risk_assessment['risk_level'],
            json.dumps(risk_assessment['risk_factors']),
            'allowed' if granted else 'denied'
        ))
        
        # Log security event for audit trail
        event_details = {
            'access_log_id': access_log_id,
            'student_id': student_id,
            'card_id': card_id,
            'location_id': location_id,
            'access_type': access_type,
            'granted': granted,
            'risk_level': risk_assessment['risk_level'],
            'denial_reason': denial_reason
        }
        
        log_security_event(
            'access_attempt',
            json.dumps(event_details),
            user_id=getattr(request, 'current_user', {}).get('user_id') if hasattr(request, 'current_user') else None
        )
        
        conn.commit()
        logger.info(f"Access attempt logged: Student {student_id}, Location {location_id}, Granted: {granted}")
        return True
        
    except mysql.connector.Error as err:
        logger.error(f"Error logging enhanced access: {err}")
        return False
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def create_enhanced_security_alert(alert_type, severity, location_id, student_id=None, 
                                 card_id=None, message="", auto_escalate=True):
    """Create enhanced security alert with auto-escalation"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Create security alert
        query = """
            INSERT INTO security_alerts (alert_type, severity, location_id, student_id, 
                                       card_id, alert_message)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (alert_type, severity, location_id, student_id, card_id, message))
        alert_id = cursor.lastrowid
        
        # Auto-escalate to incident if severity is high or critical
        if auto_escalate and severity in ['high', 'critical']:
            incident_query = """
                INSERT INTO security_incidents (incident_type, severity, title, description, 
                                              location_id, detected_by, detected_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            incident_title = f"Security Alert #{alert_id}: {alert_type.replace('_', ' ').title()}"
            incident_desc = f"Auto-escalated from security alert. {message}"
            
            cursor.execute(incident_query, (
                alert_type, severity, incident_title, incident_desc,
                location_id, 2,  # Default to security officer user ID
                datetime.now()
            ))
            
            logger.warning(f"Security incident auto-created for alert {alert_id}")
        
        conn.commit()
        logger.warning(f"Security alert created: Type {alert_type}, Severity {severity}")
        return alert_id
        
    except mysql.connector.Error as err:
        logger.error(f"Error creating enhanced alert: {err}")
        return False
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Enhanced login with security features"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        verification_code = request.form.get('verification_code')
        remember_me = request.form.get('remember_me')
        
        if not username or not password:
            flash('Username and password are required', 'error')
            return render_template('login.html')
        
        # Check for account lockout
        if security_manager.is_account_locked(username):
            log_security_event('login_attempt_locked', f'Login attempt on locked account: {username}')
            flash('Account is temporarily locked due to failed login attempts. Try again later.', 'error')
            return render_template('login.html')
        
        conn = get_db_connection()
        if not conn:
            flash('System error. Please try again.', 'error')
            return render_template('login.html')
        
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM system_users WHERE username = %s AND status = 'active'", (username,))
            user = cursor.fetchone()
            
            if not user or not security_manager.verify_password(password, user['password_hash']):
                # Track failed attempt
                security_manager.track_failed_attempt(username)
                log_security_event('login_failed', f'Failed login attempt: {username}')
                
                flash('Invalid username or password', 'error')
                return render_template('login.html')
            
            # Check for 2FA requirement
            if user['two_factor_enabled']:
                if not verification_code:
                    # Generate and send 2FA code (simulated)
                    flash('Two-factor authentication required. Code sent to your registered device.', 'info')
                    session['pending_2fa_user'] = user['user_id']
                    return render_template('login.html', show_2fa=True)
                elif verification_code != '123456':  # Demo code for educational purposes
                    flash('Invalid verification code', 'error')
                    return render_template('login.html', show_2fa=True)
            
            # Successful login
            token = security_manager.generate_session_token(user['user_id'], user['role'])
            session['auth_token'] = token
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            session['role'] = user['role']
            
            # Update last login
            cursor.execute("UPDATE system_users SET last_login = %s, failed_login_attempts = 0 WHERE user_id = %s",
                         (datetime.now(), user['user_id']))
            
            # Log successful login
            log_security_event('login_success', f'User {username} logged in successfully', user['user_id'])
            
            flash(f'Welcome back, {user["full_name"]}!', 'success')
            
            # Redirect based on role
            if user['role'] == 'admin':
                return redirect(url_for('advanced_dashboard'))
            elif user['role'] in ['security_officer', 'staff']:
                return redirect(url_for('dashboard'))
            else:
                return redirect(url_for('index'))
                
        except mysql.connector.Error as err:
            logger.error(f"Login database error: {err}")
            flash('System error during login. Please try again.', 'error')
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Secure logout with session cleanup"""
    user_id = session.get('user_id')
    username = session.get('username')
    
    if user_id:
        log_security_event('logout', f'User {username} logged out', user_id)
    
    # Clear session
    session.clear()
    
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))

@app.route('/')
def index():
    """Main virtual campus interface (public access)"""
    # Get all campus locations for the virtual map
    conn = get_db_connection()
    locations = []
    
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM campus_locations WHERE is_active = TRUE ORDER BY building, location_name")
            locations = cursor.fetchall()
        except mysql.connector.Error as err:
            logger.error(f"Error fetching locations: {err}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    
    return render_template('virtual_campus.html', locations=locations)

@app.route('/scan_card', methods=['POST'])
def scan_card():
    """Enhanced card scanning with advanced security checks"""
    data = request.get_json()
    card_id = data.get('card_id')
    location_id = data.get('location_id')
    access_type = data.get('access_type', 'entry')
    
    if not card_id or not location_id:
        return jsonify({'success': False, 'message': 'Missing card ID or location ID'})
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection failed'})
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Check if card exists and get student info
        cursor.execute("SELECT * FROM students WHERE card_id = %s", (card_id,))
        student = cursor.fetchone()
        
        if not student:
            # Unknown card - create enhanced alert
            create_enhanced_security_alert('unauthorized_access', 'high', location_id, 
                                          card_id=card_id, 
                                          message=f'Unknown card {card_id} attempted access at location {location_id}')
            enhanced_log_access_attempt(None, card_id, location_id, access_type, False, 'Unknown card')
            
            return jsonify({
                'success': False, 
                'message': 'ACCESS DENIED: Unknown card',
                'alert': True,
                'alert_type': 'unauthorized_access',
                'risk_level': 'high'
            })
        
        # Perform risk assessment
        risk_assessment = policy_engine.assess_access_risk(student['student_id'], location_id)
        
        # Check if student is active
        if student['status'] != 'active':
            enhanced_log_access_attempt(student['student_id'], card_id, location_id, access_type, 
                                      False, f'Student status: {student["status"]}', risk_assessment)
            return jsonify({
                'success': False, 
                'message': f'ACCESS DENIED: Student status is {student["status"]}',
                'student_name': student['full_name'],
                'risk_level': risk_assessment['risk_level']
            })
        
        # Check if card is lost or stolen
        cursor.execute("SELECT COUNT(*) as count FROM lost_stolen_cards WHERE card_id = %s AND status = 'active'", (card_id,))
        lost_stolen_count = cursor.fetchone()['count']
        
        if lost_stolen_count > 0:
            create_enhanced_security_alert('lost_card_used', 'critical', location_id, 
                                          student['student_id'], card_id,
                                          message=f'Lost/stolen card used by {student["full_name"]} at location {location_id}')
            enhanced_log_access_attempt(student['student_id'], card_id, location_id, access_type, 
                                      False, 'Card reported as lost/stolen', risk_assessment)
            return jsonify({
                'success': False, 
                'message': 'ACCESS DENIED: Card reported as lost/stolen',
                'alert': True,
                'alert_type': 'lost_card_used',
                'student_name': student['full_name'],
                'risk_level': 'critical'
            })
        
        # Get location info and check access policies
        cursor.execute("SELECT * FROM campus_locations WHERE location_id = %s", (location_id,))
        location = cursor.fetchone()
        
        # Check access level permissions
        if location and location['access_level'] == 'staff_only':
            enhanced_log_access_attempt(student['student_id'], card_id, location_id, access_type, 
                                      False, 'Insufficient access level - staff only', risk_assessment)
            return jsonify({
                'success': False, 
                'message': 'ACCESS DENIED: Staff access required',
                'student_name': student['full_name'],
                'location_name': location['location_name'],
                'risk_level': risk_assessment['risk_level']
            })
        
        # Check if additional authentication is required based on risk
        if risk_assessment['requires_additional_auth']:
            # In a real system, this would trigger additional authentication
            create_enhanced_security_alert('high_risk_access', 'medium', location_id,
                                          student['student_id'], card_id,
                                          message=f'High-risk access attempt by {student["full_name"]} requires additional verification')
        
        # Access granted - log successful entry
        enhanced_log_access_attempt(student['student_id'], card_id, location_id, access_type, True, 
                                  risk_assessment=risk_assessment)
        
        return jsonify({
            'success': True, 
            'message': f'ACCESS GRANTED',
            'student_name': student['full_name'],
            'student_id': student['student_id'],
            'location_name': location['location_name'] if location else 'Unknown Location',
            'access_type': access_type.upper(),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'risk_level': risk_assessment['risk_level'],
            'additional_auth_required': risk_assessment['requires_additional_auth']
        })
        
    except mysql.connector.Error as err:
        logger.error(f"Database error during enhanced card scan: {err}")
        return jsonify({'success': False, 'message': 'System error occurred'})
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/dashboard')
@require_auth('view_logs')
def dashboard():
    """Enhanced security monitoring dashboard"""
    conn = get_db_connection()
    dashboard_data = {
        'recent_access': [],
        'active_alerts': [],
        'stats': {
            'total_access_today': 0,
            'denied_access_today': 0,
            'active_alerts': 0,
            'total_students': 0,
            'high_risk_attempts': 0,
            'policy_violations': 0
        }
    }
    
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Get recent access logs with risk information
            cursor.execute("""
                SELECT al.*, s.full_name, cl.location_name, cl.building
                FROM access_logs al
                LEFT JOIN students s ON al.student_id = s.student_id
                LEFT JOIN campus_locations cl ON al.location_id = cl.location_id
                ORDER BY al.access_time DESC
                LIMIT 50
            """)
            dashboard_data['recent_access'] = cursor.fetchall()
            
            # Get active alerts
            cursor.execute("""
                SELECT sa.*, cl.location_name, s.full_name
                FROM security_alerts sa
                LEFT JOIN campus_locations cl ON sa.location_id = cl.location_id
                LEFT JOIN students s ON sa.student_id = s.student_id
                WHERE sa.status IN ('new', 'acknowledged', 'investigating')
                ORDER BY sa.alert_time DESC, sa.severity DESC
                LIMIT 20
            """)
            dashboard_data['active_alerts'] = cursor.fetchall()
            
            # Get enhanced statistics
            today = datetime.now().strftime('%Y-%m-%d')
            
            cursor.execute("SELECT COUNT(*) as total FROM access_logs WHERE DATE(access_time) = %s", (today,))
            dashboard_data['stats']['total_access_today'] = cursor.fetchone()['total']
            
            cursor.execute("SELECT COUNT(*) as denied FROM access_logs WHERE DATE(access_time) = %s AND access_granted = FALSE", (today,))
            dashboard_data['stats']['denied_access_today'] = cursor.fetchone()['denied']
            
            cursor.execute("SELECT COUNT(*) as alerts FROM security_alerts WHERE status IN ('new', 'acknowledged', 'investigating')")
            dashboard_data['stats']['active_alerts'] = cursor.fetchone()['alerts']
            
            cursor.execute("SELECT COUNT(*) as students FROM students WHERE status = 'active'")
            dashboard_data['stats']['total_students'] = cursor.fetchone()['students']
            
            cursor.execute("SELECT COUNT(*) as high_risk FROM access_logs WHERE DATE(access_time) = %s AND risk_score >= 3", (today,))
            dashboard_data['stats']['high_risk_attempts'] = cursor.fetchone()['high_risk']
            
            cursor.execute("SELECT COUNT(*) as violations FROM access_logs WHERE DATE(access_time) = %s AND requires_review = TRUE", (today,))
            dashboard_data['stats']['policy_violations'] = cursor.fetchone()['violations']
            
        except mysql.connector.Error as err:
            logger.error(f"Dashboard data error: {err}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    
    return render_template('dashboard.html', data=dashboard_data)

@app.route('/advanced_dashboard')
@require_auth('all')
def advanced_dashboard():
    """Advanced security dashboard for administrators"""
    conn = get_db_connection()
    dashboard_data = {
        'active_incidents': [],
        'recent_audit_logs': [],
        'active_policies': [],
        'user_sessions': [],
        'stats': {
            'active_sessions': 0,
            'blocked_attempts': 0,
            'policy_violations': 0,
            'risk_assessments': 0,
            'unique_users': 0
        }
    }
    
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Get active incidents
            cursor.execute("SELECT * FROM active_security_incidents LIMIT 10")
            dashboard_data['active_incidents'] = cursor.fetchall()
            
            # Get recent audit logs
            cursor.execute("""
                SELECT * FROM security_audit_log 
                ORDER BY timestamp DESC 
                LIMIT 20
            """)
            dashboard_data['recent_audit_logs'] = cursor.fetchall()
            
            # Get active policies
            cursor.execute("SELECT * FROM access_policies WHERE is_active = TRUE LIMIT 10")
            dashboard_data['active_policies'] = cursor.fetchall()
            
            # Get user sessions
            cursor.execute("SELECT * FROM user_activity_summary LIMIT 10")
            dashboard_data['user_sessions'] = cursor.fetchall()
            
            # Get advanced statistics
            today = datetime.now().strftime('%Y-%m-%d')
            
            cursor.execute("SELECT COUNT(*) as sessions FROM user_sessions WHERE is_active = TRUE")
            dashboard_data['stats']['active_sessions'] = cursor.fetchone()['sessions']
            
            cursor.execute("SELECT COUNT(*) as blocked FROM access_logs WHERE DATE(access_time) = %s AND access_granted = FALSE", (today,))
            dashboard_data['stats']['blocked_attempts'] = cursor.fetchone()['blocked']
            
            cursor.execute("SELECT COUNT(*) as violations FROM access_logs WHERE DATE(access_time) = %s AND requires_review = TRUE", (today,))
            dashboard_data['stats']['policy_violations'] = cursor.fetchone()['violations']
            
            cursor.execute("SELECT COUNT(*) as assessments FROM risk_assessments WHERE DATE(assessment_time) = %s", (today,))
            dashboard_data['stats']['risk_assessments'] = cursor.fetchone()['assessments']
            
            cursor.execute("SELECT COUNT(DISTINCT user_id) as users FROM user_sessions WHERE DATE(last_activity) = %s", (today,))
            dashboard_data['stats']['unique_users'] = cursor.fetchone()['users']
            
        except mysql.connector.Error as err:
            logger.error(f"Advanced dashboard error: {err}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    
    # Calculate security score (simplified algorithm)
    security_score = 85  # Base score
    if dashboard_data['stats']['policy_violations'] > 5:
        security_score -= 10
    if dashboard_data['stats']['blocked_attempts'] > 10:
        security_score -= 5
    
    threat_level = 'low'
    if security_score < 60:
        threat_level = 'critical'
    elif security_score < 70:
        threat_level = 'high'
    elif security_score < 80:
        threat_level = 'medium'
    
    return render_template('advanced_dashboard.html', 
                         data=dashboard_data, 
                         security_score=security_score,
                         threat_level=threat_level)

@app.route('/card_simulator')
def card_simulator():
    """Virtual card simulator interface"""
    # Get students for the simulator dropdown
    conn = get_db_connection()
    students = []
    
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT student_id, card_id, full_name, program FROM students WHERE status = 'active'")
            students = cursor.fetchall()
        except mysql.connector.Error as err:
            logger.error(f"Error fetching students: {err}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    
    return render_template('card_simulator.html', students=students)

@app.route('/api/recent_activity')
@require_api_auth('view_logs')
def recent_activity():
    """API endpoint for real-time activity updates"""
    conn = get_db_connection()
    activity = []
    
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT al.*, s.full_name, cl.location_name
                FROM access_logs al
                LEFT JOIN students s ON al.student_id = s.student_id
                LEFT JOIN campus_locations cl ON al.location_id = cl.location_id
                WHERE al.access_time >= DATE_SUB(NOW(), INTERVAL 5 MINUTE)
                ORDER BY al.access_time DESC
                LIMIT 10
            """)
            activity = cursor.fetchall()
            
            # Convert datetime objects to strings for JSON serialization
            for item in activity:
                if item['access_time']:
                    item['access_time'] = item['access_time'].strftime('%Y-%m-%d %H:%M:%S')
                    
        except mysql.connector.Error as err:
            logger.error(f"Recent activity error: {err}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    
    return jsonify(activity)

@app.route('/api/recent_security_events')
@require_api_auth('view_logs')
def recent_security_events():
    """API endpoint for recent security audit events"""
    conn = get_db_connection()
    events = []
    
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT * FROM security_audit_log 
                WHERE timestamp >= DATE_SUB(NOW(), INTERVAL 1 MINUTE)
                ORDER BY timestamp DESC
                LIMIT 5
            """)
            events = cursor.fetchall()
            
            # Convert datetime objects to strings
            for event in events:
                if event['timestamp']:
                    event['timestamp'] = event['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
                    
        except mysql.connector.Error as err:
            logger.error(f"Recent security events error: {err}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    
    return jsonify(events)

@app.errorhandler(403)
def forbidden(e):
    """Custom 403 error handler"""
    return render_template('error.html', 
                         error_code=403,
                         error_message="Access Denied: Insufficient permissions"), 403

@app.errorhandler(404)
def not_found(e):
    """Custom 404 error handler"""
    return render_template('error.html',
                         error_code=404,
                         error_message="Page not found"), 404

if __name__ == '__main__':
    logger.info("Starting Smart Campus Security System - Phase 2")
    app.run(debug=True, host='0.0.0.0', port=5000)