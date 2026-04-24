# -*- coding: utf-8 -*-
"""
设备ORM模型
"""

from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, Float
from app.core.database.session import Base


class Device(Base):
    """设备表"""

    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    imei = Column(String(32), unique=True, nullable=False, index=True)

    # SIM卡信息
    iccid = Column(String(32), nullable=True, index=True)

    # 固件信息
    firmware_version = Column(String(16), nullable=True)
    hardware_version = Column(String(16), nullable=True)

    # 设备指纹
    fingerprint = Column(String(128), nullable=True)

    # 状态
    status = Column(String(16), default="offline")  # online, offline, error
    mode = Column(String(16), default="normal")  # normal, low_power, alarm, sleep

    # 设备状态
    battery = Column(Integer, nullable=True)  # 0-100
    signal_strength = Column(Integer, nullable=True)  # 0-100
    temperature = Column(Float, nullable=True)  # 摄氏度
    satellites = Column(Integer, nullable=True)  # 可见卫星数

    # 位置信息
    last_location_lat = Column(String(16), nullable=True)
    last_location_lng = Column(String(16), nullable=True)
    last_location_alt = Column(String(16), nullable=True)
    last_location_speed = Column(String(16), nullable=True)
    last_location_direction = Column(String(16), nullable=True)
    last_location_accuracy = Column(String(16), nullable=True)
    last_location_time = Column(DateTime, nullable=True)

    # 注册状态
    registered = Column(Integer, default=0)  # 0: 未注册, 1: 已注册
    registered_at = Column(DateTime, nullable=True)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_seen = Column(DateTime, nullable=True)

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "imei": self.imei,
            "iccid": self.iccid,
            "firmware_version": self.firmware_version,
            "hardware_version": self.hardware_version,
            "status": self.status,
            "mode": self.mode,
            "battery": self.battery,
            "signal_strength": self.signal_strength,
            "temperature": self.temperature,
            "satellites": self.satellites,
            "last_location": {
                "lat": self.last_location_lat,
                "lng": self.last_location_lng,
                "alt": self.last_location_alt,
                "speed": self.last_location_speed,
                "direction": self.last_location_direction,
                "accuracy": self.last_location_accuracy,
                "time": self.last_location_time.isoformat() if self.last_location_time else None,
            },
            "registered": self.registered,
            "registered_at": self.registered_at.isoformat() if self.registered_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_seen": self.last_seen.isoformat() if self.last_seen else None,
        }


class Alarm(Base):
    """报警记录表"""

    __tablename__ = "alarms"

    id = Column(Integer, primary_key=True, autoincrement=True)
    alarm_id = Column(String(64), unique=True, nullable=False, index=True)
    device_id = Column(String(32), nullable=False, index=True)

    # 报警信息
    alarm_type = Column(Integer, nullable=False)  # 1-6
    alarm_level = Column(Integer, nullable=False)  # 1-4
    status = Column(String(16), default="pending")  # pending, resolved, ignored

    # 位置信息
    latitude = Column(String(16), nullable=True)
    longitude = Column(String(16), nullable=True)
    accuracy = Column(String(16), nullable=True)

    # 设备状态
    battery = Column(Integer, nullable=True)

    # 报警详情
    alarm_data = Column(Text, nullable=True)

    # 处理信息
    handled_by = Column(String(64), nullable=True)
    handled_at = Column(DateTime, nullable=True)
    handle_note = Column(Text, nullable=True)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "alarm_id": self.alarm_id,
            "device_id": self.device_id,
            "alarm_type": self.alarm_type,
            "alarm_level": self.alarm_level,
            "status": self.status,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "accuracy": self.accuracy,
            "battery": self.battery,
            "alarm_data": self.alarm_data,
            "handled_by": self.handled_by,
            "handled_at": self.handled_at.isoformat() if self.handled_at else None,
            "handle_note": self.handle_note,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class LocationHistory(Base):
    """位置历史表"""

    __tablename__ = "location_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String(32), nullable=False, index=True)

    # 位置信息
    latitude = Column(String(16), nullable=False)
    longitude = Column(String(16), nullable=False)
    altitude = Column(String(16), nullable=True)
    speed = Column(String(16), nullable=True)
    direction = Column(String(16), nullable=True)
    accuracy = Column(String(16), nullable=True)
    satellites = Column(Integer, nullable=True)

    # 设备状态
    battery = Column(Integer, nullable=True)
    signal_strength = Column(Integer, nullable=True)
    mode = Column(String(16), nullable=True)

    # GPS时间戳
    timestamp = Column(String(32), nullable=False)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "device_id": self.device_id,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "altitude": self.altitude,
            "speed": self.speed,
            "direction": self.direction,
            "accuracy": self.accuracy,
            "satellites": self.satellites,
            "battery": self.battery,
            "signal_strength": self.signal_strength,
            "mode": self.mode,
            "timestamp": self.timestamp,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Command(Base):
    """指令记录表"""

    __tablename__ = "commands"

    id = Column(Integer, primary_key=True, autoincrement=True)
    command_id = Column(String(64), unique=True, nullable=False, index=True)
    device_id = Column(String(32), nullable=False, index=True)

    # 指令信息
    command_type = Column(String(32), nullable=False)
    command_data = Column(Text, nullable=True)
    result = Column(String(16), nullable=True)  # pending, success, failed
    result_data = Column(Text, nullable=True)
    error_message = Column(String(256), nullable=True)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "command_id": self.command_id,
            "device_id": self.device_id,
            "command_type": self.command_type,
            "command_data": self.command_data,
            "result": self.result,
            "result_data": self.result_data,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class OTATask(Base):
    """OTA升级任务表"""

    __tablename__ = "ota_tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    upgrade_id = Column(String(64), unique=True, nullable=False, index=True)
    device_id = Column(String(32), nullable=False, index=True)

    # 升级信息
    version = Column(String(16), nullable=False)
    url = Column(String(512), nullable=False)
    size = Column(Integer, nullable=False)
    checksum = Column(String(64), nullable=False)

    # 状态
    status = Column(String(16), default="pending")  # pending, downloading, verifying, upgrading, success, failed
    progress = Column(Integer, default=0)  # 0-100
    error_code = Column(Integer, nullable=True)
    error_message = Column(String(256), nullable=True)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "upgrade_id": self.upgrade_id,
            "device_id": self.device_id,
            "version": self.version,
            "status": self.status,
            "progress": self.progress,
            "error_code": self.error_code,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class DeviceError(Base):
    """设备错误记录表"""

    __tablename__ = "device_errors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String(32), nullable=False, index=True)

    # 错误信息
    error_type = Column(String(32), nullable=False)
    error_level = Column(Integer, nullable=False)  # 1-4
    error_code = Column(Integer, nullable=True)
    error_message = Column(String(512), nullable=True)
    extra_data = Column(Text, nullable=True)

    # 状态
    status = Column(String(16), default="pending")  # pending, resolved
    resolved_at = Column(DateTime, nullable=True)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "device_id": self.device_id,
            "error_type": self.error_type,
            "error_level": self.error_level,
            "error_code": self.error_code,
            "error_message": self.error_message,
            "extra_data": self.extra_data,
            "status": self.status,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
