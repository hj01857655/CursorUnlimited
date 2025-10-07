# -*- coding: utf-8 -*-
"""
账号切换服务
"""

import time
from typing import Optional, Dict
from .database_manager import DatabaseManager
from ..models.account import Account
from ..automation.cursor_manager import CursorManager
from ..automation.config_manager import CursorConfigManager
from ..utils.logger import setup_logger


class AccountSwitcher:
    """账号切换服务"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.logger = setup_logger("AccountSwitcher")
        self.logger.info("初始化AccountSwitcher服务")
        
        self.db_manager = db_manager
        self.cursor_manager = CursorManager()
        self.config_manager = CursorConfigManager()
        
        self.logger.debug("AccountSwitcher服务初始化完成")
    
    def switch_account(self, account_id: int, kill_cursor: bool = True) -> tuple[bool, str]:
        """
        切换到指定账号
        
        Args:
            account_id: 账号ID
            kill_cursor: 是否关闭Cursor进程
        
        Returns:
            (成功标志, 消息)
        """
        self.logger.info(f"开始切换账号: account_id={account_id}, kill_cursor={kill_cursor}")
        start_time = time.time()
        
        # 获取账号信息
        self.logger.debug(f"获取账号信息: account_id={account_id}")
        account = self.db_manager.get_account(account_id)
        if not account:
            self.logger.warning(f"账号不存在: account_id={account_id}")
            return False, "账号不存在"
        
        self.logger.debug(f"账号信息: email={account.email}")
        
        if not account.is_active:
            self.logger.warning(f"账号已禁用: {account.email}")
            return False, "账号已禁用"
        
        # 检查必要字段
        if not account.access_token:
            self.logger.error(f"账号token为空: {account.email}")
            return False, "账号token为空"
        
        try:
            # 1. 备份当前配置
            self.logger.info("备份当前配置...")
            current_info = self.config_manager.get_current_account_info()
            if current_info and current_info.get('email'):
                backup_name = f"backup_{current_info['email']}_{int(time.time())}"
                self.logger.debug(f"备份名称: {backup_name}")
                self.config_manager.backup_config(backup_name)
                self.logger.info(f"配置备份完成: {current_info['email']}")
            else:
                self.logger.info("未检测到当前账号，跳过备份")
            
            # 2. 关闭Cursor进程
            if kill_cursor:
                if self.cursor_manager.is_running():
                    self.logger.info("关闭Cursor进程...")
                    killed = self.cursor_manager.kill_all()
                    self.logger.info(f"已关闭 {killed} 个Cursor进程")
                    if killed > 0:
                        self.logger.debug("等待进程完全关闭(2秒)...")
                        time.sleep(2)  # 等待进程完全关闭
                else:
                    self.logger.info("Cursor未运行，跳过关闭进程")
            
            # 3. 更新配置文件
            self.logger.info(f"更新配置文件: {account.email}")
            success = self.config_manager.set_account_tokens(
                email=account.email,
                access_token=account.access_token,
                refresh_token=account.refresh_token
            )
            
            if not success:
                self.logger.error(f"更新配置文件失败: {account.email}")
                self.db_manager.add_usage_log(account_id, 'switch', success=False, error_message='更新配置文件失败')
                return False, "更新配置文件失败"
            
            self.logger.info("配置文件更新成功")
            
            # 4. 更新设备ID（如果有）
            # TODO: 处理机器配置
            
            # 5. 更新数据库中的最后登录时间
            self.logger.debug("更新最后登录时间")
            from datetime import datetime
            self.db_manager.update_account(account_id, last_login_at=datetime.utcnow())
            
            # 6. 记录日志
            self.db_manager.add_usage_log(account_id, 'switch', success=True)
            
            # 7. 重启Cursor
            if kill_cursor:
                self.logger.info("启动Cursor...")
                time.sleep(1)
                started = self.cursor_manager.start()
                if started:
                    self.logger.info("Cursor启动成功")
                else:
                    self.logger.warning("Cursor启动失败，可能需要手动启动")
            
            duration = time.time() - start_time
            self.logger.info(f"账号切换成功: {account.email}，耗时: {duration:.2f}秒")
            
            return True, f"成功切换到账号: {account.email}"
            
        except Exception as e:
            error_msg = f"切换失败: {str(e)}"
            self.logger.error(f"账号切换异常: account_id={account_id}, error={str(e)}", exc_info=True)
            self.db_manager.add_usage_log(account_id, 'switch', success=False, error_message=error_msg)
            return False, error_msg
    
    def get_current_account(self) -> Optional[Account]:
        """获取当前登录的账号信息"""
        self.logger.debug("获取当前账号信息")
        current_info = self.config_manager.get_current_account_info()
        if not current_info or not current_info.get('email'):
            self.logger.debug("未检测到当前账号")
            return None
        
        self.logger.debug(f"当前账号邮箱: {current_info['email']}")
        # 从数据库中查找对应账号
        account = self.db_manager.get_account_by_email(current_info['email'])
        if account:
            self.logger.debug(f"找到对应账号: id={account.id}")
        else:
            self.logger.warning(f"数据库中未找到账号: {current_info['email']}")
        return account
    
    def logout(self) -> tuple[bool, str]:
        """登出当前账号"""
        self.logger.info("开始登出当前账号")
        try:
            # 备份当前配置
            current_info = self.config_manager.get_current_account_info()
            if current_info and current_info.get('email'):
                self.logger.info(f"备份当前账号配置: {current_info['email']}")
                backup_name = f"backup_{current_info['email']}_{int(time.time())}"
                self.config_manager.backup_config(backup_name)
            
            # 关闭Cursor
            if self.cursor_manager.is_running():
                self.logger.info("关闭Cursor进程...")
                killed = self.cursor_manager.kill_all()
                self.logger.info(f"已关闭 {killed} 个进程")
                time.sleep(2)
            else:
                self.logger.info("Cursor未运行")
            
            # 清空token
            self.logger.info("清空账号token")
            self.config_manager.clear_all_tokens()
            
            self.logger.info("登出成功")
            return True, "登出成功"
            
        except Exception as e:
            self.logger.error(f"登出失败: {str(e)}", exc_info=True)
            return False, f"登出失败: {str(e)}"
    
    def sync_current_account(self) -> tuple[bool, str]:
        """同步当前Cursor中的账号信息到数据库"""
        self.logger.info("开始同步当前账号信息到数据库")
        try:
            current_info = self.config_manager.get_current_account_info()
            if not current_info or not current_info.get('email'):
                self.logger.warning("未检测到登录账号")
                return False, "未检测到登录账号"
            
            email = current_info['email']
            self.logger.info(f"检测到账号: {email}")
            
            # 检查数据库中是否存在
            account = self.db_manager.get_account_by_email(email)
            
            if account:
                self.logger.info(f"更新已存在的账号: {email} (ID: {account.id})")
                # 更新token
                self.db_manager.update_account_tokens(
                    account.id,
                    current_info['access_token'],
                    current_info.get('refresh_token')
                )
                self.logger.debug("Token更新完成")
                
                self.logger.info(f"账号同步成功: {email}")
                return True, f"已更新账号: {email}"
            else:
                self.logger.info(f"添加新账号: {email}")
                # 添加新账号
                account = self.db_manager.add_account(
                    email=email,
                    password="",  # 密码字段是必需的，但可以为空
                    access_token=current_info['access_token'],
                    refresh_token=current_info.get('refresh_token')
                )
                
                if account:
                    self.logger.info(f"新账号添加成功: {email} (ID: {account.id})")
                    return True, f"已添加新账号: {email}"
                else:
                    return False, "添加账号失败"
            
        except Exception as e:
            self.logger.error(f"同步账号失败: {str(e)}", exc_info=True)
            return False, f"同步失败: {str(e)}"
