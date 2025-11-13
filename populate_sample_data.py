#!/usr/bin/env python3
"""
Smart Campus ID Security System - Sample Data Population Script
St. Lawrence University Uganda - Cybersecurity Club

This script populates the empty database with realistic sample data for demonstration purposes.
Run this AFTER setting up the empty database with database_empty_setup.sql

Usage: python3 populate_sample_data.py
"""

import mysql.connector
import hashlib
import secrets
from datetime import datetime, timedelta, date
import json
import sys

# Database configuration - Update these as needed
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'milka',  # Change to your MySQL password
    'database': 'smart_campus_security',
    'autocommit': True
}

def hash_password(password):
    """Create a simple hash for demo purposes"""
    return hashlib.sha256(password.encode()).hexdigest()

def get_db_connection():
    """Create database connection"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        print("✅ Connected to database successfully")
        return conn
    except mysql.connector.Error as err:
        print(f"❌ Database connection error: {err}")
        return None

def populate_system_users(conn):
    """Populate system users table with admin and staff accounts"""
    print("\n📝 Populating system users...")
    
    cursor = conn.cursor()
    
    users_data = [
        # (username, password, email, full_name, role)
        ('admin', 'admin123', 'admin@slau.edu.ug', 'System Administrator', 'admin'),
        ('security', 'security123', 'security@slau.edu.ug', 'Security Officer John', 'security_officer'),
        ('john_doe', 'staff123', 'john.doe@slau.edu.ug', 'John Doe', 'staff'),
        ('mary_smith', 'staff123', 'mary.smith@slau.edu.ug', 'Mary Smith', 'security_officer'),
        ('supervisor', 'super123', 'supervisor@slau.edu.ug', 'Security Supervisor', 'supervisor'),
    ]
    
    for username, password, email, full_name, role in users_data:
        password_hash = hash_password(password)
        
        query = """
            INSERT INTO system_users (username, password_hash, email, full_name, role, status, two_factor_enabled)
            VALUES (%s, %s, %s, %s, %s, 'active', %s)
        """
        cursor.execute(query, (username, password_hash, email, full_name, role, role == 'admin'))
    
    print(f"✅ Added {len(users_data)} system users")

def populate_campus_locations(conn):
    """Populate campus locations table"""
    print("\n📍 Populating campus locations...")
    
    cursor = conn.cursor()
    
    locations_data = [
        # (location_name, location_type, building, floor_level, room_number, access_level, max_occupancy, description)
        ('University Main Library', 'library', 'Central Library Building', 'Ground Floor', 'LIB-001', 'public', 200, 'Main library with study areas and computer access'),
        ('Reference Section', 'library', 'Central Library Building', '1st Floor', 'LIB-101', 'public', 50, 'Quiet study area with reference materials'),
        ('Computer Laboratory 1', 'laboratory', 'School of Computing & IT', 'Ground Floor', 'ICT-001', 'restricted', 40, 'Main computer lab for programming courses'),
        ('Computer Laboratory 2', 'laboratory', 'School of Computing & IT', '1st Floor', 'ICT-101', 'restricted', 35, 'Advanced computing lab with specialized software'),
        ('Student Center', 'recreational', 'Student Center Building', 'Ground Floor', 'SC-001', 'public', 300, 'Main student gathering area with cafeteria'),
        ('Cafeteria Main', 'cafeteria', 'Student Center Building', 'Ground Floor', 'SC-CAF', 'public', 150, 'Main dining facility for students and staff'),
        ('Lecture Hall A', 'classroom', 'Academic Block A', 'Ground Floor', 'LHA-001', 'public', 100, 'Large lecture hall for major courses'),
        ('Lecture Hall B', 'classroom', 'Academic Block A', '1st Floor', 'LHA-101', 'public', 80, 'Medium-sized lecture hall'),
        ('Tutorial Room 1', 'classroom', 'Academic Block B', 'Ground Floor', 'TR-001', 'public', 30, 'Small classroom for tutorials'),
        ('Tutorial Room 2', 'classroom', 'Academic Block B', '1st Floor', 'TR-101', 'public', 25, 'Small classroom for group work'),
        ('Science Building Main Entrance', 'entrance', 'Science Building', 'Ground Floor', 'SCI-ENT', 'public', None, 'Main entrance to science laboratories'),
        ('Administration Office', 'admin', 'Administration Building', '1st Floor', 'ADM-101', 'staff_only', 20, 'Main administrative offices'),
        ('Registrar Office', 'admin', 'Administration Building', 'Ground Floor', 'ADM-001', 'staff_only', 15, 'Student records and registration'),
        ('Security Office', 'security', 'Security Building', 'Ground Floor', 'SEC-001', 'staff_only', 10, 'Campus security headquarters'),
        ('ICT Server Room', 'maintenance', 'School of Computing & IT', 'Basement', 'ICT-B01', 'admin_only', 5, 'Network infrastructure and servers'),
        ('Chemistry Laboratory', 'laboratory', 'Science Building', '1st Floor', 'CHEM-101', 'restricted', 30, 'Chemistry lab with safety protocols'),
        ('Physics Laboratory', 'laboratory', 'Science Building', '2nd Floor', 'PHYS-201', 'restricted', 25, 'Physics experiments and equipment'),
        ('Biology Laboratory', 'laboratory', 'Science Building', '1st Floor', 'BIO-101', 'restricted', 35, 'Biology and life sciences lab'),
        ('Engineering Workshop', 'laboratory', 'Engineering Building', 'Ground Floor', 'ENG-001', 'restricted', 20, 'Mechanical and electrical workshop'),
        ('Dormitory Block A', 'dormitory', 'Residential Area', 'Multi-floor', 'DORM-A', 'restricted', 100, 'Student accommodation block A'),
        ('Sports Complex', 'recreational', 'Sports Center', 'Ground Floor', 'SPORT-001', 'public', 500, 'Indoor sports facilities and gymnasium'),
        ('Medical Center', 'admin', 'Health Center', 'Ground Floor', 'MED-001', 'restricted', 20, 'Campus health and medical services'),
    ]
    
    for location_data in locations_data:
        query = """
            INSERT INTO campus_locations (location_name, location_type, building, floor_level, room_number, 
                                        access_level, max_occupancy, description, current_occupancy)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        # Add random current occupancy (0-50% of max)
        current_occupancy = 0 if location_data[5] is None else secrets.randbelow(int(location_data[5] * 0.5) + 1)
        cursor.execute(query, location_data + (current_occupancy,))
    
    print(f"✅ Added {len(locations_data)} campus locations")

