-- ============================================
-- Rakt-Sathi Database Schema
-- Database Name: rakth_sathi
-- ============================================

-- Create Database
CREATE DATABASE IF NOT EXISTS rakth_sathi;
USE rakth_sathi;

-- ============================================
-- Table 1: Donors
-- ============================================
CREATE TABLE IF NOT EXISTS Donors (
    donor_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    contact_number VARCHAR(20) NOT NULL,
    age INT,
    gender VARCHAR(20),
    blood_group VARCHAR(5) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    availability VARCHAR(50) DEFAULT 'Yes',
    months_since_first_donation INT DEFAULT 0,
    number_of_donation INT DEFAULT 0,
    pints_donated INT DEFAULT 0,
    last_donation_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_blood_group (blood_group),
    INDEX idx_city (city),
    INDEX idx_availability (availability)
);

-- ============================================
-- Table 2: Requests
-- ============================================
CREATE TABLE IF NOT EXISTS Requests (
    request_id INT AUTO_INCREMENT PRIMARY KEY,
    blood_group_needed VARCHAR(5) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100),
    urgency VARCHAR(50),
    status VARCHAR(50) DEFAULT 'Open',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_blood_group (blood_group_needed),
    INDEX idx_city (city),
    INDEX idx_status (status)
);

-- ============================================
-- Table 3: Matches
-- ============================================
CREATE TABLE IF NOT EXISTS Matches (
    match_id INT AUTO_INCREMENT PRIMARY KEY,
    request_id INT NOT NULL,
    donor_id INT NOT NULL,
    blood_match INT DEFAULT 0,
    distance_km FLOAT,
    compatibility_score FLOAT,
    status VARCHAR(50) DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (request_id) REFERENCES Requests(request_id) ON DELETE CASCADE,
    FOREIGN KEY (donor_id) REFERENCES Donors(donor_id) ON DELETE CASCADE,
    INDEX idx_request_id (request_id),
    INDEX idx_donor_id (donor_id),
    INDEX idx_status (status)
);

-- ============================================
-- Table 4: Notifications
-- ============================================
CREATE TABLE IF NOT EXISTS Notifications (
    notification_id INT AUTO_INCREMENT PRIMARY KEY,
    donor_id INT,
    donor_email VARCHAR(100),
    patient_name VARCHAR(100),
    patient_phone VARCHAR(20),
    hospital_name VARCHAR(150),
    blood_group VARCHAR(5),
    units_required INT DEFAULT 1,
    city VARCHAR(100),
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (donor_id) REFERENCES Donors(donor_id) ON DELETE SET NULL,
    INDEX idx_donor_email (donor_email),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);

-- ============================================
-- Table 5: Users (for authentication)
-- ============================================
CREATE TABLE IF NOT EXISTS Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255),
    role VARCHAR(50) DEFAULT 'donor',
    is_active TINYINT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_role (role)
);

-- ============================================
-- Table 6: DonationHistory
-- ============================================
CREATE TABLE IF NOT EXISTS DonationHistory (
    donation_id INT AUTO_INCREMENT PRIMARY KEY,
    donor_id INT NOT NULL,
    donation_date DATE NOT NULL,
    blood_type_collected VARCHAR(5),
    units_collected INT,
    hospital_name VARCHAR(150),
    city VARCHAR(100),
    status VARCHAR(50) DEFAULT 'Completed',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (donor_id) REFERENCES Donors(donor_id) ON DELETE CASCADE,
    INDEX idx_donor_id (donor_id),
    INDEX idx_donation_date (donation_date)
);

-- ============================================
-- Table 7: BloodInventory
-- ============================================
CREATE TABLE IF NOT EXISTS BloodInventory (
    inventory_id INT AUTO_INCREMENT PRIMARY KEY,
    blood_group VARCHAR(5) NOT NULL,
    city VARCHAR(100) NOT NULL,
    units_available INT DEFAULT 0,
    units_needed INT DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_blood_group (blood_group),
    INDEX idx_city (city),
    UNIQUE KEY unique_blood_city (blood_group, city)
);

