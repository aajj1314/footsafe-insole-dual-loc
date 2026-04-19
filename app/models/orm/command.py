# -*- coding: utf-8 -*-
"""
命令ORM模型
"""

from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Command(Base):
    """命令表"""

    __tablename__ = "commands"

    id = Column(Integer, primary_key=True, autoincrement=True)
    command_id = Column(String(40), unique=True, nullable=False, index=True)
    device_id = Column(String(16), nullable=False, index=True)

    # 命令信息
    command_type = Column(String(32), nullable=False)
    command_data = Column(JSON, nullable=True)
    protocol = Column(String(8), default="tcp")  # tcp or udp

    # 状态
    status = Column(String(16), default="pending")  # pending, sent, acknowledged, timeout, cancelled
    result = Column(String(16), nullable=True)  # success, failed
    result_data = Column(JSON, nullable=True)

    # 重试
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    sent_at = Column(DateTime, nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    timeout_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "command_id": self.command_id,
            "device_id": self.device_id,
            "command_type": self.command_type,
            "command_data": self.command_data,
            "protocol": self.protocol,
            "status": self.status,
            "result": self.result,
            "result_data": self.result_data,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "timeout_at": self.timeout_at.isoformat() if self.timeout_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
