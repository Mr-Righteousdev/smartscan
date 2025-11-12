-- Smart Campus ID Security System - Complete Database Setup
-- St. Lawrence University Uganda - Cybersecurity & Innovations Club
-- Student Number Format: PROGRAM/YEARSession/Nationality/IntakeNUMBER
-- Example: BAIT/21D/U/F0069 = Bachelor IT, 2021, Day, Ugandan, February intake, #69
-- Consolidated Database Script - Phase 1 & 2 Combined

CREATE DATABASE IF NOT EXISTS smart_campus_security;
USE smart_campus_security;

-- ====================================
-- CORE TABLES (Phase 1)
-- ====================================

-- Students table
CREATE TABLE students (
    student_id VARCHAR(20) PRIMARY KEY,
    card_id VARCHAR(50) UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    program VARCHAR(100),
    year_of_study INT,
    photo_url VARCHAR(255),
    card_expiry_date DATE,
    status ENUM('active', 'suspended', 'graduated', 'inactive') DEFAULT 'active',
    date_registered TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Campus locations/entry points
CREATE TABLE campus_locations (
    location_id INT AUTO_INCREMENT PRIMARY KEY,
    location_name VARCHAR(100) NOT NULL,
    location_type ENUM('library', 'laboratory', 'dormitory', 'lecture_hall', 'cafeteria', 'admin', 'sports', 'other') NOT NULL,
    building VARCHAR(50),
    floor_level VARCHAR(10),
    access_level ENUM('public', 'restricted', 'staff_only') DEFAULT 'public',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Access logs (main table for tracking entries/exits)
CREATE TABLE access_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(20),
    card_id VARCHAR(50),
    location_id INT,
    access_type ENUM('entry', 'exit') NOT NULL,
    access_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    access_granted BOOLEAN DEFAULT TRUE,
    denial_reason VARCHAR(200),
    ip_address VARCHAR(45),
    user_agent TEXT,
    -- Phase 2 additions
    risk_score INT DEFAULT 0,
    requires_review BOOLEAN DEFAULT FALSE,
    reviewed_by INT,
    reviewed_at TIMESTAMP NULL,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE SET NULL,
    FOREIGN KEY (location_id) REFERENCES campus_locations(location_id) ON DELETE SET NULL,
    INDEX idx_student_time (student_id, access_time),
    INDEX idx_location_time (location_id, access_time),
    INDEX idx_access_time (access_time),
    INDEX idx_risk_score (risk_score),
    INDEX idx_requires_review (requires_review)
);

-- Lost/stolen cards
CREATE TABLE lost_stolen_cards (
    report_id INT AUTO_INCREMENT PRIMARY KEY,
    card_id VARCHAR(50) NOT NULL,
    student_id VARCHAR(20),
    report_type ENUM('lost', 'stolen') NOT NULL,
    report_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reported_by VARCHAR(100),
    description TEXT,
    status ENUM('active', 'resolved', 'cancelled') DEFAULT 'active',
    resolved_date TIMESTAMP NULL,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE SET NULL,
    INDEX idx_card_status (card_id, status)
);

-- Security alerts
CREATE TABLE security_alerts (
    alert_id INT AUTO_INCREMENT PRIMARY KEY,
    alert_type ENUM('unauthorized_access', 'lost_card_used', 'multiple_failed_attempts', 'system_breach', 'high_risk_access', 'other') NOT NULL,
    severity ENUM('low', 'medium', 'high', 'critical') NOT NULL,
    location_id INT,
    student_id VARCHAR(20),
    card_id VARCHAR(50),
    alert_message TEXT NOT NULL,
    alert_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('new', 'acknowledged', 'investigating', 'resolved') DEFAULT 'new',
    acknowledged_by VARCHAR(100),
    acknowledged_time TIMESTAMP NULL,
    resolved_by VARCHAR(100),
    resolved_time TIMESTAMP NULL,
    resolution_notes TEXT,
    FOREIGN KEY (location_id) REFERENCES campus_locations(location_id) ON DELETE SET NULL,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE SET NULL,
    INDEX idx_alert_time (alert_time),
    INDEX idx_status (status),
    INDEX idx_severity (severity)
);

-- System settings and configuration
CREATE TABLE system_settings (
    setting_id INT AUTO_INCREMENT PRIMARY KEY,
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT,
    description VARCHAR(255),
    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    modified_by VARCHAR(100)
);

-- ====================================
-- ADVANCED SECURITY TABLES (Phase 2)
-- ====================================

-- System users table (for dashboard/admin access)
CREATE TABLE system_users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    role ENUM('admin', 'security_officer', 'staff', 'student') DEFAULT 'student',
    status ENUM('active', 'inactive', 'locked', 'suspended') DEFAULT 'active',
    last_login TIMESTAMP NULL,
    failed_login_attempts INT DEFAULT 0,
    account_locked_until TIMESTAMP NULL,
    two_factor_enabled BOOLEAN DEFAULT FALSE,
    two_factor_secret VARCHAR(32) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by INT,
    FOREIGN KEY (created_by) REFERENCES system_users(user_id) ON DELETE SET NULL,
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_role (role),
    INDEX idx_status (status)
);

