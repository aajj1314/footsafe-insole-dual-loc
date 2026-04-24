# -*- coding: utf-8 -*-
"""
OTA任务ORM模型
"""

from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class OTATask(Base):
    """OTA升级任务表"""

    __tablename__ = "ota_tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    upgrade_id = Column(String(40), unique=True, nullable=False, index=True)
    device_id = Column(String(16), nullable=False, index=True)

    # 固件信息
    version = Column(String(16), nullable=False)
    url = Column(String(512), nullable=False)
    size = Column(Integer, nullable=False)
    checksum = Column(String(64), nullable=False)

    # 状态
    status = Column(String(16), default="pending")  # pending, downloading, verifying, upgrading, success, failed
    progress = Column(Integer, default=0)
    error_code = Column(Integer, default=0)
    error_message = Column(String(256), nullable=True)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "upgrade_id": self.upgrade_id,
            "device_id": self.device_id,
            "version": self.version,
            "url": self.url,
            "size": self.size,
            "checksum": self.checksum,
            "status": self.status,
            "progress": self.progress,
            "error_code": self.error_code,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
