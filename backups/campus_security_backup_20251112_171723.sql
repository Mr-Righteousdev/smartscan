/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19-11.8.3-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: smart_campus_security
-- ------------------------------------------------------
-- Server version	11.8.3-MariaDB-1+b1 from Debian

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*M!100616 SET @OLD_NOTE_VERBOSITY=@@NOTE_VERBOSITY, NOTE_VERBOSITY=0 */;

--
-- Table structure for table `access_logs`
--

DROP TABLE IF EXISTS `access_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `access_logs` (
  `log_id` int(11) NOT NULL AUTO_INCREMENT,
  `student_id` varchar(20) DEFAULT NULL,
  `card_id` varchar(50) DEFAULT NULL,
  `location_id` int(11) DEFAULT NULL,
  `access_type` enum('entry','exit') NOT NULL,
  `access_time` timestamp NULL DEFAULT current_timestamp(),
  `access_granted` tinyint(1) DEFAULT 1,
  `denial_reason` varchar(200) DEFAULT NULL,
  `ip_address` varchar(45) DEFAULT NULL,
  `user_agent` text DEFAULT NULL,
  `risk_score` int(11) DEFAULT 0,
  `requires_review` tinyint(1) DEFAULT 0,
  `reviewed_by` int(11) DEFAULT NULL,
  `reviewed_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`log_id`),
  KEY `idx_student_time` (`student_id`,`access_time`),
  KEY `idx_location_time` (`location_id`,`access_time`),
  KEY `idx_access_time` (`access_time`),
  KEY `idx_risk_score` (`risk_score`),
  KEY `idx_requires_review` (`requires_review`),
  KEY `reviewed_by` (`reviewed_by`),
  CONSTRAINT `access_logs_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `students` (`student_id`) ON DELETE SET NULL,
  CONSTRAINT `access_logs_ibfk_2` FOREIGN KEY (`location_id`) REFERENCES `campus_locations` (`location_id`) ON DELETE SET NULL,
  CONSTRAINT `access_logs_ibfk_3` FOREIGN KEY (`reviewed_by`) REFERENCES `system_users` (`user_id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `access_logs`
--

LOCK TABLES `access_logs` WRITE;
/*!40000 ALTER TABLE `access_logs` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `access_logs` VALUES
(1,'STU002','RFID_002_DEF456',1,'entry','2025-11-12 13:49:22',1,NULL,'127.0.0.1','Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0',0,0,NULL,NULL),
(2,'STU002','RFID_002_DEF456',1,'entry','2025-11-12 13:52:04',1,NULL,'127.0.0.1','Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0',0,0,NULL,NULL),
(3,'STU001','RFID_001_ABC123',1,'entry','2025-11-12 13:55:52',1,NULL,'127.0.0.1','Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0',0,0,NULL,NULL);
/*!40000 ALTER TABLE `access_logs` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `access_policies`
--

DROP TABLE IF EXISTS `access_policies`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `access_policies` (
  `policy_id` int(11) NOT NULL AUTO_INCREMENT,
  `policy_name` varchar(100) NOT NULL,
  `policy_type` enum('time_based','location_based','role_based','risk_based') NOT NULL,
  `location_id` int(11) DEFAULT NULL,
  `student_role` varchar(50) DEFAULT NULL,
  `time_start` time DEFAULT NULL,
  `time_end` time DEFAULT NULL,
  `days_of_week` set('monday','tuesday','wednesday','thursday','friday','saturday','sunday') DEFAULT NULL,
  `risk_threshold` enum('low','medium','high','critical') DEFAULT 'medium',
  `action` enum('allow','deny','require_additional_auth','alert_only') DEFAULT 'allow',
  `is_active` tinyint(1) DEFAULT 1,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `created_by` int(11) DEFAULT NULL,
  PRIMARY KEY (`policy_id`),
  KEY `created_by` (`created_by`),
  KEY `idx_policy_type` (`policy_type`),
  KEY `idx_location_id` (`location_id`),
  KEY `idx_is_active` (`is_active`),
  CONSTRAINT `access_policies_ibfk_1` FOREIGN KEY (`location_id`) REFERENCES `campus_locations` (`location_id`) ON DELETE CASCADE,
  CONSTRAINT `access_policies_ibfk_2` FOREIGN KEY (`created_by`) REFERENCES `system_users` (`user_id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `access_policies`
--

LOCK TABLES `access_policies` WRITE;
/*!40000 ALTER TABLE `access_policies` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `access_policies` VALUES
(1,'Night Access Restriction','time_based',NULL,NULL,'22:00:00','06:00:00','monday,tuesday,wednesday,thursday,friday,saturday,sunday','medium','require_additional_auth',1,'2025-11-12 13:33:20',NULL),
(2,'Weekend Laboratory Access','time_based',NULL,NULL,'08:00:00','18:00:00','saturday,sunday','medium','allow',1,'2025-11-12 13:33:20',NULL),
(3,'Cybersecurity Lab Access Control','location_based',5,NULL,NULL,NULL,NULL,'medium','require_additional_auth',1,'2025-11-12 13:33:20',NULL),
(4,'ICT Office Access Control','location_based',10,NULL,NULL,NULL,NULL,'medium','require_additional_auth',1,'2025-11-12 13:33:20',NULL);
/*!40000 ALTER TABLE `access_policies` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Temporary table structure for view `active_alerts_summary`
--

DROP TABLE IF EXISTS `active_alerts_summary`;
/*!50001 DROP VIEW IF EXISTS `active_alerts_summary`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8mb4;
/*!50001 CREATE VIEW `active_alerts_summary` AS SELECT
 1 AS `alert_id`,
  1 AS `alert_type`,
  1 AS `severity`,
  1 AS `alert_message`,
  1 AS `alert_time`,
  1 AS `location_name`,
  1 AS `student_name` */;
