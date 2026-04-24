# -*- coding: utf-8 -*-
"""
报文字段验证器
"""

from typing import Dict, Any, Optional, List, Tuple

from app.config.constants import (
    PROTOCOL_VERSION,
    MESSAGE_TYPE_LOCATION,
    MESSAGE_TYPE_ALARM,
    MESSAGE_TYPE_HEARTBEAT,
    MESSAGE_TYPE_COMMAND_RESPONSE,
    MESSAGE_TYPE_AUTH,
    MESSAGE_TYPE_TCP_HEARTBEAT,
    MESSAGE_TYPE_OTA_PROGRESS,
    MESSAGE_TYPE_BATCH_REPORT,
    MESSAGE_TYPE_DEVICE_ERROR,
    DEVICE_MODE_NORMAL,
    DEVICE_MODE_LOW_POWER,
    DEVICE_MODE_ALARM,
    DEVICE_MODE_SLEEP,
    ALARM_TYPE_TAMPER,
    ALARM_TYPE_FALL,
    ALARM_TYPE_STILL,
    ALARM_TYPE_LOW_BATTERY,
    ALARM_TYPE_SOS,
    ALARM_TYPE_SHUTDOWN,
    ALARM_LEVEL_LOW,
    ALARM_LEVEL_MEDIUM,
    ALARM_LEVEL_HIGH,
    ALARM_LEVEL_URGENT,
)