def populate_students(conn):
    """Populate students table with realistic St. Lawrence University data"""
    print("\n👩‍🎓 Populating student records...")
    
    cursor = conn.cursor()
    
    # Sample student data with St. Lawrence University format
    students_data = [
        # Computer Science Students
        ('BACS/21D/U/A0145', 'RFID_BACS_21A_145', 'Atim Patricia', 'patricia.atim@slau.edu.ug', '+256701234567', 'BACS', 3),
        ('BACS/22D/U/A0024', 'RFID_BACS_22A_024', 'Nakato Sarah', 'sarah.nakato@slau.edu.ug', '+256702345678', 'BACS', 2),
        ('BACS/23D/U/A0156', 'RFID_BACS_23A_156', 'Okello James', 'james.okello@slau.edu.ug', '+256703456789', 'BACS', 1),
        ('BACS/21D/U/A0089', 'RFID_BACS_21A_089', 'Namutebi Grace', 'grace.namutebi@slau.edu.ug', '+256704567890', 'BACS', 3),
        ('BACS/22D/U/A0192', 'RFID_BACS_22A_192', 'Byaruhanga Moses', 'moses.byaruhanga@slau.edu.ug', '+256705678901', 'BACS', 2),
        
        # Information Technology Students
        ('BIT/21D/U/A0067', 'RFID_BIT_21A_067', 'Namukasa Joy', 'joy.namukasa@slau.edu.ug', '+256706789012', 'BIT', 3),
        ('BIT/22D/U/A0134', 'RFID_BIT_22A_134', 'Tumusiime David', 'david.tumusiime@slau.edu.ug', '+256707890123', 'BIT', 2),
        ('BIT/23D/U/A0078', 'RFID_BIT_23A_078', 'Akello Martha', 'martha.akello@slau.edu.ug', '+256708901234', 'BIT', 1),
        ('BIT/21D/U/A0203', 'RFID_BIT_21A_203', 'Ssemwanga John', 'john.ssemwanga@slau.edu.ug', '+256709012345', 'BIT', 3),
        ('BIT/22D/U/A0045', 'RFID_BIT_22A_045', 'Nabirye Susan', 'susan.nabirye@slau.edu.ug', '+256700123456', 'BIT', 2),
        
        # Engineering Students
        ('BENG/21D/U/A0112', 'RFID_BENG_21A_112', 'Opolot Francis', 'francis.opolot@slau.edu.ug', '+256711234567', 'BENG', 3),
        ('BENG/22D/U/A0087', 'RFID_BENG_22A_087', 'Kamya Rebecca', 'rebecca.kamya@slau.edu.ug', '+256712345678', 'BENG', 2),
        ('BENG/23D/U/A0156', 'RFID_BENG_23A_156', 'Mubarak Ali', 'ali.mubarak@slau.edu.ug', '+256713456789', 'BENG', 1),
        
        # Business Students
        ('BBUS/21D/U/A0234', 'RFID_BBUS_21A_234', 'Nalukenge Esther', 'esther.nalukenge@slau.edu.ug', '+256714567890', 'BBUS', 3),
        ('BBUS/22D/U/A0167', 'RFID_BBUS_22A_167', 'Kayemba Peter', 'peter.kayemba@slau.edu.ug', '+256715678901', 'BBUS', 2),
        ('BBUS/23D/U/A0089', 'RFID_BBUS_23A_089', 'Namusoke Diana', 'diana.namusoke@slau.edu.ug', '+256716789012', 'BBUS', 1),
        
        # Additional diverse students
        ('BACS/20D/U/A0145', 'RFID_BACS_20A_145', 'Kiprotich Samuel', 'samuel.kiprotich@slau.edu.ug', '+256717890123', 'BACS', 4),
        ('BIT/20D/U/A0234', 'RFID_BIT_20A_234', 'Namuli Christine', 'christine.namuli@slau.edu.ug', '+256718901234', 'BIT', 4),
        ('BENG/21D/U/A0045', 'RFID_BENG_21A_045', 'Otim Patrick', 'patrick.otim@slau.edu.ug', '+256719012345', 'BENG', 3),
        ('BBUS/21D/U/A0178', 'RFID_BBUS_21A_178', 'Nansubuga Mary', 'mary.nansubuga@slau.edu.ug', '+256720123456', 'BBUS', 3),
    ]
    
    current_date = date.today()
    
    for student_data in students_data:
        # Calculate card expiry (4 years from current date for undergraduates)
        card_expiry = current_date + timedelta(days=365 * (5 - student_data[6]))  # Years remaining
        
        query = """
            INSERT INTO students (student_id, card_id, full_name, email, phone, program, year_of_study, 
                                status, card_issued_date, card_expiry_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'active', %s, %s)
        """
        cursor.execute(query, student_data + (current_date, card_expiry))
    
    print(f"✅ Added {len(students_data)} student records")

