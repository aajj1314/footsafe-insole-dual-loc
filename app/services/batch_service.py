# -*- coding: utf-8 -*-
"""
批量上报服务模块
"""

from typing import Dict, Any, List
from datetime import datetime

from app.core.logger import logger
from app.protocol.serializer import ResponseSerializer
from app.config.limits import MAX_BATCH_SIZE


class BatchService:
    """批量上报服务"""

    async def process_batch(
        self,
        device_id: str,
        items: List[Dict[str, Any]],
    ) -> tuple:
        """
        处理批量数据

        Args:
            device_id: 设备IMEI
            items: 数据项列表

        Returns:
            (成功数量, 失败索引列表)
        """
        success_count = 0
        failed_indexes = []

        for i, item in enumerate(items):
            try:
                item_type = item.get("type")
                item_data = item.get("data", {})

                if item_type == "location":
                    await self._process_location_item(device_id, item_data)
                    success_count += 1
                elif item_type == "heartbeat":
                    await self._process_heartbeat_item(device_id, item_data)
                    success_count += 1
                elif item_type == "alarm":
                    await self._process_alarm_item(device_id, item_data)
                    success_count += 1
                else:
                    logger.warning(f"Unknown batch item type: {item_type}")
                    failed_indexes.append(i)

            except Exception as e:
                logger.error(f"Failed to process batch item {i}: {e}")
                failed_indexes.append(i)

        return success_count, failed_indexes

    async def _process_location_item(
        self,
        device_id: str,
        data: Dict[str, Any],
    ) -> None:
        """处理位置数据项"""
        from app.services.location_service import location_service

        await location_service.save_location(
            device_id=device_id,
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
            altitude=data.get("altitude"),
            speed=data.get("speed"),
            direction=data.get("direction"),
            accuracy=data.get("accuracy"),
            satellites=data.get("satellites"),
            battery=data.get("battery"),
            signal_strength=data.get("signal_strength"),
            charging=data.get("charging"),
            mode=data.get("mode"),
            gps_timestamp=data.get("gps_timestamp"),
        )

    async def _process_heartbeat_item(
        self,
        device_id: str,
        data: Dict[str, Any],
    ) -> None:
        """处理心跳数据项"""
        from app.services.device_service import device_service

        await device_service.update_device(
            device_id,
            {
                "battery": data.get("battery"),
                "signal_strength": data.get("signal_strength"),
                "status": "online",
                "last_seen": datetime.utcnow(),
            },
        )

    async def _process_alarm_item(
        self,
        device_id: str,
        data: Dict[str, Any],
    ) -> None:
        """处理报警数据项"""
        from app.services.alarm_service import alarm_service

        alarm_type = data.get("alarm_type")
        alarm_level = data.get("alarm_level", alarm_service.get_alarm_level(alarm_type))

        alarm_id = await alarm_service.create_alarm(
            device_id=device_id,
            alarm_type=alarm_type,
            alarm_level=alarm_level,
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
            accuracy=data.get("accuracy"),
            battery=data.get("battery"),
            alarm_data=data.get("alarm_data"),
        )

        if alarm_id:
            # 推送报警
            from app.services.push_service import push_service
            await push_service.push_alarm(device_id, alarm_id, data, alarm_type, alarm_level)


# 全局批量服务实例
batch_service = BatchService()


# ==================== 消息处理器 ====================


async def handle_batch_report(message: Dict[str, Any], conn) -> bytes:
    """
    处理批量上报消息

    Args:
        message: 消息字典
        conn: TCP连接对象

    Returns:
        响应字节
    """
    from app.core.security.checksum import verify_checksum
    from app.core.security.nonce import nonce_manager
    from app.protocol.validator import message_validator
    from app.config.settings import settings
    from app.config.constants import ERROR_SUCCESS

    device_id = message.get("device_id")
    session_id = message.get("session_id")
    data = message.get("data", {})

    # 验证session_id
    from app.protocol.tcp.session import tcp_session_manager
    if not await tcp_session_manager.validate_session(session_id, device_id):
        logger.warning(f"Invalid session for device: {device_id}")
        return ResponseSerializer.serialize_error(3001, "session_invalid")

    # 验证nonce
    nonce = message.get("nonce")
    timestamp = message.get("timestamp")
    if not await nonce_manager.is_nonce_valid(nonce, timestamp):
        logger.warning(f"Invalid nonce for device: {device_id}")
        return ResponseSerializer.serialize_error(1002, "checksum_failed")

    # 验证校验和
    checksum = message.get("checksum")
    if not verify_checksum(
        message["version"],
        device_id,
        timestamp,
        nonce,
        data,
        checksum,
        settings.DEVICE_PRESHARED_KEY,
    ):
        logger.warning(f"Checksum failed for device: {device_id}")
        return ResponseSerializer.serialize_error(1002, "checksum_failed")

    total = data.get("total", 0)
    index = data.get("index", 1)
    items = data.get("items", [])

    # 检查批量大小
    if total > MAX_BATCH_SIZE:
        logger.warning(f"Batch size too large: {total}, max: {MAX_BATCH_SIZE}")
        return ResponseSerializer.serialize_error(1003, "parameter_error")

    # 处理批量数据
    success_count, failed_indexes = await batch_service.process_batch(device_id, items)

    logger.info(
        f"Batch report processed: device={device_id}, "
        f"total={total}, index={index}, success={success_count}"
    )

    return ResponseSerializer.serialize_batch_response(success_count, failed_indexes)
