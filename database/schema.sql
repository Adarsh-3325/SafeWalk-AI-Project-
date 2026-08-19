-- SafeWalk AI Database Schema (MySQL Compatible)

CREATE DATABASE IF NOT EXISTS safewalk_db;
USE safewalk_db;

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Routes Table
CREATE TABLE IF NOT EXISTS routes (
    id VARCHAR(64) PRIMARY KEY,
    origin_address VARCHAR(255) NOT NULL,
    destination_address VARCHAR(255) NOT NULL,
    origin_lat DOUBLE NOT NULL,
    origin_lng DOUBLE NOT NULL,
    dest_lat DOUBLE NOT NULL,
    dest_lng DOUBLE NOT NULL,
    distance_km DOUBLE NOT NULL,
    duration_minutes DOUBLE NOT NULL,
    geometry_json LONGTEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Route Predictions Table
CREATE TABLE IF NOT EXISTS route_predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    route_id VARCHAR(64) NOT NULL,
    ml_safety_score DOUBLE NOT NULL,
    risk_level VARCHAR(20) NOT NULL,
    final_score DOUBLE NOT NULL,
    crime_risk DOUBLE NOT NULL,
    lighting_score DOUBLE NOT NULL,
    crowd_score DOUBLE NOT NULL,
    weather_risk DOUBLE NOT NULL,
    time_risk DOUBLE NOT NULL,
    report_risk DOUBLE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (route_id) REFERENCES routes(id) ON DELETE CASCADE
);

-- Crime Incidents Table
CREATE TABLE IF NOT EXISTS crime_incidents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    latitude DOUBLE NOT NULL,
    longitude DOUBLE NOT NULL,
    crime_type VARCHAR(50) NOT NULL,
    severity INT NOT NULL DEFAULT 1,
    description TEXT,
    incident_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_location (latitude, longitude)
);

-- Lighting Data Table
CREATE TABLE IF NOT EXISTS lighting_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    latitude DOUBLE NOT NULL,
    longitude DOUBLE NOT NULL,
    lighting_score DOUBLE NOT NULL, -- 0 (dark) to 100 (well-lit)
    light_type VARCHAR(50) DEFAULT 'street_lamp',
    is_functional BOOLEAN DEFAULT TRUE,
    INDEX idx_location (latitude, longitude)
);

-- Crowd Data Table
CREATE TABLE IF NOT EXISTS crowd_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    latitude DOUBLE NOT NULL,
    longitude DOUBLE NOT NULL,
    hour_of_day INT NOT NULL,
    density_score DOUBLE NOT NULL, -- 0 (isolated) to 100 (crowded)
    area_type VARCHAR(50) DEFAULT 'commercial',
    INDEX idx_location (latitude, longitude)
);

-- Weather Data Table
CREATE TABLE IF NOT EXISTS weather_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    temperature DOUBLE NOT NULL,
    condition_name VARCHAR(50) NOT NULL,
    visibility DOUBLE NOT NULL,
    precipitation DOUBLE NOT NULL
);

-- User Reports Table
CREATE TABLE IF NOT EXISTS user_reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category VARCHAR(50) NOT NULL,
    severity INT NOT NULL DEFAULT 1,
    description TEXT,
    latitude DOUBLE NOT NULL,
    longitude DOUBLE NOT NULL,
    user_id INT NULL,
    status VARCHAR(20) DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_location (latitude, longitude),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Search History Table
CREATE TABLE IF NOT EXISTS search_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NULL,
    origin VARCHAR(255) NOT NULL,
    destination VARCHAR(255) NOT NULL,
    selected_route_id VARCHAR(64) NULL,
    search_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Model Predictions Log Table
CREATE TABLE IF NOT EXISTS model_predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    route_id VARCHAR(64) NOT NULL,
    raw_features_json LONGTEXT NOT NULL,
    predicted_risk DOUBLE NOT NULL,
    top_risk_factors_json LONGTEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
