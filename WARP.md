# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

**Smart Campus ID Security System** - An educational cybersecurity simulation platform built for St. Lawrence University Uganda. This Flask-based web application demonstrates enterprise-grade security concepts including identity and access management, risk assessment, threat detection, and security monitoring without requiring physical hardware.

## Core Architecture

### Technology Stack
- **Backend**: Flask (Python 3.8+) with MySQL database
- **Authentication**: JWT-based sessions with role-based access control (RBAC)
- **AI/ML**: Scikit-learn with Isolation Forest for anomaly detection
- **Security**: PBKDF2 password hashing, audit logging, risk assessment engine

### Key Components

#### 1. `app.py` - Main Flask Application (2700+ lines)
The central application file containing:
- **Database Integration**: MySQL connection management via `get_db_connection()`
- **Access Control Routes**: Card scanning simulation, virtual campus interface
- **Security Dashboard Routes**: Multiple dashboards for different user roles
- **Admin Routes**: User management, location management, database operations
- **Enhanced Logging**: `enhanced_log_access_attempt()` with risk assessment integration
- **Alert System**: `create_enhanced_security_alert()` with auto-escalation

#### 2. `auth.py` - Authentication & Authorization Module
Implements comprehensive security features:
- **SecurityManager Class**: Handles password hashing, session tokens, failed login tracking
- **JWT Token Management**: Session creation, verification, and timeout enforcement
- **Role-Based Access Control**: Four roles (admin, security_officer, staff, student)
- **Security Decorators**: `@require_auth()` and `@require_api_auth()` for route protection
- **PolicyEngine Class**: Risk assessment based on time, location, and access patterns
- **Audit Logging**: `log_security_event()` with encrypted event details

#### 3. `ai_engine.py` - AI/ML Security Analysis
Machine learning integration for threat detection:
- **SecurityAIEngine Class**: Main AI orchestration
- **Anomaly Detection**: Isolation Forest model trained on access patterns
- **Incident Prediction**: Neural network simulation for threat forecasting
- **Training Data Generation**: Synthetic data creation for 6 months of simulated activity
- **Model Persistence**: Saves/loads models from `models/ai_models.pkl`
- **Fallback Mechanisms**: Rule-based analysis if ML models unavailable

### Data Flow Architecture

```
Card Scan Request → Access Validation (app.py)
                 → Risk Assessment (auth.py PolicyEngine)
                 → AI Anomaly Detection (ai_engine.py)
                 → Enhanced Logging (access_logs + risk_assessments tables)
                 → Alert Generation (security_alerts + auto-escalation to incidents)
                 → Dashboard Updates (real-time metrics)
```

### Database Schema (MySQL)

**Core Tables**:
- `students`: Student records with card mappings (student_id, card_id, status)
- `campus_locations`: Buildings and access points with security levels
- `access_logs`: Complete audit trail with risk scores and review flags
- `system_users`: Dashboard users with role-based permissions

**Security Tables**:
- `security_alerts`: Real-time alerts with severity levels and status tracking
- `security_incidents`: Escalated issues with investigation workflow
- `security_audit_log`: Encrypted audit trail of all system events
- `risk_assessments`: AI-generated risk analysis for each access attempt

**Policy Tables**:
- `access_policies`: Time/location/role-based security rules
- `user_sessions`: Active session tracking with expiration
- `lost_stolen_cards`: Card reporting and resolution tracking

## Common Development Commands

### Database Setup

```bash
# Create database and tables
mysql -u root -p < database_setup.sql

# Verify database structure
python verify_database.py

# Populate sample data (students, locations, demo users)
python populate_sample_data.py

# Empty database setup (no sample data)
mysql -u root -p < database_empty_setup.sql
```

### Application Startup

```bash
# Start Flask application (runs on http://0.0.0.0:5000)
python app.py

# The application will:
# - Initialize AI engine (loads or trains models)
# - Start Flask with debug=True
# - Listen on all interfaces, port 5000
```

### AI/ML Setup

```bash
# Install AI dependencies (numpy, scikit-learn, pandas)
python install_ai_dependencies.py

# This script will:
# - Check for existing packages
# - Install missing dependencies
# - Test AI engine initialization
# - Validate anomaly detection
```

### Database Configuration

**IMPORTANT**: Before running, update database credentials in:
- `app.py` line 34-40: `DB_CONFIG` dictionary
- `verify_database.py` line 12-17: `DB_CONFIG` dictionary