class MessageValidator:
    """报文字段验证器"""

    # 有效的报文类型
    VALID_MESSAGE_TYPES = {
        MESSAGE_TYPE_LOCATION,
        MESSAGE_TYPE_ALARM,
        MESSAGE_TYPE_HEARTBEAT,
        MESSAGE_TYPE_COMMAND_RESPONSE,
        MESSAGE_TYPE_AUTH,
        MESSAGE_TYPE_TCP_HEARTBEAT,
        MESSAGE_TYPE_OTA_PROGRESS,
        MESSAGE_TYPE_BATCH_REPORT,
        MESSAGE_TYPE_DEVICE_ERROR,
    }

    # 有效的工作模式
    VALID_DEVICE_MODES = {
        DEVICE_MODE_NORMAL,
        DEVICE_MODE_LOW_POWER,
        DEVICE_MODE_ALARM,
        DEVICE_MODE_SLEEP,
    }

    # 有效的报警类型
    VALID_ALARM_TYPES = {
        ALARM_TYPE_TAMPER,
        ALARM_TYPE_FALL,
        ALARM_TYPE_STILL,
        ALARM_TYPE_LOW_BATTERY,
        ALARM_TYPE_SOS,
        ALARM_TYPE_SHUTDOWN,
    }

    # 有效的报警级别
    VALID_ALARM_LEVELS = {
        ALARM_LEVEL_LOW,
        ALARM_LEVEL_MEDIUM,
        ALARM_LEVEL_HIGH,
        ALARM_LEVEL_URGENT,
    }

    def validate_base(self, message: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        验证基础报文结构

        Args:
            message: 消息字典

        Returns:
            (是否有效, 错误信息)
        """
        # 验证版本
        if message.get("version") != PROTOCOL_VERSION:
            return False, f"Invalid version: {message.get('version')}, expected: {PROTOCOL_VERSION}"

        # 验证device_id
        device_id = message.get("device_id")
        if not device_id or not isinstance(device_id, str):
            return False, "Invalid or missing device_id"

        if len(device_id) > 16:
            return False, f"device_id too long: {len(device_id)}, max: 16"

        # 验证timestamp
        timestamp = message.get("timestamp")
        if not timestamp or not isinstance(timestamp, str):
            return False, "Invalid or missing timestamp"

        # 验证nonce
        nonce = message.get("nonce")
        if not nonce or not isinstance(nonce, str):
            return False, "Invalid or missing nonce"

        # 验证type
        msg_type = message.get("type")
        if msg_type not in self.VALID_MESSAGE_TYPES:
            return False, f"Invalid message type: {msg_type}"

        # 验证data
        data = message.get("data")
        if data is None or not isinstance(data, dict):
            return False, "Invalid or missing data"

        # 验证checksum
        checksum = message.get("checksum")
        if not checksum or not isinstance(checksum, str):
            return False, "Invalid or missing checksum"

        return True, None

    def validate_location(self, data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        验证位置数据

        Args:
            data: 数据字典

        Returns:
            (是否有效, 错误信息)
        """
        # 纬度
        latitude = data.get("latitude")
        if not isinstance(latitude, (int, float)):
            return False, "Invalid latitude type"
        if not -90.0 <= latitude <= 90.0:
            return False, f"Latitude out of range: {latitude}"

        # 经度
        longitude = data.get("longitude")
        if not isinstance(longitude, (int, float)):
            return False, "Invalid longitude type"
        if not -180.0 <= longitude <= 180.0:
            return False, f"Longitude out of range: {longitude}"

        # 海拔
        altitude = data.get("altitude")
        if not isinstance(altitude, (int, float)):
            return False, "Invalid altitude type"
        if not -1000.0 <= altitude <= 10000.0:
            return False, f"Altitude out of range: {altitude}"

        # 速度
        speed = data.get("speed")
        if not isinstance(speed, (int, float)):
            return False, "Invalid speed type"
        if not 0.0 <= speed <= 100.0:
            return False, f"Speed out of range: {speed}"

        # 方向
        direction = data.get("direction")
        if not isinstance(direction, int):
            return False, "Invalid direction type"
        if not 0 <= direction <= 359:
            return False, f"Direction out of range: {direction}"

        # 精度
        accuracy = data.get("accuracy")
        if not isinstance(accuracy, (int, float)):
            return False, "Invalid accuracy type"
        if not 0.0 <= accuracy <= 100.0:
            return False, f"Accuracy out of range: {accuracy}"

        # 卫星数
        satellites = data.get("satellites")
        if not isinstance(satellites, int):
            return False, "Invalid satellites type"
        if not 0 <= satellites <= 24:
            return False, f"Satellites out of range: {satellites}"

        # 电量
        battery = data.get("battery")
        if not isinstance(battery, int):
            return False, "Invalid battery type"
        if not 0 <= battery <= 100:
            return False, f"Battery out of range: {battery}"

        # 信号强度
        signal_strength = data.get("signal_strength")
        if not isinstance(signal_strength, int):
            return False, "Invalid signal_strength type"
        if not 0 <= signal_strength <= 100:
            return False, f"Signal_strength out of range: {signal_strength}"

        # 充电状态
        charging = data.get("charging")
        if not isinstance(charging, bool):
            return False, "Invalid charging type, expected boolean"

        # 工作模式
        mode = data.get("mode")
        if mode not in self.VALID_DEVICE_MODES:
            return False, f"Invalid mode: {mode}"

        return True, None

    def validate_alarm(self, data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        验证报警数据

        Args:
            data: 数据字典

        Returns:
            (是否有效, 错误信息)
        """
        # 报警类型
        alarm_type = data.get("alarm_type")
        if alarm_type not in self.VALID_ALARM_TYPES:
            return False, f"Invalid alarm_type: {alarm_type}"

        # 报警级别
        alarm_level = data.get("alarm_level")
        if alarm_level not in self.VALID_ALARM_LEVELS:
            return False, f"Invalid alarm_level: {alarm_level}"

        # 纬度
        latitude = data.get("latitude")
        if not isinstance(latitude, (int, float)):
            return False, "Invalid latitude type"

        # 经度
        longitude = data.get("longitude")
        if not isinstance(longitude, (int, float)):
            return False, "Invalid longitude type"

        # 精度
        accuracy = data.get("accuracy")
        if not isinstance(accuracy, (int, float)):
            return False, "Invalid accuracy type"

        # 电量
        battery = data.get("battery")
        if not isinstance(battery, int):
            return False, "Invalid battery type"

        return True, None

    def validate_heartbeat(self, data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        验证心跳数据

        Args:
            data: 数据字典

        Returns:
            (是否有效, 错误信息)
        """
        # 电量
        battery = data.get("battery")
        if not isinstance(battery, int):
            return False, "Invalid battery type"
        if not 0 <= battery <= 100:
            return False, f"Battery out of range: {battery}"

        # 信号强度
        signal_strength = data.get("signal_strength")
        if not isinstance(signal_strength, int):
            return False, "Invalid signal_strength type"
        if not 0 <= signal_strength <= 100:
            return False, f"Signal_strength out of range: {signal_strength}"

        # 充电状态
        charging = data.get("charging")
        if not isinstance(charging, bool):
            return False, "Invalid charging type, expected boolean"

        # 温度
        temperature = data.get("temperature")
        if not isinstance(temperature, (int, float)):
            return False, "Invalid temperature type"
        if not -40.0 <= temperature <= 85.0:
            return False, f"Temperature out of range: {temperature}"

        return True, None

    def validate_auth(self, data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        验证认证数据

        Args:
            data: 数据字典

        Returns:
            (是否有效, 错误信息)
        """
        # 固件版本
        firmware_version = data.get("firmware_version")
        if not firmware_version or not isinstance(firmware_version, str):
            return False, "Invalid firmware_version"

        # 硬件版本
        hardware_version = data.get("hardware_version")
        if not hardware_version or not isinstance(hardware_version, str):
            return False, "Invalid hardware_version"

        # ICCID
        iccid = data.get("iccid")
        if not iccid or not isinstance(iccid, str):
            return False, "Invalid iccid"

        # 指纹
        fingerprint = data.get("fingerprint")
        if not fingerprint or not isinstance(fingerprint, str):
            return False, "Invalid fingerprint"

        return True, None


# 全局验证器实例
message_validator = MessageValidator()
