-- 创建数据库
CREATE DATABASE IF NOT EXISTS ai_detector CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE ai_detector;

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 分析记录表
CREATE TABLE IF NOT EXISTS analysis_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    original_text TEXT NOT NULL,
    ai_probability DECIMAL(5,4) NOT NULL,
    human_probability DECIMAL(5,4) NOT NULL,
    sentence_analysis JSON NOT NULL,
    analysis_time DECIMAL(8,3) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at)
);

-- 将 user_id 修改为允许 NULL
ALTER TABLE analysis_records MODIFY user_id INT NULL;