# -*- coding: utf-8 -*-
"""
连接管理模块
"""

import asyncio
from typing import Optional, Dict, Set
from dataclasses import dataclass, field
from datetime import datetime
import uuid

from app.core.logger import logger


@dataclass
class Connection:
    """连接对象"""

    conn_id: str
    device_id: Optional[str] = None
    session_id: Optional[str] = None
    remote_addr: tuple = ("", 0)
    protocol: str = "tcp"  # tcp or udp
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_active: datetime = field(default_factory=datetime.utcnow)
    is_authenticated: bool = False
    metadata: Dict = field(default_factory=dict)

    def update_activity(self) -> None:
        """更新最后活跃时间"""
        self.last_active = datetime.utcnow()

    def is_expired(self, timeout: int = 300) -> bool:
        """
        检查是否过期

        Args:
            timeout: 超时时间(秒)

        Returns:
            是否过期
        """
        delta = datetime.utcnow() - self.last_active
        return delta.total_seconds() > timeout


class ConnectionManager:
    """连接管理器"""

    def __init__(self):
        """初始化连接管理器"""
        self._connections: Dict[str, Connection] = {}
        self._device_connections: Dict[str, Set[str]] = {}  # device_id -> set of conn_ids
        self._lock = asyncio.Lock()

    async def add_connection(self, conn: Connection) -> None:
        """
        添加连接

        Args:
            conn: 连接对象
        """
        async with self._lock:
            self._connections[conn.conn_id] = conn

            if conn.device_id:
                if conn.device_id not in self._device_connections:
                    self._device_connections[conn.device_id] = set()
                self._device_connections[conn.device_id].add(conn.conn_id)

        logger.debug(f"Connection added: {conn.conn_id}, device: {conn.device_id}")

    async def remove_connection(self, conn_id: str) -> None:
        """
        移除连接

        Args:
            conn_id: 连接ID
        """
        async with self._lock:
            conn = self._connections.pop(conn_id, None)

            if conn and conn.device_id:
                device_conns = self._device_connections.get(conn.device_id)
                if device_conns:
                    device_conns.discard(conn_id)
                    if not device_conns:
                        self._device_connections.pop(conn.device_id, None)

        if conn:
            logger.debug(f"Connection removed: {conn_id}, device: {conn.device_id}")

    async def get_connection(self, conn_id: str) -> Optional[Connection]:
        """获取连接"""
        return self._connections.get(conn_id)

    async def get_device_connections(self, device_id: str) -> Set[str]:
        """获取设备的所有连接"""
        async with self._lock:
            return self._device_connections.get(device_id, set()).copy()

    async def get_all_connections(self) -> Dict[str, Connection]:
        """获取所有连接"""
        async with self._lock:
            return self._connections.copy()

    async def cleanup_expired(self, timeout: int = 300) -> int:
        """
        清理过期连接

        Args:
            timeout: 超时时间(秒)

        Returns:
            清理的连接数
        """
        async with self._lock:
            expired_ids = [
                conn_id
                for conn_id, conn in self._connections.items()
                if conn.is_expired(timeout)
            ]

            for conn_id in expired_ids:
                conn = self._connections.pop(conn_id, None)
                if conn and conn.device_id:
                    device_conns = self._device_connections.get(conn.device_id)
                    if device_conns:
                        device_conns.discard(conn_id)

        if expired_ids:
            logger.info(f"Cleaned up {len(expired_ids)} expired connections")

        return len(expired_ids)

    async def update_connection_device(
        self,
        conn_id: str,
        device_id: str,
        session_id: Optional[str] = None,
    ) -> None:
        """
        更新连接的设备信息

        Args:
            conn_id: 连接ID
            device_id: 设备ID
            session_id: 会话ID
        """
        async with self._lock:
            conn = self._connections.get(conn_id)
            if conn:
                # 从旧的设备连接集合中移除
                if conn.device_id and conn.device_id != device_id:
                    old_device_conns = self._device_connections.get(conn.device_id)
                    if old_device_conns:
                        old_device_conns.discard(conn_id)

                # 更新连接信息
                conn.device_id = device_id
                conn.session_id = session_id
                conn.is_authenticated = True
                conn.update_activity()

                # 添加到新的设备连接集合
                if device_id not in self._device_connections:
                    self._device_connections[device_id] = set()
                self._device_connections[device_id].add(conn_id)

    def get_stats(self) -> dict:
        """
        获取连接统计

        Returns:
            统计信息字典
        """
        return {
            "total_connections": len(self._connections),
            "unique_devices": len(self._device_connections),
            "connections_per_device": {
                device_id: len(conns)
                for device_id, conns in self._device_connections.items()
            },
        }


# 全局连接管理器实例
connection_manager = ConnectionManager()