def populate_access_policies(conn):
    """Populate access control policies"""
    print("\n📋 Populating access control policies...")
    
    cursor = conn.cursor()
    
    # Get first admin user ID for created_by
    cursor.execute("SELECT user_id FROM system_users WHERE role = 'admin' LIMIT 1")
    admin_id = cursor.fetchone()[0]
    
    policies_data = [
        # Time-based policies
        ('Night Access Restriction', 'time_based', 'Restricts student access during night hours', '22:00:00', '06:00:00', 'monday,tuesday,wednesday,thursday,friday,saturday,sunday', None, 'all', 3, 'require_additional_auth', True, True),
        ('Weekend Laboratory Access', 'time_based', 'Limited weekend access to laboratories', '08:00:00', '18:00:00', 'saturday,sunday', None, 'student', 2, 'require_additional_auth', True, True),
        ('Business Hours Policy', 'time_based', 'Standard business hours access', '08:00:00', '17:00:00', 'monday,tuesday,wednesday,thursday,friday', None, 'all', 1, 'allow', True, False),
        
        # Location-based policies
        ('Server Room Access', 'location_based', 'Restricted access to ICT server room', None, None, None, 15, 'admin', 5, 'deny', True, True),
        ('Laboratory Safety Policy', 'location_based', 'Safety requirements for laboratory access', None, None, None, 16, 'all', 3, 'require_additional_auth', True, True),
        ('Administrative Office Policy', 'location_based', 'Staff access to administration offices', None, None, None, 12, 'staff', 2, 'allow', True, True),
        
        # Risk-based policies
        ('High Risk Access Control', 'risk_based', 'Additional authentication for high-risk access', None, None, None, None, 'all', 4, 'require_additional_auth', True, True),
        ('Critical Area Monitoring', 'risk_based', 'Enhanced monitoring for critical areas', None, None, None, None, 'all', 5, 'notify_security', True, True),
    ]
    
    for policy_data in policies_data:
        query = """
            INSERT INTO access_policies (policy_name, policy_type, description, time_start, time_end, 
                                       days_of_week, location_id, target_role, risk_threshold, action, 
                                       is_active, log_violations, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, policy_data + (admin_id,))
    
    print(f"✅ Added {len(policies_data)} access policies")

def populate_sample_access_logs(conn):
    """Populate with realistic access log entries"""
    print("\n📝 Populating sample access logs...")
    
    cursor = conn.cursor()
    
    # Get some student and location IDs
    cursor.execute("SELECT student_id, card_id FROM students LIMIT 10")
    students = cursor.fetchall()
    
    cursor.execute("SELECT location_id FROM campus_locations WHERE access_level = 'public' LIMIT 5")
    public_locations = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT location_id FROM campus_locations WHERE access_level = 'restricted' LIMIT 3")
    restricted_locations = [row[0] for row in cursor.fetchall()]
    
    # Create realistic access logs for the past week
    import random
    
    access_logs = []
    now = datetime.now()
    
    for days_ago in range(7):  # Past week
        day_start = now - timedelta(days=days_ago)
        
        for _ in range(random.randint(15, 30)):  # 15-30 access attempts per day
            student_id, card_id = random.choice(students)
            
            # 80% public locations, 20% restricted
            if random.random() < 0.8:
                location_id = random.choice(public_locations)
                access_granted = True
                risk_score = random.randint(1, 3)
            else:
                location_id = random.choice(restricted_locations)
                access_granted = random.choice([True, True, True, False])  # 75% success rate
                risk_score = random.randint(2, 4) if access_granted else random.randint(3, 5)
            
            # Random time during the day (mostly business hours)
            if random.random() < 0.7:  # 70% during business hours
                hour = random.randint(8, 17)
            else:
                hour = random.randint(6, 23)
            
            access_time = day_start.replace(hour=hour, minute=random.randint(0, 59), second=random.randint(0, 59))
            access_type = random.choice(['entry', 'entry', 'entry', 'exit'])  # More entries than exits
            
            denial_reason = None if access_granted else random.choice([
                'Insufficient access level',
                'Card expired',
                'Outside allowed hours',
                'Unknown card'
            ])
            
            access_logs.append((student_id, card_id, location_id, access_time, access_type, access_granted, denial_reason, risk_score))
    
    # Bulk insert access logs
    query = """
        INSERT INTO access_logs (student_id, card_id, location_id, access_time, access_type, 
                               access_granted, denial_reason, risk_score)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.executemany(query, access_logs)
    
    print(f"✅ Added {len(access_logs)} access log entries")