SET character_set_client = @saved_cs_client;

--
-- Temporary table structure for view `active_security_incidents`
--

DROP TABLE IF EXISTS `active_security_incidents`;
/*!50001 DROP VIEW IF EXISTS `active_security_incidents`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8mb4;
/*!50001 CREATE VIEW `active_security_incidents` AS SELECT
 1 AS `incident_id`,
  1 AS `incident_type`,
  1 AS `severity`,
  1 AS `status`,
  1 AS `title`,
  1 AS `description`,
  1 AS `affected_systems`,
  1 AS `affected_users`,
  1 AS `location_id`,
  1 AS `detected_by`,
  1 AS `assigned_to`,
  1 AS `detected_at`,
  1 AS `responded_at`,
  1 AS `resolved_at`,
  1 AS `resolution_notes`,
  1 AS `impact_assessment`,
  1 AS `lessons_learned`,
  1 AS `detected_by_name`,
  1 AS `assigned_to_name`,
  1 AS `location_name` */;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `campus_locations`
--

DROP TABLE IF EXISTS `campus_locations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `campus_locations` (
  `location_id` int(11) NOT NULL AUTO_INCREMENT,
  `location_name` varchar(100) NOT NULL,
  `location_type` enum('library','laboratory','dormitory','lecture_hall','cafeteria','admin','sports','other') NOT NULL,
  `building` varchar(50) DEFAULT NULL,
  `floor_level` varchar(10) DEFAULT NULL,
  `access_level` enum('public','restricted','staff_only') DEFAULT 'public',
  `is_active` tinyint(1) DEFAULT 1,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`location_id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `campus_locations`
--