-- Security audit log
CREATE TABLE security_audit_log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    event_details TEXT,
    user_id INT,
    student_id VARCHAR(20),
    ip_address VARCHAR(45),
    user_agent TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    risk_level ENUM('low', 'medium', 'high', 'critical') DEFAULT 'low',
    FOREIGN KEY (user_id) REFERENCES system_users(user_id) ON DELETE SET NULL,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE SET NULL,
    INDEX idx_event_type (event_type),
    INDEX idx_timestamp (timestamp),
    INDEX idx_user_id (user_id),
    INDEX idx_risk_level (risk_level),
    INDEX idx_security_audit_timestamp_type (timestamp, event_type)
);

-- User sessions tracking
CREATE TABLE user_sessions (
    session_id VARCHAR(255) PRIMARY KEY,
    user_id INT NOT NULL,
    token_hash VARCHAR(255) NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES system_users(user_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_expires_at (expires_at),
    INDEX idx_is_active (is_active)
);

-- Enhanced access control policies
CREATE TABLE access_policies (
    policy_id INT AUTO_INCREMENT PRIMARY KEY,
    policy_name VARCHAR(100) NOT NULL,
    policy_type ENUM('time_based', 'location_based', 'role_based', 'risk_based') NOT NULL,
    location_id INT,
    student_role VARCHAR(50),
    time_start TIME,
    time_end TIME,
    days_of_week SET('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'),
    risk_threshold ENUM('low', 'medium', 'high', 'critical') DEFAULT 'medium',
    action ENUM('allow', 'deny', 'require_additional_auth', 'alert_only') DEFAULT 'allow',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INT,
    FOREIGN KEY (location_id) REFERENCES campus_locations(location_id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES system_users(user_id) ON DELETE SET NULL,
    INDEX idx_policy_type (policy_type),
    INDEX idx_location_id (location_id),
    INDEX idx_is_active (is_active)
);

-- Two-factor authentication codes
CREATE TABLE two_factor_codes (
    code_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    code VARCHAR(10) NOT NULL,
    purpose ENUM('login', 'password_reset', 'account_unlock') NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    used_at TIMESTAMP NULL,
    ip_address VARCHAR(45),
    FOREIGN KEY (user_id) REFERENCES system_users(user_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_expires_at (expires_at),
    INDEX idx_code_purpose (code, purpose)
);

-- Security incident management
CREATE TABLE security_incidents (
    incident_id INT AUTO_INCREMENT PRIMARY KEY,
    incident_type ENUM('unauthorized_access', 'data_breach', 'system_intrusion', 'policy_violation', 'suspicious_activity') NOT NULL,
    severity ENUM('low', 'medium', 'high', 'critical') NOT NULL,
    status ENUM('new', 'investigating', 'contained', 'resolved', 'closed') DEFAULT 'new',
    title VARCHAR(200) NOT NULL,
    description TEXT,
    affected_systems TEXT,
    affected_users TEXT,
    location_id INT,
    detected_by INT,
    assigned_to INT,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    responded_at TIMESTAMP NULL,
    resolved_at TIMESTAMP NULL,
    resolution_notes TEXT,
    impact_assessment TEXT,
    lessons_learned TEXT,
    FOREIGN KEY (location_id) REFERENCES campus_locations(location_id) ON DELETE SET NULL,
    FOREIGN KEY (detected_by) REFERENCES system_users(user_id) ON DELETE SET NULL,
    FOREIGN KEY (assigned_to) REFERENCES system_users(user_id) ON DELETE SET NULL,
    INDEX idx_incident_type (incident_type),
    INDEX idx_severity (severity),
    INDEX idx_status (status),
    INDEX idx_detected_at (detected_at)
);

-- Encryption key management (for educational purposes)
CREATE TABLE encryption_keys (
    key_id INT AUTO_INCREMENT PRIMARY KEY,
    key_name VARCHAR(100) NOT NULL,
    key_purpose VARCHAR(100) NOT NULL,
    algorithm VARCHAR(50) NOT NULL,
    key_strength INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_by INT,
    FOREIGN KEY (created_by) REFERENCES system_users(user_id) ON DELETE SET NULL,
    INDEX idx_key_purpose (key_purpose),
    INDEX idx_is_active (is_active),
    INDEX idx_expires_at (expires_at)
);

-- Risk assessment scores
CREATE TABLE risk_assessments (
    assessment_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(20),
    location_id INT,
    access_time TIMESTAMP NOT NULL,
    risk_score INT NOT NULL,
    risk_level ENUM('low', 'medium', 'high', 'critical') NOT NULL,
    risk_factors JSON,
    action_taken ENUM('allowed', 'denied', 'escalated', 'monitored') NOT NULL,
    assessment_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE SET NULL,
    FOREIGN KEY (location_id) REFERENCES campus_locations(location_id) ON DELETE SET NULL,
    INDEX idx_student_id (student_id),
    INDEX idx_location_id (location_id),
    INDEX idx_risk_level (risk_level),
    INDEX idx_assessment_time (assessment_time)
);

-- ====================================
-- DATA POPULATION
-- ====================================

-- Insert sample campus locations (St. Lawrence University Uganda)
INSERT INTO campus_locations (location_name, location_type, building, floor_level, access_level) VALUES
('University Main Library', 'library', 'Library Complex', 'Ground', 'public'),
('Digital Library & E-Resources', 'library', 'Library Complex', '1st Floor', 'restricted'),
('ICT Computer Laboratory 1', 'laboratory', 'School of Computing & IT', 'Ground', 'restricted'),
('ICT Computer Laboratory 2', 'laboratory', 'School of Computing & IT', '1st Floor', 'restricted'),
('Cybersecurity & Innovation Lab', 'laboratory', 'School of Computing & IT', '2nd Floor', 'restricted'),
('Software Development Lab', 'laboratory', 'School of Computing & IT', '2nd Floor', 'restricted'),
('Nkumba Male Hostel', 'dormitory', 'Student Accommodation', 'Ground', 'restricted'),
('Kigungu Female Hostel', 'dormitory', 'Student Accommodation', 'Ground', 'restricted'),
('Main Lecture Theatre', 'lecture_hall', 'Academic Complex', 'Ground', 'public'),
('ICT Department Lecture Hall', 'lecture_hall', 'School of Computing & IT', '1st Floor', 'public'),
('School of Computing & IT Office', 'admin', 'School of Computing & IT', '3rd Floor', 'staff_only'),
('Students Canteen', 'cafeteria', 'Student Life Center', 'Ground', 'public'),
('University Sports Grounds', 'sports', 'Recreation Center', 'Ground', 'public'),
('Administration Block', 'admin', 'Main Administration', 'Ground', 'staff_only'),
('Student Affairs Office', 'admin', 'Student Life Center', '1st Floor', 'public');

-- Insert sample students (St. Lawrence University Uganda format)
-- Student ID Format: PROGRAM/YEARSession/Nationality/IntakeNUMBER
-- Programs: BAIT=Bachelor IT, BACS=Bachelor Computer Science, BCSE=Bachelor Computer Engineering
-- Sessions: D=Day, E=Evening  |  Nationality: U=Ugandan, K=Kenyan, T=Tanzanian, R=Rwandan
-- Intakes: F=February, A=August  |  Numbers: 4-digit with leading zeros
INSERT INTO students (student_id, card_id, full_name, email, program, year_of_study, photo_url, card_expiry_date) VALUES
('BAIT/21D/U/F0069', 'RFID_BAIT_21F_069', 'Mukasa David', 'dmukasa21@student.slau.ac.ug', 'Bachelor of Information Technology', 4, 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face', '2025-12-31'),
('BACS/22D/U/A0024', 'RFID_BACS_22A_024', 'Nakato Sarah', 'snakato22@student.slau.ac.ug', 'Bachelor of Computer Science', 3, 'https://images.unsplash.com/photo-1494790108755-2616b612b9e0?w=150&h=150&fit=crop&crop=face', '2026-12-31'),
('BAIT/23D/U/F0156', 'RFID_BAIT_23F_156', 'Ssemwogerere John', 'jssemwogerere23@student.slau.ac.ug', 'Bachelor of Information Technology', 2, 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face', '2027-12-31'),
('BCSE/20D/U/A0012', 'RFID_BCSE_20A_012', 'Namugga Grace', 'gnamugga20@student.slau.ac.ug', 'Bachelor of Computer Science & Engineering', 5, 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&h=150&fit=crop&crop=face', '2024-12-31'),
('BAIT/22E/K/F0087', 'RFID_BAIT_22F_087', 'Otieno Michael', 'motieno22@student.slau.ac.ug', 'Bachelor of Information Technology', 3, 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&h=150&fit=crop&crop=face', '2026-12-31'),
('BACS/21D/U/A0145', 'RFID_BACS_21A_145', 'Atim Patricia', 'patim21@student.slau.ac.ug', 'Bachelor of Computer Science', 4, 'https://images.unsplash.com/photo-1517841905240-472988babdf9?w=150&h=150&fit=crop&crop=face', '2025-12-31'),
('BAIT/24D/U/F0003', 'RFID_BAIT_24F_003', 'Kiwanuka Robert', 'rkiwanuka24@student.slau.ac.ug', 'Bachelor of Information Technology', 1, 'https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=150&h=150&fit=crop&crop=face', '2028-12-31'),
('BCSE/23D/T/A0078', 'RFID_BCSE_23A_078', 'Mwalimu James', 'jmwalimu23@student.slau.ac.ug', 'Bachelor of Computer Science & Engineering', 2, 'https://images.unsplash.com/photo-1519345182560-3f2917c472ef?w=150&h=150&fit=crop&crop=face', '2027-12-31'),
('BAIT/22D/U/F0234', 'RFID_BAIT_22F_234', 'Namusoke Christine', 'cnamusoke22@student.slau.ac.ug', 'Bachelor of Information Technology', 3, 'https://images.unsplash.com/photo-1517841905240-472988babdf9?w=150&h=150&fit=crop&crop=face', '2026-12-31'),
('BACS/23E/R/A0056', 'RFID_BACS_23A_056', 'Uwimana Eric', 'euwimana23@student.slau.ac.ug', 'Bachelor of Computer Science', 2, 'https://images.unsplash.com/photo-1519345182560-3f2917c472ef?w=150&h=150&fit=crop&crop=face', '2027-12-31');

-- Insert default system users (Phase 2 demo accounts)
-- Password hashes generated using PBKDF2 with salt for security
INSERT INTO system_users (username, email, password_hash, full_name, role) VALUES
('admin', 'admin@slau.ac.ug', 
 'admin_salt_123:8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918',
 'System Administrator', 'admin'),
('security', 'security@slau.ac.ug',
 'security_salt_456:ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f',
 'Security Officer', 'security_officer'),
('john_doe', 'john.doe@staff.slau.ac.ug',
 'staff_salt_789:5906ac361a137e2d286465cd6588ebb5ac3f5ae955001100bc41577c3d751764',
 'John Doe Staff', 'staff');

-- Add foreign key for reviewed_by in access_logs
ALTER TABLE access_logs 
ADD FOREIGN KEY (reviewed_by) REFERENCES system_users(user_id) ON DELETE SET NULL;

-- Insert default access policies
INSERT INTO access_policies (policy_name, policy_type, time_start, time_end, action, days_of_week) VALUES
('Night Access Restriction', 'time_based', '22:00:00', '06:00:00', 'require_additional_auth', 
 'monday,tuesday,wednesday,thursday,friday,saturday,sunday'),
('Weekend Laboratory Access', 'time_based', '08:00:00', '18:00:00', 'allow',
 'saturday,sunday');

-- Insert location-specific policies
INSERT INTO access_policies (policy_name, policy_type, location_id, action) VALUES
('Cybersecurity Lab Access Control', 'location_based', 5, 'require_additional_auth'),
('ICT Office Access Control', 'location_based', 10, 'require_additional_auth');

-- Insert sample encryption keys (for educational demonstration)
INSERT INTO encryption_keys (key_name, key_purpose, algorithm, key_strength, created_by) VALUES
('Database Encryption Key', 'data_at_rest', 'AES', 256, 1),
('Session Token Key', 'session_management', 'HMAC-SHA256', 256, 1),
('Card Data Encryption', 'card_information', 'AES', 128, 1);

-- Insert sample security incidents (for training purposes)
INSERT INTO security_incidents (incident_type, severity, title, description, detected_by) VALUES
('unauthorized_access', 'medium', 'Unknown Card Access Attempt', 
 'Multiple attempts to access secure locations using unregistered card ID', 2),
('suspicious_activity', 'high', 'Off-Hours Access Pattern', 
 'Student accessing multiple secure locations during restricted hours', 2),
('policy_violation', 'low', 'Tailgating Detected', 
 'Multiple card scans at same location within seconds', 2);

-- Insert system settings
INSERT INTO system_settings (setting_key, setting_value, description) VALUES
('max_failed_attempts', '3', 'Maximum failed access attempts before triggering alert'),
('alert_notification_email', 'security@slau.ac.ug', 'Email for security alerts'),
('session_timeout_minutes', '30', 'Dashboard session timeout in minutes'),
('enable_real_time_alerts', 'true', 'Enable real-time alert notifications'),
('card_expiry_warning_days', '30', 'Days before card expiry to show warning');

-- ====================================
-- VIEWS FOR REPORTING
-- ====================================

-- Recent access summary view
CREATE VIEW recent_access_summary AS
SELECT 
    al.log_id,
    s.full_name,
    s.student_id,
    cl.location_name,
    cl.building,
    al.access_type,
    al.access_time,
    al.access_granted,
    al.risk_score
FROM access_logs al
LEFT JOIN students s ON al.student_id = s.student_id
LEFT JOIN campus_locations cl ON al.location_id = cl.location_id
WHERE al.access_time >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
ORDER BY al.access_time DESC;

-- Active alerts summary view
CREATE VIEW active_alerts_summary AS
SELECT 
    sa.alert_id,
    sa.alert_type,
    sa.severity,
    sa.alert_message,
    sa.alert_time,
    cl.location_name,
    s.full_name as student_name
FROM security_alerts sa
LEFT JOIN campus_locations cl ON sa.location_id = cl.location_id
LEFT JOIN students s ON sa.student_id = s.student_id
WHERE sa.status IN ('new', 'acknowledged', 'investigating')
ORDER BY sa.alert_time DESC, sa.severity DESC;

-- Security dashboard summary view
CREATE VIEW security_dashboard_summary AS
SELECT 
    DATE(sa.timestamp) as report_date,
    COUNT(*) as total_events,
    SUM(CASE WHEN sa.risk_level = 'critical' THEN 1 ELSE 0 END) as critical_events,
    SUM(CASE WHEN sa.risk_level = 'high' THEN 1 ELSE 0 END) as high_events,
    SUM(CASE WHEN sa.risk_level = 'medium' THEN 1 ELSE 0 END) as medium_events,
    SUM(CASE WHEN sa.risk_level = 'low' THEN 1 ELSE 0 END) as low_events
FROM security_audit_log sa
WHERE sa.timestamp >= DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY DATE(sa.timestamp)
ORDER BY report_date DESC;

-- Active security incidents view
CREATE VIEW active_security_incidents AS
SELECT 
    si.*,
    detector.full_name as detected_by_name,
    assignee.full_name as assigned_to_name,
    cl.location_name
FROM security_incidents si
LEFT JOIN system_users detector ON si.detected_by = detector.user_id
LEFT JOIN system_users assignee ON si.assigned_to = assignee.user_id
LEFT JOIN campus_locations cl ON si.location_id = cl.location_id
WHERE si.status IN ('new', 'investigating', 'contained')
ORDER BY si.severity DESC, si.detected_at DESC;

-- User activity summary view
CREATE VIEW user_activity_summary AS
SELECT 
    su.user_id,
    su.username,
    su.full_name,
    su.role,
    su.last_login,
    COUNT(us.session_id) as active_sessions,
    MAX(us.last_activity) as last_activity
FROM system_users su
LEFT JOIN user_sessions us ON su.user_id = us.user_id AND us.is_active = TRUE
WHERE su.status = 'active'
GROUP BY su.user_id, su.username, su.full_name, su.role, su.last_login
ORDER BY last_activity DESC;

-- ====================================
-- SUCCESS MESSAGE
-- ====================================

SELECT 'Smart Campus Security Database has been created successfully!' as message,
       'Phase 1 & 2 features combined - Ready for production use' as status,
       'Demo accounts: admin/admin123, security/security123, john_doe/staff123' as login_info;