# -*- coding: utf-8 -*-
"""
通用字段模型
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class GPSLocation(BaseModel):
    """GPS位置信息"""

    latitude: float = Field(..., ge=-90.0, le=90.0, description="纬度")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="经度")
    altitude: float = Field(..., ge=-1000.0, le=10000.0, description="海拔高度(米)")
    speed: float = Field(..., ge=0.0, le=100.0, description="移动速度(米/秒)")
    direction: int = Field(..., ge=0, le=359, description="移动方向(度)")
    accuracy: float = Field(..., ge=0.0, le=100.0, description="定位精度(米)")
    satellites: int = Field(..., ge=0, le=24, description="可见卫星数量")


class DeviceStatus(BaseModel):
    """设备状态信息"""

    battery: int = Field(..., ge=0, le=100, description="电量百分比")
    signal_strength: int = Field(..., ge=0, le=100, description="4G信号强度(%)")
    charging: bool = Field(..., description="是否正在充电")
    temperature: Optional[float] = Field(None, ge=-40.0, le=85.0, description="设备温度(摄氏度)")


class LocationData(GPSLocation, DeviceStatus):
    """位置数据模型"""

    mode: str = Field(..., description="设备工作模式")
    gps_timestamp: str = Field(..., description="GPS定位时间戳")


class AlarmData(GPSLocation):
    """报警数据模型"""

    alarm_type: int = Field(..., description="报警类型")
    alarm_level: int = Field(..., description="报警级别")
    battery: int = Field(..., ge=0, le=100, description="电量百分比")
    alarm_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="报警附加数据")


class HeartbeatData(DeviceStatus):
    """心跳数据模型"""

    pass


class CommandResponseData(BaseModel):
    """命令响应数据模型"""

    command_id: str = Field(..., description="命令唯一标识(UUID)")
    command_type: str = Field(..., description="命令类型")
    result: str = Field(..., description="执行结果：success/failed")
    result_data: Optional[Dict[str, Any]] = Field(default=None, description="命令执行结果数据")
