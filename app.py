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
from ai_engine import get_ai_engine

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
    'password': 'milka',  # Change to your MySQL password
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
        
        # Debug logging for student data
        logger.info(f"Student query for card {card_id}: {student}")
        
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
        
        # Get location info first (needed for AI analysis)
        cursor.execute("SELECT * FROM campus_locations WHERE location_id = %s", (location_id,))
        location = cursor.fetchone()
        
        # Debug logging for location data
        logger.info(f"Location query for ID {location_id}: {location}")
        
        if not location:
            logger.warning(f"Location not found for ID: {location_id}")
            # Check if location exists at all
            cursor.execute("SELECT location_id, location_name FROM campus_locations WHERE is_active = TRUE")
            available_locations = cursor.fetchall()
            logger.info(f"Available locations: {available_locations}")
            
            return jsonify({
                'success': False,
                'message': 'ACCESS DENIED: Invalid location',
                'error_detail': f'Location ID {location_id} not found',
                'available_locations': [{'id': loc['location_id'], 'name': loc['location_name']} for loc in available_locations] if available_locations else []
            })
        
        # Perform risk assessment with AI enhancement
        risk_assessment = policy_engine.assess_access_risk(student['student_id'], location_id)
        
        # AI-powered anomaly detection
        ai_engine = get_ai_engine()
        
        # Prepare data for AI analysis
        access_analysis_data = {
            'student_id': student['student_id'],
            'location_id': location_id,
            'hour': datetime.now().hour,
            'day_of_week': datetime.now().weekday(),
            'is_weekend': datetime.now().weekday() >= 5,
            'current_risk_score': risk_assessment['risk_score'],
            'time_between_access': get_time_since_last_access(student['student_id']),
            'locations_per_hour': get_recent_location_count(student['student_id']),
            'location_security_level': location.get('access_level', 'public') if location else 'public'
        }
        
        # Get AI anomaly detection results
        try:
            ai_analysis = ai_engine.detect_anomaly(access_analysis_data)
        except Exception as ai_error:
            logger.error(f"AI analysis error: {ai_error}")
            # Fallback AI response
            ai_analysis = {
                'is_anomaly': False,
                'anomaly_score': 1,
                'confidence': 85,
                'risk_level': 'low',
                'explanation': 'AI analysis using fallback mode'
            }
        
        # Ensure AI analysis has all required fields and JSON-serializable types
        ai_analysis = {
            'is_anomaly': bool(ai_analysis.get('is_anomaly', False)),
            'anomaly_score': float(ai_analysis.get('anomaly_score', 1)),
            'confidence': float(ai_analysis.get('confidence', 85)),
            'risk_level': str(ai_analysis.get('risk_level', 'low')),
            'explanation': str(ai_analysis.get('explanation', 'Normal access pattern'))
        }
        
        # Enhance risk assessment with AI insights
        if ai_analysis['is_anomaly']:
            risk_assessment['risk_score'] = max(risk_assessment['risk_score'], int(ai_analysis['anomaly_score']))
            risk_assessment['risk_level'] = ai_analysis['risk_level']
            risk_assessment['ai_detected'] = True
            risk_assessment['ai_explanation'] = ai_analysis['explanation']
        else:
            risk_assessment['ai_detected'] = False
            risk_assessment['ai_explanation'] = 'Normal behavior pattern'
        
        # Check if student is active
        if student['status'] != 'active':
            enhanced_log_access_attempt(student['student_id'], card_id, location_id, access_type, 
                                      False, f'Student status: {student["status"]}', risk_assessment)
            return jsonify({
                'success': False, 
                'message': f'ACCESS DENIED: Student status is {student["status"]}',
                'student_name': student['full_name'],
                'risk_level': risk_assessment['risk_level'],
                'ai_analysis': ai_analysis
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
        
        # Location info already retrieved above for AI analysis
        
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
            'additional_auth_required': risk_assessment['requires_additional_auth'],
            'photo_url': student.get('photo_url'),
            'program': student.get('program'),
            'year_of_study': student.get('year_of_study'),
            'ai_analysis': ai_analysis,
            'ai_confidence': ai_analysis.get('confidence', 0)
        })
        
    except mysql.connector.Error as err:
        logger.error(f"Database error during enhanced card scan: {err}")
        return jsonify({'success': False, 'message': 'System error occurred'})
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def get_time_since_last_access(student_id):
    """Get minutes since student's last access attempt"""
    conn = get_db_connection()
    if not conn:
        return 60  # Default to 60 minutes
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT access_time FROM access_logs 
            WHERE student_id = %s 
            ORDER BY access_time DESC 
            LIMIT 1
        """, (student_id,))
        
        result = cursor.fetchone()
        if result and result['access_time']:
            last_access = result['access_time']
            time_diff = datetime.now() - last_access
            return int(time_diff.total_seconds() / 60)  # Convert to minutes
        
        return 120  # No previous access, return 2 hours
        
    except mysql.connector.Error:
        return 60  # Default fallback
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def get_recent_location_count(student_id):
    """Get number of locations accessed in the last hour"""
    conn = get_db_connection()
    if not conn:
        return 1  # Default
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(DISTINCT location_id) as count
            FROM access_logs 
            WHERE student_id = %s 
            AND access_time >= DATE_SUB(NOW(), INTERVAL 1 HOUR)
        """, (student_id,))
        
        result = cursor.fetchone()
        return result[0] if result else 1
        
    except mysql.connector.Error:
        return 1  # Default fallback
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

