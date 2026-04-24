# -*- coding: utf-8 -*-
"""
安全服务模块
"""

import asyncio
from typing import Optional, Dict, Any
from datetime import datetime

from app.core.logger import logger, security_logger
from app.core.database.mysql import mysql_pool
from app.config.settings import settings
from app.config.constants import (
    ERROR_SUCCESS,
    ERROR_DEVICE_NOT_REGISTERED,
    ERROR_CHECKSUM_FAILED,
    ERROR_SESSION_INVALID,
)


class SecurityService:
    """安全服务"""

    async def authenticate(
        self,
        device_id: str,
        iccid: str,
        firmware_version: str,
        hardware_version: str,
        fingerprint: str,
    ) -> tuple:
        """
        设备身份认证

        Args:
            device_id: 设备IMEI
            iccid: SIM卡ICCID
            firmware_version: 固件版本
            hardware_version: 硬件版本
            fingerprint: 设备指纹

        Returns:
            (错误码, 会话ID或错误信息)
        """
        from app.services.device_service import device_service
        from app.protocol.tcp.session import tcp_session_manager
        from app.protocol.tcp.connection import tcp_connection_manager

        # 检查设备是否注册
        device = await device_service.get_device(device_id)
        if not device:
            logger.warning(f"Device not registered: {device_id}")
            return ERROR_DEVICE_NOT_REGISTERED, "device_not_registered"

        # 检查设备是否被锁定
        if device.get("locked"):
            logger.warning(f"Device is locked: {device_id}")
            return 3002, "device_locked"

        # 验证指纹
        if settings.DEVICE_FINGERPRINT_ENABLED:
            from app.core.security.fingerprint import generate_fingerprint
            expected_fingerprint = generate_fingerprint(
                device_id,
                iccid or device.get("iccid", ""),
                firmware_version,
                hardware_version,
            )

            if fingerprint != expected_fingerprint and device.get("fingerprint"):
                logger.warning(f"Fingerprint mismatch: {device_id}")
                return 3003, "signature_invalid"

        # 创建会话
        session = await tcp_session_manager.create_session(device_id)

        # 更新设备信息
        await device_service.update_device(
            device_id,
            {
                "iccid": iccid,
                "firmware_version": firmware_version,
                "hardware_version": hardware_version,
                "fingerprint": fingerprint,
                "session_id": session.session_id,
                "status": "online",
                "last_seen": datetime.utcnow(),
            },
        )

        logger.info(f"Device authenticated: {device_id}, session: {session.session_id}")

        return ERROR_SUCCESS, session.session_id

    async def record_auth_failure(self, device_id: str) -> None:
        """
        记录认证失败

        Args:
            device_id: 设备IMEI
        """
        from app.services.device_service import device_service

        device = await device_service.get_device(device_id)
        if not device:
            return

        failure_count = (device.get("auth_failures") or 0) + 1

        # 如果失败次数超过阈值，锁定设备
        if failure_count >= settings.MAX_AUTH_FAILURES:
            await device_service.update_device(
                device_id,
                {
                    "locked": True,
                    "lock_until": datetime.utcnow(),
                    "auth_failures": failure_count,
                },
            )
            logger.warning(f"Device locked due to auth failures: {device_id}")
        else:
            await device_service.update_device(
                device_id,
                {"auth_failures": failure_count},
            )

    async def clear_auth_failures(self, device_id: str) -> None:
        """
        清除认证失败记录

        Args:
            device_id: 设备IMEI
        """
        from app.services.device_service import device_service

        await device_service.update_device(
            device_id,
            {"auth_failures": 0},
        )


# 全局安全服务实例
security_service = SecurityService()


# ==================== 消息处理器 ====================


async def handle_auth(message: Dict[str, Any], conn) -> bytes:
    """
    处理认证消息

    Args:
        message: 消息字典
        conn: TCP连接对象

    Returns:
        响应字节
    """
    from app.core.security.checksum import verify_checksum
    from app.core.security.nonce import nonce_manager
    from app.protocol.serializer import ResponseSerializer
    from app.protocol.tcp.session import tcp_session_manager
    from app.config.settings import settings
    from app.config.limits import TCP_HEARTBEAT_INTERVAL
    from app.core.security.audit import security_auditor

    device_id = message.get("device_id")
    data = message.get("data", {})

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
        await security_service.record_auth_failure(device_id)
        security_auditor.log_auth_failure(device_id, "checksum_failed", 0)
        return ResponseSerializer.serialize_error(1002, "checksum_failed")

    # 执行认证
    code, result = await security_service.authenticate(
        device_id=device_id,
        iccid=data.get("iccid"),
        firmware_version=data.get("firmware_version"),
        hardware_version=data.get("hardware_version"),
        fingerprint=data.get("fingerprint"),
    )

    if code != ERROR_SUCCESS:
        security_auditor.log_auth_failure(device_id, result, 0)
        return ResponseSerializer.serialize_error(code, result)

    session_id = result

    # 更新连接信息
    conn.device_id = device_id
    conn.session_id = session_id
    conn.is_authenticated = True
    await tcp_connection_manager.update_device_connection(conn.conn_id, device_id, session_id)

    # 记录安全审计
    security_auditor.log_auth_success(device_id, session_id, data.get("fingerprint"))

    logger.info(f"Auth success for device: {device_id}")

    return ResponseSerializer.serialize_auth_response(
        session_id=session_id,
        heartbeat_interval=TCP_HEARTBEAT_INTERVAL,
        key_version=1,
    )