-- ============================================
-- Table 8: ChatbotLogs
-- ============================================
CREATE TABLE IF NOT EXISTS ChatbotLogs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    user_email VARCHAR(100),
    user_message TEXT,
    bot_reply TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_email (user_email),
    INDEX idx_created_at (created_at)
);

-- ============================================
-- Sample Data for Testing
-- ============================================

-- Insert sample donors
INSERT INTO Donors (name, email, contact_number, age, gender, blood_group, city, state, latitude, longitude, availability, pints_donated, created_at)
VALUES 
('Rajesh Kumar', 'rajesh.kumar@email.com', '9876543210', 28, 'Male', 'O+', 'Vijayawada', 'Andhra Pradesh', 16.5062, 80.6480, 'Yes', 2, NOW()),
('Priya Singh', 'priya.singh@email.com', '9876543211', 25, 'Female', 'A+', 'Hyderabad', 'Telangana', 17.3850, 78.4867, 'Yes', 1, NOW()),
('Arun Patel', 'arun.patel@email.com', '9876543212', 35, 'Male', 'B+', 'Visakhapatnam', 'Andhra Pradesh', 17.6868, 83.2185, 'Yes', 3, NOW()),
('Deepa Nair', 'deepa.nair@email.com', '9876543213', 30, 'Female', 'O-', 'Guntur', 'Andhra Pradesh', 16.3067, 80.4365, 'Yes', 4, NOW()),
('Vikram Sharma', 'vikram.sharma@email.com', '9876543214', 32, 'Male', 'AB+', 'Warangal', 'Telangana', 17.9689, 79.5941, 'Yes', 2, NOW());

-- Insert sample blood requests
INSERT INTO Requests (blood_group_needed, city, state, urgency, status, created_at)
VALUES 
('O+', 'Vijayawada', 'Andhra Pradesh', 'High', 'Open', NOW()),
('A+', 'Hyderabad', 'Telangana', 'Critical', 'Open', NOW()),
('B+', 'Visakhapatnam', 'Andhra Pradesh', 'Medium', 'Closed', NOW()),
('O-', 'Guntur', 'Andhra Pradesh', 'Critical', 'Open', NOW());

-- Insert sample matches
INSERT INTO Matches (request_id, donor_id, blood_match, distance_km, compatibility_score, status)
VALUES 
(1, 1, 1, 5.2, 0.95, 'Accepted'),
(2, 2, 1, 12.5, 0.85, 'Pending'),
(3, 3, 1, 8.3, 0.90, 'Accepted'),
(4, 4, 1, 3.1, 0.98, 'Pending');

-- Insert sample users for authentication
INSERT INTO Users (email, password_hash, role, is_active)
VALUES 
('raktasathi@gmail.com', 'Raktsathi@2025', 'admin', 1),
('rajesh.kumar@email.com', 'password123', 'donor', 1),
('priya.singh@email.com', 'password123', 'donor', 1);

-- Insert sample blood inventory
INSERT INTO BloodInventory (blood_group, city, units_available, units_needed)
VALUES 
('O+', 'Vijayawada', 10, 5),
('A+', 'Hyderabad', 8, 3),
('B+', 'Visakhapatnam', 6, 4),
('O-', 'Guntur', 3, 7),
('AB+', 'Warangal', 2, 2);

-- ============================================
-- Views for easier querying
-- ============================================

-- View: Available Donors by Blood Group
CREATE OR REPLACE VIEW AvailableDonorsByBlood AS
SELECT 
    blood_group,
    city,
    COUNT(*) as donor_count,
    GROUP_CONCAT(CONCAT(name, ' (', contact_number, ')')) as donor_list
FROM Donors
WHERE availability = 'Yes'
GROUP BY blood_group, city;

-- View: Urgent Requests Summary
CREATE OR REPLACE VIEW UrgentRequests AS
SELECT 
    request_id,
    blood_group_needed,
    city,
    urgency,
    status,
    created_at,
    DATEDIFF(NOW(), created_at) as days_pending
