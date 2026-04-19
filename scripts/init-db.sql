-- 足安智能防走失系统
-- 数据库初始化SQL脚本

-- 创建数据库
CREATE DATABASE IF NOT EXISTS shoe_insole
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE shoe_insole;

-- 创建设备表
CREATE TABLE IF NOT EXISTS devices (
    id INT PRIMARY KEY AUTO_INCREMENT,
    imei VARCHAR(16) UNIQUE NOT NULL,
    iccid VARCHAR(24),
    firmware_version VARCHAR(16),
    hardware_version VARCHAR(16),
    fingerprint VARCHAR(64),
    last_location_lat VARCHAR(32),
    last_location_lng VARCHAR(32),
    last_location_time DATETIME,
    battery INT DEFAULT 100,
    signal_strength INT DEFAULT 0,
    mode VARCHAR(16) DEFAULT 'normal',
    status VARCHAR(16) DEFAULT 'offline',
    session_id VARCHAR(40),
    locked BOOLEAN DEFAULT FALSE,
    lock_until DATETIME,
    auth_failures INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_seen DATETIME,
    INDEX idx_imei (imei),
    INDEX idx_status (status),
    INDEX idx_last_seen (last_seen)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建报警表
CREATE TABLE IF NOT EXISTS alarms (
    id INT PRIMARY KEY AUTO_INCREMENT,
    alarm_id VARCHAR(40) UNIQUE NOT NULL,
    device_id VARCHAR(16) NOT NULL,
    alarm_type INT NOT NULL,
    alarm_level INT NOT NULL,
    latitude VARCHAR(32),
    longitude VARCHAR(32),
    accuracy VARCHAR(16),
    battery INT,
    status VARCHAR(16) DEFAULT 'pending',
    push_count INT DEFAULT 0,
    push_time DATETIME,
    acknowledge_time DATETIME,
    alarm_data TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_device_id (device_id),
    INDEX idx_alarm_id (alarm_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建设备错误表
CREATE TABLE IF NOT EXISTS device_errors (
    id INT PRIMARY KEY AUTO_INCREMENT,
    device_id VARCHAR(16) NOT NULL,
    error_id VARCHAR(40) UNIQUE NOT NULL,
    error_type VARCHAR(32) NOT NULL,
    error_level INT NOT NULL,
    error_code INT NOT NULL,
    error_message VARCHAR(256),
    extra_data TEXT,
    status VARCHAR(16) DEFAULT 'pending',
    resolved_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_device_id (device_id),
    INDEX idx_error_id (error_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建OTA任务表
CREATE TABLE IF NOT EXISTS ota_tasks (
    id INT PRIMARY KEY AUTO_INCREMENT,
    upgrade_id VARCHAR(40) UNIQUE NOT NULL,
    device_id VARCHAR(16) NOT NULL,
    version VARCHAR(16) NOT NULL,
    url VARCHAR(512) NOT NULL,
    size INT NOT NULL,
    checksum VARCHAR(64) NOT NULL,
    status VARCHAR(16) DEFAULT 'pending',
    progress INT DEFAULT 0,
    error_code INT DEFAULT 0,
    error_message VARCHAR(256),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    started_at DATETIME,
    completed_at DATETIME,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_upgrade_id (upgrade_id),
    INDEX idx_device_id (device_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建命令表
CREATE TABLE IF NOT EXISTS commands (
    id INT PRIMARY KEY AUTO_INCREMENT,
    command_id VARCHAR(40) UNIQUE NOT NULL,
    device_id VARCHAR(16) NOT NULL,
    command_type VARCHAR(32) NOT NULL,
    command_data JSON,
    protocol VARCHAR(8) DEFAULT 'tcp',
    status VARCHAR(16) DEFAULT 'pending',
    result VARCHAR(16),
    result_data JSON,
    retry_count INT DEFAULT 0,
    max_retries INT DEFAULT 3,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    sent_at DATETIME,
    acknowledged_at DATETIME,
    timeout_at DATETIME,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_command_id (command_id),
    INDEX idx_device_id (device_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建安全审计表
CREATE TABLE IF NOT EXISTS security_audits (
    id INT PRIMARY KEY AUTO_INCREMENT,
    event_id VARCHAR(40) UNIQUE NOT NULL,
    device_id VARCHAR(16),
    session_id VARCHAR(40),
    event_type VARCHAR(32) NOT NULL,
    event_data JSON,
    ip_address VARCHAR(45),
    user_agent VARCHAR(256),
    result VARCHAR(16),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_event_id (event_id),
    INDEX idx_device_id (device_id),
    INDEX idx_event_type (event_type),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 插入测试设备
INSERT INTO devices (imei, iccid, firmware_version, hardware_version, fingerprint, status)
VALUES
    ('860000000000001', '89860000000000000001', '1.0.0', '1.0', 'test_fingerprint_1', 'offline'),
    ('860000000000002', '89860000000000000002', '1.0.0', '1.0', 'test_fingerprint_2', 'offline'),
    ('860000000000003', '89860000000000000003', '1.0.0', '1.0', 'test_fingerprint_3', 'offline')
ON DUPLICATE KEY UPDATE updated_at = CURRENT_TIMESTAMP;