# ====================================
# ADMIN MANAGEMENT ROUTES
# ====================================

@app.route('/admin/manage')
@require_auth('all')
def admin_management():
    """Admin management dashboard"""
    return render_template('admin_management.html')

@app.route('/admin/students')
@require_auth('all')
def admin_students():
    """Student management interface"""
    conn = get_db_connection()
    students = []
    
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT s.*, 
                       CASE WHEN s.card_expiry_date < NOW() THEN 'expired'
                            WHEN s.card_expiry_date < DATE_ADD(NOW(), INTERVAL 30 DAY) THEN 'expiring'
                            ELSE 'active' END as card_status
                FROM students s 
                ORDER BY s.full_name
            """)
            students = cursor.fetchall()
        except mysql.connector.Error as err:
            logger.error(f"Error fetching students: {err}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    
    return render_template('admin_students.html', students=students)

@app.route('/admin/add_student', methods=['GET', 'POST'])
@require_auth('all')
def add_student():
    """Add new student"""
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        # Generate unique card ID
        card_id = f"RFID_{secrets.token_hex(3).upper()}_{secrets.token_hex(3).upper()}"
        
        # Calculate card expiry (4 years for undergraduate, 2 years for postgraduate)
        years = 4 if int(data.get('year_of_study', 1)) <= 4 else 2
        expiry_date = datetime.now() + timedelta(days=365 * years)
        
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                query = """
                    INSERT INTO students (student_id, card_id, full_name, email, phone, 
                                        program, year_of_study, photo_url, card_expiry_date, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (
                    data.get('student_id'),
                    card_id,
                    data.get('full_name'),
                    data.get('email'),
                    data.get('phone'),
                    data.get('program'),
                    data.get('year_of_study'),
                    data.get('photo_url'),
                    expiry_date,
                    'active'
                ))
                
                # Log the action
                log_security_event('student_added', 
                                 f'New student added: {data.get("full_name")} ({data.get("student_id")})',
                                 request.current_user['user_id'])
                
                conn.commit()
                flash(f'Student {data.get("full_name")} added successfully! Card ID: {card_id}', 'success')
                
                if request.is_json:
                    return jsonify({'success': True, 'card_id': card_id, 'expiry_date': expiry_date.isoformat()})
                
            except mysql.connector.Error as err:
                logger.error(f"Error adding student: {err}")
                flash('Error adding student. Please try again.', 'error')
                if request.is_json:
                    return jsonify({'success': False, 'error': str(err)})
            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()
        
        return redirect(url_for('admin_students'))
    
    return render_template('add_student.html')

