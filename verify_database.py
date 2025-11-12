#!/usr/bin/env python3
"""
Database Verification Script
Smart Campus Security System - St. Lawrence University
"""

import mysql.connector
import sys
from datetime import datetime

# Database configuration (same as app.py)
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',  # Change to your MySQL username
    'password': '',  # Change to your MySQL password
    'database': 'smart_campus_security',
    'autocommit': True
}

def test_database_connection():
    """Test basic database connectivity"""
    print("🔍 Testing database connection...")
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        print("✅ Database connection successful!")
        return conn
    except mysql.connector.Error as err:
        print(f"❌ Database connection failed: {err}")
        print("\n💡 Common solutions:")
        print("   1. Check if MySQL is running: sudo systemctl status mysql")
        print("   2. Verify database credentials in DB_CONFIG")
        print("   3. Check if database exists: SHOW DATABASES;")
        return None

def check_database_exists(cursor):
    """Check if the smart_campus_security database exists"""
    print("\n🔍 Checking if database exists...")
    try:
        cursor.execute("SELECT DATABASE()")
        current_db = cursor.fetchone()
        if current_db and current_db[0] == 'smart_campus_security':
            print("✅ Database 'smart_campus_security' exists and is selected!")
            return True
        else:
            print(f"❌ Wrong database selected: {current_db}")
            return False
    except mysql.connector.Error as err:
        print(f"❌ Error checking database: {err}")
        return False

def check_tables(cursor):
    """Check if all required tables exist"""
    print("\n🔍 Checking required tables...")
    
    required_tables = [
        'students',
        'campus_locations', 
        'access_logs',
        'security_alerts',
        'system_users',
        'security_audit_log'
    ]
    
    try:
        cursor.execute("SHOW TABLES")
        existing_tables = [table[0] for table in cursor.fetchall()]
        
        print(f"📋 Found {len(existing_tables)} tables: {existing_tables}")
        
        missing_tables = []
        for table in required_tables:
            if table in existing_tables:
                print(f"✅ Table '{table}' exists")
            else:
                print(f"❌ Table '{table}' missing!")
                missing_tables.append(table)
        
        if missing_tables:
            print(f"\n⚠️ Missing tables: {missing_tables}")
            print("💡 Run: mysql -u root -p < database_setup.sql")
            return False
        
        return True
        
    except mysql.connector.Error as err:
        print(f"❌ Error checking tables: {err}")
        return False

def check_sample_data(cursor):
    """Check if sample data exists"""
    print("\n🔍 Checking sample data...")
    
    try:
        # Check students
        cursor.execute("SELECT COUNT(*) FROM students")
        student_count = cursor.fetchone()[0]
        print(f"👥 Students: {student_count}")
        
        if student_count > 0:
            cursor.execute("SELECT student_id, full_name, card_id FROM students LIMIT 3")
            students = cursor.fetchall()
            for student in students:
                print(f"   - {student[0]}: {student[1]} (Card: {student[2]})")
        
        # Check locations
        cursor.execute("SELECT COUNT(*) FROM campus_locations")
        location_count = cursor.fetchone()[0]
        print(f"📍 Locations: {location_count}")
        
        if location_count > 0:
            cursor.execute("SELECT location_id, location_name, building FROM campus_locations LIMIT 5")
            locations = cursor.fetchall()
            for location in locations:
                print(f"   - ID {location[0]}: {location[1]} ({location[2]})")
        
        # Check access logs
        cursor.execute("SELECT COUNT(*) FROM access_logs")
        log_count = cursor.fetchone()[0]
        print(f"📝 Access logs: {log_count}")
        
        # Check system users
        cursor.execute("SELECT COUNT(*) FROM system_users")
        user_count = cursor.fetchone()[0]
        print(f"👤 System users: {user_count}")
        
        if user_count > 0:
            cursor.execute("SELECT username, full_name, role FROM system_users")
            users = cursor.fetchall()
            for user in users:
                print(f"   - {user[0]}: {user[1]} ({user[2]})")
        
        # Verify data integrity
        if student_count == 0:
            print("⚠️ No students found! Run database_setup.sql")
            return False
        
        if location_count == 0:
            print("⚠️ No locations found! Run database_setup.sql")
            return False
            
        return True
        
    except mysql.connector.Error as err:
        print(f"❌ Error checking sample data: {err}")
        return False

