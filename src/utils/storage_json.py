# -*- coding: utf-8 -*-
"""
Cursor 配置文件操作工具类
专门用于操作 Cursor 的 storage.json 配置文件
"""

import json
import os
import shutil
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime
from .logger import get_logger

logger = get_logger(__name__)


class CursorStorageJson:
    """
    Cursor storage.json 专用操作类
    
    storage.json 结构：扁平的 JSON 对象
    {
        "cursorAuth/accessToken": "...",
        "cursorAuth/cachedEmail": "...",
        "cursorAuth/refreshToken": "...",
        "cursorAuth/cachedSignUpType": "Auth_0",
        "storage.serviceMachineId": "uuid",
        "telemetry.machineId": "hash",
        "telemetry.macMachineId": "hash",
        "telemetry.devDeviceId": "uuid",
        "telemetry.sqmId": "{GUID}",
        "backupWorkspaces": {...},
        "profileAssociations": {...},
        "theme": "vs-dark",
        "windowsState": {...},
        ... 其他配置
    }
    """
    
    # Cursor 认证字段（storage.json 中的 4 个）
    AUTH_KEYS = [
        'cursorAuth/accessToken',
        'cursorAuth/cachedEmail',
        'cursorAuth/refreshToken',
        'cursorAuth/cachedSignUpType'
    ]
    
    # 注意：以下字段只在 state.vscdb 数据库中，不在 storage.json
    # - cursorAuth/onboardingDate
    # - cursorAuth/stripeMembershipType
    
    # 机器标识字段
    MACHINE_ID_KEYS = [
        'storage.serviceMachineId',
        'telemetry.machineId',
        'telemetry.macMachineId',
        'telemetry.devDeviceId',
        'telemetry.sqmId'
    ]
    
    # 不应该在账号切换时修改的系统字段
    SYSTEM_KEYS = [
        'backupWorkspaces',
        'profileAssociations',
        'theme',
        'themeBackground',
        'windowSplash',
        'windowSplashWorkspaceOverride',
        'windowsState',
        'windowControlHeight'
    ]
    
    @staticmethod
    def read(file_path: str) -> Optional[Dict[str, Any]]:
        """
        读取 storage.json
        
        Args:
            file_path: storage.json 文件路径
        
        Returns:
            配置字典
        """
        if not os.path.exists(file_path):
            logger.warning(f"storage.json 不存在: {file_path}")
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.debug(f"读取 storage.json 成功: {file_path}")
            return data
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"读取 storage.json 失败 {file_path}: {e}")
            return None
    
    @staticmethod
    def write(file_path: str, data: Dict[str, Any], backup: bool = True) -> bool:
        """
        写入 storage.json
        
        Args:
            file_path: storage.json 文件路径
            data: 配置字典
            backup: 是否备份原文件
        
        Returns:
            是否成功
        """
        try:
            # 备份原文件（带时间戳）
            if backup and os.path.exists(file_path):
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_path = f"{file_path}.bak.{timestamp}"
                shutil.copy2(file_path, backup_path)
                logger.debug(f"备份 storage.json: {backup_path}")
            
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # 写入文件（无缩进，与 Cursor 原格式一致）
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"写入 storage.json 成功: {file_path}")
            return True
        except (IOError, OSError) as e:
            logger.error(f"写入 storage.json 失败 {file_path}: {e}")
            return False
    
    @classmethod
    def get_auth_info(cls, file_path: str) -> Dict[str, Optional[str]]:
        """
        获取认证信息
        
        Args:
            file_path: storage.json 文件路径
        
        Returns:
            认证信息字典
        """
        data = cls.read(file_path)
        if not data:
            return {}
        
        return {
            key: data.get(key)
            for key in cls.AUTH_KEYS
        }
    
    @classmethod
    def set_auth_info(cls, file_path: str, auth_info: Dict[str, str]) -> bool:
        """
        设置认证信息
        
        Args:
            file_path: storage.json 文件路径
            auth_info: 认证信息字典
        
        Returns:
            是否成功
        """
        data = cls.read(file_path)
        if data is None:
            data = {}
        
        updated_keys = []
        for key, value in auth_info.items():
            if key in cls.AUTH_KEYS and value:
                data[key] = value
                updated_keys.append(key)
        
        if updated_keys:
            logger.info(f"更新认证信息: {', '.join(updated_keys)}")
        
        return cls.write(file_path, data)
    
    @classmethod
    def clear_auth_info(cls, file_path: str) -> bool:
        """
        清空认证信息（登出）
        
        Args:
            file_path: storage.json 文件路径
        
        Returns:
            是否成功
        """
        data = cls.read(file_path)
        if not data:
            return False
        
        cleared_keys = []
        for key in cls.AUTH_KEYS:
            if key in data:
                del data[key]
                cleared_keys.append(key)
        
        if cleared_keys:
            logger.info(f"清空认证信息: {', '.join(cleared_keys)}")
        
        return cls.write(file_path, data)
    
    @classmethod
    def get_machine_ids(cls, file_path: str) -> Dict[str, Optional[str]]:
        """
        获取机器标识
        
        Args:
            file_path: storage.json 文件路径
        
        Returns:
            机器标识字典
        """
        data = cls.read(file_path)
        if not data:
            return {}
        
        return {
            key: data.get(key)
            for key in cls.MACHINE_ID_KEYS
        }
    
    @classmethod
    def set_machine_ids(cls, file_path: str, machine_ids: Dict[str, str]) -> bool:
        """
        设置机器标识
        
        Args:
            file_path: storage.json 文件路径
            machine_ids: 机器标识字典
        
        Returns:
            是否成功
        """
        data = cls.read(file_path)
        if data is None:
            data = {}
        
        for key, value in machine_ids.items():
            if key in cls.MACHINE_ID_KEYS and value:
                data[key] = value
        
        return cls.write(file_path, data)
    
    @classmethod
    def update_fields(cls, file_path: str, updates: Dict[str, Any]) -> bool:
        """
        更新任意字段
        
        Args:
            file_path: storage.json 文件路径
            updates: 要更新的字段字典
        
        Returns:
            是否成功
        """
        data = cls.read(file_path)
        if data is None:
            data = {}
        
        data.update(updates)
        return cls.write(file_path, data)
    
    @classmethod
    def get_field(cls, file_path: str, key: str, default: Any = None) -> Any:
        """
        获取单个字段的值
        
        Args:
            file_path: storage.json 文件路径
            key: 字段名
            default: 默认值
        
        Returns:
            字段值
        """
        data = cls.read(file_path)
        if not data:
            return default
        return data.get(key, default)
    
    @classmethod
    def set_field(cls, file_path: str, key: str, value: Any) -> bool:
        """
        设置单个字段的值
        
        Args:
            file_path: storage.json 文件路径
            key: 字段名
            value: 值
        
        Returns:
            是否成功
        """
        return cls.update_fields(file_path, {key: value})


