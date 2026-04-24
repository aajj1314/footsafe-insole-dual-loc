# -*- coding: utf-8 -*-
"""
TCP服务器模块
"""

import asyncio
from typing import Optional

from app.config.settings import settings
from app.config.limits import TCP_PORT, TCP_MAX_CONNECTIONS
from app.core.logger import logger
from app.core.security.audit import SecurityAuditor
from app.protocol.tcp.connection import tcp_connection_manager, TCPConnection
from app.protocol.tcp.session import tcp_session_manager
from app.protocol.tcp.sender import TCPSender


class TCPServer:
    """TCP服务器"""

    def __init__(
        self,
        host: str = None,
        port: int = None,
        security_auditor: Optional[SecurityAuditor] = None,
    ):
        """
        初始化TCP服务器

        Args:
            host: 监听地址
            port: 监听端口
            security_auditor: 安全审计器
        """
        self.host = host or settings.HOST
        self.port = port or TCP_PORT
        self.security_auditor = security_auditor

        self._server: Optional[asyncio.Server] = None
        self._running = False
        self.sender: Optional[TCPSender] = None

    async def start(self) -> None:
        """启动TCP服务器"""
        if self._running:
            return

        # 创建TCP服务器
        self._server = await asyncio.start_server(
            self.handle_client,
            self.host,
            self.port,
            limit=TCP_MAX_CONNECTIONS,
        )

        self._running = True

        # 初始化发送器
        self.sender = TCPSender(tcp_connection_manager)

        # 获取服务器地址
        addr = self._server.sockets[0].getsockname()
        logger.info(f"TCP server started on {addr[0]}:{addr[1]}")

    async def stop(self) -> None:
        """停止TCP服务器"""
        if not self._running:
            return

        self._running = False

        if self._server:
            self._server.close()
            await self._server.wait_closed()
            self._server = None

        logger.info(f"TCP server stopped on {self.host}:{self.port}")

    async def handle_client(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ) -> None:
        """
        处理客户端连接

        Args:
            reader: 流读取器
            writer: 流写入器
        """
        # 创建连接对象
        conn = TCPConnection(reader, writer)
        await tcp_connection_manager.add_connection(conn)

        logger.info(f"TCP client connected: {conn.conn_id} from {conn.remote_addr}")

        # 记录安全审计日志
        if self.security_auditor:
            self.security_auditor.log_event(
                "tcp_connect",
                extra_data={"conn_id": conn.conn_id, "addr": conn.remote_addr},
            )

        try:
            # 处理连接
            await self.process_connection(conn)

        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error processing TCP connection: {e}")
        finally:
            # 清理连接
            await tcp_connection_manager.remove_connection(conn.conn_id)

            # 记录安全审计日志
            if self.security_auditor:
                self.security_auditor.log_event(
                    "tcp_disconnect",
                    device_id=conn.device_id,
                    extra_data={"conn_id": conn.conn_id},
                )

            logger.info(f"TCP client disconnected: {conn.conn_id}")

    async def process_connection(self, conn: TCPConnection) -> None:
        """
        处理连接数据

        Args:
            conn: TCP连接对象
        """
        while not conn.is_closed() and self._running:
            try:
                # 读取数据
                data = await conn.recv(settings.MAX_TCP_PACKET_SIZE)

                if not data:
                    break

                # 处理数据
                await self.handle_packet(conn, data)

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error in connection loop: {e}")
                break

    async def handle_packet(self, conn: TCPConnection, data: bytes) -> None:
        """
        处理数据包

        Args:
            conn: TCP连接对象
            data: 数据包
        """
        from app.protocol.parser import MessageParser
        from app.services.device_service import handle_auth, handle_tcp_heartbeat
        from app.services.command_service import handle_command_response
        from app.services.ota_service import handle_ota_progress
        from app.services.batch_service import handle_batch_report
        from app.services.error_service import handle_device_error
        from app.config.constants import (
            MESSAGE_TYPE_AUTH,
            MESSAGE_TYPE_TCP_HEARTBEAT,
            MESSAGE_TYPE_COMMAND_RESPONSE,
            MESSAGE_TYPE_OTA_PROGRESS,
            MESSAGE_TYPE_BATCH_REPORT,
            MESSAGE_TYPE_DEVICE_ERROR,
        )

        try:
            parser = MessageParser()
            message = parser.parse(data)

            if not message:
                return

            msg_type = message.get("type")
            device_id = message.get("device_id")

            # 更新连接设备信息（如果已认证）
            if conn.is_authenticated and device_id:
                await tcp_connection_manager.update_device_connection(
                    conn.conn_id, device_id, conn.session_id
                )

            # 路由到对应处理器
            if msg_type == MESSAGE_TYPE_AUTH:
                response = await handle_auth(message, conn)
                if response:
                    await conn.send(response)
            elif msg_type == MESSAGE_TYPE_TCP_HEARTBEAT:
                response = await handle_tcp_heartbeat(message, conn)
                if response:
                    await conn.send(response)
            elif msg_type == MESSAGE_TYPE_COMMAND_RESPONSE:
                await handle_command_response(message, conn)
            elif msg_type == MESSAGE_TYPE_OTA_PROGRESS:
                await handle_ota_progress(message, conn)
            elif msg_type == MESSAGE_TYPE_BATCH_REPORT:
                response = await handle_batch_report(message, conn)
                if response:
                    await conn.send(response)
            elif msg_type == MESSAGE_TYPE_DEVICE_ERROR:
                await handle_device_error(message, conn)
            else:
                logger.warning(f"Unknown TCP message type: {msg_type}")

        except Exception as e:
            logger.error(f"Error handling TCP packet: {e}")

    @property
    def is_running(self) -> bool:
        """检查服务器是否运行"""
        return self._running
