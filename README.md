# Smart Campus ID Security System - Virtual Simulation

## Project Overview

This is a **Phase 1 implementation** of the Smart Campus ID Security System for the **St. Lawrence University Uganda Cybersecurity & Innovations Club**. Since we don't have budget for hardware components, this is a complete software simulation that teaches the same cybersecurity concepts as the physical system.

## 🎯 Why Python Over PHP?

We chose **Python with Flask** because:
- **Better for cybersecurity education** - extensive security libraries
- **Easier to learn and maintain** for students
- **More relevant to modern cybersecurity careers**
- **Excellent for rapid prototyping and simulations**
- **Strong community support** for security projects

## 🚀 Quick Setup Guide

### 1. Install Prerequisites

**On Windows:**
```bash
# Install Python 3.8+ from python.org
# Install MySQL Community Server from mysql.com
```

**On Ubuntu/Linux:**
```bash
sudo apt update
sudo apt install python3 python3-pip mysql-server
sudo mysql_secure_installation
```

### 2. Database Setup

```bash
# Start MySQL service
sudo systemctl start mysql  # Linux
# or start MySQL from Services on Windows

# Login to MySQL
mysql -u root -p

# Run the database setup script
source database_setup.sql

# Exit MySQL
exit
```

### 3. Python Environment Setup

```bash
# Clone/download the project files
cd smart-campus-security

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 4. Configure Database Connection

Edit `app.py` and update the database credentials:

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',           # Your MySQL username
    'password': 'your_password',  # Your MySQL password
    'database': 'smart_campus_security',
    'autocommit': True
}
```

### 5. Run the Application

```bash
python app.py
```

Visit: http://localhost:5000

## 🎮 How to Use the Simulation

### Virtual Campus Interface
1. Visit the main page to see the virtual campus map
2. Click on any entry point (doors) to simulate card scanning
3. Enter a card ID when prompted
4. Observe the security response

### Card Simulator
1. Go to "Card Simulator" in the navigation
2. Select a student from the dropdown
3. Choose a campus location
4. Click "Simulate Card Scan" to test access

### Security Dashboard
1. View real-time access logs
2. Monitor security alerts
3. Check system statistics
4. Filter by access status (granted/denied)

## 🧪 Test Scenarios

### Valid Access Test
- **Card:** `RFID_001_ABC123` (John Doe)
- **Location:** Main Library Entrance
- **Expected:** Access Granted ✅

### Unauthorized Card Test
- **Card:** `UNKNOWN_CARD_123`
- **Location:** Any location
- **Expected:** Access Denied + Security Alert 🚨

### Staff Area Test
- **Card:** `RFID_002_DEF456` (Jane Smith - Student)
- **Location:** ICT Department Office (Staff Only)
- **Expected:** Access Denied ❌

### Lost Card Test
```sql
-- Add this to MySQL to test lost card scenario
INSERT INTO lost_stolen_cards (card_id, student_id, report_type) 
VALUES ('RFID_003_GHI789', 'STU003', 'lost');
```

## 📚 Learning Objectives

Students will learn:
- **Access Control Systems** - Authentication and authorization
- **Database Security** - Secure data storage and retrieval
- **Web Application Security** - Session management and input validation
- **Real-time Monitoring** - Security dashboards and alerting
- **Incident Response** - Security alert handling
- **System Architecture** - Multi-tier application design

## 🔧 System Architecture

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────┐
│ Virtual Campus  │───▶│   Flask App  │───▶│  Dashboard  │
│ (Frontend UI)   │    │   (Backend)  │    │ (Monitoring)│
└─────────────────┘    └──────────────┘    └─────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌──────────────┐
│ Card Simulator  │    │   MySQL DB   │
│ (Virtual RFID)  │    │  (Data Store)│
└─────────────────┘    └──────────────┘
```

## 🗃️ Database Schema

### Key Tables:
- **students** - Student information and card IDs
- **campus_locations** - Entry points and access levels
- **access_logs** - All access attempts and results
- **security_alerts** - Security incidents and notifications
- **lost_stolen_cards** - Reported lost/stolen cards

## 🚀 Phase 2 & 3 Roadmap

### Phase 2: Advanced Security Features (Week 2)
- [ ] User authentication system
- [ ] Role-based access control
- [ ] Advanced encryption simulation
- [ ] Security incident workflows
- [ ] Audit trails and compliance

### Phase 3: IoT Integration Simulation (Week 3)
- [ ] Virtual IoT device management
- [ ] Network security simulation
- [ ] Wireless communication protocols
- [ ] Edge computing concepts
- [ ] Cloud integration

## 🏆 Club Project Benefits

✅ **Zero Hardware Cost** - Complete software simulation  
✅ **Educational Value** - Same learning as physical system  
✅ **Portfolio Project** - Demonstrable cybersecurity skills  
✅ **Scalable** - Easy to add features and students  
✅ **Presentation Ready** - Professional interface for demonstrations  

## 🛠️ Troubleshooting

### Common Issues:

**Database Connection Error:**
```bash
# Check MySQL service is running
sudo systemctl status mysql

# Verify credentials in app.py
```

**Port Already in Use:**
```bash
# Change port in app.py
app.run(debug=True, host='0.0.0.0', port=5001)
```

**Missing Dependencies:**
```bash
# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

## 📞 Support

For club members:
- Create issues in the project repository
- Ask questions during club meetings
- Join our WhatsApp group for quick support

## 📄 License

Educational use only - St. Lawrence University Uganda Cybersecurity Club

---

**Built by:** SLAU Cybersecurity & Innovations Club  
**Purpose:** Educational simulation for cybersecurity learning  
**Year:** 2025  

*"Learning cybersecurity through hands-on simulation"*