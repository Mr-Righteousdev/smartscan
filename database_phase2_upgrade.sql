-- Phase 2: Advanced Security Features Database Upgrade
-- Smart Campus ID Security System

USE smart_campus_security;

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
    INDEX idx_risk_level (risk_level)
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

-- Insert default system users
INSERT INTO system_users (username, email, password_hash, full_name, role) VALUES
('admin', 'admin@slau.ac.ug', 
 'f3b1c4d5e6f7a8b9c0d1e2f3a4b5c6d7:8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d',
 'System Administrator', 'admin'),
('security', 'security@slau.ac.ug',
 'a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6:1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b',
 'Security Officer', 'security_officer'),
('john_doe', 'john.doe@staff.slau.ac.ug',
 'z9y8x7w6v5u4t3s2r1q0p9o8n7m6l5k4:9o8n7m6l5k4j3i2h1g0f9e8d7c6b5a4z9y8x7w6v5u4t3s2r1q0p9o8n7m6l5k4j3i',
 'John Doe Staff', 'staff');

-- Insert default access policies
INSERT INTO access_policies (policy_name, policy_type, time_start, time_end, action, days_of_week) VALUES
('Night Access Restriction', 'time_based', '22:00:00', '06:00:00', 'require_additional_auth', 
 'monday,tuesday,wednesday,thursday,friday,saturday,sunday'),
('Weekend Laboratory Access', 'time_based', '08:00:00', '18:00:00', 'allow',
 'saturday,sunday'),
('High Security Locations', 'location_based', NULL, NULL, 'require_additional_auth', NULL);

-- Update access policies for specific high-security locations
UPDATE access_policies SET location_id = 5 WHERE policy_name = 'High Security Locations';
INSERT INTO access_policies (policy_name, policy_type, location_id, action) VALUES
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

-- Create views for security reporting
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

-- Add enhanced constraints and triggers
ALTER TABLE access_logs 
ADD COLUMN risk_score INT DEFAULT 0,
ADD COLUMN requires_review BOOLEAN DEFAULT FALSE,
ADD COLUMN reviewed_by INT,
ADD COLUMN reviewed_at TIMESTAMP NULL,
ADD FOREIGN KEY (reviewed_by) REFERENCES system_users(user_id) ON DELETE SET NULL;

-- Add indexes for better performance on security queries
CREATE INDEX idx_access_logs_risk_score ON access_logs(risk_score);
CREATE INDEX idx_access_logs_requires_review ON access_logs(requires_review);
CREATE INDEX idx_security_audit_timestamp_type ON security_audit_log(timestamp, event_type);

-- Success message
SELECT 'Phase 2 Advanced Security Features database upgrade completed successfully!' as message,
       'New tables: system_users, security_audit_log, user_sessions, access_policies, security_incidents' as new_features;