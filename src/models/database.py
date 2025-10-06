# -*- coding: utf-8 -*-
"""
数据库管理模块
"""

import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import contextmanager


class Database:
    """数据库管理类"""
    
    def __init__(self, db_path: str = "data/cursor_accounts.db"):
        self.db_path = db_path
        self._ensure_db_dir()
        self._init_database()
    
    def _ensure_db_dir(self):
        """确保数据库目录存在"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接（上下文管理器）"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _init_database(self):
        """初始化数据库表结构"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 创建账号表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT,
                    username TEXT,
                    access_token TEXT,
                    refresh_token TEXT,
                    device_id TEXT,
                    machine_id TEXT,
                    account_type TEXT DEFAULT 'free',
                    status TEXT DEFAULT 'normal',
                    pro_expire_date DATETIME,
                    is_active INTEGER DEFAULT 1,
                    last_login_time DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    remark TEXT
                )
            ''')
            
            # 创建使用记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS usage_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_id INTEGER,
                    action TEXT,
                    result TEXT,
                    error_message TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (account_id) REFERENCES accounts(id)
                )
            ''')
            
            # 创建索引
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_accounts_email ON accounts(email)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_logs_account_id ON usage_logs(account_id)')
