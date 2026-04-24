# -*- coding: utf-8 -*-
"""
限流、超时、内存限制配置
"""

# ==================== 通信端口配置 ====================
UDP_PORT = 8888
TCP_PORT = 8889
TCP_MAX_CONNECTIONS = 100000
TCP_CONNECTION_TIMEOUT = 300  # 秒

# ==================== 安全配置 ====================
NONCE_EXPIRE_SECONDS = 300
MAX_REQUESTS_PER_SECOND = 10
MAX_BATCH_SIZE = 100
ALARM_RETRY_COUNT = 3
ALARM_RETRY_INTERVAL_MS = 1000
HEARTBEAT_RETRY_COUNT = 2
TCP_HEARTBEAT_RETRY_COUNT = 3
BATCH_RETRY_INTERVAL_MS = 5000

# ==================== 心跳配置 ====================
UDP_HEARTBEAT_INTERVAL = 30  # 秒
TCP_HEARTBEAT_INTERVAL = 30  # 秒
HEARTBEAT_EXPIRE_SECONDS = 90  # 秒

# ==================== 会话配置 ====================
SESSION_ID_LENGTH = 36
SESSION_EXPIRE_SECONDS = 300

# ==================== 缓存配置 ====================
LOCAL_CACHE_MAX_SIZE = 10000
LOCAL_CACHE_TTL = 60  # 秒
REDIS_CACHE_TTL = 300  # 秒

# ==================== 内存配置 ====================
OBJECT_POOL_MAX_SIZE = 1000
OBJECT_POOL_IDLE_TIMEOUT = 300
MAX_MEMORY_USAGE = 536870912  # 512MB
MEMORY_MONITOR_INTERVAL = 60

# ==================== 位置上报配置 ====================
LOCATION_REPORT_INTERVAL_NORMAL = 60  # 秒
LOCATION_REPORT_INTERVAL_SPORT = 30  # 秒
LOCATION_REPORT_INTERVAL_ALARM = 5  # 秒
LOCATION_CHANGE_THRESHOLD = 50  # 米

# ==================== 可靠性配置 ====================
MAX_OFFLINE_CACHE_SIZE = 1000
MAX_UDP_PACKET_SIZE = 512
MAX_TCP_PACKET_SIZE = 1024
BUFFER_POOL_SIZE = 8

# ==================== 连续失败阈值 ====================
HEARTBEAT_MISS_THRESHOLD = 3  # 连续3次未收到心跳标记为离线
RATE_LIMIT_INCREASE_THRESHOLD = 3  # 连续3次上报失败，延长间隔至300秒

# ==================== WebSocket配置 ====================
WS_PING_INTERVAL = 30  # 秒
WS_PING_TIMEOUT = 10  # 秒
WS_MAX_QUEUE_SIZE = 100

# ==================== OTA配置 ====================
OTA_PROGRESS_REPORT_INTERVAL = 10  # 每10%上报一次
OTA_DOWNLOAD_TIMEOUT = 300  # 秒
OTA_VERIFY_TIMEOUT = 60  # 秒
OTA_UPGRADE_TIMEOUT = 120  # 秒
