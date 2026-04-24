# -*- coding: utf-8 -*-
"""
用户绑定设备表
"""

from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from app.core.database.session import Base


class UserDevice(Base):
    """用户-设备绑定表"""

    __tablename__ = "user_devices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False, index=True)

    # 绑定信息
    nickname = Column(String(64), nullable=True)  # 设备昵称，如"爷爷"
    relation = Column(String(32), nullable=True)  # 关系，如"爷爷"

    # 状态
    status = Column(String(16), default="active")  # active, unbinded

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "device_id": self.device_id,
            "nickname": self.nickname,
            "relation": self.relation,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
