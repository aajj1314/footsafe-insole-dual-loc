# -*- coding: utf-8 -*-
"""
常量定义模块
与API接口v2.1和硬件端100%对应
"""

# ==================== 协议版本 ====================
PROTOCOL_VERSION = "1.0"

# ==================== 报文类型 ====================
MESSAGE_TYPE_LOCATION = "location"
MESSAGE_TYPE_ALARM = "alarm"
MESSAGE_TYPE_HEARTBEAT = "heartbeat"
MESSAGE_TYPE_COMMAND_RESPONSE = "command_response"
MESSAGE_TYPE_AUTH = "auth"
MESSAGE_TYPE_TCP_HEARTBEAT = "tcp_heartbeat"
MESSAGE_TYPE_OTA_PROGRESS = "ota_progress"
MESSAGE_TYPE_BATCH_REPORT = "batch_report"
MESSAGE_TYPE_DEVICE_ERROR = "device_error"

# ==================== 报警类型 ====================
ALARM_TYPE_TAMPER = 1
ALARM_TYPE_FALL = 2
ALARM_TYPE_STILL = 3
ALARM_TYPE_LOW_BATTERY = 4
ALARM_TYPE_SOS = 5
ALARM_TYPE_SHUTDOWN = 6

ALARM_TYPE_NAMES = {
    ALARM_TYPE_TAMPER: "tamper",
    ALARM_TYPE_FALL: "fall",
    ALARM_TYPE_STILL: "still",
    ALARM_TYPE_LOW_BATTERY: "low_battery",
    ALARM_TYPE_SOS: "sos",
    ALARM_TYPE_SHUTDOWN: "shutdown",
}

# ==================== 报警级别 ====================
ALARM_LEVEL_LOW = 1
ALARM_LEVEL_MEDIUM = 2
ALARM_LEVEL_HIGH = 3
ALARM_LEVEL_URGENT = 4

ALARM_LEVEL_NAMES = {
    ALARM_LEVEL_LOW: "low",
    ALARM_LEVEL_MEDIUM: "medium",
    ALARM_LEVEL_HIGH: "high",
    ALARM_LEVEL_URGENT: "urgent",
}

# ==================== 设备工作模式 ====================
DEVICE_MODE_NORMAL = "normal"
DEVICE_MODE_LOW_POWER = "low_power"
DEVICE_MODE_ALARM = "alarm"
DEVICE_MODE_SLEEP = "sleep"

# ==================== 错误码 ====================
ERROR_SUCCESS = 0
ERROR_DEVICE_NOT_REGISTERED = 1001
ERROR_CHECKSUM_FAILED = 1002
ERROR_PARAMETER_ERROR = 1003
ERROR_SERVER_BUSY = 1004
ERROR_SESSION_INVALID = 1005
ERROR_RATE_LIMIT_EXCEEDED = 1006
ERROR_SESSION_EXPIRED = 3001
ERROR_DEVICE_LOCKED = 3002
ERROR_SIGNATURE_INVALID = 3003
ERROR_ENCRYPTION_FAILED = 3004

ERROR_MESSAGES = {
    ERROR_SUCCESS: "success",
    ERROR_DEVICE_NOT_REGISTERED: "device_not_registered",
    ERROR_CHECKSUM_FAILED: "checksum_failed",
    ERROR_PARAMETER_ERROR: "parameter_error",
    ERROR_SERVER_BUSY: "server_busy",
    ERROR_SESSION_INVALID: "session_invalid",
    ERROR_RATE_LIMIT_EXCEEDED: "rate_limit_exceeded",
    ERROR_SESSION_EXPIRED: "session_expired",
    ERROR_DEVICE_LOCKED: "device_locked",
    ERROR_SIGNATURE_INVALID: "signature_invalid",
    ERROR_ENCRYPTION_FAILED: "encryption_failed",
}

# ==================== 设备错误类型 error_code ====================
DEVICE_ERROR_GPS_FAULT = 1001
DEVICE_ERROR_COMMUNICATION_FAULT = 1002
DEVICE_ERROR_SENSOR_FAULT = 1003
DEVICE_ERROR_BATTERY_FAULT = 1004
DEVICE_ERROR_MEMORY_FAULT = 1005
DEVICE_ERROR_FIRMWARE_CRASH = 1006
DEVICE_ERROR_WATCHDOG_TIMEOUT = 1007

DEVICE_ERROR_TYPES = {
    DEVICE_ERROR_GPS_FAULT: "gps_fault",
    DEVICE_ERROR_COMMUNICATION_FAULT: "communication_fault",
    DEVICE_ERROR_SENSOR_FAULT: "sensor_fault",
    DEVICE_ERROR_BATTERY_FAULT: "battery_fault",
    DEVICE_ERROR_MEMORY_FAULT: "memory_fault",
    DEVICE_ERROR_FIRMWARE_CRASH: "firmware_crash",
    DEVICE_ERROR_WATCHDOG_TIMEOUT: "watchdog_timeout",
}

# ==================== 命令类型 ====================
# UDP指令
COMMAND_TYPE_GET_LOCATION = "get_location"
COMMAND_TYPE_GET_STATUS = "get_status"
COMMAND_TYPE_RESET = "reset"

# TCP指令
COMMAND_TYPE_SET_REPORT_INTERVAL = "set_report_interval"
COMMAND_TYPE_SET_MODE = "set_mode"
COMMAND_TYPE_GET_CONFIG = "get_config"
COMMAND_TYPE_OTA_START = "ota_start"
COMMAND_TYPE_OTA_CANCEL = "ota_cancel"
COMMAND_TYPE_FACTORY_RESET = "factory_reset"
COMMAND_TYPE_LOCK_DEVICE = "lock_device"

UDP_COMMANDS = {
    COMMAND_TYPE_GET_LOCATION,
    COMMAND_TYPE_GET_STATUS,
    COMMAND_TYPE_RESET,
}

TCP_COMMANDS = {
    COMMAND_TYPE_SET_REPORT_INTERVAL,
    COMMAND_TYPE_SET_MODE,
    COMMAND_TYPE_GET_CONFIG,
    COMMAND_TYPE_OTA_START,
    COMMAND_TYPE_OTA_CANCEL,
    COMMAND_TYPE_FACTORY_RESET,
    COMMAND_TYPE_LOCK_DEVICE,
}

# ==================== OTA状态 ====================
OTA_STATUS_DOWNLOADING = "downloading"
OTA_STATUS_VERIFYING = "verifying"
OTA_STATUS_UPGRADING = "upgrading"
OTA_STATUS_SUCCESS = "success"
OTA_STATUS_FAILED = "failed"

# ==================== 命令执行结果 ====================
COMMAND_RESULT_SUCCESS = "success"
COMMAND_RESULT_FAILED = "failed"

# ==================== 设备状态 ====================
DEVICE_STATUS_ONLINE = "online"
DEVICE_STATUS_OFFLINE = "offline"
DEVICE_STATUS_ALARM = "alarm"
DEVICE_STATUS_LOCKED = "locked"
