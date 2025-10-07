# -*- coding: utf-8 -*-
"""
SQLite 数据库操作工具类
提供通用的 SQLite 数据库读写方法
支持 Cursor state.vscdb 数据库的操作
"""

import sqlite3
import os
import shutil
from contextlib import contextmanager
from typing import Optional, Any, List, Dict, Tuple
from datetime import datetime
from .logger import get_logger

logger = get_logger(__name__)


class SqliteUtil:
    """SQLite 数据库操作工具类"""
    
    # Cursor state.vscdb 数据库配置
    CURSOR_TABLE_NAME = 'ItemTable'  # Cursor 使用的表名
    CURSOR_KEY_COLUMN = 'key'        # 键列名
    CURSOR_VALUE_COLUMN = 'value'    # 值列名
    
    # 数据库连接配置
    DB_TIMEOUT = 10.0  # 超时时间（秒）
    DB_ISOLATION_LEVEL = None  # 自动提交模式
    
    # 机器标识相关的键
    MACHINE_ID_KEYS = [
        'storage.serviceMachineId',
        'telemetry.machineId',
        'telemetry.macMachineId',
        'telemetry.devDeviceId',
        'telemetry.sqmId',
        'telemetry.firstSessionDate',
        'telemetry.currentSessionDate',
        'telemetry.lastSessionDate'
    ]
    
    # 账号认证相关的键 (cursorAuth/*)
    AUTH_KEYS = [
        'cursorAuth/accessToken',
        'cursorAuth/cachedEmail',
        'cursorAuth/refreshToken',
        'cursorAuth/cachedSignUpType',
        'cursorAuth/onboardingDate',
        'cursorAuth/stripeMembershipType'
    ]
    
    # 不应该备份/切换的系统键（UI状态、窗口位置等）
    EXCLUDED_KEYS_PATTERNS = [
        'workbench.',           # 工作台UI状态
        'terminal.',            # 终端状态
        'window.',              # 窗口位置和大小
        'editor.',              # 编辑器状态
        'files.hotExit',        # 热退出状态
        'search.history',       # 搜索历史
        'debug.',               # 调试状态
    ]
    
    # ========== 数据库连接管理 ==========
    
    @classmethod
    @contextmanager
    def get_connection(cls, db_path: str):
        """
        获取数据库连接的上下文管理器
        
        Args:
            db_path: 数据库文件路径
        
        Yields:
            数据库连接对象
        
        Example:
            with SqliteUtil.get_connection(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM table")
        """
        if not os.path.exists(db_path):
            logger.error(f"数据库文件不存在: {db_path}")
            raise FileNotFoundError(f"数据库文件不存在: {db_path}")
        
        conn = None
        try:
            conn = sqlite3.connect(
                db_path,
                timeout=cls.DB_TIMEOUT,
                isolation_level=cls.DB_ISOLATION_LEVEL
            )
            conn.row_factory = sqlite3.Row  # 使结果可以通过列名访问
            yield conn
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            logger.error(f"数据库操作失败: {e}")
            raise sqlite3.Error(f"数据库操作失败: {e}")
        finally:
            if conn:
                conn.close()
    
    @classmethod
    def backup_database(cls, db_path: str, backup_path: str) -> bool:
        """
        备份数据库文件
        
        Args:
            db_path: 源数据库路径
            backup_path: 备份路径
        
        Returns:
            是否成功
        """
        if not os.path.exists(db_path):
            return False
        
        try:
            # 确保备份目录存在
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            
            # 使用 SQLite 的在线备份 API
            with cls.get_connection(db_path) as source_conn:
                with sqlite3.connect(backup_path) as backup_conn:
                    source_conn.backup(backup_conn)
            logger.info(f"备份数据库成功: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"备份数据库失败 {db_path}: {e}")
            # 降级使用文件复制
            try:
                shutil.copy2(db_path, backup_path)
                logger.warning(f"使用文件复制备份: {backup_path}")
                return True
            except Exception as e2:
                logger.error(f"文件复制备份也失败: {e2}")
                return False
    
    # ========== 通用数据库操作方法 ==========
    
    @staticmethod
    def read_value(db_path: str, table: str, key_column: str, 
                   key_value: str, value_column: str) -> Optional[Any]:
        """
        从 SQLite 数据库读取值
        
        Args:
            db_path: 数据库文件路径
            table: 表名
            key_column: 键列名
            key_value: 键值
            value_column: 值列名
        
        Returns:
            查询结果，失败返回 None
        """
        if not os.path.exists(db_path):
            return None
        
        try:
            with SqliteUtil.get_connection(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    f"SELECT {value_column} FROM {table} WHERE {key_column} = ?",
                    (key_value,)
                )
                result = cursor.fetchone()
                return result[0] if result else None
        except (sqlite3.Error, IndexError) as e:
            logger.error(f"读取数据库失败 {db_path}: {e}")
            return None
    
    @staticmethod
    def write_value(db_path: str, table: str, key_column: str, 
                    key_value: str, value_column: str, value: Any) -> bool:
        """
        向 SQLite 数据库写入或更新值
        
        Args:
            db_path: 数据库文件路径
            table: 表名
            key_column: 键列名
            key_value: 键值
            value_column: 值列名
            value: 要写入的值
        
        Returns:
            是否成功
        """
        if not os.path.exists(db_path):
            return False
        
        try:
            with SqliteUtil.get_connection(db_path) as conn:
                cursor = conn.cursor()
                
                # 检查是否存在
                cursor.execute(
                    f"SELECT 1 FROM {table} WHERE {key_column} = ?",
                    (key_value,)
                )
                exists = cursor.fetchone()
                
                if exists:
                    # 更新
                    cursor.execute(
                        f"UPDATE {table} SET {value_column} = ? WHERE {key_column} = ?",
                        (value, key_value)
                    )
                else:
                    # 插入
                    cursor.execute(
                        f"INSERT INTO {table} ({key_column}, {value_column}) VALUES (?, ?)",
                        (key_value, value)
                    )
                
                conn.commit()
                return True
        except sqlite3.Error as e:
            logger.error(f"写入数据库失败 {db_path}: {e}")
            return False
    
    @staticmethod
    def query_all(db_path: str, table: str, key_column: str, 
                  value_column: str, condition: str = None) -> List[tuple]:
        """
        查询数据库中的所有记录
        
        Args:
            db_path: 数据库文件路径
            table: 表名
            key_column: 键列名
            value_column: 值列名
            condition: WHERE 条件（可选）
        
        Returns:
            查询结果列表
        """
        if not os.path.exists(db_path):
            return []
        
        try:
            with SqliteUtil.get_connection(db_path) as conn:
                cursor = conn.cursor()
                
                query = f"SELECT {key_column}, {value_column} FROM {table}"
                if condition:
                    query += f" WHERE {condition}"
                
                cursor.execute(query)
                results = cursor.fetchall()
                return results
        except sqlite3.Error as e:
            logger.error(f"查询数据库失败 {db_path}: {e}")
            return []
    
    @staticmethod
    def execute_query(db_path: str, query: str, params: tuple = None) -> Optional[List[tuple]]:
        """
        执行自定义 SQL 查询
        
        Args:
            db_path: 数据库文件路径
            query: SQL 查询语句
            params: 查询参数（可选）
        
        Returns:
            查询结果列表，失败返回 None
        """
        if not os.path.exists(db_path):
            return None
        
        try:
            with SqliteUtil.get_connection(db_path) as conn:
                cursor = conn.cursor()
                
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                results = cursor.fetchall()
                return results
        except sqlite3.Error as e:
            logger.error(f"执行查询失败 {db_path}: {e}")
            return None
    
    @staticmethod
    def execute_update(db_path: str, query: str, params: tuple = None) -> bool:
        """
        执行更新操作（INSERT/UPDATE/DELETE）
        
        Args:
            db_path: 数据库文件路径
            query: SQL 语句
            params: 参数（可选）
        
        Returns:
            是否成功
        """
        if not os.path.exists(db_path):
            return False
        
        try:
            with SqliteUtil.get_connection(db_path) as conn:
                cursor = conn.cursor()
                
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                conn.commit()
                return True
        except sqlite3.Error as e:
            logger.error(f"执行更新失败 {db_path}: {e}")
            return False
    
    # ========== Cursor 专用方法 ==========
    
    @classmethod
    def read_cursor_value(cls, db_path: str, key: str) -> Optional[str]:
        """
        从 Cursor state.vscdb 读取值（简化版）
        
        Args:
            db_path: state.vscdb 数据库路径
            key: 键名
        
        Returns:
            值，失败返回 None
        """
        return cls.read_value(db_path, cls.CURSOR_TABLE_NAME, 
                            cls.CURSOR_KEY_COLUMN, key, cls.CURSOR_VALUE_COLUMN)
    
    @classmethod
    def write_cursor_value(cls, db_path: str, key: str, value: str) -> bool:
        """
        写入值到 Cursor state.vscdb（简化版）
        
        Args:
            db_path: state.vscdb 数据库路径
            key: 键名
            value: 值
        
        Returns:
            是否成功
        """
        return cls.write_value(db_path, cls.CURSOR_TABLE_NAME,
                             cls.CURSOR_KEY_COLUMN, key, cls.CURSOR_VALUE_COLUMN, value)
    
    @classmethod
    def get_machine_ids(cls, db_path: str) -> Dict[str, Optional[str]]:
        """
        获取所有机器标识字段
        
        Args:
            db_path: state.vscdb 数据库路径
        
        Returns:
            机器标识字典
        """
        machine_ids = {}
        for key in cls.MACHINE_ID_KEYS:
            machine_ids[key] = cls.read_cursor_value(db_path, key)
        return machine_ids
    
    @classmethod
    def set_machine_ids(cls, db_path: str, machine_ids: Dict[str, str]) -> bool:
        """
        批量设置机器标识字段（优化版：单次连接）
        
        Args:
            db_path: state.vscdb 数据库路径
            machine_ids: 机器标识字典（key为完整的键名）
        
        Returns:
            是否全部成功
        """
        if not os.path.exists(db_path):
            return False
        
        try:
            with cls.get_connection(db_path) as conn:
                cursor = conn.cursor()
                
                for key, value in machine_ids.items():
                    if value and key in cls.MACHINE_ID_KEYS:
                        # 检查是否存在
                        cursor.execute(
                            f"SELECT 1 FROM {cls.CURSOR_TABLE_NAME} WHERE {cls.CURSOR_KEY_COLUMN} = ?",
                            (key,)
                        )
                        exists = cursor.fetchone()
                        
                        if exists:
                            cursor.execute(
                                f"UPDATE {cls.CURSOR_TABLE_NAME} SET {cls.CURSOR_VALUE_COLUMN} = ? WHERE {cls.CURSOR_KEY_COLUMN} = ?",
                                (value, key)
                            )
                        else:
                            cursor.execute(
                                f"INSERT INTO {cls.CURSOR_TABLE_NAME} ({cls.CURSOR_KEY_COLUMN}, {cls.CURSOR_VALUE_COLUMN}) VALUES (?, ?)",
                                (key, value)
                            )
                
                conn.commit()
                logger.info(f"批量设置机器标识成功")
                return True
        except sqlite3.Error as e:
            logger.error(f"批量设置机器标识失败 {db_path}: {e}")
            return False
    
    @classmethod
    def get_auth_info(cls, db_path: str) -> Dict[str, Optional[str]]:
        """
        获取所有账号认证字段
        
        Args:
            db_path: state.vscdb 数据库路径
        
        Returns:
            认证信息字典
        """
        auth_info = {}
        for key in cls.AUTH_KEYS:
            auth_info[key] = cls.read_cursor_value(db_path, key)
        return auth_info
    
    @classmethod
    def set_auth_info(cls, db_path: str, auth_info: Dict[str, str]) -> bool:
        """
        批量设置账号认证字段（优化版：单次连接）
        
        Args:
            db_path: state.vscdb 数据库路径
            auth_info: 认证信息字典（key为完整的键名）
        
        Returns:
            是否全部成功
        """
        if not os.path.exists(db_path):
            return False
        
        try:
            with cls.get_connection(db_path) as conn:
                cursor = conn.cursor()
                
                for key, value in auth_info.items():
                    if value and key in cls.AUTH_KEYS:
                        # 检查是否存在
                        cursor.execute(
                            f"SELECT 1 FROM {cls.CURSOR_TABLE_NAME} WHERE {cls.CURSOR_KEY_COLUMN} = ?",
                            (key,)
                        )
                        exists = cursor.fetchone()
                        
                        if exists:
                            cursor.execute(
                                f"UPDATE {cls.CURSOR_TABLE_NAME} SET {cls.CURSOR_VALUE_COLUMN} = ? WHERE {cls.CURSOR_KEY_COLUMN} = ?",
                                (value, key)
                            )
                        else:
                            cursor.execute(
                                f"INSERT INTO {cls.CURSOR_TABLE_NAME} ({cls.CURSOR_KEY_COLUMN}, {cls.CURSOR_VALUE_COLUMN}) VALUES (?, ?)",
                                (key, value)
                            )
                
                conn.commit()
                logger.info(f"批量设置认证信息成功")
                return True
        except sqlite3.Error as e:
            logger.error(f"批量设置认证信息失败 {db_path}: {e}")
            return False
    
    @classmethod
    def clear_auth_info(cls, db_path: str) -> bool:
        """
        清空所有账号认证字段（用于登出）
        
        Args:
            db_path: state.vscdb 数据库路径
        
        Returns:
            是否成功
        """
        if not os.path.exists(db_path):
            return False
        
        try:
            with cls.get_connection(db_path) as conn:
                cursor = conn.cursor()
                
                for key in cls.AUTH_KEYS:
                    cursor.execute(
                        f"DELETE FROM {cls.CURSOR_TABLE_NAME} WHERE {cls.CURSOR_KEY_COLUMN} = ?",
                        (key,)
                    )
                
                conn.commit()
                logger.info(f"清空认证信息成功")
                return True
        except sqlite3.Error as e:
            logger.error(f"清空认证信息失败 {db_path}: {e}")
            return False
    
    @classmethod
    def get_all_keys(cls, db_path: str) -> List[str]:
        """
        获取数据库中所有的键名
        
        Args:
            db_path: state.vscdb 数据库路径
        
        Returns:
            键名列表
        """
        if not os.path.exists(db_path):
            return []
        
        try:
            with cls.get_connection(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT {cls.CURSOR_KEY_COLUMN} FROM {cls.CURSOR_TABLE_NAME}")
                results = cursor.fetchall()
                return [row[0] for row in results]
        except sqlite3.Error as e:
            logger.error(f"获取所有键失败 {db_path}: {e}")
            return []
