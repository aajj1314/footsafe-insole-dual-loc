# -*- coding: utf-8 -*-
"""
自定义异常体系
"""

from typing import Optional, Any, Dict


class BaseServiceException(Exception):
    """基础异常类"""

    code: int = -1
    message: str = "unknown error"

    def __init__(
        self,
        message: Optional[str] = None,
        code: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message or self.__class__.message
        if code is not None:
            self.code = code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details,
        }


class DeviceNotRegisteredException(BaseServiceException):
    """设备未注册异常"""

    code = 1001
    message = "device_not_registered"


class ChecksumFailedException(BaseServiceException):
    """校验失败异常"""

    code = 1002
    message = "checksum_failed"


class ParameterErrorException(BaseServiceException):
    """参数错误异常"""

    code = 1003
    message = "parameter_error"


class ServerBusyException(BaseServiceException):
    """服务器繁忙异常"""

    code = 1004
    message = "server_busy"


class SessionInvalidException(BaseServiceException):
    """会话无效异常"""

    code = 1005
    message = "session_invalid"


class RateLimitExceededException(BaseServiceException):
    """频率超限异常"""

    code = 1006
    message = "rate_limit_exceeded"


class SessionExpiredException(BaseServiceException):
    """会话过期异常"""

    code = 3001
    message = "session_expired"


class DeviceLockedException(BaseServiceException):
    """设备已锁定异常"""

    code = 3002
    message = "device_locked"


class SignatureInvalidException(BaseServiceException):
    """签名无效异常"""

    code = 3003
    message = "signature_invalid"


class EncryptionFailedException(BaseServiceException):
    """加密失败异常"""

    code = 3004
    message = "encryption_failed"


class ProtocolParseException(BaseServiceException):
    """协议解析异常"""

    code = 2001
    message = "protocol_parse_error"


class DeviceNotOnlineException(BaseServiceException):
    """设备不在线异常"""

    code = 2002
    message = "device_not_online"


class CommandNotFoundException(BaseServiceException):
    """命令未找到异常"""

    code = 2003
    message = "command_not_found"


class DatabaseException(BaseServiceException):
    """数据库异常"""

    code = 5001
    message = "database_error"


class CacheException(BaseServiceException):
    """缓存异常"""

    code = 5002
    message = "cache_error"


class NetworkException(BaseServiceException):
    """网络异常"""

    code = 5003
    message = "network_error"
