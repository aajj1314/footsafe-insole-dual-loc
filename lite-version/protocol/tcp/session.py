# -*- coding: utf-8 -*-
"""
TCP会话管理模块
"""

import asyncio
import uuid
from typing import Optional, Dict
from datetime import datetime, timedelta
from dataclasses import dataclass, field

from app.config.limits import SESSION_EXPIRE_SECONDS, HEARTBEAT_EXPIRE_SECONDS
from app.core.database.redis import redis_pool, SessionManager
from app.core.logger import logger


@dataclass
class Session:
    """会话对象"""

    session_id: str
    device_id: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_active: datetime = field(default_factory=datetime.utcnow)
    heartbeat_count: int = 0
    is_valid: bool = True

    def update_activity(self) -> None:
        """更新最后活跃时间"""
        self.last_active = datetime.utcnow()

    def is_expired(self) -> bool:
        """检查会话是否过期"""
        delta = datetime.utcnow() - self.last_active
        return delta.total_seconds() > SESSION_EXPIRE_SECONDS

    def touch(self) -> None:
        """刷新会话"""
        self.update_activity()
        self.heartbeat_count += 1


class TCPSessionManager:
    """TCP会话管理器"""

    def __init__(self):
        """初始化会话管理器"""
        self._sessions: Dict[str, Session] = {}
        self._device_sessions: Dict[str, str] = {}  # device_id -> session_id
        self._lock = asyncio.Lock()
        self._redis_session_manager: Optional[SessionManager] = None

    def set_redis_session_manager(self, manager: SessionManager) -> None:
        """设置Redis会话管理器"""
        self._redis_session_manager = manager

    async def create_session(self, device_id: str) -> Session:
        """
        创建新会话

        Args:
            device_id: 设备ID

        Returns:
            新会话对象
        """
        async with self._lock:
            # 如果设备已有会话，先删除
            if device_id in self._device_sessions:
                old_session_id = self._device_sessions[device_id]
                old_session = self._sessions.pop(old_session_id, None)
                if old_session and self._redis_session_manager:
                    await self._redis_session_manager.delete_session(old_session_id)

            # 生成新的session_id
            session_id = str(uuid.uuid4())

            # 创建新会话
            session = Session(
                session_id=session_id,
                device_id=device_id,
            )

            self._sessions[session_id] = session
            self._device_sessions[device_id] = session_id

            # 在Redis中也创建会话
            if self._redis_session_manager:
                await self._redis_session_manager.create_session(session_id, device_id)

            logger.info(f"Session created: {session_id} for device: {device_id}")

            return session

    async def get_session(self, session_id: str) -> Optional[Session]:
        """
        获取会话

        Args:
            session_id: 会话ID

        Returns:
            会话对象或None
        """
        async with self._lock:
            session = self._sessions.get(session_id)

            if session and session.is_expired():
                await self.delete_session(session_id)
                return None

            return session

    async def get_session_by_device(self, device_id: str) -> Optional[Session]:
        """
        通过设备ID获取会话

        Args:
            device_id: 设备ID

        Returns:
            会话对象或None
        """
        async with self._lock:
            session_id = self._device_sessions.get(device_id)
            if not session_id:
                return None

            return await self.get_session(session_id)

    async def delete_session(self, session_id: str) -> bool:
        """
        删除会话

        Args:
            session_id: 会话ID

        Returns:
            是否删除成功
        """
        async with self._lock:
            session = self._sessions.pop(session_id, None)

            if session:
                self._device_sessions.pop(session.device_id, None)

                if self._redis_session_manager:
                    await self._redis_session_manager.delete_session(session_id)

                logger.info(f"Session deleted: {session_id}")
                return True

            return False

    async def update_session(self, session_id: str) -> bool:
        """
        更新会话（心跳）

        Args:
            session_id: 会话ID

        Returns:
            是否更新成功
        """
        session = await self.get_session(session_id)
        if not session:
            return False

        session.touch()

        # 更新Redis中的会话
        if self._redis_session_manager:
            await self._redis_session_manager.update_session_ttl(session_id)

        return True

    async def validate_session(self, session_id: str, device_id: str) -> bool:
        """
        验证会话是否有效

        Args:
            session_id: 会话ID
            device_id: 设备ID

        Returns:
            会话是否有效
        """
        session = await self.get_session(session_id)
        if not session:
            return False

        if session.device_id != device_id:
            logger.warning(
                f"Session device mismatch: {session.device_id} != {device_id}"
            )
            return False

        return session.is_valid

    async def cleanup_expired(self) -> int:
        """
        清理过期会话

        Returns:
            清理的会话数
        """
        async with self._lock:
            expired_ids = [
                sid
                for sid, session in self._sessions.items()
                if session.is_expired()
            ]

            for sid in expired_ids:
                session = self._sessions.pop(sid, None)
                if session:
                    self._device_sessions.pop(session.device_id, None)

                    if self._redis_session_manager:
                        await self._redis_session_manager.delete_session(sid)

            if expired_ids:
                logger.info(f"Cleaned up {len(expired_ids)} expired sessions")

            return len(expired_ids)

    def get_stats(self) -> dict:
        """获取会话统计"""
        return {
            "total_sessions": len(self._sessions),
            "unique_devices": len(self._device_sessions),
        }


# 全局TCP会话管理器实例
tcp_session_manager = TCPSessionManager()