Default credentials:
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'milka',  # Change to your MySQL password
    'database': 'smart_campus_security',
    'autocommit': True
}
```

### Demo Credentials

**System Administrator**:
- Username: `admin`
- Password: `admin123`
- Access: Full system control, advanced dashboard, user management

**Security Officer**:
- Username: `security`
- Password: `security123`
- Access: Security monitoring, incident management, alerts

**Staff Member**:
- Username: `john_doe`
- Password: `staff123`
- Access: Basic logs, limited dashboard

## Testing Approach

**No formal test suite exists**. To verify functionality:

1. **Start the application**: `python app.py`
2. **Access the simulator**: http://localhost:5000
3. **Test scenarios**:
   - Valid access: Select student → location → scan
   - Unauthorized access: Use "Unknown Card" → restricted location
   - Role-based access: Student card → staff-only location (should deny)
   - High-risk detection: Multiple rapid scans → triggers anomaly alerts

4. **Verify in dashboard**: Login as `security` to view alerts and logs
5. **Check database**: Run queries to verify `access_logs`, `security_alerts`, `risk_assessments`

## Development Patterns & Conventions

### Adding New Routes

```python
@app.route('/new_feature')
@require_auth('permission_name')  # Optional: add permission check
def new_feature():
    """Route for new feature"""
    # Get database connection
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database error'}), 500
    
    try:
        cursor = conn.cursor(dictionary=True)
        # Your database operations
        cursor.execute("SELECT ...")
        results = cursor.fetchall()
        
        # Log security event if relevant
        log_security_event('event_type', 'details', session.get('user_id'))
        
        return jsonify({'success': True, 'data': results})
    except mysql.connector.Error as err:
        logger.error(f"Error: {err}")
        return jsonify({'error': str(err)}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
```

### Security Logging Pattern

Always log security-relevant events:
```python
# For access attempts
enhanced_log_access_attempt(
    student_id, card_id, location_id, 
    access_type='entry',
    granted=True/False,
    denial_reason="reason if denied",
    risk_assessment=policy_engine.assess_access_risk(student_id, location_id)
)

# For security alerts
create_enhanced_security_alert(
    alert_type='unauthorized_access',
    severity='high',  # low, medium, high, critical
    location_id=location_id,
    student_id=student_id,
    message="Alert description",
    auto_escalate=True  # Creates incident if severity is high/critical
)

# For audit trail
log_security_event(
    'event_type',
    json.dumps(event_details),
    user_id=request.current_user['user_id']
)
```

### Risk Assessment Integration

Use the PolicyEngine for risk-aware access control:
```python
from auth import policy_engine

# Assess risk before granting access
risk_assessment = policy_engine.assess_access_risk(student_id, location_id)

# risk_assessment contains:
# - 'risk_level': 'low', 'medium', 'high', 'critical'
# - 'risk_score': integer value
# - 'risk_factors': list of contributing factors
# - 'requires_additional_auth': boolean flag

if risk_assessment['risk_level'] == 'critical':
    # Deny or require additional authentication
    pass
```

### AI Anomaly Detection Usage

```python
from ai_engine import get_ai_engine

ai_engine = get_ai_engine()

# Prepare access data
access_data = {
    'hour': datetime.now().hour,
    'day_of_week': datetime.now().weekday(),
    'is_weekend': datetime.now().weekday() >= 5,
    'locations_per_hour': recent_location_count,
    'time_between_access': minutes_since_last_access,
    'current_risk_score': base_risk_score
}

# Detect anomaly
result = ai_engine.detect_anomaly(access_data)
# Returns: {'is_anomaly': bool, 'confidence': float, 'explanation': str}

if result['is_anomaly'] and result['confidence'] > 80:
    create_enhanced_security_alert(...)
```

## File Structure

```
smartscan/
├── app.py                          # Main Flask application
├── auth.py                         # Authentication & authorization
├── ai_engine.py                    # AI/ML security analysis
├── database_setup.sql              # Full database schema with sample data
├── database_empty_setup.sql        # Schema only, no data
├── populate_sample_data.py         # Script to populate demo data
├── verify_database.py              # Database verification utility
├── install_ai_dependencies.py      # AI package installer
├── requirements.txt                # Python dependencies
├── models/                         # AI model storage
│   └── ai_models.pkl              # Trained ML models
├── templates/                      # Jinja2 HTML templates
│   ├── login.html
│   ├── dashboard.html
│   ├── advanced_dashboard.html
│   ├── card_simulator.html
│   ├── virtual_campus.html
│   └── ...
├── backups/                        # Database backup directory
└── security.log                    # Application security logs
```

## Important Notes for Development

### Session Management
- Sessions use JWT tokens stored in Flask session
- Default timeout: 30 minutes (configurable in `auth.py` SecurityManager)
- Token verification on every protected route via decorators

### Database Transactions
- `autocommit=True` is set in DB_CONFIG
- Explicit `conn.commit()` still used in many places for clarity
- Always use try/finally to ensure cursor/connection cleanup

### AI Model Lifecycle
- Models automatically initialize on first import of `ai_engine.py`
- If `models/ai_models.pkl` exists, loads from disk
- Otherwise, generates training data and trains models
- Fallback to rule-based analysis if ML initialization fails

### Security Event Encryption
- Audit log details are encrypted using SecurityManager.encrypt_data()
- Current implementation uses ROT13 (educational demo only)
- For production: replace with AES-256 or similar

### Adding New User Roles
1. Update `ROLES` dictionary in `auth.py`
2. Define permissions list for the role
3. Update `@require_auth()` decorator logic if needed
4. Modify dashboard routes to handle new role

### Extending Risk Assessment
To add new risk factors:
1. Update `SecurityPolicyEngine.assess_access_risk()` in `auth.py`
2. Add factor to `policies['risk_assessment']['factors']`
3. Adjust risk_score calculation logic
4. Update AI training data generation in `ai_engine.py` to include new features

## Backup & Recovery

```bash
# Create database backup (via web UI or command line)
# Web UI: Advanced Dashboard → Database Management → Create Backup

# Manual backup
mysqldump --host localhost --user root --password='milka' \
  --single-transaction --routines --triggers \
  smart_campus_security > backup.sql

# Restore from backup
mysql -u root -p smart_campus_security < backup.sql
```

## Educational Context

This is a **simulation system** for teaching cybersecurity concepts. Key educational features:
- Zero hardware cost - fully software-based
- Real-world security frameworks and patterns
- Hands-on experience with IAM, SIEM, risk assessment
- Suitable for university cybersecurity programs

When adding features, maintain the educational value by:
- Clear logging and audit trails
- Visible security decision-making process
- Realistic threat scenarios
- Comprehensive documentation of security concepts