def test_queries(cursor):
    """Test common queries used by the application"""
    print("\n🔍 Testing application queries...")
    
    try:
        # Test student lookup by card
        test_card = 'RFID_001_ABC123'
        cursor.execute("SELECT * FROM students WHERE card_id = %s", (test_card,))
        student = cursor.fetchone()
        
        if student:
            print(f"✅ Student lookup works: Found {student[2]} with card {test_card}")
        else:
            print(f"❌ Student lookup failed: No student found with card {test_card}")
            return False
        
        # Test location lookup
        test_location_id = 1
        cursor.execute("SELECT * FROM campus_locations WHERE location_id = %s", (test_location_id,))
        location = cursor.fetchone()
        
        if location:
            print(f"✅ Location lookup works: Found {location[1]} with ID {test_location_id}")
        else:
            print(f"❌ Location lookup failed: No location found with ID {test_location_id}")
            return False
        
        # Test access log insertion
        cursor.execute("""
            INSERT INTO access_logs (student_id, card_id, location_id, access_type, access_granted)
            VALUES (%s, %s, %s, %s, %s)
        """, (student[0], test_card, test_location_id, 'entry', True))
        
        print("✅ Access log insertion works")
        
        return True
        
    except mysql.connector.Error as err:
        print(f"❌ Error testing queries: {err}")
        return False

def check_permissions(cursor):
    """Check database permissions"""
    print("\n🔍 Checking database permissions...")
    
    try:
        # Test basic operations
        cursor.execute("SELECT 1")  # SELECT permission
        print("✅ SELECT permission works")
        
        # Test if we can insert (already tested above)
        print("✅ INSERT permission works")
        
        # Test if we can update
        cursor.execute("SELECT log_id FROM access_logs ORDER BY log_id DESC LIMIT 1")
        result = cursor.fetchone()
        if result:
            log_id = result[0]
            cursor.execute("UPDATE access_logs SET access_granted = access_granted WHERE log_id = %s", (log_id,))
            print("✅ UPDATE permission works")
        
        return True
        
    except mysql.connector.Error as err:
        print(f"❌ Permission error: {err}")
        return False

def main():
    print("🤖 Smart Campus Security System - Database Verification")
    print("=" * 60)
    
    # Test connection
    conn = test_database_connection()
    if not conn:
        sys.exit(1)
    
    cursor = conn.cursor(dictionary=True)
    
    # Run all checks
    checks = [
        check_database_exists(cursor),
        check_tables(cursor),
        check_sample_data(cursor),
        test_queries(cursor),
        check_permissions(cursor)
    ]
    
    # Summary
    print("\n" + "="*60)
    passed_checks = sum(checks)
    total_checks = len(checks)
    
    if passed_checks == total_checks:
        print("🎉 All database checks passed! Your database is ready.")
        print("\n✅ You can now run: python app.py")
    else:
        print(f"⚠️ {total_checks - passed_checks} checks failed out of {total_checks}")
        print("\n💡 Suggested fixes:")
        print("   1. Run the database setup: mysql -u root -p < database_setup.sql")
        print("   2. Check MySQL service: sudo systemctl start mysql")
        print("   3. Verify database credentials in app.py")
        print("   4. Check MySQL error logs")
    
    # Show current database status
    print(f"\n📊 Current Database Status:")
    try:
        cursor.execute("SELECT COUNT(*) FROM students")
        student_count = cursor.fetchone()['COUNT(*)']
        
        cursor.execute("SELECT COUNT(*) FROM campus_locations")
        location_count = cursor.fetchone()['COUNT(*)']
        
        cursor.execute("SELECT COUNT(*) FROM access_logs")
        log_count = cursor.fetchone()['COUNT(*)']
        
        print(f"   👥 Students: {student_count}")
        print(f"   📍 Locations: {location_count}")
        print(f"   📝 Access Logs: {log_count}")
        
    except:
        print("   ❌ Could not retrieve database statistics")
    
    # Cleanup
    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()