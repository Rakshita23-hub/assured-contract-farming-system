CREATE DATABASE assured_farming;

USE assured_farming;

-- Users table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('farmer', 'buyer', 'admin') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Farmer details
CREATE TABLE farmers (
    farmer_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    location VARCHAR(150),
    crop VARCHAR(100),
    quantity DECIMAL(10,2),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Buyer details
CREATE TABLE buyers (
    buyer_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    company_name VARCHAR(150),
    location VARCHAR(150),
    required_crop VARCHAR(100),
    required_quantity DECIMAL(10,2),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Contracts
CREATE TABLE contracts (
    contract_id INT AUTO_INCREMENT PRIMARY KEY,
    buyer_id INT NOT NULL,
    crop VARCHAR(100) NOT NULL,
    variety VARCHAR(100),
    quantity DECIMAL(10,2),
    offered_price DECIMAL(10,2),
    quality_requirement VARCHAR(255),
    delivery_location VARCHAR(150),
    delivery_date DATE,
    status ENUM('open', 'accepted', 'completed', 'cancelled')
        DEFAULT 'open',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (buyer_id) REFERENCES buyers(buyer_id)
);

-- Farmer applications for contracts
CREATE TABLE contract_applications (
    application_id INT AUTO_INCREMENT PRIMARY KEY,
    contract_id INT NOT NULL,
    farmer_id INT NOT NULL,
    status ENUM('pending', 'accepted', 'rejected')
        DEFAULT 'pending',
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (contract_id) REFERENCES contracts(contract_id),
    FOREIGN KEY (farmer_id) REFERENCES farmers(farmer_id)
);

-- Price predictions
CREATE TABLE price_predictions (
    prediction_id INT AUTO_INCREMENT PRIMARY KEY,
    farmer_id INT,
    commodity VARCHAR(100),
    market VARCHAR(100),
    predicted_price DECIMAL(12,2),
    prediction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (farmer_id) REFERENCES farmers(farmer_id)
);