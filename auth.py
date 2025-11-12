# Advanced Authentication and Authorization Module
# Phase 2: Enhanced Security Features

import hashlib
import secrets
import time
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import session, request, jsonify, redirect, url_for

class SecurityManager:
    """Advanced security management for the campus system"""
    
    def __init__(self):
        self.secret_key = secrets.token_hex(32)
        self.failed_attempts = {}  # Track failed login attempts
        self.active_sessions = {}  # Track active user sessions
        self.security_policies = {
            'max_failed_attempts': 3,
            'lockout_duration': 300,  # 5 minutes
            'session_timeout': 1800,  # 30 minutes
            'password_min_length': 8,
            'require_2fa': False,
            'encryption_enabled': True
        }
    
    def hash_password(self, password, salt=None):
        """Secure password hashing with salt"""
        if not salt:
            salt = secrets.token_hex(16)
        
        # Use SHA256 for demo purposes (in production, use PBKDF2 with more iterations)
        password_hash = hashlib.sha256(f"{salt}:{password}".encode('utf-8')).hexdigest()
        
        return f"{salt}:{password_hash}"
    
    def verify_password(self, password, stored_hash):
        """Verify password against stored hash"""
        try:
            salt, hash_part = stored_hash.split(':')
            # For demo accounts, use simple verification
            if salt in ['admin_salt_123', 'security_salt_456', 'staff_salt_789']:
                # Demo password verification
                demo_passwords = {
                    'admin_salt_123': 'admin123',
                    'security_salt_456': 'security123', 
                    'staff_salt_789': 'staff123'
                }
                return password == demo_passwords.get(salt)
            else:
                # Normal password verification
                expected_hash = hashlib.sha256(f"{salt}:{password}".encode('utf-8')).hexdigest()
                return expected_hash == hash_part
        except:
            return False
    
    def generate_session_token(self, user_id, role):
        """Generate secure JWT session token"""
        payload = {
            'user_id': user_id,
            'role': role,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(seconds=self.security_policies['session_timeout'])
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm='HS256')
        self.active_sessions[user_id] = {
            'token': token,
            'created': datetime.utcnow(),
            'last_activity': datetime.utcnow(),
            'ip_address': request.remote_addr if request else 'unknown'
        }
        
        return token
    
    def verify_session_token(self, token):
        """Verify and decode session token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            user_id = payload['user_id']
            
            # Check if session is still active
            if user_id in self.active_sessions:
                session_info = self.active_sessions[user_id]
                
                # Update last activity
                session_info['last_activity'] = datetime.utcnow()
                
                return payload
            
            return None
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def track_failed_attempt(self, identifier):
        """Track failed login attempts"""
        current_time = time.time()
        
        if identifier not in self.failed_attempts:
            self.failed_attempts[identifier] = []
        
        # Remove old attempts (older than lockout duration)
        self.failed_attempts[identifier] = [
            attempt for attempt in self.failed_attempts[identifier]
            if current_time - attempt < self.security_policies['lockout_duration']
        ]
        
        # Add current attempt
        self.failed_attempts[identifier].append(current_time)
    
    def is_account_locked(self, identifier):
        """Check if account is locked due to failed attempts"""
        if identifier not in self.failed_attempts:
            return False
        
        current_time = time.time()
        recent_attempts = [
            attempt for attempt in self.failed_attempts[identifier]
            if current_time - attempt < self.security_policies['lockout_duration']
        ]
        
        return len(recent_attempts) >= self.security_policies['max_failed_attempts']
    
    def encrypt_data(self, data):
        """Simple encryption simulation for educational purposes"""
        if not self.security_policies['encryption_enabled']:
            return data
        
        # Simple Caesar cipher for demonstration (NOT secure for real use)
        key = 13  # ROT13
        encrypted = ""
        
        for char in str(data):
            if char.isalpha():
                ascii_offset = ord('a') if char.islower() else ord('A')
                encrypted += chr((ord(char) - ascii_offset + key) % 26 + ascii_offset)
            else:
                encrypted += char
        
        return f"ENCRYPTED:{encrypted}"
    
    def decrypt_data(self, encrypted_data):
        """Decrypt data (educational simulation)"""
        if not encrypted_data.startswith("ENCRYPTED:"):
            return encrypted_data
        
        data = encrypted_data[10:]  # Remove "ENCRYPTED:" prefix
        key = -13  # Reverse ROT13
        decrypted = ""
        
        for char in data:
            if char.isalpha():
                ascii_offset = ord('a') if char.islower() else ord('A')
                decrypted += chr((ord(char) - ascii_offset + key) % 26 + ascii_offset)
            else:
                decrypted += char
        
        return decrypted

# Global security manager instance
security_manager = SecurityManager()

# Role definitions
ROLES = {
    'admin': {
        'name': 'System Administrator',
        'permissions': ['all']
    },
    'security_officer': {
        'name': 'Security Officer',
        'permissions': ['view_logs', 'manage_alerts', 'view_reports', 'manage_cards']
    },
    'staff': {
        'name': 'Staff Member', 
        'permissions': ['view_logs', 'basic_reports']
    },
    'student': {
        'name': 'Student',
        'permissions': ['view_own_logs']
    }
}

def require_auth(required_permission=None):
    """Decorator to require authentication and optional permission"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if user is authenticated
            if 'auth_token' not in session:
                return redirect(url_for('login'))
            
            # Verify token
            token_data = security_manager.verify_session_token(session['auth_token'])
            if not token_data:
                session.pop('auth_token', None)
                return redirect(url_for('login'))
            
            # Check permissions if required
            if required_permission:
                user_role = token_data.get('role')
                role_permissions = ROLES.get(user_role, {}).get('permissions', [])
                
                if 'all' not in role_permissions and required_permission not in role_permissions:
                    return jsonify({'error': 'Insufficient permissions'}), 403
            
            # Store user info in request context
            request.current_user = token_data
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_api_auth(required_permission=None):
    """Decorator for API endpoints requiring authentication"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({'error': 'Authentication required'}), 401
            
            token = auth_header.split(' ')[1]
            token_data = security_manager.verify_session_token(token)
            
            if not token_data:
                return jsonify({'error': 'Invalid or expired token'}), 401
            
            # Check permissions
            if required_permission:
                user_role = token_data.get('role')
                role_permissions = ROLES.get(user_role, {}).get('permissions', [])
                
                if 'all' not in role_permissions and required_permission not in role_permissions:
                    return jsonify({'error': 'Insufficient permissions'}), 403
            
            request.current_user = token_data
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def log_security_event(event_type, details, user_id=None):
    """Log security events for audit trail"""
    from app import get_db_connection  # Import here to avoid circular imports
    
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        query = """
            INSERT INTO security_audit_log (event_type, event_details, user_id, 
                                           ip_address, user_agent, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(query, (
            event_type,
            security_manager.encrypt_data(details),  # Encrypt sensitive details
            user_id,
            request.remote_addr if request else 'system',
            request.headers.get('User-Agent') if request else 'system',
            datetime.now()
        ))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Error logging security event: {e}")
        return False
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

class SecurityPolicyEngine:
    """Advanced security policy enforcement"""
    
    def __init__(self):
        self.policies = {
            'time_based_access': {
                'enabled': True,
                'restricted_hours': {
                    'start': '22:00',  # 10 PM
                    'end': '06:00'     # 6 AM
                }
            },
            'location_based_access': {
                'enabled': True,
                'high_security_locations': [5, 10],  # Cybersecurity Lab, ICT Office
                'require_additional_auth': True
            },
            'risk_assessment': {
                'enabled': True,
                'factors': ['time', 'location', 'user_behavior', 'access_pattern']
            }
        }
    
    def assess_access_risk(self, student_id, location_id, access_time=None):
        """Assess risk level of access attempt"""
        if not access_time:
            access_time = datetime.now()
        
        risk_score = 0
        risk_factors = []
        
        # Time-based risk assessment
        if self.policies['time_based_access']['enabled']:
            hour = access_time.hour
            if hour >= 22 or hour <= 6:
                risk_score += 2
                risk_factors.append('off_hours_access')
        
        # Location-based risk assessment
        if self.policies['location_based_access']['enabled']:
            if location_id in self.policies['location_based_access']['high_security_locations']:
                risk_score += 3
                risk_factors.append('high_security_location')
        
        # Determine risk level
        if risk_score <= 1:
            risk_level = 'low'
        elif risk_score <= 3:
            risk_level = 'medium'
        elif risk_score <= 5:
            risk_level = 'high'
        else:
            risk_level = 'critical'
        
        return {
            'risk_level': risk_level,
            'risk_score': risk_score,
            'risk_factors': risk_factors,
            'requires_additional_auth': risk_score >= 3
        }

# Global policy engine instance
policy_engine = SecurityPolicyEngine()