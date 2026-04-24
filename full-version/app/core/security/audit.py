# -*- coding: utf-8 -*-
"""
安全审计日志模块
记录所有安全相关事件
"""

from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

from app.core.logger import security_logger


class SecurityEventType(Enum):
    """安全事件类型"""

    # 认证事件
    AUTH_SUCCESS = "auth_success"
    AUTH_FAILURE = "auth_failure"
    AUTH_LOCKED = "auth_locked"

    # 连接事件
    TCP_CONNECT = "tcp_connect"
    TCP_DISCONNECT = "tcp_disconnect"
    UDP_PACKET_RECEIVED = "udp_packet_received"

    # 会话事件
    SESSION_CREATED = "session_created"
    SESSION_EXPIRED = "session_expired"
    SESSION_INVALID = "session_invalid"

    # 命令事件
    COMMAND_SENT = "command_sent"
    COMMAND_RESPONSE_RECEIVED = "command_response_received"

    # 安全事件
    CHECKSUM_FAILED = "checksum_failed"
    NONCE_REPLAY = "nonce_replay"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"

    # 报警事件
    ALARM_TRIGGERED = "alarm_triggered"
    ALARM_PUSHED = "alarm_pushed"


class SecurityAuditor:
    """安全审计器"""

    def __init__(self):
        """初始化安全审计器"""
        self._enabled = True

    def start(self) -> None:
        """启动审计器"""
        self._enabled = True
        security_logger.info("Security auditor started")

    def stop(self) -> None:
        """停止审计器"""
        self._enabled = False
        security_logger.info("Security auditor stopped")

    def log_event(
        self,
        event_type: SecurityEventType,
        device_id: Optional[str] = None,
        session_id: Optional[str] = None,
        extra_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        记录安全事件

        Args:
            event_type: 事件类型
            device_id: 设备ID
            session_id: 会话ID
            extra_data: 附加数据
        """
        if not self._enabled:
            return

        log_data = {
            "event_type": event_type.value,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        if device_id:
            log_data["device_id"] = device_id

        if session_id:
            log_data["session_id"] = session_id

        if extra_data:
            log_data.update(extra_data)

        security_logger.info(
            f"Security event: {event_type.value}",
            extra=log_data,
        )

    def log_auth_success(
        self,
        device_id: str,
        session_id: str,
        fingerprint: str,
    ) -> None:
        """记录认证成功"""
        self.log_event(
            SecurityEventType.AUTH_SUCCESS,
            device_id=device_id,
            session_id=session_id,
            extra_data={"fingerprint": fingerprint},
        )

    def log_auth_failure(
        self,
        device_id: str,
        reason: str,
        failure_count: int,
    ) -> None:
        """记录认证失败"""
        self.log_event(
            SecurityEventType.AUTH_FAILURE,
            device_id=device_id,
            extra_data={
                "reason": reason,
                "failure_count": failure_count,
            },
        )

    def log_session_created(
        self,
        device_id: str,
        session_id: str,
    ) -> None:
        """记录会话创建"""
        self.log_event(
            SecurityEventType.SESSION_CREATED,
            device_id=device_id,
            session_id=session_id,
        )

    def log_session_expired(
        self,
        device_id: str,
        session_id: str,
    ) -> None:
        """记录会话过期"""
        self.log_event(
            SecurityEventType.SESSION_EXPIRED,
            device_id=device_id,
            session_id=session_id,
        )

    def log_checksum_failed(
        self,
        device_id: str,
        expected: str,
        received: str,
    ) -> None:
        """记录校验失败"""
        self.log_event(
            SecurityEventType.CHECKSUM_FAILED,
            device_id=device_id,
            extra_data={
                "expected": expected,
                "received": received,
            },
        )

    def log_alarm_triggered(
        self,
        device_id: str,
        alarm_type: int,
        alarm_level: int,
    ) -> None:
        """记录报警触发"""
        self.log_event(
            SecurityEventType.ALARM_TRIGGERED,
            device_id=device_id,
            extra_data={
                "alarm_type": alarm_type,
                "alarm_level": alarm_level,
            },
        )


# 全局安全审计器实例
security_auditor = SecurityAuditor()