def populate_security_alerts(conn):
    """Populate with sample security alerts"""
    print("\n🚨 Populating security alerts...")
    
    cursor = conn.cursor()
    
    # Get some student and location IDs
    cursor.execute("SELECT student_id, card_id FROM students LIMIT 5")
    students = cursor.fetchall()
    
    cursor.execute("SELECT location_id FROM campus_locations LIMIT 5")
    locations = [row[0] for row in cursor.fetchall()]
    
    alerts_data = [
        ('unauthorized_access', 'high', locations[0], None, 'UNKNOWN_CARD_123', 'Unknown card attempted access to restricted area', datetime.now() - timedelta(hours=2), 'new'),
        ('suspicious_activity', 'medium', locations[1], students[0][0], students[0][1], 'Multiple rapid access attempts detected', datetime.now() - timedelta(hours=6), 'acknowledged'),
        ('policy_violation', 'low', locations[2], students[1][0], students[1][1], 'Access attempt outside allowed hours', datetime.now() - timedelta(hours=12), 'resolved'),
        ('high_risk_access', 'high', locations[3], students[2][0], students[2][1], 'High-risk behavior pattern detected', datetime.now() - timedelta(hours=1), 'new'),
        ('lost_card_used', 'critical', locations[4], students[3][0], students[3][1], 'Previously reported lost card used for access', datetime.now() - timedelta(minutes=30), 'investigating'),
    ]
    
    for alert_data in alerts_data:
        query = """
            INSERT INTO security_alerts (alert_type, severity, location_id, student_id, card_id, 
                                       alert_message, alert_time, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, alert_data)
    
    print(f"✅ Added {len(alerts_data)} security alerts")

def populate_security_incidents(conn):
    """Populate with sample security incidents"""
    print("\n🚨 Populating security incidents...")
    
    cursor = conn.cursor()
    
    # Get security officer user ID
    cursor.execute("SELECT user_id FROM system_users WHERE role = 'security_officer' LIMIT 1")
    security_officer_id = cursor.fetchone()[0]
    
    incidents_data = [
        ('unauthorized_access', 'medium', 'Unknown Card Access Investigation', 'Investigation into multiple unauthorized access attempts using unregistered cards', 1, security_officer_id, 'investigating', 'high'),
        ('suspicious_activity', 'high', 'Off-Hours Access Pattern Analysis', 'Student accessing multiple secure locations during restricted hours - potential policy violation', 2, security_officer_id, 'in_progress', 'medium'),
        ('policy_violation', 'low', 'Tailgating Incident Report', 'Multiple card scans detected at same location within seconds - possible tailgating', 3, None, 'new', 'low'),
        ('system_breach', 'critical', 'Security System Anomaly', 'Unusual patterns detected in access control system requiring immediate investigation', None, security_officer_id, 'investigating', 'urgent'),
    ]
    
    for incident_data in incidents_data:
        query = """
            INSERT INTO security_incidents (incident_type, severity, title, description, location_id, 
                                          detected_by, assigned_to, status, priority)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, incident_data)
    
    print(f"✅ Added {len(incidents_data)} security incidents")

