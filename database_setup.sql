-- Smart Campus ID Security System Database
-- St. Lawrence University - Cybersecurity Club
-- Database Setup Script

CREATE DATABASE IF NOT EXISTS smart_campus_security;
USE smart_campus_security;

-- Students table
CREATE TABLE students (
    student_id VARCHAR(20) PRIMARY KEY,
    card_id VARCHAR(50) UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    program VARCHAR(100),
    year_of_study INT,
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
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE SET NULL,
    FOREIGN KEY (location_id) REFERENCES campus_locations(location_id) ON DELETE SET NULL,
    INDEX idx_student_time (student_id, access_time),
    INDEX idx_location_time (location_id, access_time),
    INDEX idx_access_time (access_time)
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
    alert_type ENUM('unauthorized_access', 'lost_card_used', 'multiple_failed_attempts', 'system_breach', 'other') NOT NULL,
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

-- Insert sample campus locations
INSERT INTO campus_locations (location_name, location_type, building, floor_level, access_level) VALUES
('Main Library Entrance', 'library', 'Library Building', 'Ground', 'public'),
('Library Study Rooms', 'library', 'Library Building', '1st Floor', 'restricted'),
('Computer Lab 1', 'laboratory', 'ICT Building', 'Ground', 'restricted'),
('Computer Lab 2', 'laboratory', 'ICT Building', '1st Floor', 'restricted'),
('Cybersecurity Lab', 'laboratory', 'ICT Building', '2nd Floor', 'restricted'),
('Male Dormitory Block A', 'dormitory', 'Dormitory A', 'Ground', 'restricted'),
('Female Dormitory Block B', 'dormitory', 'Dormitory B', 'Ground', 'restricted'),
('Lecture Hall 1', 'lecture_hall', 'Academic Block', 'Ground', 'public'),
('Lecture Hall 2', 'lecture_hall', 'Academic Block', '1st Floor', 'public'),
('ICT Department Office', 'admin', 'ICT Building', '3rd Floor', 'staff_only'),
('Main Cafeteria', 'cafeteria', 'Student Center', 'Ground', 'public'),
('Sports Complex', 'sports', 'Sports Building', 'Ground', 'public');

-- Insert sample students (for testing)
INSERT INTO students (student_id, card_id, full_name, email, program, year_of_study) VALUES
('STU001', 'RFID_001_ABC123', 'John Doe', 'john.doe@student.slau.ac.ug', 'Computer Science', 3),
('STU002', 'RFID_002_DEF456', 'Jane Smith', 'jane.smith@student.slau.ac.ug', 'Cybersecurity', 2),
('STU003', 'RFID_003_GHI789', 'David Wilson', 'david.wilson@student.slau.ac.ug', 'Information Technology', 1),
('STU004', 'RFID_004_JKL012', 'Sarah Johnson', 'sarah.johnson@student.slau.ac.ug', 'Computer Engineering', 4),
('STU005', 'RFID_005_MNO345', 'Michael Brown', 'michael.brown@student.slau.ac.ug', 'Data Science', 2);

-- Insert system settings
INSERT INTO system_settings (setting_key, setting_value, description) VALUES
('max_failed_attempts', '3', 'Maximum failed access attempts before triggering alert'),
('alert_notification_email', 'security@slau.ac.ug', 'Email for security alerts'),
('session_timeout_minutes', '30', 'Dashboard session timeout in minutes'),
('enable_real_time_alerts', 'true', 'Enable real-time alert notifications'),
('card_expiry_warning_days', '30', 'Days before card expiry to show warning');

-- Create views for commonly used queries
CREATE VIEW recent_access_summary AS
SELECT 
    al.log_id,
    s.full_name,
    s.student_id,
    cl.location_name,
    cl.building,
    al.access_type,
    al.access_time,
    al.access_granted
FROM access_logs al
LEFT JOIN students s ON al.student_id = s.student_id
LEFT JOIN campus_locations cl ON al.location_id = cl.location_id
WHERE al.access_time >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
ORDER BY al.access_time DESC;

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

-- Create a user for the application (adjust password as needed)
-- CREATE USER 'campus_security'@'localhost' IDENTIFIED BY 'SecurePassword123!';
-- GRANT SELECT, INSERT, UPDATE, DELETE ON smart_campus_security.* TO 'campus_security'@'localhost';
-- FLUSH PRIVILEGES;

-- Display success message
SELECT 'Smart Campus Security Database has been created successfully!' as message;