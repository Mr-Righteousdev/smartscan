-- Smart Campus ID Security System - Empty Database Setup
-- St. Lawrence University Uganda - Cybersecurity Club
-- This creates an empty database structure without any sample data

-- Create database (run this first if database doesn't exist)
-- CREATE DATABASE smart_campus_security;
-- USE smart_campus_security;

-- Drop existing tables if they exist (in correct order to avoid foreign key constraints)
DROP TABLE IF EXISTS security_audit_log;
DROP TABLE IF EXISTS user_sessions;
DROP TABLE IF EXISTS lost_stolen_cards;
DROP TABLE IF EXISTS security_incidents;
DROP TABLE IF EXISTS security_alerts;
DROP TABLE IF EXISTS risk_assessments;
DROP TABLE IF EXISTS access_logs;
DROP TABLE IF EXISTS access_policies;
DROP TABLE IF EXISTS encryption_keys;
DROP TABLE IF EXISTS campus_locations;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS system_users;

-- Create system users table (admin, security officers, staff)
CREATE TABLE system_users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    full_name VARCHAR(100) NOT NULL,
    role ENUM('admin', 'security_officer', 'staff', 'supervisor') DEFAULT 'staff',
    status ENUM('active', 'inactive', 'locked') DEFAULT 'active',
    last_login TIMESTAMP NULL,
    failed_login_attempts INT DEFAULT 0,
    two_factor_enabled BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INT,
    FOREIGN KEY (created_by) REFERENCES system_users(user_id)
);

-- Create campus locations table
CREATE TABLE campus_locations (
    location_id INT AUTO_INCREMENT PRIMARY KEY,
    location_name VARCHAR(100) NOT NULL,
    location_type ENUM('classroom', 'laboratory', 'office', 'library', 'cafeteria', 'dormitory', 'admin', 'security', 'maintenance', 'recreational', 'entrance', 'exit') NOT NULL,
    building VARCHAR(100),
    floor_level VARCHAR(10),
    room_number VARCHAR(20),
    access_level ENUM('public', 'restricted', 'staff_only', 'admin_only') DEFAULT 'public',
    max_occupancy INT,
    current_occupancy INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    under_maintenance BOOLEAN DEFAULT FALSE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create students table
CREATE TABLE students (
    student_id VARCHAR(20) PRIMARY KEY,
    card_id VARCHAR(50) UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20),
    program VARCHAR(10),
    year_of_study INT,
    status ENUM('active', 'inactive', 'graduated', 'suspended') DEFAULT 'active',
    photo_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    card_issued_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    card_expiry_date DATE
);

-- Enhanced access logs table with risk assessment
CREATE TABLE access_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(20),
    card_id VARCHAR(50),
    location_id INT,
    access_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    access_type ENUM('entry', 'exit', 'denied') NOT NULL,
    access_granted BOOLEAN DEFAULT FALSE,
    denial_reason VARCHAR(255),
    ip_address VARCHAR(45),
    user_agent TEXT,
    risk_score INT DEFAULT 1,
    requires_review BOOLEAN DEFAULT FALSE,
    additional_auth_used BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (location_id) REFERENCES campus_locations(location_id),
    INDEX idx_access_time (access_time),
    INDEX idx_student_id (student_id),
    INDEX idx_location_id (location_id)
);

-- Security alerts table for real-time monitoring
CREATE TABLE security_alerts (
    alert_id INT AUTO_INCREMENT PRIMARY KEY,
    alert_type ENUM('unauthorized_access', 'lost_card_used', 'suspicious_activity', 'policy_violation', 'system_breach', 'high_risk_access') NOT NULL,
    severity ENUM('low', 'medium', 'high', 'critical') DEFAULT 'medium',
    location_id INT,
    student_id VARCHAR(20),
    card_id VARCHAR(50),
    alert_message TEXT,
    alert_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('new', 'acknowledged', 'investigating', 'resolved', 'false_positive') DEFAULT 'new',
    acknowledged_by INT,
    acknowledged_at TIMESTAMP NULL,
    resolved_by INT,
    resolved_at TIMESTAMP NULL,
    resolution_notes TEXT,
    FOREIGN KEY (location_id) REFERENCES campus_locations(location_id),
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (acknowledged_by) REFERENCES system_users(user_id),
    FOREIGN KEY (resolved_by) REFERENCES system_users(user_id),
    INDEX idx_alert_time (alert_time),
    INDEX idx_severity (severity),
    INDEX idx_status (status)
);

