#!/usr/bin/env python3
"""
AI Dependencies Installation Script
Smart Campus Security System - St. Lawrence University
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a Python package using pip"""
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
        print(f"✅ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Failed to install {package}")
        return False

def check_package(package_name, import_name=None):
    """Check if a package is already installed"""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        print(f"✅ {package_name} is already installed")
        return True
    except ImportError:
        print(f"❌ {package_name} is not installed")
        return False

def main():
    print("🤖 Smart Campus Security System - AI Dependencies Installer")
    print("=" * 60)
    
    # Required packages for AI features
    ai_packages = [
        ('numpy', 'numpy'),
        ('scikit-learn', 'sklearn'),
        ('pandas', 'pandas'),
    ]
    
    # Optional packages (will install with fallbacks if failed)
    optional_packages = [
        ('matplotlib', 'matplotlib'),
        ('seaborn', 'seaborn'),
    ]
    
    print("\n🔍 Checking AI dependencies...")
    
    # Check and install required packages
    missing_packages = []
    for package, import_name in ai_packages:
        if not check_package(package, import_name):
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📦 Installing {len(missing_packages)} missing packages...")
        for package in missing_packages:
            print(f"\n🔄 Installing {package}...")
            if not install_package(package):
                print(f"⚠️ Warning: {package} installation failed. AI features may have limited functionality.")
    else:
        print("\n✅ All required AI packages are already installed!")
    
    # Try to install optional packages
    print(f"\n📦 Installing optional packages...")
    for package, import_name in optional_packages:
        if not check_package(package, import_name):
            print(f"\n🔄 Installing optional package {package}...")
            install_package(package)
    
    # Test AI system
    print(f"\n🧪 Testing AI system...")
    try:
        from ai_engine import get_ai_engine
        ai_engine = get_ai_engine()
        print("✅ AI engine loaded successfully!")
        
        # Test anomaly detection
        test_data = {
            'hour': 14,
            'day_of_week': 1,
            'is_weekend': False,
            'locations_per_hour': 2,
            'time_between_access': 30,
            'current_risk_score': 3
        }
        
        result = ai_engine.detect_anomaly(test_data)
        print(f"✅ AI anomaly detection test passed!")
        print(f"   - Test result: {result['explanation']}")
        print(f"   - Confidence: {result['confidence']:.1f}%")
        
    except Exception as e:
        print(f"⚠️ AI system test failed: {e}")
        print("   The system will fall back to rule-based analysis.")
    
    print(f"\n🎉 Installation complete!")
    print("=" * 60)
    print("📋 Next steps:")
    print("   1. Restart your Python application: python app.py")
    print("   2. Test the card simulator with multiple location scans")
    print("   3. Watch the AI detect anomalies in real-time!")
    print("\n💡 Tip: Try scanning 5+ locations quickly to trigger anomaly detection")

if __name__ == "__main__":
    main()