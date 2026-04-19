# -*- coding: utf-8 -*-
"""
AES数据加密模块
与硬件端encryption.c完全一致，使用AES-256-GCM
"""

import os
import hashlib
from typing import Optional, Tuple

try:
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import padding
    HAS_CRYPTOGRAPHY = True
except ImportError:
    HAS_CRYPTOGRAPHY = False


class AESCipher:
    """AES加密解密类"""

    def __init__(self, key: bytes):
        """
        初始化AES加密器

        Args:
            key: 256位密钥(32字节)
        """
        if len(key) != 32:
            raise ValueError("AES-256 requires a 32-byte key")
        self.key = key
        self.backend = default_backend()

    def encrypt(self, plaintext: bytes) -> Tuple[bytes, bytes, bytes]:
        """
        AES-256-GCM加密

        Args:
            plaintext: 明文数据

        Returns:
            (ciphertext, iv, tag) 密文、初始向量、认证标签
        """
        # 生成96位随机IV
        iv = os.urandom(12)

        # 创建GCM模式加密器
        cipher = Cipher(
            algorithms.AES(self.key),
            modes.GCM(iv),
            backend=self.backend,
        )
        encryptor = cipher.encryptor()

        # 加密
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()

        return ciphertext, iv, encryptor.tag

    def decrypt(self, ciphertext: bytes, iv: bytes, tag: bytes) -> bytes:
        """
        AES-256-GCM解密

        Args:
            ciphertext: 密文
            iv: 初始向量
            tag: 认证标签

        Returns:
            明文数据
        """
        cipher = Cipher(
            algorithms.AES(self.key),
            modes.GCM(iv, tag),
            backend=self.backend,
        )
        decryptor = cipher.decryptor()

        return decryptor.update(ciphertext) + decryptor.finalize()

    @staticmethod
    def pkcs7_pad(data: bytes, block_size: int = 16) -> bytes:
        """PKCS7填充"""
        pad_len = block_size - (len(data) % block_size)
        return data + bytes([pad_len] * pad_len)

    @staticmethod
    def pkcs7_unpad(data: bytes) -> bytes:
        """PKCS7去填充"""
        if not data:
            return data
        pad_len = data[-1]
        return data[:-pad_len]


def derive_key_from_preshared_key(preshared_key: str, device_id: str) -> bytes:
    """
    从预共享密钥派生设备专用密钥

    Args:
        preshared_key: 预共享密钥
        device_id: 设备IMEI

    Returns:
        256位密钥
    """
    concat = preshared_key + device_id
    return hashlib.sha256(concat.encode("utf-8")).digest()


def encrypt_data(
    data: bytes,
    key: bytes,
) -> Tuple[bytes, bytes, bytes]:
    """
    加密数据

    Args:
        data: 待加密数据
        key: 加密密钥

    Returns:
        (ciphertext, iv, tag)
    """
    cipher = AESCipher(key)
    return cipher.encrypt(data)


def decrypt_data(
    ciphertext: bytes,
    iv: bytes,
    tag: bytes,
    key: bytes,
) -> bytes:
    """
    解密数据

    Args:
        ciphertext: 密文
        iv: 初始向量
        tag: 认证标签
        key: 解密密钥

    Returns:
        明文数据
    """
    cipher = AESCipher(key)
    return cipher.decrypt(ciphertext, iv, tag)
