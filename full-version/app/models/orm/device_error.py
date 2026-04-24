# -*- coding: utf-8 -*-
"""
设备错误ORM模型
"""

from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class DeviceError(Base):
    """设备错误表"""

    __tablename__ = "device_errors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String(16), nullable=False, index=True)
    error_id = Column(String(40), unique=True, nullable=False)

    # 错误信息
    error_type = Column(String(32), nullable=False)
    error_level = Column(Integer, nullable=False)
    error_code = Column(Integer, nullable=False)
    error_message = Column(String(256), nullable=True)
    extra_data = Column(Text, nullable=True)

    # 状态
    status = Column(String(16), default="pending")  # pending, resolved
    resolved_at = Column(DateTime, nullable=True)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "device_id": self.device_id,
            "error_id": self.error_id,
            "error_type": self.error_type,
            "error_level": self.error_level,
            "error_code": self.error_code,
            "error_message": self.error_message,
            "extra_data": self.extra_data,
            "status": self.status,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
