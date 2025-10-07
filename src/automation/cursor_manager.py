# -*- coding: utf-8 -*-
"""
Cursor 进程管理模块
"""

import psutil
import os
import winreg
from typing import Optional, List, Dict
from ..utils.logger import setup_logger


class CursorManager:
    """Cursor 进程管理器"""
    
    PROCESS_NAMES = ['Cursor.exe', 'cursor.exe']
    
    def __init__(self):
        self.logger = setup_logger("CursorManager")
        self.logger.info("初始化CursorManager")
        
        self.install_path = self.get_install_path()
        self.user_data_path = self.get_user_data_path()
        
        if self.install_path:
            self.logger.info(f"Cursor安装路径: {self.install_path}")
        else:
            self.logger.warning("未找到Cursor安装路径")
        
        self.logger.debug(f"用户数据路径: {self.user_data_path}")
    
    @staticmethod
    def get_install_path() -> Optional[str]:
        """获取Cursor安装路径"""
        logger = setup_logger("CursorManager")
        logger.debug("开始查找Cursor安装路径")
        
        # 常见安装路径
        common_paths = [
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', 'Cursor'),
            os.path.join(os.environ.get('PROGRAMFILES', ''), 'Cursor'),
            os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), 'Cursor'),
        ]
        
        for path in common_paths:
            cursor_exe = os.path.join(path, 'Cursor.exe')
            if os.path.exists(cursor_exe):
                logger.info(f"在常用路径找到Cursor: {path}")
                return path
        
        # 尝试从注册表读取
        try:
            logger.debug("尝试从注册表读取Cursor路径")
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Uninstall\Cursor')
            install_location, _ = winreg.QueryValueEx(key, 'InstallLocation')
            winreg.CloseKey(key)
            logger.info(f"从注册表找到Cursor: {install_location}")
            return install_location
        except Exception as e:
            logger.debug(f"从注册表读取失败: {str(e)}")
        
        logger.warning("未找到Cursor安装路径")
        return None
    
    @staticmethod
    def get_user_data_path() -> str:
        """获取Cursor用户数据路径"""
        return os.path.join(os.environ.get('APPDATA', ''), 'Cursor')
    
    def is_running(self) -> bool:
        """检查Cursor是否正在运行"""
        self.logger.debug("检查Cursor进程是否运行")
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'] in self.PROCESS_NAMES:
                    self.logger.debug(f"检测到Cursor进程正在运行: PID={proc.pid}")
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                self.logger.debug(f"无法访问进程: {str(e)}")
                continue
        self.logger.debug("Cursor未运行")
        return False
    
    def get_processes(self) -> List[Dict]:
        """获取所有Cursor进程信息"""
        self.logger.debug("获取所有Cursor进程信息")
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
            try:
                if proc.info['name'] in self.PROCESS_NAMES:
                    process_info = {
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'exe': proc.info['exe'],
                        'cmdline': proc.info['cmdline']
                    }
                    processes.append(process_info)
                    self.logger.debug(f"找到Cursor进程: PID={proc.info['pid']}, Name={proc.info['name']}")
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                self.logger.debug(f"无法访问进程: {str(e)}")
                continue
        
        self.logger.info(f"共找到 {len(processes)} 个Cursor进程")
        return processes
    
    def kill_all(self) -> int:
        """关闭所有Cursor进程"""
        self.logger.info("开始关闭所有Cursor进程")
        killed_count = 0
        for proc in psutil.process_iter(['name', 'pid']):
            try:
                if proc.info['name'] in self.PROCESS_NAMES:
                    pid = proc.info['pid']
                    self.logger.debug(f"正在关闭进程: PID={pid}, Name={proc.info['name']}")
                    proc.kill()
                    proc.wait(timeout=5)
                    killed_count += 1
                    self.logger.info(f"成功关闭进程: PID={pid}")
            except psutil.NoSuchProcess:
                self.logger.debug(f"进程已不存在: PID={proc.info.get('pid', 'unknown')}")
            except psutil.AccessDenied:
                self.logger.warning(f"无权限关闭进程: PID={proc.info.get('pid', 'unknown')}")
            except psutil.TimeoutExpired:
                self.logger.warning(f"关闭进程超时: PID={proc.info.get('pid', 'unknown')}")
            except Exception as e:
                self.logger.error(f"关闭进程异常: {str(e)}")
        
        self.logger.info(f"共关闭 {killed_count} 个Cursor进程")
        return killed_count
    
    def start(self, args: List[str] = None) -> bool:
        """启动Cursor"""
        self.logger.info("开始启动Cursor")
        
        if not self.install_path:
            self.logger.error("Cursor安装路径未知，无法启动")
            return False
        
        cursor_exe = os.path.join(self.install_path, 'Cursor.exe')
        if not os.path.exists(cursor_exe):
            self.logger.error(f"Cursor可执行文件不存在: {cursor_exe}")
            return False
        
        try:
            import subprocess
            cmd = [cursor_exe]
            if args:
                cmd.extend(args)
                self.logger.debug(f"启动参数: {args}")
            
            self.logger.debug(f"执行命令: {' '.join(cmd)}")
            subprocess.Popen(cmd, shell=False)
            self.logger.info("Cursor启动成功")
            return True
        except Exception as e:
            self.logger.error(f"启动Cursor失败: {str(e)}", exc_info=True)
            return False
