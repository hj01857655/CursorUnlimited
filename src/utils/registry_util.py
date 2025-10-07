# -*- coding: utf-8 -*-
"""
Windows 注册表工具类
提供注册表读写的通用方法
"""

import winreg
from typing import Optional, Any


class RegistryUtil:
    """Windows 注册表操作工具类"""
    
    # 常用的根键
    HKEY_CURRENT_USER = winreg.HKEY_CURRENT_USER
    HKEY_LOCAL_MACHINE = winreg.HKEY_LOCAL_MACHINE
    HKEY_CLASSES_ROOT = winreg.HKEY_CLASSES_ROOT
    
    @staticmethod
    def read_value(root_key: int, sub_key: str, value_name: str) -> Optional[Any]:
        """
        读取注册表值
        
        Args:
            root_key: 根键（如 HKEY_LOCAL_MACHINE）
            sub_key: 子键路径
            value_name: 值名称
        
        Returns:
            注册表值，读取失败返回 None
        """
        try:
            key = winreg.OpenKey(root_key, sub_key)
            value, reg_type = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            return value
        except (FileNotFoundError, OSError):
            return None
    
    @staticmethod
    def write_value(root_key: int, sub_key: str, value_name: str, 
                    value: Any, value_type: int = winreg.REG_SZ) -> bool:
        """
        写入注册表值
        
        Args:
            root_key: 根键
            sub_key: 子键路径
            value_name: 值名称
            value: 要写入的值
            value_type: 值类型（默认 REG_SZ 字符串）
        
        Returns:
            是否成功
        """
        try:
            key = winreg.OpenKey(root_key, sub_key, 0, winreg.KEY_WRITE)
            winreg.SetValueEx(key, value_name, 0, value_type, value)
            winreg.CloseKey(key)
            return True
        except (FileNotFoundError, OSError, PermissionError):
            return False
    
    @staticmethod
    def key_exists(root_key: int, sub_key: str) -> bool:
        """
        检查注册表键是否存在
        
        Args:
            root_key: 根键
            sub_key: 子键路径
        
        Returns:
            是否存在
        """
        try:
            key = winreg.OpenKey(root_key, sub_key)
            winreg.CloseKey(key)
            return True
        except (FileNotFoundError, OSError):
            return False
    
    @staticmethod
    def delete_value(root_key: int, sub_key: str, value_name: str) -> bool:
        """
        删除注册表值
        
        Args:
            root_key: 根键
            sub_key: 子键路径
            value_name: 值名称
        
        Returns:
            是否成功
        """
        try:
            key = winreg.OpenKey(root_key, sub_key, 0, winreg.KEY_WRITE)
            winreg.DeleteValue(key, value_name)
            winreg.CloseKey(key)
            return True
        except (FileNotFoundError, OSError, PermissionError):
            return False


class WindowsMachineInfo:
    """Windows 机器信息读取类"""
    
    @staticmethod
    def get_machine_guid() -> Optional[str]:
        """获取 Windows MachineGuid"""
        return RegistryUtil.read_value(
            RegistryUtil.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Cryptography",
            "MachineGuid"
        )
    
    @staticmethod
    def get_sqm_machine_id() -> Optional[str]:
        """获取 Windows SQM MachineId"""
        return RegistryUtil.read_value(
            RegistryUtil.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\SQMClient",
            "MachineId"
        )
    
    @staticmethod
    def get_product_id() -> Optional[str]:
        """获取 Windows Product ID"""
        return RegistryUtil.read_value(
            RegistryUtil.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Windows NT\CurrentVersion",
            "ProductId"
        )
