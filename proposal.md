🧠 Smart Campus ID Security System

Project Proposal
Department of Cyber Security
St. Lawrence University (2025)

1. Project Title

Smart Campus ID Security System

2. Project Overview

The Smart Campus ID Security System aims to strengthen campus security and streamline student access management through the integration of RFID/NFC smart identification technology. This system replaces traditional student ID cards with smart badges that automatically record entry and exit events across various campus facilities such as libraries, laboratories, lecture halls, and dormitories.

Each scan logs the student’s identity, time, and location into a centralized database, enabling real-time monitoring via a secure web dashboard. Additionally, if a lost or unauthorized card is used, the system triggers an instant security alert, preventing misuse and ensuring campus safety.

3. Objectives

* Enhance access control and student identity verification.
* Provide real-time security alerts for unauthorized card usage.
* Automate attendance tracking and campus entry logging.
* Create a centralized digital record of movements for audit and analysis.
* Support the university’s move towards a smart, secure, and technology-driven campus.

4. System Components

Hardware

* RFID/NFC Reader (RC522 Module)
* Arduino Mega or Raspberry Pi
* LCD Display
* Buzzer and LED Indicators

Software

* Backend: PHP or Python
* Database: MySQL
* Frontend: HTML, CSS, JavaScript
* Hosting: Local server or university intranet

5. System Functionality

1. Students scan their RFID/NFC ID cards at entry points.
2. The reader communicates with the microcontroller (Arduino/Raspberry Pi).
3. Data is sent securely to the backend server.
4. The server records, validates, and displays the information on a web dashboard.
5. If an invalid or reported-lost card is detected, the system alerts security through a buzzer, LED, and dashboard notification.

6. Expected Benefits to the Campus

* Improved Campus Security: Prevents unauthorized access to sensitive areas.
* Operational Efficiency: Reduces manual entry logs and human errors.
* Transparency: Provides real-time data for the administration.
* Automation: Attendance and movement tracking become seamless.
* Cyber Awareness: Promotes smart security integration within the university ecosystem.

7. Technologies and Tools

| Category              | Tools/Technologies                                |
| --------------------- | ------------------------------------------------- |
| Programming Languages | PHP, Python, C++ (for hardware integration)       |
| Database              | MySQL                                             |
| Hardware              | Arduino Mega, Raspberry Pi, RC522 RFID/NFC Module |
| Interface             | HTML, CSS, JavaScript                             |
| Security Features     | Encryption of card data, secure database access   |
| Hosting               | XAMPP / Local Server / University Intranet        |

8. Project Architecture

The system architecture integrates hardware-level authentication with a web-based monitoring dashboard.

*  Input Layer: RFID Reader and Card Interaction
*  Processing Layer: Arduino or Raspberry Pi handling communication and data validation
*  Application Layer: Backend processing using PHP/Python with MySQL
* Presentation Layer: Dashboard accessible by security and admin personnel

9. Ethical and Legal Considerations

* Ensure data privacy by encrypting student information.
* Restrict system access to authorized personnel only.
* Comply with University Data Protection and ICT Policies.
* Avoid misuse of personal movement data for non-security purposes.

10. Limitations

* Requires initial infrastructure cost (RFID readers, cards, and hardware).
* Dependence on stable network connectivity.
* Limited outdoor functionality if not weather-protected.

11. Risk Analysis

| Risk             | Impact | Mitigation Strategy                   |
| ---------------- | ------ | ------------------------------------- |
| Hardware failure | Medium | Regular maintenance and backup units  |
| Data breaches    | High   | Implement encryption and secure login |
| Power outages    | Medium | Backup power or battery modules       |
| System misuse    | High   | Strict access controls and logging    |

12. Project Schedule

| Phase   | Task                           | Duration | Output                                                         |
| ------- | ------------------------------ | -------- | -------------------------------------------------------------- |
| Phase 1 | Research & System Planning     | 1 hour   | Finalized system design and task distribution                  |
| Phase 2 | Hardware Setup & Configuration | 2 hours  | RFID/NFC reader connected and tested with Arduino/Raspberry Pi |
| Phase 3 | Software Development           | 3 hours  | Working backend (PHP/Python) and MySQL connection              |
| Phase 4 | Integration & Testing          | 2 hours  | Complete integration of hardware and web dashboard             |
| Phase 5 | Presentation & Evaluation      | 1 hour   | Functional system demonstration and project report             |


13. Team Structure

| Member Name | Role               | Responsibility                                       |
| ----------- | ------------------ | ---------------------------------------------------- |
| [Name 1]    | Team Leader        | Coordination, documentation, and final presentation  |
| [Name 2]    | Hardware Engineer  | RFID setup, Arduino/Raspberry Pi integration         |
| [Name 3]    | Backend Developer  | PHP/Python and database connection                   |
| [Name 4]    | Frontend Developer | Web dashboard design (HTML, CSS, JS)                 |
| [Name 5]    | Security Analyst   | Data encryption, system testing, and risk assessment |

14. Performance Metrics

* System response time during scans.
* Accuracy of access logs and attendance.
* Reliability of alert notifications.
* Data security compliance.

15. References

1. St. Lawrence University IT Policies (2025). Network and Cybersecurity Guidelines for Campus Deployment.*
2. Arduino Documentation (2024). RFID/NFC Reader Integration Guide.
3. MySQL Developers Network (2024). Database Security Best Practices.
4. Raspberry Pi Foundation (2024). IoT-Based Access Control Systems.
