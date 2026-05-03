CREATE DATABASE task_management;
USE task_management;

-- =============================
-- 👤 USERS TABLE
-- =============================
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password VARCHAR(255),
    role ENUM('admin','manager','employee'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================
-- 📋 TASKS TABLE
-- =============================
CREATE TABLE tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255),
    description TEXT,
    assigned_to INT,
    assigned_by INT,
    status ENUM('pending','in_progress','completed') DEFAULT 'pending',
    progress INT DEFAULT 0,
    deadline DATE,
    FOREIGN KEY (assigned_to) REFERENCES users(id),
    FOREIGN KEY (assigned_by) REFERENCES users(id)
);

-- =============================
-- 💬 MESSAGES TABLE
-- =============================
CREATE TABLE messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sender_id INT,
    receiver_id INT,
    message TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_id) REFERENCES users(id),
    FOREIGN KEY (receiver_id) REFERENCES users(id)
);

-- =============================
-- 🔐 INSERT DEFAULT ADMIN
-- =============================
INSERT INTO users(name, email, password, role)
VALUES ('Admin', 'admin@gmail.com', '$2b$12$AHOGTaa/CCtKwF/Li2LVj.unE1eVSmnsKkkzH94pvSZdTPuW7sG8q', 'admin');