LOCK TABLES `campus_locations` WRITE;
/*!40000 ALTER TABLE `campus_locations` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `campus_locations` VALUES
(1,'Main Library Entrance','library','Library Building','Ground','public',1,'2025-11-12 13:33:19'),
(2,'Library Study Rooms','library','Library Building','1st Floor','restricted',1,'2025-11-12 13:33:19'),
(3,'Computer Lab 1','laboratory','ICT Building','Ground','restricted',1,'2025-11-12 13:33:19'),
(4,'Computer Lab 2','laboratory','ICT Building','1st Floor','restricted',1,'2025-11-12 13:33:19'),
(5,'Cybersecurity Lab','laboratory','ICT Building','2nd Floor','restricted',1,'2025-11-12 13:33:19'),
(6,'Male Dormitory Block A','dormitory','Dormitory A','Ground','restricted',1,'2025-11-12 13:33:19'),
(7,'Female Dormitory Block B','dormitory','Dormitory B','Ground','restricted',1,'2025-11-12 13:33:19'),
(8,'Lecture Hall 1','lecture_hall','Academic Block','Ground','public',1,'2025-11-12 13:33:19'),
(9,'Lecture Hall 2','lecture_hall','Academic Block','1st Floor','public',1,'2025-11-12 13:33:19'),
(10,'ICT Department Office','admin','ICT Building','3rd Floor','staff_only',1,'2025-11-12 13:33:19'),
(11,'Main Cafeteria','cafeteria','Student Center','Ground','public',1,'2025-11-12 13:33:19'),
(12,'Sports Complex','sports','Sports Building','Ground','public',1,'2025-11-12 13:33:19');
/*!40000 ALTER TABLE `campus_locations` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `encryption_keys`
--

DROP TABLE IF EXISTS `encryption_keys`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `encryption_keys` (
  `key_id` int(11) NOT NULL AUTO_INCREMENT,
  `key_name` varchar(100) NOT NULL,
  `key_purpose` varchar(100) NOT NULL,
  `algorithm` varchar(50) NOT NULL,
  `key_strength` int(11) NOT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `expires_at` timestamp NULL DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT 1,
  `created_by` int(11) DEFAULT NULL,
  PRIMARY KEY (`key_id`),
  KEY `created_by` (`created_by`),
  KEY `idx_key_purpose` (`key_purpose`),
  KEY `idx_is_active` (`is_active`),
  KEY `idx_expires_at` (`expires_at`),
  CONSTRAINT `encryption_keys_ibfk_1` FOREIGN KEY (`created_by`) REFERENCES `system_users` (`user_id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `encryption_keys`
--

LOCK TABLES `encryption_keys` WRITE;
/*!40000 ALTER TABLE `encryption_keys` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `encryption_keys` VALUES
(1,'Database Encryption Key','data_at_rest','AES',256,'2025-11-12 13:33:20',NULL,1,1),
(2,'Session Token Key','session_management','HMAC-SHA256',256,'2025-11-12 13:33:20',NULL,1,1),
(3,'Card Data Encryption','card_information','AES',128,'2025-11-12 13:33:20',NULL,1,1);
/*!40000 ALTER TABLE `encryption_keys` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `lost_stolen_cards`
--

DROP TABLE IF EXISTS `lost_stolen_cards`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `lost_stolen_cards` (
  `report_id` int(11) NOT NULL AUTO_INCREMENT,
  `card_id` varchar(50) NOT NULL,
  `student_id` varchar(20) DEFAULT NULL,
  `report_type` enum('lost','stolen') NOT NULL,
  `report_date` timestamp NULL DEFAULT current_timestamp(),
  `reported_by` varchar(100) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `status` enum('active','resolved','cancelled') DEFAULT 'active',
  `resolved_date` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`report_id`),
  KEY `student_id` (`student_id`),
  KEY `idx_card_status` (`card_id`,`status`),
  CONSTRAINT `lost_stolen_cards_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `students` (`student_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lost_stolen_cards`
--

LOCK TABLES `lost_stolen_cards` WRITE;
/*!40000 ALTER TABLE `lost_stolen_cards` DISABLE KEYS */;
set autocommit=0;
/*!40000 ALTER TABLE `lost_stolen_cards` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Temporary table structure for view `recent_access_summary`
--

DROP TABLE IF EXISTS `recent_access_summary`;
/*!50001 DROP VIEW IF EXISTS `recent_access_summary`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8mb4;
/*!50001 CREATE VIEW `recent_access_summary` AS SELECT
 1 AS `log_id`,
  1 AS `full_name`,
  1 AS `student_id`,
  1 AS `location_name`,
  1 AS `building`,
  1 AS `access_type`,
  1 AS `access_time`,
  1 AS `access_granted`,
  1 AS `risk_score` */;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `risk_assessments`
--

