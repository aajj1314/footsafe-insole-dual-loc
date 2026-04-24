# -*- coding: utf-8 -*-
"""
TCP连接管理模块
"""

import asyncio
from typing import Optional, Dict
from datetime import datetime
import uuid

from app.core.logger import logger


class TCPConnection:
    """TCP连接对象"""

    def __init__(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
        conn_id: Optional[str] = None,
    ):
        """
        初始化TCP连接

        Args:
            reader: 流读取器
            writer: 流写入器
            conn_id: 连接ID
        """
        self.conn_id = conn_id or str(uuid.uuid4())
        self.reader = reader
        self.writer = writer
        self.device_id: Optional[str] = None
        self.session_id: Optional[str] = None
        self.remote_addr = writer.get_extra_info("peername")
        self.created_at = datetime.utcnow()
        self.last_active = datetime.utcnow()
        self.is_authenticated = False

    def update_activity(self) -> None:
        """更新最后活跃时间"""
        self.last_active = datetime.utcnow()

    async def send(self, data: bytes) -> int:
        """
        发送数据

        Args:
            data: 待发送数据

        Returns:
            发送字节数
        """
        self.writer.write(data)
        await self.writer.drain()
        self.update_activity()
        return len(data)

    async def recv(self, max_size: int = 1024) -> bytes:
        """
        接收数据

        Args:
            max_size: 最大接收字节数

        Returns:
            接收的数据
        """
        data = await self.reader.read(max_size)
        self.update_activity()
        return data

    def close(self) -> None:
        """关闭连接"""
        self.writer.close()
        try:
            self.writer.wait_closed()
        except Exception:
            pass

    def is_closed(self) -> bool:
        """检查连接是否已关闭"""
        return self.writer.is_closing()


class TCPConnectionManager:
    """TCP连接管理器"""

    def __init__(self):
        """初始化连接管理器"""
        self._connections: Dict[str, TCPConnection] = {}
        self._device_connections: Dict[str, str] = {}  # device_id -> conn_id
        self._lock = asyncio.Lock()

    async def add_connection(self, conn: TCPConnection) -> None:
        """
        添加连接

        Args:
            conn: TCP连接对象
        """
        async with self._lock:
            self._connections[conn.conn_id] = conn

            if conn.device_id:
                self._device_connections[conn.device_id] = conn.conn_id

        logger.debug(f"TCP connection added: {conn.conn_id}, device: {conn.device_id}")

    async def remove_connection(self, conn_id: str) -> None:
        """
        移除连接

        Args:
            conn_id: 连接ID
        """
        async with self._lock:
            conn = self._connections.pop(conn_id, None)

            if conn and conn.device_id:
                self._device_connections.pop(conn.device_id, None)

            if conn:
                logger.debug(f"TCP connection removed: {conn_id}")
                conn.close()

    async def get_connection(self, conn_id: str) -> Optional[TCPConnection]:
        """获取连接"""
        return self._connections.get(conn_id)

    async def get_connection_by_device(self, device_id: str) -> Optional[TCPConnection]:
        """通过设备ID获取连接"""
        async with self._lock:
            conn_id = self._device_connections.get(device_id)
            if conn_id:
                return self._connections.get(conn_id)
            return None

    async def update_device_connection(
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
            if not conn:
                return

            # 从旧设备连接映射中移除
            if conn.device_id and conn.device_id != device_id:
                self._device_connections.pop(conn.device_id, None)

            # 更新连接信息
            conn.device_id = device_id
            conn.session_id = session_id
            conn.is_authenticated = True

            # 添加到新设备连接映射
            self._device_connections[device_id] = conn_id

    async def get_all_connections(self) -> Dict[str, TCPConnection]:
        """获取所有连接"""
        async with self._lock:
            return self._connections.copy()

    async def cleanup_closed(self) -> int:
        """
        清理已关闭的连接

        Returns:
            清理的连接数
        """
        async with self._lock:
            closed_ids = [
                conn_id
                for conn_id, conn in self._connections.items()
                if conn.is_closed()
            ]

            for conn_id in closed_ids:
                conn = self._connections.pop(conn_id, None)
                if conn:
                    if conn.device_id:
                        self._device_connections.pop(conn.device_id, None)
                    conn.close()

            if closed_ids:
                logger.info(f"Cleaned up {len(closed_ids)} closed TCP connections")

            return len(closed_ids)

    def get_stats(self) -> dict:
        """获取连接统计"""
        return {
            "total_connections": len(self._connections),
            "unique_devices": len(self._device_connections),
        }


# 全局TCP连接管理器实例
tcp_connection_manager = TCPConnectionManager()
