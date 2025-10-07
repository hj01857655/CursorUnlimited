# -*- coding: utf-8 -*-
"""
Cursor 账号认证管理模块
负责账号登录、登出、切换和Token管理
"""

import os
from typing import Dict, Optional, List
from .config_manager import CursorConfigManager
from ..utils.logger import get_logger

logger = get_logger(__name__)


class CursorAuthManager:
    """Cursor 账号认证管理器"""
    
    def __init__(self, config_manager: CursorConfigManager = None):
        self.config_manager = config_manager or CursorConfigManager()
        logger.debug("初始化 CursorAuthManager")
    
    def get_current_account(self) -> Optional[Dict]:
        """
        获取当前登录的账号信息
        
        Returns:
            账号信息字典，包含email和tokens
        """
        account = self.config_manager.get_current_account_info()
        if account and account.get('email'):
            logger.debug(f"当前账号: {account.get('email')}")
        else:
            logger.debug("未找到当前登录的账号")
        return account
    
    def login(self, email: str, access_token: str, refresh_token: str = None, 
              sync_to_db: bool = True, signup_type: str = None, 
              onboarding_date: str = None, membership_type: str = None) -> bool:
        """
        登录账号
        
        Args:
            email: 邮箱地址
            access_token: 访问令牌
            refresh_token: 刷新令牌（可选，默认使用access_token）
            sync_to_db: 是否同步到state.vscdb数据库
            signup_type: 注册类型（如 Auth_0）
            onboarding_date: 入职日期
            membership_type: 会员类型（如 free, pro）
        
        Returns:
            是否成功
        """
        logger.info(f"登录账号: {email}, 同步到DB: {sync_to_db}")
        
        if refresh_token is None:
            refresh_token = access_token
        
        # 更新storage.json
        success = self.config_manager.set_account_tokens(email, access_token, refresh_token)
        
        # 同步到state.vscdb（包括所有8个字段）
        if success and sync_to_db:
            logger.debug("同步账号信息到 state.vscdb")
            success &= self.config_manager.sync_account_to_vscdb(
                email, access_token, refresh_token,
                signup_type, onboarding_date, membership_type
            )
        
        if success:
            logger.info(f"账号 {email} 登录成功")
        else:
            logger.error(f"账号 {email} 登录失败")
        
        return success
    
    def logout(self) -> bool:
        """
        登出当前账号（清空所有token）
        
        Returns:
            是否成功
        """
        logger.info("执行账号登出")
        success = self.config_manager.clear_all_tokens()
        if success:
            logger.info("账号登出成功")
        else:
            logger.error("账号登出失败")
        return success
    
    def switch_account(self, email: str, access_token: str, refresh_token: str = None,
                       sync_to_db: bool = True, signup_type: str = None,
                       onboarding_date: str = None, membership_type: str = None) -> bool:
        """
        切换到指定账号
        
        Args:
            email: 邮箱地址
            access_token: 访问令牌
            refresh_token: 刷新令牌
            sync_to_db: 是否同步到数据库
        
        Returns:
            是否成功
        """
        logger.info(f"切换到账号: {email}")
        return self.login(email, access_token, refresh_token, sync_to_db,
                         signup_type, onboarding_date, membership_type)
    
    def get_account_list(self) -> List[Dict]:
        """
        从account.json获取账号列表
        
        Returns:
            账号列表
        """
        accounts = self.config_manager.read_account_json()
        logger.debug(f"获取账号列表，共 {len(accounts)} 个账号")
        return accounts
    
    def add_account_to_list(self, email: str, token: str, refresh_token: str = None,
                           workos_token: str = None, set_as_current: bool = False) -> bool:
        """
        添加账号到account.json列表
        
        Args:
            email: 邮箱地址
            token: 访问令牌
            refresh_token: 刷新令牌
            workos_token: WorkOS会话令牌
            set_as_current: 是否设为当前账号
        
        Returns:
            是否成功
        """
        logger.info(f"添加账号到列表: {email}, 设为当前: {set_as_current}")
        success = self.config_manager.add_account_to_list(
            email, token, refresh_token, workos_token, set_as_current
        )
        if success:
            logger.info(f"成功添加账号 {email} 到列表")
        else:
            logger.error(f"添加账号 {email} 到列表失败")
        return success
    
    def get_current_account_from_list(self) -> Optional[Dict]:
        """
        从account.json获取标记为当前的账号
        
        Returns:
            当前账号信息
        """
        account = self.config_manager.get_current_account_from_list()
        if account:
            logger.debug(f"从列表获取当前账号: {account.get('email')}")
        else:
            logger.debug("列表中没有标记为当前的账号")
        return account
    
    def switch_account_from_list(self, email: str, sync_to_db: bool = True) -> bool:
        """
        从account.json列表中切换到指定账号
        
        Args:
            email: 要切换到的账号邮箱
            sync_to_db: 是否同步到数据库
        
        Returns:
            是否成功
        """
        logger.info(f"从列表切换到账号: {email}")
        accounts = self.get_account_list()
        
        target_account = None
        for acc in accounts:
            if acc.get('email') == email:
                target_account = acc
                break
        
        if not target_account:
            logger.error(f"账号不存在: {email}")
            return False
        
        logger.debug(f"找到目标账号: {email}")
        
        # 执行切换
        success = self.login(
            email=target_account['email'],
            access_token=target_account['token'],
            refresh_token=target_account.get('refresh_token'),
            sync_to_db=sync_to_db
        )
        
        if success:
            # 更新account.json中的current标记
            logger.debug("更新account.json中的current标记")
            for acc in accounts:
                acc['is_current'] = (acc['email'] == email)
            self.config_manager.write_account_json(accounts)
            logger.info(f"成功切换到账号: {email}")
        else:
            logger.error(f"切换到账号 {email} 失败")
        
        return success
    
    def refresh_token(self, new_access_token: str, new_refresh_token: str = None,
                     sync_to_db: bool = True) -> bool:
        """
        刷新当前账号的token
        
        Args:
            new_access_token: 新的访问令牌
            new_refresh_token: 新的刷新令牌
            sync_to_db: 是否同步到数据库
        
        Returns:
            是否成功
        """
        logger.info("刷新当前账号的token")
        
        current = self.get_current_account()
        if not current or not current.get('email'):
            logger.error("没有当前登录的账号，无法刷新token")
            return False
        
        logger.debug(f"刷新账号 {current['email']} 的token")
        
        success = self.login(
            email=current['email'],
            access_token=new_access_token,
            refresh_token=new_refresh_token or new_access_token,
            sync_to_db=sync_to_db
        )
        
        if success:
            logger.info(f"成功刷新账号 {current['email']} 的token")
        else:
            logger.error(f"刷新账号 {current['email']} 的token失败")
        
        return success
    
    def validate_token(self) -> bool:
        """
        验证当前token是否有效（检查是否存在）
        
        Returns:
            token是否有效
        """
        current = self.get_current_account()
        is_valid = bool(current and current.get('access_token'))
        
        if is_valid:
            logger.debug(f"Token验证通过，账号: {current.get('email')}")
        else:
            logger.debug("Token验证失败，未找到有效token")
        
        return is_valid
    
    def get_account_info_summary(self) -> Dict:
        """
        获取账号信息摘要（用于显示）
        
        Returns:
            账号信息摘要
        """
        current = self.get_current_account()
        if not current:
            logger.debug("账号信息摘要: 未登录")
            return {
                'logged_in': False,
                'email': None,
                'has_token': False
            }
        
        summary = {
            'logged_in': True,
            'email': current.get('email'),
            'has_token': bool(current.get('access_token')),
            'has_refresh_token': bool(current.get('refresh_token'))
        }
        
        logger.debug(f"账号信息摘要: {summary['email']}, 已登录: {summary['logged_in']}, 有token: {summary['has_token']}")
        return summary
