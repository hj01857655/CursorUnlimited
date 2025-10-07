# -*- coding: utf-8 -*-
"""
账号数据模型定义 - 使用SQLAlchemy ORM
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# 创建基类
Base = declarative_base()


class AccountStatus(Enum):
    """账号状态枚举"""
    ACTIVE = "active"          # 活跃
    INACTIVE = "inactive"      # 未激活
    EXPIRED = "expired"        # 过期
    SUSPENDED = "suspended"    # 暂停
    ERROR = "error"           # 错误


class Account(Base):
    """账号模型"""
    __tablename__ = 'accounts'
    
    # 基础字段
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(Text, nullable=False)  # 加密存储
    username = Column(String(100), nullable=True)
    
    # 认证信息
    access_token = Column(Text, nullable=True)  # 加密存储
    refresh_token = Column(Text, nullable=True)  # 加密存储
    token_expires_at = Column(DateTime, nullable=True)
    
    # 状态信息
    status = Column(SQLEnum(AccountStatus), default=AccountStatus.INACTIVE)
    is_primary = Column(Boolean, default=False)  # 是否为主账号
    is_active = Column(Boolean, default=True)    # 是否启用
    
    # 配额信息
    total_quota = Column(Float, default=0.0)     # 总配额
    used_quota = Column(Float, default=0.0)      # 已使用配额
    quota_reset_date = Column(DateTime, nullable=True)  # 配额重置日期
    
    # 使用统计
    login_count = Column(Integer, default=0)     # 登录次数
    last_login_at = Column(DateTime, nullable=True)  # 最后登录时间
    last_used_at = Column(DateTime, nullable=True)   # 最后使用时间
    total_usage_time = Column(Float, default=0.0)    # 总使用时长（小时）
    
    # 其他信息
    notes = Column(Text, nullable=True)          # 备注
    tags = Column(String(500), nullable=True)    # 标签（逗号分隔）
    proxy_config = Column(Text, nullable=True)   # 代理配置（JSON）
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    machine_profiles = relationship("MachineProfile", back_populates="account", cascade="all, delete-orphan")
    usage_logs = relationship("UsageLog", back_populates="account", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Account(email='{self.email}', status='{self.status.value if self.status else 'unknown'}')>"
    
    @property
    def remaining_quota(self) -> float:
        """获取剩余配额"""
        return max(0, self.total_quota - self.used_quota)
    
    @property
    def quota_percentage(self) -> float:
        """获取配额使用百分比"""
        if self.total_quota <= 0:
            return 0.0
        return min(100, (self.used_quota / self.total_quota) * 100)
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'status': self.status.value if self.status else None,
            'is_primary': self.is_primary,
            'is_active': self.is_active,
            'total_quota': self.total_quota,
            'used_quota': self.used_quota,
            'remaining_quota': self.remaining_quota,
            'quota_percentage': self.quota_percentage,
            'login_count': self.login_count,
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None,
            'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None,
            'notes': self.notes,
            'tags': self.tags.split(',') if self.tags else [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class MachineProfile(Base):
    """机器ID配置模型"""
    __tablename__ = 'machine_profiles'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    name = Column(String(100), nullable=False)
    
    # 机器ID信息
    machine_id = Column(String(255), nullable=False)
    device_id = Column(String(255), nullable=True)
    mac_machine_id = Column(String(255), nullable=True)
    
    # Windows特定
    sqm_user_id = Column(String(255), nullable=True)
    telemetry_id = Column(String(255), nullable=True)
    
    # 配置信息
    config_json = Column(Text, nullable=True)  # 完整配置JSON
    is_default = Column(Boolean, default=False)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    account = relationship("Account", back_populates="machine_profiles")
    
    def __repr__(self):
        return f"<MachineProfile(name='{self.name}', machine_id='{self.machine_id}')>"
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'account_id': self.account_id,
            'name': self.name,
            'machine_id': self.machine_id,
            'device_id': self.device_id,
            'mac_machine_id': self.mac_machine_id,
            'sqm_user_id': self.sqm_user_id,
            'telemetry_id': self.telemetry_id,
            'config_json': self.config_json,
            'is_default': self.is_default,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class UsageLog(Base):
    """使用日志模型"""
    __tablename__ = 'usage_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    
    # 操作信息
    action = Column(String(50), nullable=False)  # login, logout, switch, api_call等
    details = Column(Text, nullable=True)        # 详细信息（JSON）
    
    # 配额信息
    quota_before = Column(Float, nullable=True)  # 操作前配额
    quota_after = Column(Float, nullable=True)   # 操作后配额
    quota_consumed = Column(Float, default=0.0)  # 消耗配额
    
    # 时间和状态
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    duration = Column(Float, nullable=True)      # 操作耗时（秒）
    success = Column(Boolean, default=True)      # 是否成功
    error_message = Column(Text, nullable=True)  # 错误信息
    
    # IP和设备信息
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    device_info = Column(Text, nullable=True)    # 设备信息（JSON）
    
    # 关联关系
    account = relationship("Account", back_populates="usage_logs")
    
    def __repr__(self):
        return f"<UsageLog(action='{self.action}', timestamp='{self.timestamp}')>"
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'account_id': self.account_id,
            'action': self.action,
            'details': self.details,
            'quota_before': self.quota_before,
            'quota_after': self.quota_after,
            'quota_consumed': self.quota_consumed,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'duration': self.duration,
            'success': self.success,
            'error_message': self.error_message,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'device_info': self.device_info
        }
