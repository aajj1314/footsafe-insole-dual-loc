# -*- coding: utf-8 -*-
"""
TCP报文模型
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


class AuthRequestData(BaseModel):
    """认证请求数据"""

    firmware_version: str = Field(..., description="固件版本号")
    hardware_version: str = Field(..., description="硬件版本号")
    iccid: str = Field(..., description="SIM卡ICCID")
    fingerprint: str = Field(..., description="设备指纹")


class AuthResponseData(BaseModel):
    """认证响应数据"""

    session_id: str = Field(..., description="会话ID(UUID)")
    heartbeat_interval: int = Field(..., description="心跳间隔(秒)")
    server_time: str = Field(..., description="服务器当前时间")
    key_version: int = Field(default=1, description="加密密钥版本号")


class AuthRequest(BaseModel):
    """认证请求"""

    version: str = Field(default="1.0")
    device_id: str = Field(..., description="设备IMEI号")
    timestamp: str = Field(..., description="ISO 8601时间戳")
    nonce: str = Field(..., description="随机字符串(12位)")
    type: str = Field(default="auth")
    data: AuthRequestData
    checksum: str = Field(..., description="MD5校验值")


class AuthResponse(BaseModel):
    """认证响应"""

    code: int = Field(..., description="错误码")
    message: str = Field(..., description="错误信息")
    data: AuthResponseData
    timestamp: str = Field(..., description="服务器时间戳")


class TCPHeartbeatRequest(BaseModel):
    """TCP心跳请求"""

    version: str = Field(default="1.0")
    device_id: str = Field(..., description="设备IMEI号")
    session_id: str = Field(..., description="会话ID(UUID)")
    timestamp: str = Field(..., description="ISO 8601时间戳")
    nonce: str = Field(..., description="随机字符串(12位)")
    type: str = Field(default="tcp_heartbeat")
    data: Dict[str, Any] = Field(default_factory=dict)
    checksum: str = Field(..., description="MD5校验值")


class OTAProgressData(BaseModel):
    """OTA升级进度数据"""

    upgrade_id: str = Field(..., description="升级任务ID(UUID)")
    status: str = Field(..., description="状态")
    progress: int = Field(..., ge=0, le=100, description="进度")
    error_code: int = Field(default=0, description="错误码")
    error_message: str = Field(default="", description="错误信息")


class OTAProgressRequest(BaseModel):
    """OTA进度上报请求"""

    version: str = Field(default="1.0")
    device_id: str = Field(..., description="设备IMEI号")
    session_id: str = Field(..., description="会话ID(UUID)")
    timestamp: str = Field(..., description="ISO 8601时间戳")
    nonce: str = Field(..., description="随机字符串(12位)")
    type: str = Field(default="ota_progress")
    data: OTAProgressData
    checksum: str = Field(..., description="MD5校验值")


class BatchItem(BaseModel):
    """批量上报项"""

    type: str = Field(..., description="数据类型")
    timestamp: str = Field(..., description="时间戳")
    data: Dict[str, Any] = Field(..., description="数据")


class BatchReportData(BaseModel):
    """批量上报数据"""

    total: int = Field(..., description="总条数")
    index: int = Field(..., description="当前批次序号")
    items: List[BatchItem] = Field(..., description="数据项数组")


class BatchReportRequest(BaseModel):
    """批量上报请求"""

    version: str = Field(default="1.0")
    device_id: str = Field(..., description="设备IMEI号")
    session_id: str = Field(..., description="会话ID(UUID)")
    timestamp: str = Field(..., description="ISO 8601时间戳")
    nonce: str = Field(..., description="随机字符串(12位)")
    type: str = Field(default="batch_report")
    data: BatchReportData
    checksum: str = Field(..., description="MD5校验值")


class BatchReportResponse(BaseModel):
    """批量上报响应"""

    code: int = Field(..., description="错误码")
    message: str = Field(..., description="错误信息")
    data: Dict[str, Any] = Field(
        default_factory=lambda: {"success_count": 0, "failed_indexes": []}
    )
    timestamp: str = Field(..., description="服务器时间戳")


class DeviceErrorData(BaseModel):
    """设备错误数据"""

    error_type: str = Field(..., description="错误类型")
    error_level: int = Field(..., description="错误级别")
    error_message: str = Field(..., description="错误信息")
    error_code: int = Field(..., description="错误码")
    extra_data: Optional[Dict[str, Any]] = Field(default=None, description="附加数据")


class DeviceErrorRequest(BaseModel):
    """设备错误上报请求"""

    version: str = Field(default="1.0")
    device_id: str = Field(..., description="设备IMEI号")
    session_id: str = Field(..., description="会话ID(UUID)")
    timestamp: str = Field(..., description="ISO 8601时间戳")
    nonce: str = Field(..., description="随机字符串(12位)")
    type: str = Field(default="device_error")
    data: DeviceErrorData
    checksum: str = Field(..., description="MD5校验值")
