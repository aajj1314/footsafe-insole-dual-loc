# -*- coding: utf-8 -*-
"""
配置加载与验证模块
"""

import os
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置类"""

    # ==================== 服务基础配置 ====================
    SERVICE_NAME: str = "足安智能防走失系统"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/terminal_service.log"
    MAX_WORKERS: int = 4

    # ==================== HTTP API配置 ====================
    HTTP_API_PORT: int = 8090

    # ==================== 通信端口配置 ====================
    UDP_PORT: int = 8888
    TCP_PORT: int = 8889
    TCP_MAX_CONNECTIONS: int = 100000
    TCP_CONNECTION_TIMEOUT: int = 300

    # ==================== 安全配置 ====================
    ENCRYPTION_ENABLED: bool = True
    ENCRYPTION_ALGORITHM: str = "AES-256-GCM"
    KEY_ROTATION_INTERVAL: int = 604800  # 7天

    DEVICE_FINGERPRINT_ENABLED: bool = True
    MAX_AUTH_FAILURES: int = 5
    AUTH_LOCK_DURATION: int = 3600  # 秒

    NONCE_EXPIRE_SECONDS: int = 300
    NONCE_CLEANUP_INTERVAL: int = 600  # 秒

    # ==================== 重试配置 ====================
    ALARM_RETRY_COUNT: int = 3
    ALARM_RETRY_INTERVAL_MS: int = 1000
    HEARTBEAT_RETRY_COUNT: int = 2
    TCP_HEARTBEAT_RETRY_COUNT: int = 3
    BATCH_RETRY_INTERVAL_MS: int = 5000

    # ==================== 会话配置 ====================
    SESSION_EXPIRE_SECONDS: int = 300
    SESSION_ID_LENGTH: int = 36

    # ==================== 心跳配置 ====================
    UDP_HEARTBEAT_INTERVAL: int = 30
    TCP_HEARTBEAT_INTERVAL: int = 30
    HEARTBEAT_EXPIRE_SECONDS: int = 90

    # ==================== 内存配置 ====================
    OBJECT_POOL_MAX_SIZE: int = 1000
    OBJECT_POOL_IDLE_TIMEOUT: int = 300

    LOCAL_CACHE_MAX_SIZE: int = 10000
    LOCAL_CACHE_TTL: int = 60
    REDIS_CACHE_TTL: int = 300

    MAX_MEMORY_USAGE: int = 536870912
    MEMORY_MONITOR_INTERVAL: int = 60

    # ==================== 可靠性配置 ====================
    MAX_REQUESTS_PER_SECOND: int = 10
    MAX_BATCH_SIZE: int = 100

    # ==================== Redis配置 ====================
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    REDIS_POOL_SIZE: int = 100
    REDIS_POOL_MAX_OVERFLOW: int = 200

    # ==================== MySQL配置 ====================
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_DATABASE: str = "zu_an"
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = ""
    MYSQL_POOL_SIZE: int = 50
    MYSQL_POOL_MAX_OVERFLOW: int = 100

    @property
    def DATABASE_URL(self) -> str:
        """数据库连接URL"""
        # 开发环境使用SQLite
        db_path = Path(__file__).parent.parent.parent / "zu_an.db"
        return f"sqlite+aiosqlite:///{db_path}"

    # ==================== InfluxDB配置 ====================
    INFLUXDB_URL: str = "http://localhost:8086"
    INFLUXDB_TOKEN: str = ""
    INFLUXDB_ORG: str = "shoe_insole"
    INFLUXDB_BUCKET: str = "location"
    INFLUXDB_POOL_SIZE: int = 20

    # ==================== 预共享密钥 ====================
    DEVICE_PRESHARED_KEY: str = "default_preshared_key_change_me"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 确保日志目录存在
        log_dir = Path(self.LOG_FILE).parent
        if not log_dir.exists():
            log_dir.mkdir(parents=True, exist_ok=True)


# 全局配置实例
settings = Settings()
