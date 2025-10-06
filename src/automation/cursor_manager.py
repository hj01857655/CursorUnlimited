# -*- coding: utf-8 -*-
"""
Cursor 进程管理模块
"""

import psutil
import os
import winreg
from typing import Optional, List, Dict


class CursorManager:
    """Cursor 进程管理器"""
    
    PROCESS_NAMES = ['Cursor.exe', 'cursor.exe']
    
    def __init__(self):
        self.install_path = self.get_install_path()
        self.user_data_path = self.get_user_data_path()
    
    @staticmethod
    def get_install_path() -> Optional[str]:
        """获取Cursor安装路径"""
        # 常见安装路径
        common_paths = [
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', 'Cursor'),
            os.path.join(os.environ.get('PROGRAMFILES', ''), 'Cursor'),
            os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), 'Cursor'),
        ]
        
        for path in common_paths:
            cursor_exe = os.path.join(path, 'Cursor.exe')
            if os.path.exists(cursor_exe):
                return path
        
        # 尝试从注册表读取
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Uninstall\Cursor')
            install_location, _ = winreg.QueryValueEx(key, 'InstallLocation')
            winreg.CloseKey(key)
            return install_location
        except:
            pass
        
        return None
    
    @staticmethod
    def get_user_data_path() -> str:
        """获取Cursor用户数据路径"""
        return os.path.join(os.environ.get('APPDATA', ''), 'Cursor')
    
    def is_running(self) -> bool:
        """检查Cursor是否正在运行"""
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'] in self.PROCESS_NAMES:
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False
    
    def get_processes(self) -> List[Dict]:
        """获取所有Cursor进程信息"""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
            try:
                if proc.info['name'] in self.PROCESS_NAMES:
                    processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'exe': proc.info['exe'],
                        'cmdline': proc.info['cmdline']
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return processes
    
    def kill_all(self) -> int:
        """关闭所有Cursor进程"""
        killed_count = 0
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'] in self.PROCESS_NAMES:
                    proc.kill()
                    proc.wait(timeout=5)
                    killed_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                continue
        return killed_count
    
    def start(self, args: List[str] = None) -> bool:
        """启动Cursor"""
        if not self.install_path:
            return False
        
        cursor_exe = os.path.join(self.install_path, 'Cursor.exe')
        if not os.path.exists(cursor_exe):
            return False
        
        try:
            import subprocess
            cmd = [cursor_exe]
            if args:
                cmd.extend(args)
            subprocess.Popen(cmd, shell=False)
            return True
        except Exception as e:
            print(f"启动Cursor失败: {e}")
            return False
