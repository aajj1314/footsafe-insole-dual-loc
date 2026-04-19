# -*- coding: utf-8 -*-
"""
推送服务模块
"""

import asyncio
import json
from typing import Dict, Any, Optional, Set

from app.core.logger import logger
from app.core.database.redis import redis_pool


class PushService:
    """推送服务"""

    # WebSocket连接管理
    _ws_connections: Dict[str, Set] = {}  # device_id -> set of websocket connections

    async def push_location(
        self,
        device_id: str,
        location_data: Dict[str, Any],
    ) -> None:
        """
        推送位置给用户

        Args:
            device_id: 设备IMEI
            location_data: 位置数据
        """
        try:
            # 查找设备绑定的用户
            # TODO: 从数据库获取绑定的用户列表

            # 构建推送消息
            message = {
                "type": "location",
                "device_id": device_id,
                "data": location_data,
            }

            # 发布到Redis频道
            channel = f"push:location:{device_id}"
            await redis_pool.publish(channel, json.dumps(message))

            logger.debug(f"Location push published: device={device_id}")

        except Exception as e:
            logger.error(f"Failed to push location: {e}")

    async def push_alarm(
        self,
        device_id: str,
        alarm_id: str,
        alarm_data: Dict[str, Any],
        alarm_type: int,
        alarm_level: int,
    ) -> None:
        """
        推送报警给用户

        Args:
            device_id: 设备IMEI
            alarm_id: 报警ID
            alarm_data: 报警数据
            alarm_type: 报警类型
            alarm_level: 报警级别
        """
        try:
            # 查找设备绑定的用户和监护人
            # TODO: 从数据库获取绑定的用户和监护人列表

            # 构建推送消息
            message = {
                "type": "alarm",
                "device_id": device_id,
                "alarm_id": alarm_id,
                "alarm_type": alarm_type,
                "alarm_level": alarm_level,
                "data": alarm_data,
            }

            # 发布到Redis频道
            channel = f"push:alarm:{device_id}"
            await redis_pool.publish(channel, json.dumps(message))

            logger.info(
                f"Alarm push published: device={device_id}, "
                f"alarm_id={alarm_id}, type={alarm_type}, level={alarm_level}"
            )

        except Exception as e:
            logger.error(f"Failed to push alarm: {e}")

    async def push_command(
        self,
        device_id: str,
        command_id: str,
        command_type: str,
        command_data: Dict[str, Any],
    ) -> None:
        """
        推送命令给设备（通过WebSocket）

        Args:
            device_id: 设备IMEI
            command_id: 命令ID
            command_type: 命令类型
            command_data: 命令数据
        """
        try:
            message = {
                "type": "command",
                "command_id": command_id,
                "command_type": command_type,
                "data": command_data,
            }

            # 发布到Redis频道
            channel = f"push:command:{device_id}"
            await redis_pool.publish(channel, json.dumps(message))

            logger.info(
                f"Command push published: device={device_id}, "
                f"command_id={command_id}, type={command_type}"
            )

        except Exception as e:
            logger.error(f"Failed to push command: {e}")

    @classmethod
    def register_websocket(
        cls,
        device_id: str,
        websocket,
    ) -> None:
        """
        注册WebSocket连接

        Args:
            device_id: 设备IMEI
            websocket: WebSocket连接
        """
        if device_id not in cls._ws_connections:
            cls._ws_connections[device_id] = set()
        cls._ws_connections[device_id].add(websocket)

    @classmethod
    def unregister_websocket(
        cls,
        device_id: str,
        websocket,
    ) -> None:
        """
        取消注册WebSocket连接

        Args:
            device_id: 设备IMEI
            websocket: WebSocket连接
        """
        if device_id in cls._ws_connections:
            cls._ws_connections[device_id].discard(websocket)
            if not cls._ws_connections[device_id]:
                del cls._ws_connections[device_id]

    @classmethod
    async def broadcast_to_device(
        cls,
        device_id: str,
        message: Dict[str, Any],
    ) -> None:
        """
        向设备绑定的WebSocket连接广播消息

        Args:
            device_id: 设备IMEI
            message: 消息
        """
        if device_id not in cls._ws_connections:
            return

        dead_connections = set()
        for ws in cls._ws_connections[device_id]:
            try:
                await ws.send_json(message)
            except Exception:
                dead_connections.add(ws)

        # 清理死连接
        for ws in dead_connections:
            cls.unregister_websocket(device_id, ws)


# 全局推送服务实例
push_service = PushService()