DROP TABLE IF EXISTS `risk_assessments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `risk_assessments` (
  `assessment_id` int(11) NOT NULL AUTO_INCREMENT,
  `student_id` varchar(20) DEFAULT NULL,
  `location_id` int(11) DEFAULT NULL,
  `access_time` timestamp NOT NULL,
  `risk_score` int(11) NOT NULL,
  `risk_level` enum('low','medium','high','critical') NOT NULL,
  `risk_factors` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`risk_factors`)),
  `action_taken` enum('allowed','denied','escalated','monitored') NOT NULL,
  `assessment_time` timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`assessment_id`),
  KEY `idx_student_id` (`student_id`),
  KEY `idx_location_id` (`location_id`),
  KEY `idx_risk_level` (`risk_level`),
  KEY `idx_assessment_time` (`assessment_time`),
  CONSTRAINT `risk_assessments_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `students` (`student_id`) ON DELETE SET NULL,
  CONSTRAINT `risk_assessments_ibfk_2` FOREIGN KEY (`location_id`) REFERENCES `campus_locations` (`location_id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `risk_assessments`
--

LOCK TABLES `risk_assessments` WRITE;
/*!40000 ALTER TABLE `risk_assessments` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `risk_assessments` VALUES
(1,'STU002',1,'2025-11-12 13:49:22',0,'low','[]','allowed','2025-11-12 13:49:22'),
(2,'STU002',1,'2025-11-12 13:52:04',0,'low','[]','allowed','2025-11-12 13:52:04'),
(3,'STU001',1,'2025-11-12 13:55:52',0,'low','[]','allowed','2025-11-12 13:55:52');
/*!40000 ALTER TABLE `risk_assessments` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `security_alerts`
--

DROP TABLE IF EXISTS `security_alerts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `security_alerts` (
  `alert_id` int(11) NOT NULL AUTO_INCREMENT,
  `alert_type` enum('unauthorized_access','lost_card_used','multiple_failed_attempts','system_breach','high_risk_access','other') NOT NULL,
  `severity` enum('low','medium','high','critical') NOT NULL,
  `location_id` int(11) DEFAULT NULL,
  `student_id` varchar(20) DEFAULT NULL,
  `card_id` varchar(50) DEFAULT NULL,
  `alert_message` text NOT NULL,
  `alert_time` timestamp NULL DEFAULT current_timestamp(),
  `status` enum('new','acknowledged','investigating','resolved') DEFAULT 'new',
  `acknowledged_by` varchar(100) DEFAULT NULL,
  `acknowledged_time` timestamp NULL DEFAULT NULL,
  `resolved_by` varchar(100) DEFAULT NULL,
  `resolved_time` timestamp NULL DEFAULT NULL,
  `resolution_notes` text DEFAULT NULL,
  PRIMARY KEY (`alert_id`),
  KEY `location_id` (`location_id`),
  KEY `student_id` (`student_id`),
  KEY `idx_alert_time` (`alert_time`),
  KEY `idx_status` (`status`),
  KEY `idx_severity` (`severity`),
  CONSTRAINT `security_alerts_ibfk_1` FOREIGN KEY (`location_id`) REFERENCES `campus_locations` (`location_id`) ON DELETE SET NULL,
  CONSTRAINT `security_alerts_ibfk_2` FOREIGN KEY (`student_id`) REFERENCES `students` (`student_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `security_alerts`
--

LOCK TABLES `security_alerts` WRITE;
/*!40000 ALTER TABLE `security_alerts` DISABLE KEYS */;
set autocommit=0;
/*!40000 ALTER TABLE `security_alerts` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `security_audit_log`
--

DROP TABLE IF EXISTS `security_audit_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `security_audit_log` (
  `log_id` int(11) NOT NULL AUTO_INCREMENT,
  `event_type` varchar(50) NOT NULL,
  `event_details` text DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  `student_id` varchar(20) DEFAULT NULL,
  `ip_address` varchar(45) DEFAULT NULL,
  `user_agent` text DEFAULT NULL,
  `timestamp` timestamp NULL DEFAULT current_timestamp(),
  `risk_level` enum('low','medium','high','critical') DEFAULT 'low',
  PRIMARY KEY (`log_id`),
  KEY `student_id` (`student_id`),
  KEY `idx_event_type` (`event_type`),
  KEY `idx_timestamp` (`timestamp`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_risk_level` (`risk_level`),
  KEY `idx_security_audit_timestamp_type` (`timestamp`,`event_type`),
  CONSTRAINT `security_audit_log_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `system_users` (`user_id`) ON DELETE SET NULL,
  CONSTRAINT `security_audit_log_ibfk_2` FOREIGN KEY (`student_id`) REFERENCES `students` (`student_id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `security_audit_log`
--

LOCK TABLES `security_audit_log` WRITE;
/*!40000 ALTER TABLE `security_audit_log` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `security_audit_log` VALUES
(1,'login_success','ENCRYPTED:Hfre nqzva ybttrq va fhpprffshyyl',1,NULL,'127.0.0.1','Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0','2025-11-12 13:33:44','low'),
(2,'login_success','ENCRYPTED:Hfre nqzva ybttrq va fhpprffshyyl',1,NULL,'127.0.0.1','Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0','2025-11-12 13:33:57','low'),
(3,'access_attempt','ENCRYPTED:{\"npprff_ybt_vq\": 1, \"fghqrag_vq\": \"FGH002\", \"pneq_vq\": \"ESVQ_002_QRS456\", \"ybpngvba_vq\": 1, \"npprff_glcr\": \"ragel\", \"tenagrq\": gehr, \"evfx_yriry\": \"ybj\", \"qravny_ernfba\": ahyy}',NULL,NULL,'127.0.0.1','Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0','2025-11-12 13:49:22','low'),
(4,'access_attempt','ENCRYPTED:{\"npprff_ybt_vq\": 2, \"fghqrag_vq\": \"FGH002\", \"pneq_vq\": \"ESVQ_002_QRS456\", \"ybpngvba_vq\": 1, \"npprff_glcr\": \"ragel\", \"tenagrq\": gehr, \"evfx_yriry\": \"ybj\", \"qravny_ernfba\": ahyy}',NULL,NULL,'127.0.0.1','Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0','2025-11-12 13:52:04','low'),
(5,'access_attempt','ENCRYPTED:{\"npprff_ybt_vq\": 3, \"fghqrag_vq\": \"FGH001\", \"pneq_vq\": \"ESVQ_001_NOP123\", \"ybpngvba_vq\": 1, \"npprff_glcr\": \"ragel\", \"tenagrq\": gehr, \"evfx_yriry\": \"ybj\", \"qravny_ernfba\": ahyy}',NULL,NULL,'127.0.0.1','Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0','2025-11-12 13:55:52','low'),
(6,'login_success','ENCRYPTED:Hfre nqzva ybttrq va fhpprffshyyl',1,NULL,'127.0.0.1','Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0','2025-11-12 13:56:20','low'),
(7,'login_success','ENCRYPTED:Hfre frphevgl ybttrq va fhpprffshyyl',2,NULL,'127.0.0.1','Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0','2025-11-12 13:59:39','low'),
(8,'logout','ENCRYPTED:Hfre frphevgl ybttrq bhg',2,NULL,'127.0.0.1','Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0','2025-11-12 14:00:04','low'),
(9,'login_success','ENCRYPTED:Hfre nqzva ybttrq va fhpprffshyyl',1,NULL,'127.0.0.1','Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0','2025-11-12 14:00:07','low'),
(10,'login_success','ENCRYPTED:Hfre nqzva ybttrq va fhpprffshyyl',1,NULL,'127.0.0.1','Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0','2025-11-12 14:16:39','low'),
(11,'login_success','ENCRYPTED:Hfre nqzva ybttrq va fhpprffshyyl',1,NULL,'127.0.0.1','Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0','2025-11-12 14:16:49','low');
/*!40000 ALTER TABLE `security_audit_log` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Temporary table structure for view `security_dashboard_summary`
--

DROP TABLE IF EXISTS `security_dashboard_summary`;
/*!50001 DROP VIEW IF EXISTS `security_dashboard_summary`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8mb4;
/*!50001 CREATE VIEW `security_dashboard_summary` AS SELECT
 1 AS `report_date`,
  1 AS `total_events`,
  1 AS `critical_events`,
  1 AS `high_events`,
  1 AS `medium_events`,
  1 AS `low_events` */;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `security_incidents`
--

DROP TABLE IF EXISTS `security_incidents`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `security_incidents` (
  `incident_id` int(11) NOT NULL AUTO_INCREMENT,
  `incident_type` enum('unauthorized_access','data_breach','system_intrusion','policy_violation','suspicious_activity') NOT NULL,
  `severity` enum('low','medium','high','critical') NOT NULL,
  `status` enum('new','investigating','contained','resolved','closed') DEFAULT 'new',
  `title` varchar(200) NOT NULL,
  `description` text DEFAULT NULL,
  `affected_systems` text DEFAULT NULL,
  `affected_users` text DEFAULT NULL,
  `location_id` int(11) DEFAULT NULL,
  `detected_by` int(11) DEFAULT NULL,
  `assigned_to` int(11) DEFAULT NULL,
  `detected_at` timestamp NULL DEFAULT current_timestamp(),
  `responded_at` timestamp NULL DEFAULT NULL,
  `resolved_at` timestamp NULL DEFAULT NULL,
  `resolution_notes` text DEFAULT NULL,
  `impact_assessment` text DEFAULT NULL,
  `lessons_learned` text DEFAULT NULL,
  PRIMARY KEY (`incident_id`),
  KEY `location_id` (`location_id`),
  KEY `detected_by` (`detected_by`),
  KEY `assigned_to` (`assigned_to`),
  KEY `idx_incident_type` (`incident_type`),
  KEY `idx_severity` (`severity`),
  KEY `idx_status` (`status`),
  KEY `idx_detected_at` (`detected_at`),
  CONSTRAINT `security_incidents_ibfk_1` FOREIGN KEY (`location_id`) REFERENCES `campus_locations` (`location_id`) ON DELETE SET NULL,
  CONSTRAINT `security_incidents_ibfk_2` FOREIGN KEY (`detected_by`) REFERENCES `system_users` (`user_id`) ON DELETE SET NULL,
  CONSTRAINT `security_incidents_ibfk_3` FOREIGN KEY (`assigned_to`) REFERENCES `system_users` (`user_id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `security_incidents`
--

LOCK TABLES `security_incidents` WRITE;
/*!40000 ALTER TABLE `security_incidents` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `security_incidents` VALUES
(1,'unauthorized_access','medium','new','Unknown Card Access Attempt','Multiple attempts to access secure locations using unregistered card ID',NULL,NULL,NULL,2,NULL,'2025-11-12 13:33:20',NULL,NULL,NULL,NULL,NULL),
(2,'suspicious_activity','high','new','Off-Hours Access Pattern','Student accessing multiple secure locations during restricted hours',NULL,NULL,NULL,2,NULL,'2025-11-12 13:33:20',NULL,NULL,NULL,NULL,NULL),
(3,'policy_violation','low','new','Tailgating Detected','Multiple card scans at same location within seconds',NULL,NULL,NULL,2,NULL,'2025-11-12 13:33:20',NULL,NULL,NULL,NULL,NULL);
/*!40000 ALTER TABLE `security_incidents` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `students`
--

DROP TABLE IF EXISTS `students`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `students` (
  `student_id` varchar(20) NOT NULL,
  `card_id` varchar(50) NOT NULL,
  `full_name` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `program` varchar(100) DEFAULT NULL,
  `year_of_study` int(11) DEFAULT NULL,
  `photo_url` varchar(255) DEFAULT NULL,
  `card_expiry_date` date DEFAULT NULL,
  `status` enum('active','suspended','graduated','inactive') DEFAULT 'active',
  `date_registered` timestamp NULL DEFAULT current_timestamp(),
  `last_updated` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`student_id`),
  UNIQUE KEY `card_id` (`card_id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `students`
--

LOCK TABLES `students` WRITE;
/*!40000 ALTER TABLE `students` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `students` VALUES
('STU001','RFID_001_ABC123','John Doe','john.doe@student.slau.ac.ug',NULL,'Computer Science',3,'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face','2026-12-31','active','2025-11-12 13:33:19','2025-11-12 13:33:19'),
('STU002','RFID_002_DEF456','Jane Smith','jane.smith@student.slau.ac.ug',NULL,'Cybersecurity',2,'https://images.unsplash.com/photo-1494790108755-2616b612b9e0?w=150&h=150&fit=crop&crop=face','2027-12-31','active','2025-11-12 13:33:19','2025-11-12 13:33:19'),
('STU003','RFID_003_GHI789','David Wilson','david.wilson@student.slau.ac.ug',NULL,'Information Technology',1,'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face','2028-12-31','active','2025-11-12 13:33:19','2025-11-12 13:33:19'),
('STU004','RFID_004_JKL012','Sarah Johnson','sarah.johnson@student.slau.ac.ug',NULL,'Computer Engineering',4,'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&h=150&fit=crop&crop=face','2025-12-31','active','2025-11-12 13:33:19','2025-11-12 13:33:19'),
('STU005','RFID_005_MNO345','Michael Brown','michael.brown@student.slau.ac.ug',NULL,'Data Science',2,'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&h=150&fit=crop&crop=face','2027-12-31','active','2025-11-12 13:33:19','2025-11-12 13:33:19');
/*!40000 ALTER TABLE `students` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `system_settings`
--

DROP TABLE IF EXISTS `system_settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `system_settings` (
  `setting_id` int(11) NOT NULL AUTO_INCREMENT,
  `setting_key` varchar(100) NOT NULL,
  `setting_value` text DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  `last_modified` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `modified_by` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`setting_id`),
  UNIQUE KEY `setting_key` (`setting_key`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `system_settings`
--

LOCK TABLES `system_settings` WRITE;
/*!40000 ALTER TABLE `system_settings` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `system_settings` VALUES
(1,'max_failed_attempts','3','Maximum failed access attempts before triggering alert','2025-11-12 13:33:20',NULL),
(2,'alert_notification_email','security@slau.ac.ug','Email for security alerts','2025-11-12 13:33:20',NULL),
(3,'session_timeout_minutes','30','Dashboard session timeout in minutes','2025-11-12 13:33:20',NULL),
(4,'enable_real_time_alerts','true','Enable real-time alert notifications','2025-11-12 13:33:20',NULL),
(5,'card_expiry_warning_days','30','Days before card expiry to show warning','2025-11-12 13:33:20',NULL);
/*!40000 ALTER TABLE `system_settings` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `system_users`
--

DROP TABLE IF EXISTS `system_users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `system_users` (
  `user_id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `full_name` varchar(100) NOT NULL,
  `role` enum('admin','security_officer','staff','student') DEFAULT 'student',
  `status` enum('active','inactive','locked','suspended') DEFAULT 'active',
  `last_login` timestamp NULL DEFAULT NULL,
  `failed_login_attempts` int(11) DEFAULT 0,
  `account_locked_until` timestamp NULL DEFAULT NULL,
  `two_factor_enabled` tinyint(1) DEFAULT 0,
  `two_factor_secret` varchar(32) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `created_by` int(11) DEFAULT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`),
  KEY `created_by` (`created_by`),
  KEY `idx_username` (`username`),
  KEY `idx_email` (`email`),
  KEY `idx_role` (`role`),
  KEY `idx_status` (`status`),
  CONSTRAINT `system_users_ibfk_1` FOREIGN KEY (`created_by`) REFERENCES `system_users` (`user_id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `system_users`
--

LOCK TABLES `system_users` WRITE;
/*!40000 ALTER TABLE `system_users` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `system_users` VALUES
(1,'admin','admin@slau.ac.ug','admin_salt_123:8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918','System Administrator','admin','active','2025-11-12 14:16:49',0,NULL,0,NULL,'2025-11-12 13:33:19','2025-11-12 14:16:49',NULL),
(2,'security','security@slau.ac.ug','security_salt_456:ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f','Security Officer','security_officer','active','2025-11-12 13:59:39',0,NULL,0,NULL,'2025-11-12 13:33:19','2025-11-12 13:59:39',NULL),
(3,'john_doe','john.doe@staff.slau.ac.ug','staff_salt_789:5906ac361a137e2d286465cd6588ebb5ac3f5ae955001100bc41577c3d751764','John Doe Staff','staff','active',NULL,0,NULL,0,NULL,'2025-11-12 13:33:19','2025-11-12 13:33:19',NULL);
/*!40000 ALTER TABLE `system_users` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `two_factor_codes`
--

DROP TABLE IF EXISTS `two_factor_codes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `two_factor_codes` (
  `code_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `code` varchar(10) NOT NULL,
  `purpose` enum('login','password_reset','account_unlock') NOT NULL,
  `expires_at` timestamp NOT NULL,
  `used_at` timestamp NULL DEFAULT NULL,
  `ip_address` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`code_id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_expires_at` (`expires_at`),
  KEY `idx_code_purpose` (`code`,`purpose`),
  CONSTRAINT `two_factor_codes_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `system_users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `two_factor_codes`
--

LOCK TABLES `two_factor_codes` WRITE;
/*!40000 ALTER TABLE `two_factor_codes` DISABLE KEYS */;
set autocommit=0;
/*!40000 ALTER TABLE `two_factor_codes` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Temporary table structure for view `user_activity_summary`
--

DROP TABLE IF EXISTS `user_activity_summary`;
/*!50001 DROP VIEW IF EXISTS `user_activity_summary`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8mb4;
/*!50001 CREATE VIEW `user_activity_summary` AS SELECT
 1 AS `user_id`,
  1 AS `username`,
  1 AS `full_name`,
  1 AS `role`,
  1 AS `last_login`,
  1 AS `active_sessions`,
  1 AS `last_activity` */;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `user_sessions`
--

DROP TABLE IF EXISTS `user_sessions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_sessions` (
  `session_id` varchar(255) NOT NULL,
  `user_id` int(11) NOT NULL,
  `token_hash` varchar(255) NOT NULL,
  `ip_address` varchar(45) DEFAULT NULL,
  `user_agent` text DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `last_activity` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `expires_at` timestamp NOT NULL,
  `is_active` tinyint(1) DEFAULT 1,
  PRIMARY KEY (`session_id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_expires_at` (`expires_at`),
  KEY `idx_is_active` (`is_active`),
  CONSTRAINT `user_sessions_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `system_users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_sessions`
--

LOCK TABLES `user_sessions` WRITE;
/*!40000 ALTER TABLE `user_sessions` DISABLE KEYS */;
set autocommit=0;
/*!40000 ALTER TABLE `user_sessions` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Dumping routines for database 'smart_campus_security'
--

--
-- Final view structure for view `active_alerts_summary`
--

/*!50001 DROP VIEW IF EXISTS `active_alerts_summary`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_unicode_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `active_alerts_summary` AS select `sa`.`alert_id` AS `alert_id`,`sa`.`alert_type` AS `alert_type`,`sa`.`severity` AS `severity`,`sa`.`alert_message` AS `alert_message`,`sa`.`alert_time` AS `alert_time`,`cl`.`location_name` AS `location_name`,`s`.`full_name` AS `student_name` from ((`security_alerts` `sa` left join `campus_locations` `cl` on(`sa`.`location_id` = `cl`.`location_id`)) left join `students` `s` on(`sa`.`student_id` = `s`.`student_id`)) where `sa`.`status` in ('new','acknowledged','investigating') order by `sa`.`alert_time` desc,`sa`.`severity` desc */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `active_security_incidents`
--

/*!50001 DROP VIEW IF EXISTS `active_security_incidents`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_unicode_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `active_security_incidents` AS select `si`.`incident_id` AS `incident_id`,`si`.`incident_type` AS `incident_type`,`si`.`severity` AS `severity`,`si`.`status` AS `status`,`si`.`title` AS `title`,`si`.`description` AS `description`,`si`.`affected_systems` AS `affected_systems`,`si`.`affected_users` AS `affected_users`,`si`.`location_id` AS `location_id`,`si`.`detected_by` AS `detected_by`,`si`.`assigned_to` AS `assigned_to`,`si`.`detected_at` AS `detected_at`,`si`.`responded_at` AS `responded_at`,`si`.`resolved_at` AS `resolved_at`,`si`.`resolution_notes` AS `resolution_notes`,`si`.`impact_assessment` AS `impact_assessment`,`si`.`lessons_learned` AS `lessons_learned`,`detector`.`full_name` AS `detected_by_name`,`assignee`.`full_name` AS `assigned_to_name`,`cl`.`location_name` AS `location_name` from (((`security_incidents` `si` left join `system_users` `detector` on(`si`.`detected_by` = `detector`.`user_id`)) left join `system_users` `assignee` on(`si`.`assigned_to` = `assignee`.`user_id`)) left join `campus_locations` `cl` on(`si`.`location_id` = `cl`.`location_id`)) where `si`.`status` in ('new','investigating','contained') order by `si`.`severity` desc,`si`.`detected_at` desc */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `recent_access_summary`
--

/*!50001 DROP VIEW IF EXISTS `recent_access_summary`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_unicode_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `recent_access_summary` AS select `al`.`log_id` AS `log_id`,`s`.`full_name` AS `full_name`,`s`.`student_id` AS `student_id`,`cl`.`location_name` AS `location_name`,`cl`.`building` AS `building`,`al`.`access_type` AS `access_type`,`al`.`access_time` AS `access_time`,`al`.`access_granted` AS `access_granted`,`al`.`risk_score` AS `risk_score` from ((`access_logs` `al` left join `students` `s` on(`al`.`student_id` = `s`.`student_id`)) left join `campus_locations` `cl` on(`al`.`location_id` = `cl`.`location_id`)) where `al`.`access_time` >= current_timestamp() - interval 24 hour order by `al`.`access_time` desc */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `security_dashboard_summary`
--

/*!50001 DROP VIEW IF EXISTS `security_dashboard_summary`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_unicode_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `security_dashboard_summary` AS select cast(`sa`.`timestamp` as date) AS `report_date`,count(0) AS `total_events`,sum(case when `sa`.`risk_level` = 'critical' then 1 else 0 end) AS `critical_events`,sum(case when `sa`.`risk_level` = 'high' then 1 else 0 end) AS `high_events`,sum(case when `sa`.`risk_level` = 'medium' then 1 else 0 end) AS `medium_events`,sum(case when `sa`.`risk_level` = 'low' then 1 else 0 end) AS `low_events` from `security_audit_log` `sa` where `sa`.`timestamp` >= current_timestamp() - interval 30 day group by cast(`sa`.`timestamp` as date) order by cast(`sa`.`timestamp` as date) desc */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `user_activity_summary`
--

/*!50001 DROP VIEW IF EXISTS `user_activity_summary`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_unicode_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `user_activity_summary` AS select `su`.`user_id` AS `user_id`,`su`.`username` AS `username`,`su`.`full_name` AS `full_name`,`su`.`role` AS `role`,`su`.`last_login` AS `last_login`,count(`us`.`session_id`) AS `active_sessions`,max(`us`.`last_activity`) AS `last_activity` from (`system_users` `su` left join `user_sessions` `us` on(`su`.`user_id` = `us`.`user_id` and `us`.`is_active` = 1)) where `su`.`status` = 'active' group by `su`.`user_id`,`su`.`username`,`su`.`full_name`,`su`.`role`,`su`.`last_login` order by max(`us`.`last_activity`) desc */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*M!100616 SET NOTE_VERBOSITY=@OLD_NOTE_VERBOSITY */;

-- Dump completed on 2025-11-12 17:17:24
