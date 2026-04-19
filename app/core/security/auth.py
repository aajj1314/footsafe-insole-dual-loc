# -*- coding: utf-8 -*-
"""
设备身份认证模块
"""

import hashlib
from typing import Optional, Tuple
from datetime import datetime

from app.core.exceptions import DeviceNotRegisteredException, DeviceLockedException
from app.core.logger import security_logger


class DeviceAuthenticator:
    """设备身份认证器"""

    def __init__(self, device_registry: "DeviceRegistry"):
        """
        初始化认证器

        Args:
            device_registry: 设备注册表
        """
        self.device_registry = device_registry

    async def authenticate(
        self,
        device_id: str,
        iccid: str,
        firmware_version: str,
        hardware_version: str,
        fingerprint: str,
    ) -> Tuple[bool, Optional[dict]]:
        """
        验证设备身份

        Args:
            device_id: 设备IMEI
            iccid: SIM卡ICCID
            firmware_version: 固件版本
            hardware_version: 硬件版本
            fingerprint: 设备指纹

        Returns:
            (认证是否成功, 设备信息字典)
        """
        # 检查设备是否注册
        device = await self.device_registry.get_device(device_id)
        if not device:
            security_logger.warning(
                f"Authentication failed: device not registered",
                extra={"device_id": device_id},
            )
            raise DeviceNotRegisteredException(
                details={"device_id": device_id}
            )

        # 检查设备是否被锁定
        if device.get("locked", False):
            security_logger.warning(
                f"Authentication failed: device locked",
                extra={"device_id": device_id},
            )
            raise DeviceLockedException(
                details={"device_id": device_id}
            )

        # 验证设备指纹
        expected_fingerprint = self._generate_fingerprint(
            device_id,
            iccid or device.get("iccid", ""),
            firmware_version,
            hardware_version,
        )

        if fingerprint != expected_fingerprint:
            # 如果指纹不匹配，检查是否允许不验证指纹（首次注册）
            if not device.get("fingerprint"):
                # 首次注册，更新设备信息
                await self.device_registry.update_device(
                    device_id,
                    {
                        "iccid": iccid,
                        "firmware_version": firmware_version,
                        "hardware_version": hardware_version,
                        "fingerprint": fingerprint,
                    },
                )
            else:
                security_logger.warning(
                    f"Authentication failed: fingerprint mismatch",
                    extra={"device_id": device_id},
                )
                return False, None

        # 更新最后在线时间
        await self.device_registry.update_device(
            device_id,
            {
                "last_seen": datetime.utcnow().isoformat(),
                "status": "online",
            },
        )

        security_logger.info(
            f"Device authenticated successfully",
            extra={"device_id": device_id},
        )

        return True, device

    def _generate_fingerprint(
        self,
        device_id: str,
        iccid: str,
        firmware_version: str,
        hardware_version: str,
    ) -> str:
        """
        生成设备指纹

        指纹组成: SHA256(IMEI + ICCID + firmware_version + hardware_version)

        Args:
            device_id: 设备IMEI
            iccid: SIM卡ICCID
            firmware_version: 固件版本
            hardware_version: 硬件版本

        Returns:
            设备指纹字符串
        """
        concat = device_id + iccid + firmware_version + hardware_version
        return hashlib.sha256(concat.encode("utf-8")).hexdigest()

    async def record_auth_failure(self, device_id: str) -> int:
        """
        记录认证失败次数

        Args:
            device_id: 设备IMEI

        Returns:
            当前失败次数
        """
        count = await self.device_registry.increment_auth_failures(device_id)
        return count

    async def lock_device(self, device_id: str, duration: int = 3600) -> None:
        """
        锁定设备

        Args:
            device_id: 设备IMEI
            duration: 锁定时长(秒)
        """
        await self.device_registry.lock_device(device_id, duration)
        security_logger.warning(
            f"Device locked",
            extra={"device_id": device_id, "duration": duration},
        )


class DeviceRegistry:
    """设备注册表接口"""

    async def get_device(self, device_id: str) -> Optional[dict]:
        """获取设备信息"""
        raise NotImplementedError

    async def update_device(self, device_id: str, updates: dict) -> None:
        """更新设备信息"""
        raise NotImplementedError

    async def increment_auth_failures(self, device_id: str) -> int:
        """增加认证失败次数"""
        raise NotImplementedError

    async def lock_device(self, device_id: str, duration: int) -> None:
        """锁定设备"""
        raise NotImplementedError
