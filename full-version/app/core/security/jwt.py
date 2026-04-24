# -*- coding: utf-8 -*-
"""
JWT认证工具
"""
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

# 简单的JWT实现（用于演示，生产环境应使用PyJWT库）
class SimpleJWT:
    """简单的JWT实现"""

    def __init__(self, secret_key: str = "zu_an_secret_key_2024"):
        self.secret_key = secret_key
        self.algorithm = "HS256"
        self.expire_minutes = 60 * 24 * 7  # 7天过期

    def create_token(self, data: Dict[str, Any]) -> str:
        """
        创建JWT Token

        Args:
            data: 包含sub(用户ID)等字段

        Returns:
            JWT token字符串
        """
        import base64
        import json

        # Header
        header = {
            "alg": self.algorithm,
            "typ": "JWT"
        }

        # Payload
        payload = data.copy()
        payload["iat"] = datetime.utcnow().isoformat()
        payload["exp"] = (datetime.utcnow() + timedelta(minutes=self.expire_minutes)).isoformat()

        # 使用更安全的编码
        def base64_encode(data: dict) -> str:
            json_str = json.dumps(data, separators=(',', ':'))
            return base64.urlsafe_b64encode(json_str.encode()).decode().rstrip('=')

        header_encoded = base64_encode(header)
        payload_encoded = base64_encode(payload)

        # Signature
        message = f"{header_encoded}.{payload_encoded}"
        signature = hashlib.sha256((message + self.secret_key).encode()).hexdigest()

        return f"{header_encoded}.{payload_encoded}.{signature}"

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        验证JWT Token

        Args:
            token: JWT token字符串

        Returns:
            解码后的payload，失败返回None
        """
        import base64
        import json

        try:
            parts = token.split('.')
            if len(parts) != 3:
                return None

            header_encoded, payload_encoded, signature = parts

            # 验证签名
            message = f"{header_encoded}.{payload_encoded}"
            expected_signature = hashlib.sha256((message + self.secret_key).encode()).hexdigest()

            if signature != expected_signature:
                return None

            # 解码payload
            # 添加padding
            padding = 4 - len(payload_encoded) % 4
            if padding != 4:
                payload_encoded += '=' * padding

            payload_str = base64.urlsafe_b64decode(payload_encoded.encode()).decode()
            payload = json.loads(payload_str)

            # 检查过期
            exp_str = payload.get("exp")
            if exp_str:
                exp_time = datetime.fromisoformat(exp_str.replace('Z', '+00:00'))
                if datetime.utcnow() > exp_time:
                    return None

            return payload

        except Exception as e:
            print(f"JWT verify error: {e}")
            return None


# 全局JWT实例
_jwt_instance: Optional[SimpleJWT] = None


def get_jwt() -> SimpleJWT:
    """获取JWT实例"""
    global _jwt_instance
    if _jwt_instance is None:
        _jwt_instance = SimpleJWT()
    return _jwt_instance


def create_access_token(data: Dict[str, Any]) -> str:
    """创建访问令牌"""
    return get_jwt().create_token(data)


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """验证访问令牌"""
    return get_jwt().verify_token(token)
