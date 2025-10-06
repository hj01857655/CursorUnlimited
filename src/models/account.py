# -*- coding: utf-8 -*-
"""
账号模型
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from .database import Database


class Account:
    """账号模型类"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def add(self, email: str, password: str = None, **kwargs) -> int:
        """添加账号"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            fields = ['email', 'password', 'username', 'access_token', 'refresh_token',
                     'device_id', 'machine_id', 'account_type', 'status', 'remark']
            
            data = {'email': email, 'password': password}
            data.update({k: v for k, v in kwargs.items() if k in fields})
            
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?' for _ in data])
            
            cursor.execute(
                f'INSERT INTO accounts ({columns}) VALUES ({placeholders})',
                tuple(data.values())
            )
            
            return cursor.lastrowid
    
    def update(self, account_id: int, **kwargs) -> bool:
        """更新账号信息"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            fields = ['email', 'password', 'username', 'access_token', 'refresh_token',
                     'device_id', 'machine_id', 'account_type', 'status', 
                     'pro_expire_date', 'is_active', 'last_login_time', 'remark']
            
            data = {k: v for k, v in kwargs.items() if k in fields}
            data['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            if not data:
                return False
            
            set_clause = ', '.join([f'{k} = ?' for k in data.keys()])
            values = list(data.values()) + [account_id]
            
            cursor.execute(f'UPDATE accounts SET {set_clause} WHERE id = ?', values)
            
            return cursor.rowcount > 0
    
    def delete(self, account_id: int) -> bool:
        """删除账号"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM accounts WHERE id = ?', (account_id,))
            return cursor.rowcount > 0
    
    def get_by_id(self, account_id: int) -> Optional[Dict]:
        """根据ID获取账号"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM accounts WHERE id = ?', (account_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_by_email(self, email: str) -> Optional[Dict]:
        """根据邮箱获取账号"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM accounts WHERE email = ?', (email,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_all(self, is_active: Optional[int] = None) -> List[Dict]:
        """获取所有账号"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            if is_active is not None:
                cursor.execute('SELECT * FROM accounts WHERE is_active = ? ORDER BY created_at DESC', (is_active,))
            else:
                cursor.execute('SELECT * FROM accounts ORDER BY created_at DESC')
            
            return [dict(row) for row in cursor.fetchall()]
    
    def update_tokens(self, account_id: int, access_token: str, refresh_token: str = None) -> bool:
        """更新令牌"""
        if refresh_token is None:
            refresh_token = access_token
        
        return self.update(
            account_id,
            access_token=access_token,
            refresh_token=refresh_token,
            last_login_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )


class UsageLog:
    """使用记录模型类"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def add(self, account_id: int, action: str, result: str, error_message: str = None) -> int:
        """添加使用记录"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO usage_logs (account_id, action, result, error_message) VALUES (?, ?, ?, ?)',
                (account_id, action, result, error_message)
            )
            return cursor.lastrowid
    
    def get_by_account(self, account_id: int, limit: int = 100) -> List[Dict]:
        """获取指定账号的使用记录"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM usage_logs WHERE account_id = ? ORDER BY created_at DESC LIMIT ?',
                (account_id, limit)
            )
            return [dict(row) for row in cursor.fetchall()]