FROM Requests
WHERE status = 'Open' AND urgency IN ('High', 'Critical')
ORDER BY urgency DESC, created_at ASC;

-- View: Donor Activity
CREATE OR REPLACE VIEW DonorActivity AS
SELECT 
    d.donor_id,
    d.name,
    d.email,
    d.blood_group,
    d.city,
    COUNT(dh.donation_id) as total_donations,
    MAX(dh.donation_date) as last_donation,
    SUM(dh.units_collected) as total_units_donated
FROM Donors d
LEFT JOIN DonationHistory dh ON d.donor_id = dh.donor_id
GROUP BY d.donor_id;

-- ============================================
-- Stored Procedures
-- ============================================

-- Procedure: Find Compatible Donors
DELIMITER $$

CREATE PROCEDURE IF NOT EXISTS FindCompatibleDonors(
    IN p_blood_group VARCHAR(5),
    IN p_city VARCHAR(100),
    IN p_radius_km FLOAT
)
BEGIN
    SELECT 
        d.donor_id,
        d.name,
        d.email,
        d.contact_number,
        d.blood_group,
        d.city,
        d.latitude,
        d.longitude,
        d.availability,
        d.pints_donated,
        CASE 
            WHEN d.blood_group = p_blood_group THEN 1
            ELSE 0
        END as blood_match
    FROM Donors d
    WHERE d.availability = 'Yes'
    AND d.blood_group IN (
        SELECT compatible_group 
        FROM (
            SELECT 'O-' as compatible_group
            UNION ALL SELECT 'O+'
            UNION ALL SELECT 'A-'
            UNION ALL SELECT 'A+'
            UNION ALL SELECT 'B-'
            UNION ALL SELECT 'B+'
            UNION ALL SELECT 'AB-'
            UNION ALL SELECT 'AB+'
        ) as groups
    )
    ORDER BY blood_match DESC, d.pints_donated DESC;
END $$

DELIMITER ;

-- Procedure: Record Donation
DELIMITER $$

CREATE PROCEDURE IF NOT EXISTS RecordDonation(
    IN p_donor_id INT,
    IN p_donation_date DATE,
    IN p_blood_type VARCHAR(5),
    IN p_units_collected INT,
    IN p_hospital VARCHAR(150),
    IN p_city VARCHAR(100)
)
BEGIN
    INSERT INTO DonationHistory (donor_id, donation_date, blood_type_collected, units_collected, hospital_name, city)
    VALUES (p_donor_id, p_donation_date, p_blood_type, p_units_collected, p_hospital, p_city);
    
    UPDATE Donors 
    SET number_of_donation = number_of_donation + 1,
        pints_donated = pints_donated + p_units_collected,
        last_donation_date = p_donation_date
    WHERE donor_id = p_donor_id;
END $$

DELIMITER ;

-- ============================================
-- Indexes for Performance
-- ============================================

-- Additional indexes for better query performance
CREATE INDEX idx_donors_blood_availability ON Donors(blood_group, availability);
CREATE INDEX idx_donors_city_blood ON Donors(city, blood_group);
CREATE INDEX idx_requests_urgency_status ON Requests(urgency, status);
CREATE INDEX idx_matches_status_donor ON Matches(status, donor_id);
CREATE INDEX idx_notifications_donor_status ON Notifications(donor_email, status);
CREATE INDEX idx_donation_history_date ON DonationHistory(donation_date);
CREATE INDEX idx_blood_inventory_city ON BloodInventory(city, blood_group);

-- ============================================
-- Database Summary
-- ============================================
-- Tables: 8
-- Views: 3
-- Stored Procedures: 2
-- Sample Records: 15+
-- 
-- Key Features:
-- - Donor registration and management
-- - Blood request creation and matching
-- - Emergency notification system
-- - Donation history tracking
-- - Blood inventory management
-- - User authentication
-- - Chatbot interaction logs
-- ============================================
