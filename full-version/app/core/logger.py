# -*- coding: utf-8 -*-
"""
结构化日志配置
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime
import json


class JSONFormatter(logging.Formatter):
    """JSON格式日志 formatter"""

    def format(self, record: logging.LogRecord) -> str:
        """格式化日志记录为JSON格式"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        if hasattr(record, "device_id"):
            log_data["device_id"] = record.device_id

        if hasattr(record, "session_id"):
            log_data["session_id"] = record.session_id

        if hasattr(record, "extra_data"):
            log_data["extra_data"] = record.extra_data

        return json.dumps(log_data)


class StandardFormatter(logging.Formatter):
    """标准格式日志 formatter"""

    def __init__(self):
        super().__init__(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(module)s:%(funcName)s:%(lineno)d | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )


def setup_logger(
    name: str,
    log_file: Optional[str] = None,
    level: int = logging.INFO,
    json_format: bool = False,
) -> logging.Logger:
    """
    配置日志记录器

    Args:
        name: 日志记录器名称
        log_file: 日志文件路径（可选）
        level: 日志级别
        json_format: 是否使用JSON格式

    Returns:
        配置好的日志记录器
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.handlers.clear()

    formatter = JSONFormatter() if json_format else StandardFormatter()

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 文件处理器
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


# 全局日志记录器
logger = setup_logger(
    name="device_terminal_service",
    log_file="logs/terminal_service.log",
    level=logging.INFO,
    json_format=False,
)

# 安全审计日志记录器
security_logger = setup_logger(
    name="security_audit",
    log_file="logs/security_audit.log",
    level=logging.INFO,
    json_format=True,
)


def get_logger(name: str) -> logging.Logger:
    """获取指定名称的日志记录器"""
    return logging.getLogger(name)
