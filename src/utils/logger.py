# -*- coding: utf-8 -*-
"""
日志工具模块
支持日志轮转、彩色输出、错误日志单独记录等功能
"""

import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """带颜色的日志格式化器（仅在控制台）"""
    
    # ANSI 颜色代码
    COLORS = {
        'DEBUG': '\033[36m',      # 青色
        'INFO': '\033[32m',       # 绿色
        'WARNING': '\033[33m',    # 黄色
        'ERROR': '\033[31m',      # 红色
        'CRITICAL': '\033[35m',   # 紫色
    }
    RESET = '\033[0m'
    
    def format(self, record):
        # 为日志级别添加颜色
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.RESET}"
        return super().format(record)


def setup_logger(
    name: str = "CursorUnlimited",
    log_dir: str = "logs",
    level: int = logging.DEBUG,
    console_level: int = logging.INFO,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    use_color: bool = True,
    separate_error_log: bool = True
) -> logging.Logger:
    """
    设置并返回日志记录器
    
    Args:
        name: 日志记录器名称
        log_dir: 日志目录
        level: 文件日志级别
        console_level: 控制台日志级别
        max_bytes: 单个日志文件最大字节数
        backup_count: 保留的日志文件数量
        use_color: 控制台是否使用彩色输出
        separate_error_log: 是否单独记录错误日志
    
    Returns:
        配置好的日志记录器
    """
    
    # 创建日志目录
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 创建日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 避免重复添加处理器
    if logger.handlers:
        return logger
    
    # ========== 文件处理器（轮转）==========
    log_file = os.path.join(log_dir, f"{datetime.now().strftime('%Y%m%d')}.log")
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(level)
    
    # 文件格式（详细）
    file_formatter = logging.Formatter(
        '%(asctime)s - [%(name)s] - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # ========== 错误日志单独记录 ==========
    if separate_error_log:
        error_log_file = os.path.join(log_dir, f"{datetime.now().strftime('%Y%m%d')}_error.log")
        error_handler = RotatingFileHandler(
            error_log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        logger.addHandler(error_handler)
    
    # ========== 控制台处理器 ==========
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)
    
    # 控制台格式（简洁）
    if use_color and sys.stdout.isatty():  # 只在终端中使用颜色
        console_formatter = ColoredFormatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
    else:
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
    
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    获取已存在的日志记录器
    
    Args:
        name: 日志记录器名称，默认为 CursorUnlimited
    
    Returns:
        日志记录器
    """
    if name is None:
        name = "CursorUnlimited"
    
    logger = logging.getLogger(name)
    
    # 如果还没有初始化，则初始化
    if not logger.handlers:
        return setup_logger(name)
    
    return logger