@app.route('/admin/locations')
@require_auth('all')
def admin_locations():
    """Location management interface"""
    conn = get_db_connection()
    locations = []
    
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM campus_locations ORDER BY building, location_name")
            locations = cursor.fetchall()
        except mysql.connector.Error as err:
            logger.error(f"Error fetching locations: {err}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    
    return render_template('admin_locations.html', locations=locations)

@app.route('/admin/add_location', methods=['GET', 'POST'])
@require_auth('all')
def add_location():
    """Add new campus location"""
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                query = """
                    INSERT INTO campus_locations (location_name, location_type, building, 
                                                floor_level, access_level, is_active)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (
                    data.get('location_name'),
                    data.get('location_type'),
                    data.get('building'),
                    data.get('floor_level'),
                    data.get('access_level'),
                    True
                ))
                
                log_security_event('location_added', 
                                 f'New location added: {data.get("location_name")} in {data.get("building")}',
                                 request.current_user['user_id'])
                
                conn.commit()
                flash(f'Location {data.get("location_name")} added successfully!', 'success')
                
                if request.is_json:
                    return jsonify({'success': True})
                
            except mysql.connector.Error as err:
                logger.error(f"Error adding location: {err}")
                flash('Error adding location. Please try again.', 'error')
                if request.is_json:
                    return jsonify({'success': False, 'error': str(err)})
            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()
        
        return redirect(url_for('admin_locations'))
    
    return render_template('add_location.html')

@app.route('/admin/staff')
@require_auth('all')
def admin_staff():
    """Staff/officer management interface"""
    conn = get_db_connection()
    staff_members = []
    
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM system_users ORDER BY role, full_name")
            staff_members = cursor.fetchall()
        except mysql.connector.Error as err:
            logger.error(f"Error fetching staff: {err}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    
    return render_template('admin_staff.html', staff_members=staff_members)

@app.route('/admin/add_staff', methods=['GET', 'POST'])
@require_auth('all')
def add_staff():
    """Add new staff member/officer"""
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        # Hash password
        password_hash = security_manager.hash_password(data.get('password'))
        
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                query = """
                    INSERT INTO system_users (username, email, password_hash, full_name, 
                                            role, status, created_by)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (
                    data.get('username'),
                    data.get('email'),
                    password_hash,
                    data.get('full_name'),
                    data.get('role'),
                    'active',
                    request.current_user['user_id']
                ))
                
                log_security_event('staff_added', 
                                 f'New {data.get("role")} added: {data.get("full_name")} ({data.get("username")})',
                                 request.current_user['user_id'])
                
                conn.commit()
                flash(f'{data.get("role").replace("_", " ").title()} {data.get("full_name")} added successfully!', 'success')
                
                if request.is_json:
                    return jsonify({'success': True})
                
            except mysql.connector.Error as err:
                logger.error(f"Error adding staff: {err}")
                flash('Error adding staff member. Please try again.', 'error')
                if request.is_json:
                    return jsonify({'success': False, 'error': str(err)})
            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()
        
        return redirect(url_for('admin_staff'))
    
    return render_template('add_staff.html')

@app.route('/admin/cards')
@require_auth('all')
def admin_cards():
    """Card management interface with filters"""
    # Get filter parameters
    status_filter = request.args.get('status', 'all')
    search_query = request.args.get('search', '')
    
    conn = get_db_connection()
    cards = []
    
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Build query with filters
            base_query = """
                SELECT s.*, 
                       CASE WHEN s.card_expiry_date < NOW() THEN 'expired'
                            WHEN s.card_expiry_date < DATE_ADD(NOW(), INTERVAL 30 DAY) THEN 'expiring'
                            WHEN s.status = 'suspended' THEN 'suspended'
                            WHEN s.status = 'inactive' THEN 'inactive'
                            ELSE 'active' END as card_status,
                       ls.status as lost_stolen_status
                FROM students s
                LEFT JOIN lost_stolen_cards ls ON s.card_id = ls.card_id AND ls.status = 'active'
            """
            
            conditions = []
            params = []
            
            if status_filter != 'all':
                if status_filter == 'expired':
                    conditions.append("s.card_expiry_date < NOW()")
                elif status_filter == 'expiring':
                    conditions.append("s.card_expiry_date < DATE_ADD(NOW(), INTERVAL 30 DAY) AND s.card_expiry_date >= NOW()")
                elif status_filter == 'suspended':
                    conditions.append("s.status = 'suspended'")
                elif status_filter == 'lost_stolen':
                    conditions.append("ls.status = 'active'")
                else:
                    conditions.append("s.status = %s")
                    params.append(status_filter)
            
            if search_query:
                conditions.append("(s.full_name LIKE %s OR s.student_id LIKE %s OR s.card_id LIKE %s)")
                search_pattern = f"%{search_query}%"
                params.extend([search_pattern, search_pattern, search_pattern])
            
            if conditions:
                base_query += " WHERE " + " AND ".join(conditions)
            
            base_query += " ORDER BY s.full_name"
            
            cursor.execute(base_query, params)
            cards = cursor.fetchall()
            
        except mysql.connector.Error as err:
            logger.error(f"Error fetching cards: {err}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    
    return render_template('admin_cards.html', cards=cards, 
                         status_filter=status_filter, search_query=search_query)

@app.route('/admin/block_card/<card_id>', methods=['POST'])
@require_auth('all')
def block_card(card_id):
    """Block/suspend a student card"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE students SET status = 'suspended' WHERE card_id = %s", (card_id,))
            
            # Get student info for logging
            cursor.execute("SELECT full_name, student_id FROM students WHERE card_id = %s", (card_id,))
            student = cursor.fetchone()
            
            if student:
                log_security_event('card_blocked', 
                                 f'Card blocked for {student[0]} ({student[1]}) - Card: {card_id}',
                                 request.current_user['user_id'])
                
                conn.commit()
                flash(f'Card {card_id} has been blocked successfully!', 'success')
            else:
                flash('Card not found!', 'error')
                
        except mysql.connector.Error as err:
            logger.error(f"Error blocking card: {err}")
            flash('Error blocking card. Please try again.', 'error')
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    
    return redirect(url_for('admin_cards'))

@app.route('/admin/activate_card/<card_id>', methods=['POST'])
@require_auth('all')
def activate_card(card_id):
    """Activate a blocked/suspended card"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE students SET status = 'active' WHERE card_id = %s", (card_id,))
            
            # Get student info for logging
            cursor.execute("SELECT full_name, student_id FROM students WHERE card_id = %s", (card_id,))
            student = cursor.fetchone()
            
            if student:
                log_security_event('card_activated', 
                                 f'Card activated for {student[0]} ({student[1]}) - Card: {card_id}',
                                 request.current_user['user_id'])
                
                conn.commit()
                flash(f'Card {card_id} has been activated successfully!', 'success')
            else:
                flash('Card not found!', 'error')
                
        except mysql.connector.Error as err:
            logger.error(f"Error activating card: {err}")
            flash('Error activating card. Please try again.', 'error')
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    
    return redirect(url_for('admin_cards'))

