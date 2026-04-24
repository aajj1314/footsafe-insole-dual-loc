# -*- coding: utf-8 -*-
"""
UDP报文模型
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

from app.models.schemas.common import LocationData, AlarmData, HeartbeatData, CommandResponseData


class LocationRequest(BaseModel):
    """位置上报请求"""

    version: str = Field(default="1.0")
    device_id: str = Field(..., description="设备IMEI号")
    timestamp: str = Field(..., description="ISO 8601时间戳")
    nonce: str = Field(..., description="随机字符串(12位)")
    type: str = Field(default="location")
    data: LocationData
    checksum: str = Field(..., description="MD5校验值")


class AlarmRequest(BaseModel):
    """报警上报请求"""

    version: str = Field(default="1.0")
    device_id: str = Field(..., description="设备IMEI号")
    timestamp: str = Field(..., description="ISO 8601时间戳")
    nonce: str = Field(..., description="随机字符串(12位)")
    type: str = Field(default="alarm")
    data: AlarmData
    checksum: str = Field(..., description="MD5校验值")


class HeartbeatRequest(BaseModel):
    """心跳上报请求"""

    version: str = Field(default="1.0")
    device_id: str = Field(..., description="设备IMEI号")
    timestamp: str = Field(..., description="ISO 8601时间戳")
    nonce: str = Field(..., description="随机字符串(12位)")
    type: str = Field(default="heartbeat")
    data: HeartbeatData
    checksum: str = Field(..., description="MD5校验值")


class CommandResponseRequest(BaseModel):
    """命令响应请求"""

    version: str = Field(default="1.0")
    device_id: str = Field(..., description="设备IMEI号")
    timestamp: str = Field(..., description="ISO 8601时间戳")
    nonce: str = Field(..., description="随机字符串(12位)")
    type: str = Field(default="command_response")
    data: CommandResponseData
    checksum: str = Field(..., description="MD5校验值")
