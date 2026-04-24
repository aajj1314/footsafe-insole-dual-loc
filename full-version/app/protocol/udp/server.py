# -*- coding: utf-8 -*-
"""
UDP服务器模块
"""

import asyncio
from typing import Optional

from app.config.settings import settings
from app.config.limits import UDP_PORT
from app.core.logger import logger
from app.core.security.audit import SecurityAuditor
from app.protocol.udp.handler import udp_handler
from app.protocol.udp.sender import UDPSender


class UDPServer:
    """UDP服务器"""

    def __init__(
        self,
        host: str = None,
        port: int = None,
        security_auditor: Optional[SecurityAuditor] = None,
    ):
        """
        初始化UDP服务器

        Args:
            host: 监听地址
            port: 监听端口
            security_auditor: 安全审计器
        """
        self.host = host or settings.HOST
        self.port = port or UDP_PORT
        self.security_auditor = security_auditor

        self._sock: Optional[tuple] = None
        self._running = False
        self.sender: Optional[UDPSender] = None
        self._transport: Optional[asyncio.DatagramTransport] = None

    async def start(self) -> None:
        """启动UDP服务器"""
        if self._running:
            return

        # 获取事件循环并创建UDP socket
        loop = asyncio.get_running_loop()
        self._transport, _ = await loop.create_datagram_endpoint(
            lambda: UDPServerProtocol(self),
            local_addr=(self.host, self.port),
        )
        self._sock = (self._transport, None)

        self._running = True
        logger.info(f"UDP server started on {self.host}:{self.port}")

    async def stop(self) -> None:
        """停止UDP服务器"""
        if not self._running:
            return

        self._running = False

        if self._sock:
            self._sock[1].close()
            self._sock = None

        logger.info(f"UDP server stopped on {self.host}:{self.port}")

    async def handle_packet(self, data: bytes, addr: tuple) -> None:
        """
        处理接收到的数据包

        Args:
            data: 数据包
            addr: 来源地址
        """
        from app.protocol.parser import MessageParser
        from app.services.location_service import handle_location
        from app.services.alarm_service import handle_alarm
        from app.services.device_service import handle_heartbeat
        from app.services.command_service import handle_command_response

        try:
            parser = MessageParser()
            message = parser.parse(data)

            if not message:
                return

            msg_type = message.get("type")

            # 路由到对应处理器
            if msg_type == MESSAGE_TYPE_LOCATION:
                await handle_location(message, addr)
            elif msg_type == MESSAGE_TYPE_ALARM:
                await handle_alarm(message, addr)
            elif msg_type == MESSAGE_TYPE_HEARTBEAT:
                await handle_heartbeat(message, addr)
            elif msg_type == MESSAGE_TYPE_COMMAND_RESPONSE:
                await handle_command_response(message, addr)
            else:
                logger.warning(f"Unknown UDP message type: {msg_type}")

            # 记录安全审计日志
            if self.security_auditor:
                self.security_auditor.log_event(
                    "udp_packet_received",
                    device_id=message.get("device_id"),
                    extra_data={"type": msg_type, "addr": addr},
                )

        except Exception as e:
            logger.error(f"Error handling UDP packet: {e}")

    @property
    def is_running(self) -> bool:
        """检查服务器是否运行"""
        return self._running


class UDPServerProtocol(asyncio.DatagramProtocol):
    """UDP服务器协议"""

    def __init__(self, server: UDPServer):
        """初始化协议"""
        self.server = server
        self._transport: Optional[asyncio.DatagramTransport] = None

    def connection_made(self, transport: asyncio.DatagramTransport) -> None:
        """连接建立"""
        self._transport = transport

    def datagram_received(self, data: bytes, addr: tuple) -> None:
        """数据接收"""
        asyncio.create_task(self.server.handle_packet(data, addr))

    def error_received(self, exc: Exception) -> None:
        """错误接收"""
        logger.error(f"UDP error received: {exc}")

    def connection_lost(self, exc: Optional[Exception]) -> None:
        """连接丢失"""
        logger.info(f"UDP connection lost: {exc}")