# ====================================
# ACCESS LOGS MANAGEMENT
# ====================================

@app.route('/admin/access_logs')
@require_auth('all')
def admin_access_logs():
    """Access logs management interface with advanced filtering"""
    # Get filter parameters
    location_filter = request.args.get('location', 'all')
    date_filter = request.args.get('date', 'today')
    status_filter = request.args.get('status', 'all')
    student_filter = request.args.get('student', '')
    time_from = request.args.get('time_from', '')
    time_to = request.args.get('time_to', '')
    
    conn = get_db_connection()
    access_logs = []
    locations = []
    
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Get all locations for filter dropdown
            cursor.execute("SELECT location_id, location_name, building FROM campus_locations ORDER BY building, location_name")
            locations = cursor.fetchall()
            
            # Build query with filters
            base_query = """
                SELECT al.*, s.full_name, s.student_id, s.photo_url,
                       cl.location_name, cl.building, cl.access_level,
                       CASE WHEN al.risk_score >= 5 THEN 'high'
                            WHEN al.risk_score >= 3 THEN 'medium' 
                            ELSE 'low' END as risk_category
                FROM access_logs al
                LEFT JOIN students s ON al.student_id = s.student_id
                LEFT JOIN campus_locations cl ON al.location_id = cl.location_id
            """
            
            conditions = []
            params = []
            
            # Location filter
            if location_filter != 'all':
                conditions.append("al.location_id = %s")
                params.append(location_filter)
            
            # Date filter
            if date_filter == 'today':
                conditions.append("DATE(al.access_time) = CURDATE()")
            elif date_filter == 'yesterday':
                conditions.append("DATE(al.access_time) = DATE_SUB(CURDATE(), INTERVAL 1 DAY)")
            elif date_filter == 'week':
                conditions.append("al.access_time >= DATE_SUB(NOW(), INTERVAL 7 DAY)")
            elif date_filter == 'month':
                conditions.append("al.access_time >= DATE_SUB(NOW(), INTERVAL 30 DAY)")
            elif date_filter == 'custom' and time_from and time_to:
                conditions.append("DATE(al.access_time) BETWEEN %s AND %s")
                params.extend([time_from, time_to])
            
            # Status filter
            if status_filter == 'granted':
                conditions.append("al.access_granted = TRUE")
            elif status_filter == 'denied':
                conditions.append("al.access_granted = FALSE")
            elif status_filter == 'high_risk':
                conditions.append("al.risk_score >= 5")
            
            # Student filter
            if student_filter:
                conditions.append("(s.full_name LIKE %s OR s.student_id LIKE %s OR al.card_id LIKE %s)")
                search_pattern = f"%{student_filter}%"
                params.extend([search_pattern, search_pattern, search_pattern])
            
            if conditions:
                base_query += " WHERE " + " AND ".join(conditions)
            
            base_query += " ORDER BY al.access_time DESC LIMIT 500"
            
            cursor.execute(base_query, params)
            access_logs = cursor.fetchall()
            
        except mysql.connector.Error as err:
            logger.error(f"Error fetching access logs: {err}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    
    return render_template('admin_access_logs.html', 
                         access_logs=access_logs, 
                         locations=locations,
                         filters={
                             'location': location_filter,
                             'date': date_filter, 
                             'status': status_filter,
                             'student': student_filter,
                             'time_from': time_from,
                             'time_to': time_to
                         })

@app.route('/admin/location_report/<int:location_id>')
@require_auth('all')
def location_access_report(location_id):
    """Detailed access report for a specific location"""
    date_filter = request.args.get('date', 'today')
    
    conn = get_db_connection()
    location_info = {}
    access_data = []
    statistics = {}
    
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Get location information
            cursor.execute("SELECT * FROM campus_locations WHERE location_id = %s", (location_id,))
            location_info = cursor.fetchone()
            
            if location_info:
                # Build date condition
                if date_filter == 'today':
                    date_condition = "DATE(al.access_time) = CURDATE()"
                    params = [location_id]
                elif date_filter == 'yesterday':
                    date_condition = "DATE(al.access_time) = DATE_SUB(CURDATE(), INTERVAL 1 DAY)"
                    params = [location_id]
                elif date_filter == 'week':
                    date_condition = "al.access_time >= DATE_SUB(NOW(), INTERVAL 7 DAY)"
                    params = [location_id]
                else:  # month
                    date_condition = "al.access_time >= DATE_SUB(NOW(), INTERVAL 30 DAY)"
                    params = [location_id]
                
                # Get access logs for this location
                cursor.execute(f"""
                    SELECT al.*, s.full_name, s.student_id, s.program, s.photo_url
                    FROM access_logs al
                    LEFT JOIN students s ON al.student_id = s.student_id
                    WHERE al.location_id = %s AND {date_condition}
                    ORDER BY al.access_time DESC
                """, params)
                access_data = cursor.fetchall()
                
                # Get statistics
                cursor.execute(f"""
                    SELECT 
                        COUNT(*) as total_attempts,
                        SUM(CASE WHEN access_granted = TRUE THEN 1 ELSE 0 END) as granted_count,
                        SUM(CASE WHEN access_granted = FALSE THEN 1 ELSE 0 END) as denied_count,
                        COUNT(DISTINCT student_id) as unique_students,
                        AVG(risk_score) as avg_risk_score
                    FROM access_logs 
                    WHERE location_id = %s AND {date_condition}
                """, params)
                statistics = cursor.fetchone()
                
        except mysql.connector.Error as err:
            logger.error(f"Error fetching location report: {err}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    
    return render_template('location_access_report.html',
                         location_info=location_info,
                         access_data=access_data, 
                         statistics=statistics,
                         date_filter=date_filter)

@app.route('/admin/export_logs')
@require_auth('all')
def export_access_logs():
    """Export access logs to CSV format"""
    from io import StringIO
    import csv
    
    # Get same filters as access_logs view
    location_filter = request.args.get('location', 'all')
    date_filter = request.args.get('date', 'today')
    status_filter = request.args.get('status', 'all')
    student_filter = request.args.get('student', '')
    
    conn = get_db_connection()
    
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Same query logic as admin_access_logs but without LIMIT
            base_query = """
                SELECT 
                    al.access_time,
                    s.full_name,
                    s.student_id,
                    s.program,
                    al.card_id,
                    cl.location_name,
                    cl.building,
                    cl.access_level,
                    al.access_type,
                    CASE WHEN al.access_granted THEN 'GRANTED' ELSE 'DENIED' END as access_status,
                    al.denial_reason,
                    al.risk_score,
                    al.ip_address
                FROM access_logs al
                LEFT JOIN students s ON al.student_id = s.student_id
                LEFT JOIN campus_locations cl ON al.location_id = cl.location_id
            """
            
            conditions = []
            params = []
            
            # Apply same filters
            if location_filter != 'all':
                conditions.append("al.location_id = %s")
                params.append(location_filter)
            
            if date_filter == 'today':
                conditions.append("DATE(al.access_time) = CURDATE()")
            elif date_filter == 'yesterday':
                conditions.append("DATE(al.access_time) = DATE_SUB(CURDATE(), INTERVAL 1 DAY)")
            elif date_filter == 'week':
                conditions.append("al.access_time >= DATE_SUB(NOW(), INTERVAL 7 DAY)")
            elif date_filter == 'month':
                conditions.append("al.access_time >= DATE_SUB(NOW(), INTERVAL 30 DAY)")
            
            if status_filter == 'granted':
                conditions.append("al.access_granted = TRUE")
            elif status_filter == 'denied':
                conditions.append("al.access_granted = FALSE")
            
            if student_filter:
                conditions.append("(s.full_name LIKE %s OR s.student_id LIKE %s)")
                search_pattern = f"%{student_filter}%"
                params.extend([search_pattern, search_pattern])
            
            if conditions:
                base_query += " WHERE " + " AND ".join(conditions)
            
            base_query += " ORDER BY al.access_time DESC"
            
            cursor.execute(base_query, params)
            results = cursor.fetchall()
            
            # Create CSV
            output = StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                'Date/Time', 'Student Name', 'Student ID', 'Program', 'Card ID',
                'Location', 'Building', 'Access Level', 'Access Type', 'Status',
                'Denial Reason', 'Risk Score', 'IP Address'
            ])
            
            # Write data
            for row in results:
                writer.writerow([
                    row['access_time'].strftime('%Y-%m-%d %H:%M:%S') if row['access_time'] else '',
                    row['full_name'] or 'Unknown',
                    row['student_id'] or 'Unknown',
                    row['program'] or '',
                    row['card_id'] or '',
                    row['location_name'] or 'Unknown Location',
                    row['building'] or '',
                    row['access_level'] or '',
                    row['access_type'] or '',
                    row['access_status'],
                    row['denial_reason'] or '',
                    row['risk_score'] or 0,
                    row['ip_address'] or ''
                ])
            
            # Create response
            from flask import Response
            output.seek(0)
            filename = f"access_logs_{date_filter}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            return Response(
                output.getvalue(),
                mimetype='text/csv',
                headers={'Content-Disposition': f'attachment; filename={filename}'}
            )
            
        except mysql.connector.Error as err:
            logger.error(f"Error exporting logs: {err}")
            flash('Error exporting logs. Please try again.', 'error')
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    
    return redirect(url_for('admin_access_logs'))

