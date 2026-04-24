# -*- coding: utf-8 -*-
"""
用户ORM模型
"""

from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime
from app.core.database.session import Base


class User(Base):
    """用户表"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    password_hash = Column(String(256), nullable=False)
    phone = Column(String(16), nullable=True, index=True)
    email = Column(String(128), nullable=True)

    # 用户信息
    avatar = Column(String(256), nullable=True)
    nickname = Column(String(64), nullable=True)

    # 状态
    status = Column(String(16), default="active")  # active, disabled

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "username": self.username,
            "phone": self.phone,
            "email": self.email,
            "avatar": self.avatar,
            "nickname": self.nickname,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
        }
