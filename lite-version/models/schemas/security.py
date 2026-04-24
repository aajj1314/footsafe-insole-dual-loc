# -*- coding: utf-8 -*-
"""
安全相关模型
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class SecurityEvent(BaseModel):
    """安全事件模型"""

    event_id: str = Field(..., description="事件ID")
    event_type: str = Field(..., description="事件类型")
    device_id: Optional[str] = Field(None, description="设备ID")
    session_id: Optional[str] = Field(None, description="会话ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="事件时间")
    details: Optional[Dict[str, Any]] = Field(default_factory=dict, description="事件详情")
    ip_address: Optional[str] = Field(None, description="IP地址")


class RateLimitInfo(BaseModel):
    """限流信息模型"""

    device_id: str = Field(..., description="设备ID")
    request_count: int = Field(default=0, description="请求计数")
    window_start: datetime = Field(default_factory=datetime.utcnow, description="窗口开始时间")
    blocked: bool = Field(default=False, description="是否被限流")