@app.route('/admin/investigation_report', methods=['GET', 'POST'])
@require_auth('all')
def investigation_report():
    """Generate detailed investigation report for specific incidents"""
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        target_student = data.get('target_student')
        target_location = data.get('target_location')
        incident_date = data.get('incident_date')
        time_range_hours = int(data.get('time_range_hours', 24))
        
        # Search both current and archived logs
        investigation_data = search_logs_with_archives(
            target_student, target_location, incident_date, time_range_hours
        )
        
        return jsonify({
            'success': True,
            'data': investigation_data
        })
    
    # GET request - show investigation form
    conn = get_db_connection()
    locations = []
    recent_students = []
    
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT location_id, location_name, building FROM campus_locations ORDER BY building, location_name")
            locations = cursor.fetchall()
            
            cursor.execute("""
                SELECT DISTINCT s.student_id, s.full_name 
                FROM students s 
                JOIN access_logs al ON s.student_id = al.student_id 
                WHERE al.access_time >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                ORDER BY s.full_name
                LIMIT 50
            """)
            recent_students = cursor.fetchall()
            
        except mysql.connector.Error as err:
            logger.error(f"Error fetching investigation form data: {err}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    
    return render_template('investigation_report.html', locations=locations, recent_students=recent_students)

# ====================================
# DATABASE ARCHIVING & BACKUP SYSTEM
# ====================================

def search_logs_with_archives(target_student=None, target_location=None, incident_date=None, time_range_hours=24):
    """Search both current logs and archived logs for investigations"""
    investigation_data = {
        'target_info': {},
        'timeline': [],
        'security_alerts': [],
        'data_sources': []
    }
    
    conn = get_db_connection()
    if not conn:
        return investigation_data
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Determine date range for search
        if incident_date:
            incident_datetime = datetime.fromisoformat(incident_date.replace('Z', '+00:00'))
            start_time = incident_datetime - timedelta(hours=time_range_hours)
            end_time = incident_datetime + timedelta(hours=time_range_hours)
        else:
            end_time = datetime.now()
            start_time = end_time - timedelta(days=7)
        
        # Search current access_logs table (last 30 days)
        current_results = search_current_logs(cursor, target_student, target_location, start_time, end_time)
        investigation_data['timeline'].extend(current_results)
        investigation_data['data_sources'].append('current_database')
        
        # Check if we need to search archived data
        if start_time < datetime.now() - timedelta(days=30):
            archived_results = search_archived_logs(target_student, target_location, start_time, end_time)
            investigation_data['timeline'].extend(archived_results)
            if archived_results:
                investigation_data['data_sources'].append('archived_files')
        
        # Get target student info if provided
        if target_student:
            cursor.execute("""
                SELECT s.*, COUNT(al.log_id) as total_accesses
                FROM students s
                LEFT JOIN access_logs al ON s.student_id = al.student_id
                WHERE s.student_id = %s OR s.full_name LIKE %s
                GROUP BY s.student_id
            """, (target_student, f"%{target_student}%"))
            investigation_data['target_info'] = cursor.fetchone() or {}
        
        # Get security alerts
        if incident_date:
            cursor.execute("""
                SELECT sa.*, cl.location_name, s.full_name
                FROM security_alerts sa
                LEFT JOIN campus_locations cl ON sa.location_id = cl.location_id
                LEFT JOIN students s ON sa.student_id = s.student_id
                WHERE DATE(sa.alert_time) = DATE(%s)
                ORDER BY sa.alert_time DESC
            """, (incident_date,))
            investigation_data['security_alerts'] = cursor.fetchall()
        
        # Sort combined timeline by access_time
        investigation_data['timeline'] = sorted(
            investigation_data['timeline'], 
            key=lambda x: x.get('access_time', datetime.min)
        )
        
    except mysql.connector.Error as err:
        logger.error(f"Error searching logs with archives: {err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
    
    return investigation_data

def search_current_logs(cursor, target_student, target_location, start_time, end_time):
    """Search current access_logs table"""
    conditions = ["al.access_time BETWEEN %s AND %s"]
    params = [start_time, end_time]
    
    if target_student:
        conditions.append("(s.student_id = %s OR s.full_name LIKE %s)")
        params.extend([target_student, f"%{target_student}%"])
    
    if target_location:
        conditions.append("al.location_id = %s")
        params.append(target_location)
    
    query = """
        SELECT al.*, s.full_name, s.student_id, s.photo_url,
               cl.location_name, cl.building, 'current' as data_source
        FROM access_logs al
        LEFT JOIN students s ON al.student_id = s.student_id
        LEFT JOIN campus_locations cl ON al.location_id = cl.location_id
        WHERE """ + " AND ".join(conditions) + """
        ORDER BY al.access_time ASC
    """
    
    cursor.execute(query, params)
    return cursor.fetchall()

def search_archived_logs(target_student, target_location, start_time, end_time):
    """Search archived log files"""
    import os
    import csv
    from pathlib import Path
    
    archived_results = []
    archive_dir = Path("archive/access_logs")
    
    if not archive_dir.exists():
        return archived_results
    
    # Search through archived CSV files
    for archive_file in archive_dir.glob("*.csv"):
        try:
            with open(archive_file, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        row_time = datetime.fromisoformat(row['access_time'])
                        
                        # Check if within time range
                        if start_time <= row_time <= end_time:
                            # Apply filters
                            if target_student:
                                if not (target_student in row.get('full_name', '') or 
                                       target_student in row.get('student_id', '')):
                                    continue
                            
                            if target_location:
                                if str(target_location) != str(row.get('location_id', '')):
                                    continue
                            
                            # Convert string values back to appropriate types
                            archived_log = {
                                'access_time': row_time,
                                'full_name': row.get('full_name'),
                                'student_id': row.get('student_id'),
                                'photo_url': row.get('photo_url'),
                                'location_name': row.get('location_name'),
                                'building': row.get('building'),
                                'access_granted': row.get('access_granted', '').lower() == 'true',
                                'denial_reason': row.get('denial_reason'),
                                'risk_score': int(row.get('risk_score', 0)) if row.get('risk_score') else 0,
                                'card_id': row.get('card_id'),
                                'access_type': row.get('access_type'),
                                'data_source': 'archived'
                            }
                            
                            archived_results.append(archived_log)
                    except (ValueError, KeyError) as e:
                        continue  # Skip malformed rows
                        
        except (IOError, csv.Error) as e:
            logger.error(f"Error reading archive file {archive_file}: {e}")
            continue
    
    return archived_results

@app.route('/admin/database_management')
@require_auth('all')
def database_management():
    """Database management interface for archiving and backups"""
    conn = get_db_connection()
    db_stats = {
        'current_logs': 0,
        'archived_logs': 0,
        'database_size': '0 MB',
        'oldest_record': None,
        'archive_available': False,
        'last_backup': None,
        'retention_days': 30
    }
    
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Get current log count
            cursor.execute("SELECT COUNT(*) as count FROM access_logs")
            db_stats['current_logs'] = cursor.fetchone()['count']
            
            # Get oldest record
            cursor.execute("SELECT MIN(access_time) as oldest FROM access_logs")
            oldest = cursor.fetchone()['oldest']
            db_stats['oldest_record'] = oldest.strftime('%Y-%m-%d') if oldest else None
            
            # Get database size (approximate)
            cursor.execute("""
                SELECT 
                    ROUND(SUM(data_length + index_length) / 1024 / 1024, 1) AS size_mb
                FROM information_schema.tables 
                WHERE table_schema = DATABASE()
            """)
            result = cursor.fetchone()
            db_stats['database_size'] = f"{result['size_mb'] or 0} MB"
            
            # Check for archive directory
            import os
            archive_dir = "archive/access_logs"
            if os.path.exists(archive_dir):
                db_stats['archive_available'] = True
                # Count archived files
                db_stats['archived_logs'] = len([f for f in os.listdir(archive_dir) if f.endswith('.csv')])
            
            # Check last backup (from system settings)
            cursor.execute("SELECT setting_value FROM system_settings WHERE setting_key = 'last_backup_date'")
            backup_result = cursor.fetchone()
            if backup_result:
                db_stats['last_backup'] = backup_result['setting_value']
            
        except mysql.connector.Error as err:
            logger.error(f"Error fetching database stats: {err}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    
    return render_template('database_management.html', db_stats=db_stats)

@app.route('/admin/archive_old_logs', methods=['POST'])
@require_auth('all')
def archive_old_logs():
    """Archive access logs older than specified days"""
    data = request.get_json() if request.is_json else request.form
    retention_days = int(data.get('retention_days', 30))
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database connection failed'})
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Calculate cutoff date
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        # Get logs to archive
        cursor.execute("""
            SELECT al.*, s.full_name, s.student_id, s.photo_url, s.program,
                   cl.location_name, cl.building, cl.access_level
            FROM access_logs al
            LEFT JOIN students s ON al.student_id = s.student_id
            LEFT JOIN campus_locations cl ON al.location_id = cl.location_id
            WHERE al.access_time < %s
            ORDER BY al.access_time
        """, (cutoff_date,))
        
        logs_to_archive = cursor.fetchall()
        
        if not logs_to_archive:
            return jsonify({'success': True, 'archived_count': 0, 'message': 'No logs to archive'})
        
        # Create archive
        archive_success = create_archive_file(logs_to_archive, cutoff_date)
        
        if archive_success:
            # Delete archived logs from main table
            cursor.execute("DELETE FROM access_logs WHERE access_time < %s", (cutoff_date,))
            conn.commit()
            
            # Log the archiving action
            log_security_event(
                'database_archived',
                f'Archived {len(logs_to_archive)} access logs older than {retention_days} days',
                request.current_user['user_id']
            )
            
            return jsonify({
                'success': True, 
                'archived_count': len(logs_to_archive),
                'message': f'Successfully archived {len(logs_to_archive)} logs'
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to create archive file'})
            
    except mysql.connector.Error as err:
        logger.error(f"Error archiving logs: {err}")
        return jsonify({'success': False, 'error': str(err)})
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def create_archive_file(logs_data, cutoff_date):
    """Create CSV archive file for old logs"""
    import os
    import csv
    from pathlib import Path
    
    try:
        # Create archive directory
        archive_dir = Path("archive/access_logs")
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        # Create filename with date range
        filename = f"access_logs_archive_{cutoff_date.strftime('%Y%m%d')}.csv"
        filepath = archive_dir / filename
        
        # Write CSV file
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            if logs_data:
                fieldnames = [
                    'log_id', 'access_time', 'student_id', 'full_name', 'program',
                    'card_id', 'location_id', 'location_name', 'building', 'access_level',
                    'access_type', 'access_granted', 'denial_reason', 'risk_score',
                    'ip_address', 'user_agent', 'photo_url'
                ]
                
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for log in logs_data:
                    # Convert datetime to ISO string for CSV storage
                    log_copy = dict(log)
                    if log_copy.get('access_time'):
                        log_copy['access_time'] = log_copy['access_time'].isoformat()
                    writer.writerow(log_copy)
        
        logger.info(f"Created archive file: {filepath}")
        return True
        
    except (IOError, csv.Error) as e:
        logger.error(f"Error creating archive file: {e}")
        return False

@app.route('/admin/create_backup', methods=['POST'])
@require_auth('all')
def create_database_backup():
    """Create complete database backup"""
    import subprocess
    import os
    from datetime import datetime
    
    try:
        # Create backup directory
        backup_dir = Path("backups")
        backup_dir.mkdir(exist_ok=True)
        
        # Create backup filename
        backup_filename = f"campus_security_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
        backup_path = backup_dir / backup_filename
        
        # Create mysqldump command
        dump_cmd = [
            'mysqldump',
            '--host', DB_CONFIG['host'],
            '--user', DB_CONFIG['user'],
            '--password=' + DB_CONFIG['password'],
            '--single-transaction',
            '--routines',
            '--triggers',
            DB_CONFIG['database']
        ]
        
        # Execute backup
        with open(backup_path, 'w') as f:
            result = subprocess.run(dump_cmd, stdout=f, stderr=subprocess.PIPE, text=True)
        
        if result.returncode == 0:
            # Update last backup time in settings
            conn = get_db_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO system_settings (setting_key, setting_value, description)
                        VALUES ('last_backup_date', %s, 'Last database backup timestamp')
                        ON DUPLICATE KEY UPDATE setting_value = %s
                    """, (datetime.now().isoformat(), datetime.now().isoformat()))
                    conn.commit()
                except mysql.connector.Error:
                    pass  # Non-critical error
                finally:
                    cursor.close()
                    conn.close()
            
            # Log backup action
            log_security_event(
                'database_backup_created',
                f'Database backup created: {backup_filename}',
                request.current_user['user_id']
            )
            
            return jsonify({
                'success': True,
                'backup_file': backup_filename,
                'backup_size': f"{os.path.getsize(backup_path) / (1024*1024):.1f} MB"
            })
        else:
            logger.error(f"Backup failed: {result.stderr}")
            return jsonify({'success': False, 'error': result.stderr})
            
    except Exception as e:
        logger.error(f"Backup error: {e}")
        return jsonify({'success': False, 'error': str(e)})

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