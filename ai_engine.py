# AI Engine for Smart Campus Security System
# St. Lawrence University - Cybersecurity Club
# Artificial Intelligence Integration Module

import numpy as np
import json
import random
from datetime import datetime, timedelta
from collections import defaultdict
import logging
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
import pickle
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class SecurityAIEngine:
    """Advanced AI Engine for Security Analysis and Prediction"""
    
    def __init__(self):
        self.models = {
            'anomaly_detector': None,
            'incident_predictor': None,
            'backup_optimizer': None,
            'behavior_analyzer': None
        }
        self.scalers = {
            'access_patterns': StandardScaler(),
            'incident_features': StandardScaler()
        }
        self.training_data = {
            'access_patterns': [],
            'incidents': [],
            'backup_patterns': []
        }
        self.model_dir = Path("models")
        self.model_dir.mkdir(exist_ok=True)
        
        # Initialize with training data generation
        self.generate_training_data()
        self.train_models()
    
    def generate_training_data(self):
        """Generate realistic training data for new system"""
        logger.info("Generating AI training data...")
        
        # Generate synthetic access patterns (simulating 6 months of data)
        self._generate_access_patterns()
        
        # Generate incident scenarios
        self._generate_incident_patterns()
        
        # Generate backup patterns
        self._generate_backup_patterns()
        
        logger.info(f"Generated {len(self.training_data['access_patterns'])} access patterns, "
                   f"{len(self.training_data['incidents'])} incidents, "
                   f"{len(self.training_data['backup_patterns'])} backup scenarios")
    
    def _generate_access_patterns(self):
        """Generate realistic access pattern training data"""
        students = ['STU001', 'STU002', 'STU003', 'STU004', 'STU005']
        locations = list(range(1, 13))  # 12 campus locations
        
        # Normal patterns (80% of data)
        for _ in range(2000):
            student = random.choice(students)
            
            # Normal daily pattern
            base_time = datetime.now() - timedelta(days=random.randint(1, 180))
            
            # Students typically access 1-3 locations per day
            daily_locations = random.sample(locations, random.randint(1, 3))
            
            for loc in daily_locations:
                access_time = base_time + timedelta(
                    hours=random.randint(8, 18),  # Normal hours
                    minutes=random.randint(0, 59)
                )
                
                pattern = {
                    'student_id': student,
                    'location_id': loc,
                    'access_time': access_time,
                    'hour': access_time.hour,
                    'day_of_week': access_time.weekday(),
                    'is_weekend': access_time.weekday() >= 5,
                    'locations_per_hour': 1,
                    'time_between_access': random.randint(30, 180),  # minutes
                    'is_anomaly': False,
                    'risk_score': random.randint(1, 3)
                }
                self.training_data['access_patterns'].append(pattern)
        
        # Anomalous patterns (20% of data)
        for _ in range(500):
            student = random.choice(students)
            base_time = datetime.now() - timedelta(days=random.randint(1, 180))
            
            # Anomaly types
            anomaly_type = random.choice([
                'multiple_locations',  # Many locations in short time
                'off_hours',          # Access at unusual hours
                'rapid_succession',   # Very fast access attempts
                'unusual_pattern'     # Completely different from normal
            ])
            
            if anomaly_type == 'multiple_locations':
                # Student accessing many locations quickly
                num_locations = random.randint(5, 10)
                selected_locations = random.sample(locations, num_locations)
                
                for i, loc in enumerate(selected_locations):
                    access_time = base_time + timedelta(minutes=i * random.randint(1, 10))
                    pattern = {
                        'student_id': student,
                        'location_id': loc,
                        'access_time': access_time,
                        'hour': access_time.hour,
                        'day_of_week': access_time.weekday(),
                        'is_weekend': access_time.weekday() >= 5,
                        'locations_per_hour': num_locations,
                        'time_between_access': random.randint(1, 10),
                        'is_anomaly': True,
                        'risk_score': random.randint(7, 10)
                    }
                    self.training_data['access_patterns'].append(pattern)
            
            elif anomaly_type == 'off_hours':
                # Access during unusual hours
                unusual_hour = random.choice([0, 1, 2, 3, 22, 23])
                access_time = base_time.replace(hour=unusual_hour, minute=random.randint(0, 59))
                
                pattern = {
                    'student_id': student,
                    'location_id': random.choice(locations),
                    'access_time': access_time,
                    'hour': access_time.hour,
                    'day_of_week': access_time.weekday(),
                    'is_weekend': access_time.weekday() >= 5,
                    'locations_per_hour': 1,
                    'time_between_access': random.randint(60, 300),
                    'is_anomaly': True,
                    'risk_score': random.randint(6, 9)
                }
                self.training_data['access_patterns'].append(pattern)
    
    def _generate_incident_patterns(self):
        """Generate incident pattern training data"""
        incident_types = [
            'unauthorized_access', 'lost_card_used', 'multiple_failed_attempts',
            'tailgating', 'system_breach', 'policy_violation'
        ]
        
        for _ in range(200):
            incident_time = datetime.now() - timedelta(days=random.randint(1, 180))
            
            # Features that predict incidents
            incident = {
                'incident_type': random.choice(incident_types),
                'hour': incident_time.hour,
                'day_of_week': incident_time.weekday(),
                'is_weekend': incident_time.weekday() >= 5,
                'failed_attempts_before': random.randint(0, 10),
                'unusual_access_patterns': random.randint(0, 5),
                'off_hours_activity': random.randint(0, 3),
                'multiple_locations_accessed': random.randint(0, 8),
                'severity': random.choice(['low', 'medium', 'high', 'critical']),
                'location_security_level': random.choice(['public', 'restricted', 'staff_only']),
                'incident_occurred': True
            }
            self.training_data['incidents'].append(incident)
        
        # Add non-incident data (normal days)
        for _ in range(800):
            normal_time = datetime.now() - timedelta(days=random.randint(1, 180))
            
            non_incident = {
                'incident_type': 'none',
                'hour': normal_time.hour,
                'day_of_week': normal_time.weekday(),
                'is_weekend': normal_time.weekday() >= 5,
                'failed_attempts_before': random.randint(0, 2),
                'unusual_access_patterns': random.randint(0, 1),
                'off_hours_activity': 0,
                'multiple_locations_accessed': random.randint(0, 2),
                'severity': 'none',
                'location_security_level': random.choice(['public', 'restricted']),
                'incident_occurred': False
            }
            self.training_data['incidents'].append(non_incident)
    
    def _generate_backup_patterns(self):
        """Generate backup optimization training data"""
        for _ in range(100):
            backup_time = datetime.now() - timedelta(days=random.randint(1, 90))
            
            pattern = {
                'database_size_mb': random.randint(100, 2000),
                'daily_log_count': random.randint(1000, 50000),
                'backup_duration_minutes': random.randint(5, 60),
                'day_of_week': backup_time.weekday(),
                'hour': backup_time.hour,
                'system_load': random.uniform(0.1, 0.9),
                'available_storage_gb': random.randint(10, 100),
                'backup_success': random.choice([True, True, True, False]),  # 75% success rate
                'optimal_time': random.choice([True, False])
            }
            self.training_data['backup_patterns'].append(pattern)
    
    def train_models(self):
        """Train all AI models"""
        logger.info("Training AI models...")
        
        try:
            # Train anomaly detection model
            self._train_anomaly_detector()
            
            # Train incident prediction model
            self._train_incident_predictor()
            
            # Train backup optimizer
            self._train_backup_optimizer()
            
            # Save models
            self._save_models()
            
            logger.info("AI models trained successfully")
            
        except Exception as e:
            logger.error(f"Error training models: {e}")
            # Use simple rule-based fallbacks
            self._initialize_fallback_models()
    
    def _train_anomaly_detector(self):
        """Train anomaly detection model"""
        # Prepare features for anomaly detection
        features = []
        labels = []
        
        for pattern in self.training_data['access_patterns']:
            feature_vector = [
                pattern['hour'],
                pattern['day_of_week'],
                int(pattern['is_weekend']),
                pattern['locations_per_hour'],
                pattern['time_between_access'],
                pattern['risk_score']
            ]
            features.append(feature_vector)
            labels.append(pattern['is_anomaly'])
        
        # Convert to numpy arrays
        X = np.array(features)
        y = np.array(labels)
        
        # Scale features
        X_scaled = self.scalers['access_patterns'].fit_transform(X)
        
        # Train Isolation Forest for anomaly detection
        self.models['anomaly_detector'] = IsolationForest(
            contamination=0.2,  # 20% anomalies
            random_state=42,
            n_estimators=100
        )
        self.models['anomaly_detector'].fit(X_scaled)
        
        # Train DBSCAN for clustering normal behavior
        self.models['behavior_analyzer'] = DBSCAN(
            eps=0.5,
            min_samples=5
        )
        self.models['behavior_analyzer'].fit(X_scaled[y == False])  # Only normal patterns
    
    def _train_incident_predictor(self):
        """Train incident prediction model"""
        features = []
        labels = []
        
        for incident in self.training_data['incidents']:
            feature_vector = [
                incident['hour'],
                incident['day_of_week'],
                int(incident['is_weekend']),
                incident['failed_attempts_before'],
                incident['unusual_access_patterns'],
                incident['off_hours_activity'],
                incident['multiple_locations_accessed'],
                1 if incident['location_security_level'] == 'staff_only' else 0,
                1 if incident['location_security_level'] == 'restricted' else 0
            ]
            features.append(feature_vector)
            labels.append(int(incident['incident_occurred']))
        
        X = np.array(features)
        y = np.array(labels)
        
        X_scaled = self.scalers['incident_features'].fit_transform(X)
        
        # Simple neural network simulation using weighted features
        self.models['incident_predictor'] = {
            'weights': np.random.randn(X.shape[1]) * 0.1,
            'bias': 0.0,
            'threshold': 0.5
        }
        
        # Train with simple gradient descent simulation
        learning_rate = 0.01
        for epoch in range(100):
            predictions = self._sigmoid(X_scaled @ self.models['incident_predictor']['weights'] + 
                                      self.models['incident_predictor']['bias'])
            loss = np.mean((predictions - y) ** 2)
            
            # Update weights
            gradient = X_scaled.T @ (predictions - y) / len(y)
            self.models['incident_predictor']['weights'] -= learning_rate * gradient
    
    def _train_backup_optimizer(self):
        """Train backup optimization model"""
        features = []
        labels = []
        
        for backup in self.training_data['backup_patterns']:
            feature_vector = [
                backup['database_size_mb'] / 1000,  # Normalize
                backup['daily_log_count'] / 10000,  # Normalize
                backup['day_of_week'],
                backup['hour'],
                backup['system_load'],
                backup['available_storage_gb'] / 100  # Normalize
            ]
            features.append(feature_vector)
            labels.append(int(backup['optimal_time']))
        
        X = np.array(features)
        y = np.array(labels)
        
        # Simple decision tree simulation
        self.models['backup_optimizer'] = {
            'optimal_hours': [2, 3, 4, 22, 23],  # Low activity hours
            'min_storage_gb': 20,
            'max_system_load': 0.7
        }
    
    def _sigmoid(self, x):
        """Sigmoid activation function"""
        return 1 / (1 + np.exp(-np.clip(x, -500, 500)))
    
    def _save_models(self):
        """Save trained models to disk"""
        try:
            model_data = {
                'models': self.models,
                'scalers': self.scalers,
                'training_stats': {
                    'access_patterns': len(self.training_data['access_patterns']),
                    'incidents': len(self.training_data['incidents']),
                    'backup_patterns': len(self.training_data['backup_patterns'])
                }
            }
            
            with open(self.model_dir / 'ai_models.pkl', 'wb') as f:
                pickle.dump(model_data, f)
            
            logger.info("AI models saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving models: {e}")
    
    def _load_models(self):
        """Load trained models from disk"""
        try:
            model_file = self.model_dir / 'ai_models.pkl'
            if model_file.exists():
                with open(model_file, 'rb') as f:
                    model_data = pickle.load(f)
                
                self.models = model_data['models']
                self.scalers = model_data['scalers']
                
                logger.info("AI models loaded successfully")
                return True
        except Exception as e:
            logger.error(f"Error loading models: {e}")
        
        return False
    
    def _initialize_fallback_models(self):
        """Initialize simple rule-based models as fallback"""
        self.models = {
            'anomaly_detector': 'rule_based',
            'incident_predictor': 'rule_based', 
            'backup_optimizer': 'rule_based',
            'behavior_analyzer': 'rule_based'
        }
        logger.info("Initialized fallback rule-based models")
    
    def detect_anomaly(self, access_data):
        """AI-powered anomaly detection"""
        try:
            if self.models['anomaly_detector'] == 'rule_based':
                return self._rule_based_anomaly_detection(access_data)
            
            # Prepare features
            features = np.array([[
                access_data.get('hour', 12),
                access_data.get('day_of_week', 1),
                int(access_data.get('is_weekend', False)),
                access_data.get('locations_per_hour', 1),
                access_data.get('time_between_access', 60),
                access_data.get('current_risk_score', 3)
            ]])
            
            # Scale features
            features_scaled = self.scalers['access_patterns'].transform(features)
            
            # Predict anomaly
            anomaly_score = self.models['anomaly_detector'].decision_function(features_scaled)[0]
            is_anomaly = self.models['anomaly_detector'].predict(features_scaled)[0] == -1
            
            return {
                'is_anomaly': is_anomaly,
                'anomaly_score': float(anomaly_score),
                'confidence': min(abs(anomaly_score) * 20, 100),  # Convert to percentage
                'risk_level': self._calculate_risk_level(anomaly_score),
                'explanation': self._explain_anomaly(access_data, is_anomaly)
            }
            
        except Exception as e:
            logger.error(f"Error in anomaly detection: {e}")
            return self._rule_based_anomaly_detection(access_data)
    
    def _rule_based_anomaly_detection(self, access_data):
        """Simple rule-based anomaly detection"""
        anomaly_factors = []
        risk_score = 0
        
        # Check for multiple locations in short time
        if access_data.get('locations_per_hour', 1) > 4:
            anomaly_factors.append("Multiple locations accessed rapidly")
            risk_score += 3
        
        # Check for off-hours access
        hour = access_data.get('hour', 12)
        if hour < 6 or hour > 22:
            anomaly_factors.append("Access during off-hours")
            risk_score += 2
        
        # Check for rapid succession
        if access_data.get('time_between_access', 60) < 5:
            anomaly_factors.append("Very rapid access attempts")
            risk_score += 2
        
        # Check for weekend access to restricted areas
        if access_data.get('is_weekend') and access_data.get('location_security_level') == 'restricted':
            anomaly_factors.append("Weekend access to restricted area")
            risk_score += 1
        
        is_anomaly = risk_score >= 3
        
        return {
            'is_anomaly': is_anomaly,
            'anomaly_score': risk_score,
            'confidence': min(risk_score * 20, 100),
            'risk_level': 'high' if risk_score >= 5 else 'medium' if risk_score >= 3 else 'low',
            'explanation': '; '.join(anomaly_factors) if anomaly_factors else 'Normal access pattern'
        }
    
    def predict_incident_risk(self, current_conditions):
        """AI-powered incident risk prediction"""
        try:
            if self.models['incident_predictor'] == 'rule_based':
                return self._rule_based_incident_prediction(current_conditions)
            
            # Prepare features
            features = np.array([[
                current_conditions.get('hour', 12),
                current_conditions.get('day_of_week', 1),
                int(current_conditions.get('is_weekend', False)),
                current_conditions.get('failed_attempts_recent', 0),
                current_conditions.get('unusual_patterns_detected', 0),
                current_conditions.get('off_hours_activity', 0),
                current_conditions.get('multiple_locations_accessed', 0),
                1 if current_conditions.get('location_security_level') == 'staff_only' else 0,
                1 if current_conditions.get('location_security_level') == 'restricted' else 0
            ]])
            
            # Scale features
            features_scaled = self.scalers['incident_features'].transform(features)
            
            # Predict
            prediction = self._sigmoid(
                features_scaled @ self.models['incident_predictor']['weights'] + 
                self.models['incident_predictor']['bias']
            )[0]
            
            risk_level = self._calculate_incident_risk_level(prediction)
            
            return {
                'incident_probability': float(prediction),
                'risk_level': risk_level,
                'confidence': min(abs(prediction - 0.5) * 200, 100),
                'recommendation': self._get_incident_recommendation(prediction, current_conditions),
                'factors': self._identify_risk_factors(current_conditions)
            }
            
        except Exception as e:
            logger.error(f"Error in incident prediction: {e}")
            return self._rule_based_incident_prediction(current_conditions)
    
    def _rule_based_incident_prediction(self, conditions):
        """Rule-based incident risk prediction"""
        risk_factors = []
        probability = 0.1  # Base probability
        
        # High-risk factors
        if conditions.get('failed_attempts_recent', 0) > 3:
            risk_factors.append("Multiple recent failed attempts")
            probability += 0.3
        
        if conditions.get('off_hours_activity', 0) > 0:
            risk_factors.append("Off-hours suspicious activity")
            probability += 0.2
        
        if conditions.get('multiple_locations_accessed', 0) > 5:
            risk_factors.append("Unusual location access pattern")
            probability += 0.25
        
        # Medium-risk factors
        hour = conditions.get('hour', 12)
        if hour < 6 or hour > 22:
            risk_factors.append("Late night/early morning activity")
            probability += 0.15
        
        if conditions.get('is_weekend') and conditions.get('location_security_level') == 'restricted':
            risk_factors.append("Weekend restricted area access")
            probability += 0.1
        
        probability = min(probability, 0.95)  # Cap at 95%
        
        return {
            'incident_probability': probability,
            'risk_level': self._calculate_incident_risk_level(probability),
            'confidence': 80,
            'recommendation': self._get_incident_recommendation(probability, conditions),
            'factors': risk_factors
        }
    
    def optimize_backup_schedule(self, system_conditions):
        """AI-powered backup schedule optimization"""
        try:
            if self.models['backup_optimizer'] == 'rule_based':
                return self._rule_based_backup_optimization(system_conditions)
            
            current_hour = datetime.now().hour
            optimal_hours = self.models['backup_optimizer']['optimal_hours']
            min_storage = self.models['backup_optimizer']['min_storage_gb']
            max_load = self.models['backup_optimizer']['max_system_load']
            
            is_optimal_time = current_hour in optimal_hours
            has_storage = system_conditions.get('available_storage_gb', 0) >= min_storage
            low_load = system_conditions.get('system_load', 1.0) <= max_load
            
            recommendation = {
                'optimal_now': is_optimal_time and has_storage and low_load,
                'next_optimal_time': self._find_next_optimal_backup_time(system_conditions),
                'estimated_duration': self._estimate_backup_duration(system_conditions),
                'storage_requirement': self._calculate_storage_requirement(system_conditions),
                'recommendations': []
            }
            
            if not has_storage:
                recommendation['recommendations'].append("Insufficient storage space - cleanup required")
            if not low_load:
                recommendation['recommendations'].append("High system load - wait for lower usage period")
            if not is_optimal_time:
                recommendation['recommendations'].append(f"Better backup time: {recommendation['next_optimal_time']}")
            
            if recommendation['optimal_now']:
                recommendation['recommendations'].append("✅ Optimal conditions for backup - proceed now")
            
            return recommendation
            
        except Exception as e:
            logger.error(f"Error in backup optimization: {e}")
            return self._rule_based_backup_optimization(system_conditions)
    
    def _rule_based_backup_optimization(self, conditions):
        """Rule-based backup optimization"""
        current_hour = datetime.now().hour
        
        # Optimal hours (low activity periods)
        optimal_hours = [2, 3, 4, 22, 23]
        is_optimal_time = current_hour in optimal_hours
        
        return {
            'optimal_now': is_optimal_time,
            'next_optimal_time': self._find_next_optimal_backup_time(conditions),
            'estimated_duration': self._estimate_backup_duration(conditions),
            'storage_requirement': self._calculate_storage_requirement(conditions),
            'recommendations': [
                "✅ Proceed with backup" if is_optimal_time else "⏰ Wait for optimal time (late night/early morning)",
                "💾 Ensure sufficient storage space",
                "📊 Monitor system performance during backup"
            ]
        }
    
    def _calculate_risk_level(self, score):
        """Calculate risk level from anomaly score"""
        abs_score = abs(score)
        if abs_score > 0.5:
            return 'critical'
        elif abs_score > 0.3:
            return 'high'
        elif abs_score > 0.1:
            return 'medium'
        else:
            return 'low'
    
    def _calculate_incident_risk_level(self, probability):
        """Calculate incident risk level from probability"""
        if probability > 0.7:
            return 'critical'
        elif probability > 0.5:
            return 'high'
        elif probability > 0.3:
            return 'medium'
        else:
            return 'low'
    
    def _explain_anomaly(self, access_data, is_anomaly):
        """Generate human-readable explanation for anomaly detection"""
        if not is_anomaly:
            return "Access pattern appears normal"
        
        explanations = []
        
        if access_data.get('locations_per_hour', 1) > 3:
            explanations.append(f"High location access rate ({access_data['locations_per_hour']} locations/hour)")
        
        hour = access_data.get('hour', 12)
        if hour < 6 or hour > 22:
            explanations.append(f"Off-hours access ({hour}:00)")
        
        if access_data.get('time_between_access', 60) < 10:
            explanations.append("Rapid successive access attempts")
        
        return '; '.join(explanations) if explanations else "Unusual access pattern detected"
    
    def _get_incident_recommendation(self, probability, conditions):
        """Get recommendation based on incident probability"""
        if probability > 0.7:
            return "🚨 IMMEDIATE ACTION: Deploy security personnel, monitor closely"
        elif probability > 0.5:
            return "⚠️ HIGH ALERT: Increase monitoring, prepare response team"
        elif probability > 0.3:
            return "⚡ ENHANCED MONITORING: Watch for escalation, review recent activity"
        else:
            return "✅ NORMAL OPERATIONS: Continue routine monitoring"
    
    def _identify_risk_factors(self, conditions):
        """Identify specific risk factors"""
        factors = []
        
        if conditions.get('failed_attempts_recent', 0) > 2:
            factors.append("Recent failed access attempts")
        
        if conditions.get('unusual_patterns_detected', 0) > 0:
            factors.append("Unusual access patterns detected")
        
        if conditions.get('off_hours_activity', 0) > 0:
            factors.append("Off-hours activity")
        
        return factors
    
    def _find_next_optimal_backup_time(self, conditions):
        """Find next optimal backup time"""
        optimal_hours = [2, 3, 4, 22, 23]
        current_hour = datetime.now().hour
        
        # Find next optimal hour
        for hour in optimal_hours:
            if hour > current_hour:
                return f"{hour:02d}:00 today"
        
        # If no more optimal hours today, return first optimal hour tomorrow
        return f"{optimal_hours[0]:02d}:00 tomorrow"
    
    def _estimate_backup_duration(self, conditions):
        """Estimate backup duration based on system conditions"""
        db_size = conditions.get('database_size_mb', 500)
        
        # Simple estimation: larger databases take longer
        if db_size < 100:
            return "5-10 minutes"
        elif db_size < 500:
            return "10-20 minutes"
        elif db_size < 1000:
            return "20-30 minutes"
        else:
            return "30+ minutes"
    
    def _calculate_storage_requirement(self, conditions):
        """Calculate storage requirement for backup"""
        db_size = conditions.get('database_size_mb', 500)
        
        # Backup typically 60-80% of original size due to compression
        estimated_size = db_size * 0.7
        
        return f"{estimated_size:.1f} MB"

# Global AI engine instance
ai_engine = SecurityAIEngine()

def get_ai_engine():
    """Get the global AI engine instance"""
    return ai_engine