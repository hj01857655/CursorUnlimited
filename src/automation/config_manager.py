# -*- coding: utf-8 -*-
"""
Cursor 配置文件管理模块
"""

import json
import os
import shutil
import sqlite3
from typing import Dict, Optional, List
from pathlib import Path
from ..utils.logger import get_logger

logger = get_logger(__name__)


class CursorConfigManager:
    """Cursor配置文件管理器"""
    
    def __init__(self, cursor_data_path: str = None):
        if cursor_data_path is None:
            cursor_data_path = os.path.join(os.environ.get('APPDATA', ''), 'Cursor')
        
        self.cursor_data_path = cursor_data_path
        self.global_storage_path = os.path.join(cursor_data_path, 'User', 'globalStorage')
        self.storage_json_path = os.path.join(self.global_storage_path, 'storage.json')
        self.state_vscdb_path = os.path.join(self.global_storage_path, 'state.vscdb')
        self.retrieval_dir = os.path.join(self.global_storage_path, 'anysphere.cursor-retrieval')
        self.machineid_path = os.path.join(cursor_data_path, 'machineid')
        self.backup_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'backups')
        
        logger.debug(f"初始化 CursorConfigManager, cursor_data_path={cursor_data_path}")
        
        # 确保备份目录存在
        os.makedirs(self.backup_dir, exist_ok=True)
        logger.debug(f"备份目录: {self.backup_dir}")
    
    def read_storage(self) -> Dict:
        """读取storage.json文件"""
        if not os.path.exists(self.storage_json_path):
            logger.warning(f"storage.json 不存在: {self.storage_json_path}")
            return {}
        
        try:
            with open(self.storage_json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.debug(f"成功读取 storage.json, 包含 {len(data)} 个键")
                return data
        except Exception as e:
            logger.error(f"读取 storage.json 失败: {e}")
            return {}
    
    def write_storage(self, data: Dict) -> bool:
        """写入storage.json文件"""
        try:
            # 备份原文件
            if os.path.exists(self.storage_json_path):
                backup_path = self.storage_json_path + '.bak'
                shutil.copy2(self.storage_json_path, backup_path)
                logger.debug(f"已备份原 storage.json 到 {backup_path}")
            
            with open(self.storage_json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"成功写入 storage.json, {len(data)} 个键")
            return True
        except Exception as e:
            logger.error(f"写入 storage.json 失败: {e}")
            return False
    
    def get_current_account_info(self) -> Optional[Dict]:
        """获取当前登录账号信息（从 cursorAuth/* 字段读取）"""
        storage = self.read_storage()
        
        if not storage:
            logger.debug("storage 为空，无法获取账号信息")
            return None
        
        account_info = {
            'email': storage.get('cursorAuth/cachedEmail'),
            'access_token': storage.get('cursorAuth/accessToken'),
            'refresh_token': storage.get('cursorAuth/refreshToken'),
            'machine_id': storage.get('storage.serviceMachineId'),
            'device_id': self.read_machine_id()
        }
        
        email = account_info.get('email')
        if email:
            logger.debug(f"获取到当前账号信息: {email}")
        else:
            logger.debug("未找到当前登录的账号")
        
        return account_info
    
    def set_account_tokens(self, email: str, access_token: str, refresh_token: str = None) -> bool:
        """设置账号token（只设置 Cursor 官方的 cursorAuth/* 字段）"""
        if refresh_token is None:
            refresh_token = access_token
        
        logger.info(f"设置账号 token: {email}")
        storage = self.read_storage()
        
        # 更新 Cursor 官方认证字段
        storage['cursorAuth/accessToken'] = access_token
        storage['cursorAuth/cachedEmail'] = email
        storage['cursorAuth/refreshToken'] = refresh_token
        
        success = self.write_storage(storage)
        if success:
            logger.info(f"成功设置账号 {email} 的 token")
        else:
            logger.error(f"设置账号 {email} 的 token 失败")
        
        return success
    
    def read_account_json(self) -> list:
        """读取account.json文件（账号列表）"""
        account_json_path = os.path.join(self.cursor_data_path, 'User', 'globalStorage', 'account.json')
        
        if not os.path.exists(account_json_path):
            return []
        
        try:
            with open(account_json_path, 'r', encoding='utf-8') as f:
                accounts = json.load(f)
                logger.debug(f"读取 account.json 成功，包含 {len(accounts)} 个账号")
                return accounts
        except Exception as e:
            logger.error(f"读取 account.json 失败: {e}")
            return []
    
    def write_account_json(self, accounts: list) -> bool:
        """写入account.json文件"""
        account_json_path = os.path.join(self.cursor_data_path, 'User', 'globalStorage', 'account.json')
        
        try:
            # 备份原文件
            if os.path.exists(account_json_path):
                backup_path = account_json_path + '.bak'
                shutil.copy2(account_json_path, backup_path)
            
            with open(account_json_path, 'w', encoding='utf-8') as f:
                json.dump(accounts, f, ensure_ascii=False, indent=2)
            
            logger.info(f"成功写入 account.json，{len(accounts)} 个账号")
            return True
        except Exception as e:
            logger.error(f"写入 account.json 失败: {e}")
            return False
    
    def add_account_to_list(self, email: str, token: str, refresh_token: str = None, 
                           workos_token: str = None, set_as_current: bool = True) -> bool:
        """添加账号到account.json列表"""
        logger.info(f"添加账号到列表: {email}, 设为当前: {set_as_current}")
        accounts = self.read_account_json()
        
        # 检查是否已存在
        for acc in accounts:
            if acc.get('email') == email:
                # 更新现有账号
                logger.debug(f"账号 {email} 已存在，更新信息")
                acc['token'] = token
                acc['refresh_token'] = refresh_token or token
                if workos_token:
                    acc['workos_cursor_session_token'] = workos_token
                if set_as_current:
                    acc['is_current'] = True
                    # 取消其他账号的current标记
                    for other in accounts:
                        if other.get('email') != email:
                            other['is_current'] = False
                return self.write_account_json(accounts)
        
        # 添加新账号
        from datetime import datetime
        logger.debug(f"添加新账号 {email} 到列表")
        new_account = {
            'email': email,
            'token': token,
            'refresh_token': refresh_token or token,
            'is_current': set_as_current,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        if workos_token:
            new_account['workos_cursor_session_token'] = workos_token
        
        # 如果设为当前账号，取消其他账号的current标记
        if set_as_current:
            for acc in accounts:
                acc['is_current'] = False
        
        accounts.append(new_account)
        return self.write_account_json(accounts)
    
    def get_current_account_from_list(self) -> Optional[Dict]:
        """从account.json获取当前账号"""
        accounts = self.read_account_json()
        for acc in accounts:
            if acc.get('is_current', False):
                return acc
        return None
    
    def read_machine_id(self) -> Optional[str]:
        """读取机器ID"""
        if not os.path.exists(self.machineid_path):
            logger.debug(f"machineid 文件不存在: {self.machineid_path}")
            return None
        
        try:
            with open(self.machineid_path, 'r', encoding='utf-8') as f:
                machine_id = f.read().strip()
                logger.debug(f"读取到 machineid: {machine_id[:8]}..." if machine_id else "machineid 文件为空")
                return machine_id
        except Exception as e:
            logger.error(f"读取 machineid 失败: {e}")
            return None
    
    def write_machine_id(self, machine_id: str) -> bool:
        """写入机器ID"""
        try:
            with open(self.machineid_path, 'w', encoding='utf-8') as f:
                f.write(machine_id)
            logger.info(f"成功写入 machineid: {machine_id[:8]}...")
            return True
        except Exception as e:
            logger.error(f"写入 machineid 失败: {e}")
            return False
    
    def backup_config(self, backup_name: str) -> bool:
        """备份当前配置（排除account.json）"""
        logger.info(f"开始备份配置: {backup_name}")
        try:
            backup_path = os.path.join(self.backup_dir, backup_name)
            os.makedirs(backup_path, exist_ok=True)
            logger.debug(f"创建备份目录: {backup_path}")
            
            # 备份storage.json
            if os.path.exists(self.storage_json_path):
                shutil.copy2(self.storage_json_path, os.path.join(backup_path, 'storage.json'))
                logger.debug("已备份 storage.json")
            
            # 备份state.vscdb
            if os.path.exists(self.state_vscdb_path):
                shutil.copy2(self.state_vscdb_path, os.path.join(backup_path, 'state.vscdb'))
                logger.debug("已备份 state.vscdb")
            
            # 备份anysphere.cursor-retrieval目录
            if os.path.exists(self.retrieval_dir):
                retrieval_backup = os.path.join(backup_path, 'anysphere.cursor-retrieval')
                if os.path.exists(retrieval_backup):
                    shutil.rmtree(retrieval_backup)
                shutil.copytree(self.retrieval_dir, retrieval_backup)
                logger.debug("已备份 anysphere.cursor-retrieval 目录")
            
            # 备份machineid
            if os.path.exists(self.machineid_path):
                shutil.copy2(self.machineid_path, os.path.join(backup_path, 'machineid'))
                logger.debug("已备份 machineid")
            
            logger.info(f"配置备份成功: {backup_name}")
            return True
        except Exception as e:
            logger.error(f"备份配置失败: {e}")
            return False
    
    def restore_config(self, backup_name: str, restore_settings: bool = False) -> bool:
        """
        恢复配置（排除account.json）
        
        Args:
            backup_name: 备份名称
            restore_settings: 是否恢复用户设置（settings.json等）
        """
        try:
            backup_path = os.path.join(self.backup_dir, backup_name)
            
            if not os.path.exists(backup_path):
                logger.error(f"备份不存在: {backup_name}")
                return False
            
            # 恢复storage.json
            storage_backup = os.path.join(backup_path, 'storage.json')
            if os.path.exists(storage_backup):
                shutil.copy2(storage_backup, self.storage_json_path)
            
            # 恢复state.vscdb
            vscdb_backup = os.path.join(backup_path, 'state.vscdb')
            if os.path.exists(vscdb_backup):
                shutil.copy2(vscdb_backup, self.state_vscdb_path)
            
            # 恢复anysphere.cursor-retrieval目录
            retrieval_backup = os.path.join(backup_path, 'anysphere.cursor-retrieval')
            if os.path.exists(retrieval_backup):
                if os.path.exists(self.retrieval_dir):
                    shutil.rmtree(self.retrieval_dir)
                shutil.copytree(retrieval_backup, self.retrieval_dir)
            
            # 恢复machineid
            machineid_backup = os.path.join(backup_path, 'machineid')
            if os.path.exists(machineid_backup):
                shutil.copy2(machineid_backup, self.machineid_path)
            
            # 恢复用户设置（排除account.json）
            if restore_settings:
                user_dir = os.path.join(self.cursor_data_path, 'User')
                
                # 恢复settings.json
                settings_backup = os.path.join(backup_path, 'settings.json')
                if os.path.exists(settings_backup):
                    shutil.copy2(settings_backup, os.path.join(user_dir, 'settings.json'))
                
                # 恢复keybindings.json
                keybindings_backup = os.path.join(backup_path, 'keybindings.json')
                if os.path.exists(keybindings_backup):
                    shutil.copy2(keybindings_backup, os.path.join(user_dir, 'keybindings.json'))
            
            logger.info(f"配置恢复成功: {backup_name}")
            return True
        except Exception as e:
            logger.error(f"恢复配置失败: {e}")
            return False
    
    def list_backups(self) -> list:
        """列出所有备份"""
        if not os.path.exists(self.backup_dir):
            return []
        
        return [d for d in os.listdir(self.backup_dir) if os.path.isdir(os.path.join(self.backup_dir, d))]
    
    def clear_all_tokens(self) -> bool:
        """清空所有token（登出，只清除 Cursor 官方的 cursorAuth/* 字段）"""
        logger.info("清空所有 token")
        storage = self.read_storage()
        
        # 清除 Cursor 官方认证字段
        keys_to_remove = [
            'cursorAuth/accessToken',
            'cursorAuth/cachedEmail',
            'cursorAuth/refreshToken',
            'cursorAuth/cachedSignUpType',
            'cursorAuth/stripeMembershipType'
        ]
        
        removed_count = 0
        for key in keys_to_remove:
            if key in storage:
                del storage[key]
                removed_count += 1
        
        logger.debug(f"已清除 {removed_count} 个认证字段")
        return self.write_storage(storage)
    
    def read_vscdb_value(self, key: str) -> Optional[str]:
        """从state.vscdb读取指定key的值"""
        if not os.path.exists(self.state_vscdb_path):
            return None
        
        try:
            conn = sqlite3.connect(self.state_vscdb_path)
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM ItemTable WHERE key = ?", (key,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                logger.debug(f"从 vscdb 读取到 key={key} 的值")
            else:
                logger.debug(f"vscdb 中未找到 key={key}")
            
            return result[0] if result else None
        except Exception as e:
            logger.error(f"读取 vscdb 失败: {e}")
            return None
    
    def write_vscdb_value(self, key: str, value: str) -> bool:
        """写入或更新state.vscdb中的值"""
        if not os.path.exists(self.state_vscdb_path):
            return False
        
        try:
            conn = sqlite3.connect(self.state_vscdb_path)
            cursor = conn.cursor()
            
            # 检查key是否存在
            cursor.execute("SELECT 1 FROM ItemTable WHERE key = ?", (key,))
            exists = cursor.fetchone()
            
            if exists:
                cursor.execute("UPDATE ItemTable SET value = ? WHERE key = ?", (value, key))
            else:
                cursor.execute("INSERT INTO ItemTable (key, value) VALUES (?, ?)", (key, value))
            
            conn.commit()
            conn.close()
            
            logger.debug(f"成功写入 vscdb: key={key}")
            return True
        except Exception as e:
            logger.error(f"写入 vscdb 失败: {e}")
            return False
    
    # TODO: 机器标识管理移到 machine_id_manager.py
    # def get_machine_ids_from_storage(self) -> Dict[str, str]:
    #     """从storage.json获取所有机器标识"""
    #     storage = self.read_storage()
    #     return {
    #         'serviceMachineId': storage.get('storage.serviceMachineId'),
    #         'machineId': storage.get('telemetry.machineId'),
    #         'macMachineId': storage.get('telemetry.macMachineId'),
    #         'devDeviceId': storage.get('telemetry.devDeviceId'),
    #         'sqmId': storage.get('telemetry.sqmId')
    #     }
    
    # TODO: 机器标识管理移到 machine_id_manager.py
    # def set_machine_ids_in_storage(self, machine_ids: Dict[str, str]) -> bool:
    #     """在storage.json中设置机器标识"""
    #     storage = self.read_storage()
    #     
    #     if 'serviceMachineId' in machine_ids and machine_ids['serviceMachineId']:
    #         storage['storage.serviceMachineId'] = machine_ids['serviceMachineId']
    #     if 'machineId' in machine_ids and machine_ids['machineId']:
    #         storage['telemetry.machineId'] = machine_ids['machineId']
    #     if 'macMachineId' in machine_ids and machine_ids['macMachineId']:
    #         storage['telemetry.macMachineId'] = machine_ids['macMachineId']
    #     if 'devDeviceId' in machine_ids and machine_ids['devDeviceId']:
    #         storage['telemetry.devDeviceId'] = machine_ids['devDeviceId']
    #     if 'sqmId' in machine_ids and machine_ids['sqmId']:
    #         storage['telemetry.sqmId'] = machine_ids['sqmId']
    #     
    #     return self.write_storage(storage)
    
    def sync_account_to_vscdb(self, email: str, access_token: str, refresh_token: str = None,
                             signup_type: str = None, onboarding_date: str = None, 
                             membership_type: str = None) -> bool:
        """
        同步账号信息到state.vscdb数据库（Cursor官方的6个 cursorAuth/* 字段）
        
        Args:
            email: 邮箱地址
            access_token: 访问令牌
            refresh_token: 刷新令牌
            signup_type: 注册类型（如 Auth_0）
            onboarding_date: 入职日期
            membership_type: 会员类型（如 free, pro）
        
        Returns:
            是否成功
        """
        logger.info(f"同步账号信息到 vscdb: {email}")
        
        if refresh_token is None:
            refresh_token = access_token
        
        success = True
        # cursorAuth/* 字段 1-3：storage.json + state.vscdb
        success &= self.write_vscdb_value('cursorAuth/accessToken', access_token)
        success &= self.write_vscdb_value('cursorAuth/cachedEmail', email)
        success &= self.write_vscdb_value('cursorAuth/refreshToken', refresh_token)
        
        # cursorAuth/* 字段 4-6：只在 state.vscdb
        if signup_type:
            success &= self.write_vscdb_value('cursorAuth/cachedSignUpType', signup_type)
        if onboarding_date:
            success &= self.write_vscdb_value('cursorAuth/onboardingDate', onboarding_date)
        if membership_type:
            success &= self.write_vscdb_value('cursorAuth/stripeMembershipType', membership_type)
        
        if success:
            logger.info(f"成功同步账号 {email} 到 vscdb")
        else:
            logger.error(f"同步账号 {email} 到 vscdb 失败")
        
        return success