-- Enhanced access control policies
CREATE TABLE access_policies (
    policy_id INT AUTO_INCREMENT PRIMARY KEY,
    policy_name VARCHAR(100) NOT NULL,
    policy_type ENUM('time_based', 'location_based', 'role_based', 'risk_based', 'behavioral') NOT NULL,
    description TEXT,
    time_start TIME,
    time_end TIME,
    days_of_week SET('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'),
    location_id INT,
    target_role ENUM('all', 'student', 'staff', 'security_officer', 'admin') DEFAULT 'all',
    risk_threshold INT DEFAULT 3,
    action ENUM('allow', 'deny', 'require_additional_auth', 'notify_security') DEFAULT 'allow',
    is_active BOOLEAN DEFAULT TRUE,
    log_violations BOOLEAN DEFAULT TRUE,
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (location_id) REFERENCES campus_locations(location_id),
    FOREIGN KEY (created_by) REFERENCES system_users(user_id)
);

-- Risk assessment scores table
CREATE TABLE risk_assessments (
    assessment_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(20),
    location_id INT,
    assessment_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    risk_score INT NOT NULL,
    risk_level ENUM('low', 'medium', 'high', 'critical') DEFAULT 'low',
    risk_factors JSON,
    action_taken ENUM('allowed', 'denied', 'additional_auth_required', 'flagged_for_review') DEFAULT 'allowed',
    ai_confidence DECIMAL(5,2),
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (location_id) REFERENCES campus_locations(location_id),
    INDEX idx_assessment_time (assessment_time),
    INDEX idx_risk_level (risk_level)
);

-- Security incidents table for detailed incident management
CREATE TABLE security_incidents (
    incident_id INT AUTO_INCREMENT PRIMARY KEY,
    incident_type ENUM('unauthorized_access', 'policy_violation', 'suspicious_activity', 'system_breach', 'physical_security', 'data_breach') NOT NULL,
    severity ENUM('low', 'medium', 'high', 'critical') DEFAULT 'medium',
    title VARCHAR(200) NOT NULL,
    description TEXT,
    location_id INT,
    student_id VARCHAR(20),
    detected_by INT,
    assigned_to INT,
    status ENUM('new', 'investigating', 'in_progress', 'resolved', 'closed', 'false_positive') DEFAULT 'new',
    priority ENUM('low', 'medium', 'high', 'urgent') DEFAULT 'medium',
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP NULL,
    resolution_notes TEXT,
    evidence_files JSON,
    related_alert_id INT,
    FOREIGN KEY (location_id) REFERENCES campus_locations(location_id),
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (detected_by) REFERENCES system_users(user_id),
    FOREIGN KEY (assigned_to) REFERENCES system_users(user_id),
    FOREIGN KEY (related_alert_id) REFERENCES security_alerts(alert_id),
    INDEX idx_detected_at (detected_at),
    INDEX idx_severity (severity),
    INDEX idx_status (status)
);

-- Lost or stolen cards tracking
CREATE TABLE lost_stolen_cards (
    report_id INT AUTO_INCREMENT PRIMARY KEY,
    card_id VARCHAR(50) NOT NULL,
    student_id VARCHAR(20),
    report_type ENUM('lost', 'stolen', 'damaged') NOT NULL,
    reported_by INT,
    report_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('active', 'resolved', 'card_found') DEFAULT 'active',
    description TEXT,
    resolved_at TIMESTAMP NULL,
    resolved_by INT,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (reported_by) REFERENCES system_users(user_id),
    FOREIGN KEY (resolved_by) REFERENCES system_users(user_id),
    INDEX idx_card_id (card_id),
    INDEX idx_status (status)
);