def populate_encryption_keys(conn):
    """Populate with encryption key records (demo purposes)"""
    print("\n🔐 Populating encryption key records...")
    
    cursor = conn.cursor()
    
    # Get admin user ID
    cursor.execute("SELECT user_id FROM system_users WHERE role = 'admin' LIMIT 1")
    admin_id = cursor.fetchone()[0]
    
    keys_data = [
        ('Database Encryption Key', 'data_at_rest', 'AES', 256, secrets.token_hex(32), admin_id),
        ('Session Token Key', 'session_management', 'HMAC-SHA256', 256, secrets.token_hex(32), admin_id),
        ('Card Data Encryption', 'card_information', 'AES', 128, secrets.token_hex(16), admin_id),
        ('Communication Encryption', 'data_in_transit', 'RSA', 2048, secrets.token_hex(32), admin_id),
    ]
    
    for key_data in keys_data:
        # Hash the key for security (don't store actual keys)
        key_hash = hashlib.sha256(key_data[4].encode()).hexdigest()
        
        query = """
            INSERT INTO encryption_keys (key_name, key_purpose, algorithm, key_strength, key_hash, 
                                       expires_at, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        expires_at = datetime.now() + timedelta(days=365)  # 1 year expiry
        cursor.execute(query, key_data[:4] + (key_hash, expires_at, key_data[5]))
    
    print(f"✅ Added {len(keys_data)} encryption key records")

def main():
    """Main function to populate all sample data"""
    print("🚀 Smart Campus Security System - Sample Data Population")
    print("=" * 60)
    
    # Connect to database
    conn = get_db_connection()
    if not conn:
        print("❌ Failed to connect to database. Please check your configuration.")
        sys.exit(1)
    
    try:
        # Check if database is empty
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM system_users")
        user_count = cursor.fetchone()[0]
        
        if user_count > 0:
            response = input(f"⚠️  Database contains {user_count} users. Continue anyway? (y/N): ")
            if response.lower() != 'y':
                print("❌ Operation cancelled by user")
                return
        
        # Populate all tables
        populate_system_users(conn)
        populate_campus_locations(conn)
        populate_students(conn)
        populate_access_policies(conn)
        populate_sample_access_logs(conn)
        populate_security_alerts(conn)
        populate_security_incidents(conn)
        populate_encryption_keys(conn)
        
        print("\n" + "=" * 60)
        print("✅ Sample data population completed successfully!")
        print("\n📊 Database Summary:")
        
        # Show summary statistics
        tables = [
            'system_users', 'campus_locations', 'students', 'access_policies',
            'access_logs', 'security_alerts', 'security_incidents', 'encryption_keys'
        ]
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   {table}: {count} records")
        
        print("\n🔐 Demo Login Credentials:")
        print("   Admin: admin / admin123")
        print("   Security Officer: security / security123")
        print("   Staff: john_doe / staff123")
        
        print("\n🎯 Next Steps:")
        print("   1. Start the Flask application: python3 app.py")
        print("   2. Access the web interface at http://localhost:5000")
        print("   3. Login with admin credentials for full access")
        print("   4. Test card scanning with the sample student data")
        
    except Exception as e:
        print(f"❌ Error populating data: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if conn.is_connected():
            conn.close()
            print("\n🔌 Database connection closed")

if __name__ == "__main__":
    main()