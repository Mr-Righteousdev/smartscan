# Smart Campus ID Security System - Virtual Simulation
# St. Lawrence University - Cybersecurity Club
# Flask Web Application

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import mysql.connector
from datetime import datetime, timedelta
import secrets
import hashlib
import json
from functools import wraps

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Generate secure secret key

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
        print(f"Database connection error: {err}")
        return None

def log_access_attempt(student_id, card_id, location_id, access_type, granted=True, denial_reason=None):
    """Log access attempt to database"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        query = """
            INSERT INTO access_logs (student_id, card_id, location_id, access_type, 
                                   access_granted, denial_reason, ip_address, user_agent)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            student_id, card_id, location_id, access_type,
            granted, denial_reason, 
            request.remote_addr if request else 'simulation',
            request.headers.get('User-Agent') if request else 'virtual_scanner'
        ))
        conn.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Error logging access: {err}")
        return False
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def create_security_alert(alert_type, severity, location_id, student_id=None, card_id=None, message=""):
    """Create security alert"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        query = """
            INSERT INTO security_alerts (alert_type, severity, location_id, student_id, 
                                       card_id, alert_message)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (alert_type, severity, location_id, student_id, card_id, message))
        conn.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Error creating alert: {err}")
        return False
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def is_card_lost_or_stolen(card_id):
    """Check if card is reported as lost or stolen"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        query = """
            SELECT COUNT(*) FROM lost_stolen_cards 
            WHERE card_id = %s AND status = 'active'
        """
        cursor.execute(query, (card_id,))
        result = cursor.fetchone()
        return result[0] > 0
    except mysql.connector.Error as err:
        print(f"Error checking lost/stolen status: {err}")
        return False
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/')
def index():
    """Main virtual campus interface"""
    # Get all campus locations for the virtual map
    conn = get_db_connection()
    locations = []
    
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM campus_locations WHERE is_active = TRUE ORDER BY building, location_name")
            locations = cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Error fetching locations: {err}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    
    return render_template('virtual_campus.html', locations=locations)

@app.route('/scan_card', methods=['POST'])
def scan_card():
    """Simulate RFID card scan"""
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
            # Unknown card - create alert
            create_security_alert('unauthorized_access', 'high', location_id, 
                                card_id=card_id, 
                                message=f'Unknown card {card_id} attempted access')
            log_access_attempt(None, card_id, location_id, access_type, False, 'Unknown card')
            return jsonify({
                'success': False, 
                'message': 'ACCESS DENIED: Unknown card',
                'alert': True,
                'alert_type': 'unauthorized_access'
            })
        
        # Check if student is active
        if student['status'] != 'active':
            log_access_attempt(student['student_id'], card_id, location_id, access_type, 
                             False, f'Student status: {student["status"]}')
            return jsonify({
                'success': False, 
                'message': f'ACCESS DENIED: Student status is {student["status"]}',
                'student_name': student['full_name']
            })
        
        # Check if card is lost or stolen
        if is_card_lost_or_stolen(card_id):
            create_security_alert('lost_card_used', 'critical', location_id, 
                                student['student_id'], card_id,
                                message=f'Lost/stolen card used by {student["full_name"]}')
            log_access_attempt(student['student_id'], card_id, location_id, access_type, 
                             False, 'Card reported as lost/stolen')
            return jsonify({
                'success': False, 
                'message': 'ACCESS DENIED: Card reported as lost/stolen',
                'alert': True,
                'alert_type': 'lost_card_used',
                'student_name': student['full_name']
            })
        
        # Get location info
        cursor.execute("SELECT * FROM campus_locations WHERE location_id = %s", (location_id,))
        location = cursor.fetchone()
        
        # Check access level permissions (simplified for simulation)
        if location and location['access_level'] == 'staff_only':
            log_access_attempt(student['student_id'], card_id, location_id, access_type, 
                             False, 'Insufficient access level')
            return jsonify({
                'success': False, 
                'message': 'ACCESS DENIED: Staff access required',
                'student_name': student['full_name'],
                'location_name': location['location_name']
            })
        
        # Access granted - log successful entry
        log_access_attempt(student['student_id'], card_id, location_id, access_type, True)
        
        return jsonify({
            'success': True, 
            'message': f'ACCESS GRANTED',
            'student_name': student['full_name'],
            'student_id': student['student_id'],
            'location_name': location['location_name'] if location else 'Unknown Location',
            'access_type': access_type.upper(),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except mysql.connector.Error as err:
        print(f"Database error during card scan: {err}")
        return jsonify({'success': False, 'message': 'System error occurred'})
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/dashboard')
def dashboard():
    """Security monitoring dashboard"""
    conn = get_db_connection()
    dashboard_data = {
        'recent_access': [],
        'active_alerts': [],
        'stats': {
            'total_access_today': 0,
            'denied_access_today': 0,
            'active_alerts': 0,
            'total_students': 0
        }
    }
    
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Get recent access logs (last 50)
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
            
            # Get statistics for today
            today = datetime.now().strftime('%Y-%m-%d')
            
            cursor.execute("""
                SELECT COUNT(*) as total FROM access_logs 
                WHERE DATE(access_time) = %s
            """, (today,))
            dashboard_data['stats']['total_access_today'] = cursor.fetchone()['total']
            
            cursor.execute("""
                SELECT COUNT(*) as denied FROM access_logs 
                WHERE DATE(access_time) = %s AND access_granted = FALSE
            """, (today,))
            dashboard_data['stats']['denied_access_today'] = cursor.fetchone()['denied']
            
            cursor.execute("""
                SELECT COUNT(*) as alerts FROM security_alerts 
                WHERE status IN ('new', 'acknowledged', 'investigating')
            """)
            dashboard_data['stats']['active_alerts'] = cursor.fetchone()['alerts']
            
            cursor.execute("SELECT COUNT(*) as students FROM students WHERE status = 'active'")
            dashboard_data['stats']['total_students'] = cursor.fetchone()['students']
            
        except mysql.connector.Error as err:
            print(f"Dashboard data error: {err}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    
    return render_template('dashboard.html', data=dashboard_data)

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
            print(f"Error fetching students: {err}")
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
            print(f"Recent activity error: {err}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    
    return jsonify(activity)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)