-- Encryption keys management
CREATE TABLE encryption_keys (
    key_id INT AUTO_INCREMENT PRIMARY KEY,
    key_name VARCHAR(100) NOT NULL,
    key_purpose VARCHAR(100),
    algorithm VARCHAR(50),
    key_strength INT,
    key_hash VARCHAR(255), -- Store hash, not actual key
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    created_by INT,
    FOREIGN KEY (created_by) REFERENCES system_users(user_id)
);

-- User sessions tracking
CREATE TABLE user_sessions (
    session_id VARCHAR(255) PRIMARY KEY,
    user_id INT NOT NULL,
    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    logout_time TIMESTAMP NULL,
    session_duration_minutes INT,
    FOREIGN KEY (user_id) REFERENCES system_users(user_id),
    INDEX idx_user_id (user_id),
    INDEX idx_last_activity (last_activity)
);

-- Comprehensive security audit log
CREATE TABLE security_audit_log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    event_type VARCHAR(100) NOT NULL,
    event_details TEXT,
    user_id INT,
    ip_address VARCHAR(45),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    severity ENUM('low', 'medium', 'high', 'critical') DEFAULT 'medium',
    source_system VARCHAR(50) DEFAULT 'campus_security',
    FOREIGN KEY (user_id) REFERENCES system_users(user_id),
    INDEX idx_timestamp (timestamp),
    INDEX idx_event_type (event_type),
    INDEX idx_severity (severity)
);

-- Create useful views for common queries

-- Active security incidents view
CREATE VIEW active_security_incidents AS
SELECT 
    si.*,
    cl.location_name,
    cl.building,
    s.full_name as student_name,
    su1.full_name as detected_by_name,
    su2.full_name as assigned_to_name
FROM security_incidents si
LEFT JOIN campus_locations cl ON si.location_id = cl.location_id
LEFT JOIN students s ON si.student_id = s.student_id
LEFT JOIN system_users su1 ON si.detected_by = su1.user_id
LEFT JOIN system_users su2 ON si.assigned_to = su2.user_id
WHERE si.status IN ('new', 'investigating', 'in_progress');

-- Recent security activity summary
CREATE VIEW recent_security_activity AS
SELECT 
    'access_attempt' as activity_type,
    CONCAT(s.full_name, ' accessed ', cl.location_name) as description,
    al.access_time as activity_time,
    CASE WHEN al.access_granted THEN 'success' ELSE 'failed' END as status,
    al.risk_score
FROM access_logs al
LEFT JOIN students s ON al.student_id = s.student_id
LEFT JOIN campus_locations cl ON al.location_id = cl.location_id
WHERE al.access_time >= DATE_SUB(NOW(), INTERVAL 24 HOUR)

UNION ALL

SELECT 
    'security_alert' as activity_type,
    sa.alert_message as description,
    sa.alert_time as activity_time,
    sa.status,
    NULL as risk_score
FROM security_alerts sa
WHERE sa.alert_time >= DATE_SUB(NOW(), INTERVAL 24 HOUR)

ORDER BY activity_time DESC
LIMIT 50;

-- User activity summary
CREATE VIEW user_activity_summary AS
SELECT 
    su.user_id,
    su.username,
    su.full_name,
    su.role,
    su.last_login,
    COUNT(us.session_id) as total_sessions,
    MAX(us.last_activity) as last_activity,
    SUM(us.session_duration_minutes) as total_session_minutes
FROM system_users su
LEFT JOIN user_sessions us ON su.user_id = us.user_id
WHERE su.status = 'active'
GROUP BY su.user_id, su.username, su.full_name, su.role, su.last_login;

-- Database setup completion message
SELECT 
    'Smart Campus Security Database Setup Complete!' as status,
    'Empty database structure created successfully' as message,
    'Run populate_sample_data.py to add sample data' as next_step;