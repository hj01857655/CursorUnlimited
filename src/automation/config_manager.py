# -*- coding: utf-8 -*-
"""
Cursor 配置文件管理模块
"""

import json
import os
import shutil
from typing import Dict, Optional
from pathlib import Path


class CursorConfigManager:
    """Cursor配置文件管理器"""
    
    def __init__(self, cursor_data_path: str = None):
        if cursor_data_path is None:
            cursor_data_path = os.path.join(os.environ.get('APPDATA', ''), 'Cursor')
        
        self.cursor_data_path = cursor_data_path
        self.storage_json_path = os.path.join(cursor_data_path, 'User', 'globalStorage', 'storage.json')
        self.machineid_path = os.path.join(cursor_data_path, 'machineid')
        self.backup_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'backups')
        
        # 确保备份目录存在
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def read_storage(self) -> Dict:
        """读取storage.json文件"""
        if not os.path.exists(self.storage_json_path):
            return {}
        
        with open(self.storage_json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def write_storage(self, data: Dict) -> bool:
        """写入storage.json文件"""
        try:
            # 备份原文件
            if os.path.exists(self.storage_json_path):
                backup_path = self.storage_json_path + '.bak'
                shutil.copy2(self.storage_json_path, backup_path)
            
            with open(self.storage_json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"写入storage.json失败: {e}")
            return False
    
    def get_current_account_info(self) -> Optional[Dict]:
        """获取当前登录账号信息"""
        storage = self.read_storage()
        
        if not storage:
            return None
        
        return {
            'email': storage.get('cursor.email') or storage.get('cursorAuth/cachedEmail'),
            'access_token': storage.get('cursor.accessToken') or storage.get('cursorAuth/accessToken'),
            'refresh_token': storage.get('cursorAuth/refreshToken'),
            'machine_id': storage.get('storage.serviceMachineId'),
            'device_id': self.read_machine_id()
        }
    
    def set_account_tokens(self, email: str, access_token: str, refresh_token: str = None) -> bool:
        """设置账号token"""
        if refresh_token is None:
            refresh_token = access_token
        
        storage = self.read_storage()
        
        # 更新token信息
        storage['cursor.accessToken'] = access_token
        storage['cursor.email'] = email
        storage['cursorAuth/accessToken'] = access_token
        storage['cursorAuth/cachedEmail'] = email
        storage['cursorAuth/refreshToken'] = refresh_token
        
        return self.write_storage(storage)
    
    def read_machine_id(self) -> Optional[str]:
        """读取机器ID"""
        if not os.path.exists(self.machineid_path):
            return None
        
        with open(self.machineid_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    
    def write_machine_id(self, machine_id: str) -> bool:
        """写入机器ID"""
        try:
            with open(self.machineid_path, 'w', encoding='utf-8') as f:
                f.write(machine_id)
            return True
        except Exception as e:
            print(f"写入machineid失败: {e}")
            return False
    
    def backup_config(self, backup_name: str) -> bool:
        """备份当前配置"""
        try:
            backup_path = os.path.join(self.backup_dir, backup_name)
            os.makedirs(backup_path, exist_ok=True)
            
            # 备份storage.json
            if os.path.exists(self.storage_json_path):
                shutil.copy2(self.storage_json_path, os.path.join(backup_path, 'storage.json'))
            
            # 备份machineid
            if os.path.exists(self.machineid_path):
                shutil.copy2(self.machineid_path, os.path.join(backup_path, 'machineid'))
            
            return True
        except Exception as e:
            print(f"备份配置失败: {e}")
            return False
    
    def restore_config(self, backup_name: str) -> bool:
        """恢复配置"""
        try:
            backup_path = os.path.join(self.backup_dir, backup_name)
            
            if not os.path.exists(backup_path):
                print(f"备份不存在: {backup_name}")
                return False
            
            # 恢复storage.json
            storage_backup = os.path.join(backup_path, 'storage.json')
            if os.path.exists(storage_backup):
                shutil.copy2(storage_backup, self.storage_json_path)
            
            # 恢复machineid
            machineid_backup = os.path.join(backup_path, 'machineid')
            if os.path.exists(machineid_backup):
                shutil.copy2(machineid_backup, self.machineid_path)
            
            return True
        except Exception as e:
            print(f"恢复配置失败: {e}")
            return False
    
    def list_backups(self) -> list:
        """列出所有备份"""
        if not os.path.exists(self.backup_dir):
            return []
        
        return [d for d in os.listdir(self.backup_dir) if os.path.isdir(os.path.join(self.backup_dir, d))]
    
    def clear_all_tokens(self) -> bool:
        """清空所有token（登出）"""
        storage = self.read_storage()
        
        # 清除token相关字段
        keys_to_remove = [
            'cursor.accessToken',
            'cursor.email',
            'cursorAuth/accessToken',
            'cursorAuth/cachedEmail',
            'cursorAuth/refreshToken'
        ]
        
        for key in keys_to_remove:
            if key in storage:
                del storage[key]
        
        return self.write_storage(storage)
