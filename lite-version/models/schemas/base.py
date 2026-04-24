# -*- coding: utf-8 -*-
"""
基础模型
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class BaseSchema(BaseModel):
    """基础Schema模型"""

    class Config:
        json_schema_extra = {
            "example": {
                "version": "1.0",
                "device_id": "860000000000000",
                "timestamp": "2024-01-15T14:30:00+08:00",
            }
        }


class BaseMessage(BaseSchema):
    """基础消息模型"""

    version: str = Field(default="1.0", description="协议版本")
    device_id: str = Field(..., description="设备IMEI号")
    timestamp: str = Field(..., description="ISO 8601时间戳")
    nonce: str = Field(..., description="随机字符串(12位)")
    type: str = Field(..., description="报文类型")
    data: Dict[str, Any] = Field(default_factory=dict, description="数据体")
    checksum: str = Field(..., description="MD5校验值")


class BaseResponse(BaseSchema):
    """基础响应模型"""

    code: int = Field(..., description="错误码")
    message: str = Field(..., description="错误信息")
    data: Optional[Dict[str, Any]] = Field(default=None, description="响应数据")
    timestamp: str = Field(..., description="服务器时间戳")
