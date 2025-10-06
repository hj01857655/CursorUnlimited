# -*- coding: utf-8 -*-
"""
账号切换服务
"""

import time
from typing import Optional, Dict
from ..models.database import Database
from ..models.account import Account, UsageLog
from ..automation.cursor_manager import CursorManager
from ..automation.config_manager import CursorConfigManager


class AccountSwitcher:
    """账号切换服务"""
    
    def __init__(self, db: Database):
        self.db = db
        self.account_model = Account(db)
        self.log_model = UsageLog(db)
        self.cursor_manager = CursorManager()
        self.config_manager = CursorConfigManager()
    
    def switch_account(self, account_id: int, kill_cursor: bool = True) -> tuple[bool, str]:
        """
        切换到指定账号
        
        Args:
            account_id: 账号ID
            kill_cursor: 是否关闭Cursor进程
        
        Returns:
            (成功标志, 消息)
        """
        # 获取账号信息
        account = self.account_model.get_by_id(account_id)
        if not account:
            return False, "账号不存在"
        
        if not account['is_active']:
            return False, "账号已禁用"
        
        # 检查必要字段
        if not account['access_token']:
            return False, "账号token为空"
        
        try:
            # 1. 备份当前配置
            current_info = self.config_manager.get_current_account_info()
            if current_info and current_info.get('email'):
                backup_name = f"backup_{current_info['email']}_{int(time.time())}"
                self.config_manager.backup_config(backup_name)
            
            # 2. 关闭Cursor进程
            if kill_cursor and self.cursor_manager.is_running():
                killed = self.cursor_manager.kill_all()
                if killed > 0:
                    time.sleep(2)  # 等待进程完全关闭
            
            # 3. 更新配置文件
            success = self.config_manager.set_account_tokens(
                email=account['email'],
                access_token=account['access_token'],
                refresh_token=account.get('refresh_token')
            )
            
            if not success:
                self.log_model.add(account_id, 'switch', 'failed', '更新配置文件失败')
                return False, "更新配置文件失败"
            
            # 4. 更新设备ID（如果有）
            if account.get('device_id'):
                self.config_manager.write_machine_id(account['device_id'])
            
            # 5. 更新数据库中的最后登录时间
            self.account_model.update_login_time(account_id)
            
            # 6. 记录日志
            self.log_model.add(account_id, 'switch', 'success', None)
            
            # 7. 重启Cursor
            if kill_cursor:
                time.sleep(1)
                self.cursor_manager.start()
            
            return True, f"成功切换到账号: {account['email']}"
            
        except Exception as e:
            error_msg = f"切换失败: {str(e)}"
            self.log_model.add(account_id, 'switch', 'failed', error_msg)
            return False, error_msg
    
    def get_current_account(self) -> Optional[Dict]:
        """获取当前登录的账号信息"""
        current_info = self.config_manager.get_current_account_info()
        if not current_info or not current_info.get('email'):
            return None
        
        # 从数据库中查找对应账号
        account = self.account_model.get_by_email(current_info['email'])
        return account
    
    def logout(self) -> tuple[bool, str]:
        """登出当前账号"""
        try:
            # 备份当前配置
            current_info = self.config_manager.get_current_account_info()
            if current_info and current_info.get('email'):
                backup_name = f"backup_{current_info['email']}_{int(time.time())}"
                self.config_manager.backup_config(backup_name)
            
            # 关闭Cursor
            if self.cursor_manager.is_running():
                self.cursor_manager.kill_all()
                time.sleep(2)
            
            # 清空token
            self.config_manager.clear_all_tokens()
            
            return True, "登出成功"
            
        except Exception as e:
            return False, f"登出失败: {str(e)}"
    
    def sync_current_account(self) -> tuple[bool, str]:
        """同步当前Cursor中的账号信息到数据库"""
        try:
            current_info = self.config_manager.get_current_account_info()
            if not current_info or not current_info.get('email'):
                return False, "未检测到登录账号"
            
            email = current_info['email']
            
            # 检查数据库中是否存在
            account = self.account_model.get_by_email(email)
            
            if account:
                # 更新token
                self.account_model.update_tokens(
                    account['id'],
                    current_info['access_token'],
                    current_info.get('refresh_token')
                )
                # 更新设备信息
                if current_info.get('device_id'):
                    self.account_model.update(
                        account['id'],
                        device_id=current_info['device_id'],
                        machine_id=current_info.get('machine_id')
                    )
                
                return True, f"已更新账号: {email}"
            else:
                # 添加新账号
                account_id = self.account_model.add(
                    email=email,
                    access_token=current_info['access_token'],
                    refresh_token=current_info.get('refresh_token'),
                    device_id=current_info.get('device_id'),
                    machine_id=current_info.get('machine_id')
                )
                
                return True, f"已添加新账号: {email} (ID: {account_id})"
            
        except Exception as e:
            return False, f"同步失败: {str(e)}"