class FileBackupUtil:
    """文件备份工具类"""
    
    @staticmethod
    def backup_file(src_path: str, backup_dir: str, backup_name: str = None) -> bool:
        """
        备份单个文件
        
        Args:
            src_path: 源文件路径
            backup_dir: 备份目录
            backup_name: 备份文件名（可选，默认使用原文件名）
        
        Returns:
            是否成功
        """
        if not os.path.exists(src_path):
            return False
        
        try:
            os.makedirs(backup_dir, exist_ok=True)
            
            if backup_name is None:
                backup_name = os.path.basename(src_path)
            
            backup_path = os.path.join(backup_dir, backup_name)
            shutil.copy2(src_path, backup_path)
            return True
        except (IOError, OSError) as e:
            print(f"备份文件失败 {src_path}: {e}")
            return False
    
    @staticmethod
    def backup_directory(src_dir: str, backup_dir: str, dir_name: str = None) -> bool:
        """
        备份整个目录
        
        Args:
            src_dir: 源目录路径
            backup_dir: 备份根目录
            dir_name: 备份目录名（可选，默认使用原目录名）
        
        Returns:
            是否成功
        """
        if not os.path.exists(src_dir):
            return False
        
        try:
            os.makedirs(backup_dir, exist_ok=True)
            
            if dir_name is None:
                dir_name = os.path.basename(src_dir)
            
            backup_path = os.path.join(backup_dir, dir_name)
            
            if os.path.exists(backup_path):
                shutil.rmtree(backup_path)
            
            shutil.copytree(src_dir, backup_path)
            return True
        except (IOError, OSError) as e:
            print(f"备份目录失败 {src_dir}: {e}")
            return False
    
    @staticmethod
    def restore_file(backup_path: str, target_path: str) -> bool:
        """
        从备份恢复文件
        
        Args:
            backup_path: 备份文件路径
            target_path: 目标文件路径
        
        Returns:
            是否成功
        """
        if not os.path.exists(backup_path):
            return False
        
        try:
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            shutil.copy2(backup_path, target_path)
            return True
        except (IOError, OSError) as e:
            print(f"恢复文件失败 {backup_path}: {e}")
            return False
