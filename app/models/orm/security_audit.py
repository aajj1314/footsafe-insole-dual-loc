# -*- coding: utf-8 -*-
"""
安全审计ORM模型
"""

from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class SecurityAudit(Base):
    """安全审计表"""

    __tablename__ = "security_audits"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String(40), unique=True, nullable=False, index=True)
    device_id = Column(String(16), nullable=True, index=True)
    session_id = Column(String(40), nullable=True)

    # 事件信息
    event_type = Column(String(32), nullable=False)
    event_data = Column(JSON, nullable=True)

    # 来源信息
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(256), nullable=True)

    # 结果
    result = Column(String(16), nullable=True)  # success, failure, blocked

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "event_id": self.event_id,
            "device_id": self.device_id,
            "session_id": self.session_id,
            "event_type": self.event_type,
            "event_data": self.event_data,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "result": self.result,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
