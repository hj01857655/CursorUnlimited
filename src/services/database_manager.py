# -*- coding: utf-8 -*-
"""
数据库管理器 - 使用SQLAlchemy ORM
"""

import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker, scoped_session, Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from ..models.account import Base, Account, AccountStatus, MachineProfile, UsageLog
from ..utils.logger import setup_logger


class DatabaseManager:
    """数据库管理器类"""
    
    def __init__(self, db_path: str = "data/cursor_accounts.db"):
        """
        初始化数据库管理器
        
        Args:
            db_path: 数据库文件路径
        """
        self.logger = setup_logger("DatabaseManager")
        self.db_path = db_path
        
        # 确保数据库目录存在
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
            self.logger.info(f"创建数据库目录: {db_dir}")
        
        # 创建数据库引擎
        db_url = f"sqlite:///{db_path}"
        self.engine = create_engine(
            db_url,
            echo=False,  # 不打印SQL语句
            pool_pre_ping=True,  # 连接池预检
            connect_args={"check_same_thread": False}  # SQLite多线程支持
        )
        
        # 创建会话工厂
        self.SessionLocal = scoped_session(
            sessionmaker(
                autocommit=False, 
                autoflush=False, 
                bind=self.engine,
                expire_on_commit=False  # 不要在提交后立即过期对象
            )
        )
        
        # 创建所有表
        Base.metadata.create_all(bind=self.engine)
        self.logger.info(f"数据库初始化完成: {db_path}")
    
    @contextmanager
    def get_session(self) -> Session:
        """
        获取数据库会话（上下文管理器）
        
        Yields:
            Session: 数据库会话
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            self.logger.error(f"数据库操作失败: {str(e)}", exc_info=True)
            raise
        finally:
            session.close()
    
    # ==================== 账号管理 ====================
    
    def add_account(self, email: str, password: str = "", **kwargs) -> Optional[Account]:
        """
        添加账号
        
        Args:
            email: 邮箱
            password: 密码
            **kwargs: 其他账号属性
        
        Returns:
            Account: 创建的账号对象，失败返回None
        """
        with self.get_session() as session:
            try:
                account = Account(
                    email=email,
                    password=password,
                    status=AccountStatus.INACTIVE,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    **kwargs
                )
                session.add(account)
                session.commit()
                self.logger.info(f"添加账号成功: {email}")
                return account
            except IntegrityError:
                self.logger.warning(f"账号已存在: {email}")
                return None
            except Exception as e:
                self.logger.error(f"添加账号失败: {str(e)}", exc_info=True)
                return None
    
    def get_account(self, account_id: int) -> Optional[Account]:
        """
        获取账号
        
        Args:
            account_id: 账号ID
        
        Returns:
            Account: 账号对象，不存在返回None
        """
        with self.get_session() as session:
            return session.query(Account).filter_by(id=account_id).first()
    
    def get_account_by_email(self, email: str) -> Optional[Account]:
        """
        通过邮箱获取账号
        
        Args:
            email: 邮箱地址
        
        Returns:
            Account: 账号对象，不存在返回None
        """
        with self.get_session() as session:
            return session.query(Account).filter_by(email=email).first()
    
    def get_all_accounts(self, active_only: bool = False) -> List[Account]:
        """
        获取所有账号
        
        Args:
            active_only: 是否只获取活跃账号
        
        Returns:
            List[Account]: 账号列表
        """
        with self.get_session() as session:
            query = session.query(Account)
            if active_only:
                query = query.filter_by(is_active=True)
            return query.order_by(desc(Account.is_primary), Account.email).all()
    
    def update_account(self, account_id: int, **kwargs) -> bool:
        """
        更新账号信息
        
        Args:
            account_id: 账号ID
            **kwargs: 要更新的字段
        
        Returns:
            bool: 是否成功
        """
        with self.get_session() as session:
            try:
                account = session.query(Account).filter_by(id=account_id).first()
                if not account:
                    self.logger.warning(f"账号不存在: ID={account_id}")
                    return False
                
                for key, value in kwargs.items():
                    if hasattr(account, key):
                        setattr(account, key, value)
                
                account.updated_at = datetime.utcnow()
                session.commit()
                self.logger.info(f"更新账号成功: ID={account_id}")
                return True
            except Exception as e:
                self.logger.error(f"更新账号失败: {str(e)}", exc_info=True)
                return False
    
    def delete_account(self, account_id: int) -> bool:
        """
        删除账号
        
        Args:
            account_id: 账号ID
        
        Returns:
            bool: 是否成功
        """
        with self.get_session() as session:
            try:
                account = session.query(Account).filter_by(id=account_id).first()
                if not account:
                    self.logger.warning(f"账号不存在: ID={account_id}")
                    return False
                
                session.delete(account)
                session.commit()
                self.logger.info(f"删除账号成功: {account.email}")
                return True
            except Exception as e:
                self.logger.error(f"删除账号失败: {str(e)}", exc_info=True)
                return False
    
    def set_primary_account(self, account_id: int) -> bool:
        """
        设置主账号
        
        Args:
            account_id: 账号ID
        
        Returns:
            bool: 是否成功
        """
        with self.get_session() as session:
            try:
                # 清除当前主账号
                session.query(Account).update({Account.is_primary: False})
                
                # 设置新的主账号
                account = session.query(Account).filter_by(id=account_id).first()
                if not account:
                    self.logger.warning(f"账号不存在: ID={account_id}")
                    return False
                
                account.is_primary = True
                session.commit()
                self.logger.info(f"设置主账号成功: {account.email}")
                return True
            except Exception as e:
                self.logger.error(f"设置主账号失败: {str(e)}", exc_info=True)
                return False
    
    def update_account_tokens(self, account_id: int, access_token: str, 
                            refresh_token: Optional[str] = None) -> bool:
        """
        更新账号Token
        
        Args:
            account_id: 账号ID
            access_token: 访问Token
            refresh_token: 刷新Token（可选）
        
        Returns:
            bool: 是否成功
        """
        with self.get_session() as session:
            try:
                account = session.query(Account).filter_by(id=account_id).first()
                if not account:
                    return False
                
                account.access_token = access_token
                if refresh_token:
                    account.refresh_token = refresh_token
                account.updated_at = datetime.utcnow()
                
                session.commit()
                self.logger.info(f"更新Token成功: {account.email}")
                return True
            except Exception as e:
                self.logger.error(f"更新Token失败: {str(e)}", exc_info=True)
                return False
    
    def update_account_quota(self, account_id: int, used_quota: float = None, 
                           total_quota: float = None) -> bool:
        """
        更新账号配额
        
        Args:
            account_id: 账号ID
            used_quota: 已使用配额
            total_quota: 总配额
        
        Returns:
            bool: 是否成功
        """
        with self.get_session() as session:
            try:
                account = session.query(Account).filter_by(id=account_id).first()
                if not account:
                    return False
                
                if used_quota is not None:
                    account.used_quota = used_quota
                if total_quota is not None:
                    account.total_quota = total_quota
                
                account.updated_at = datetime.utcnow()
                session.commit()
                
                self.logger.info(f"更新配额成功: {account.email}")
                return True
            except Exception as e:
                self.logger.error(f"更新配额失败: {str(e)}", exc_info=True)
                return False
    
    # ==================== 机器配置管理 ====================
    
    def add_machine_profile(self, account_id: int, name: str, 
                           machine_id: str, **kwargs) -> Optional[MachineProfile]:
        """
        添加机器配置
        
        Args:
            account_id: 账号ID
            name: 配置名称
            machine_id: 机器ID
            **kwargs: 其他配置属性
        
        Returns:
            MachineProfile: 创建的配置对象，失败返回None
        """
        with self.get_session() as session:
            try:
                profile = MachineProfile(
                    account_id=account_id,
                    name=name,
                    machine_id=machine_id,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    **kwargs
                )
                session.add(profile)
                session.commit()
                self.logger.info(f"添加机器配置成功: {name}")
                return profile
            except Exception as e:
                self.logger.error(f"添加机器配置失败: {str(e)}", exc_info=True)
                return None
    
    def get_machine_profiles(self, account_id: int) -> List[MachineProfile]:
        """
        获取账号的机器配置列表
        
        Args:
            account_id: 账号ID
        
        Returns:
            List[MachineProfile]: 配置列表
        """
        with self.get_session() as session:
            return session.query(MachineProfile).filter_by(account_id=account_id).all()
    
    # ==================== 使用日志管理 ====================
    
    def add_usage_log(self, account_id: int, action: str, 
                     success: bool = True, **kwargs) -> Optional[UsageLog]:
        """
        添加使用日志
        
        Args:
            account_id: 账号ID
            action: 操作类型
            success: 是否成功
            **kwargs: 其他日志属性
        
        Returns:
            UsageLog: 创建的日志对象，失败返回None
        """
        with self.get_session() as session:
            try:
                log = UsageLog(
                    account_id=account_id,
                    action=action,
                    success=success,
                    timestamp=datetime.utcnow(),
                    **kwargs
                )
                session.add(log)
                session.commit()
                self.logger.debug(f"添加使用日志: {action}")
                return log
            except Exception as e:
                self.logger.error(f"添加使用日志失败: {str(e)}", exc_info=True)
                return None
    
    def get_usage_logs(self, account_id: int = None, limit: int = 100) -> List[UsageLog]:
        """
        获取使用日志
        
        Args:
            account_id: 账号ID（可选，不指定则获取所有）
            limit: 返回数量限制
        
        Returns:
            List[UsageLog]: 日志列表
        """
        with self.get_session() as session:
            query = session.query(UsageLog)
            if account_id:
                query = query.filter_by(account_id=account_id)
            return query.order_by(desc(UsageLog.timestamp)).limit(limit).all()
    
    # ==================== 数据导入导出 ====================
    
    def export_accounts(self) -> List[Dict[str, Any]]:
        """
        导出所有账号数据
        
        Returns:
            List[Dict]: 账号数据列表
        """
        accounts = self.get_all_accounts()
        return [account.to_dict() for account in accounts]
    
    def import_accounts(self, accounts_data: List[Dict[str, Any]]) -> int:
        """
        批量导入账号
        
        Args:
            accounts_data: 账号数据列表
        
        Returns:
            int: 成功导入的数量
        """
        imported_count = 0
        for data in accounts_data:
            email = data.get('email')
            if not email:
                continue
            
            # 检查是否已存在
            if self.get_account_by_email(email):
                self.logger.debug(f"账号已存在，跳过: {email}")
                continue
            
            # 添加账号
            account = self.add_account(
                email=email,
                password=data.get('password', ''),
                username=data.get('username'),
                access_token=data.get('access_token'),
                refresh_token=data.get('refresh_token'),
                notes=data.get('notes'),
                tags=data.get('tags')
            )
            
            if account:
                imported_count += 1
                self.logger.info(f"导入账号成功: {email}")
        
        return imported_count
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取统计信息
        
        Returns:
            Dict: 统计数据
        """
        with self.get_session() as session:
            total_accounts = session.query(Account).count()
            active_accounts = session.query(Account).filter_by(is_active=True).count()
            primary_account = session.query(Account).filter_by(is_primary=True).first()
            
            return {
                'total_accounts': total_accounts,
                'active_accounts': active_accounts,
                'inactive_accounts': total_accounts - active_accounts,
                'primary_account': primary_account.email if primary_account else None,
                'total_usage_logs': session.query(UsageLog).count()
            }