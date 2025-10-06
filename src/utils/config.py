# -*- coding: utf-8 -*-
"""
配置管理模块
"""

import json
import os
from typing import Any, Dict


class Config:
    """配置管理类"""
    
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.config_data = {}
        self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config_data = json.load(f)
            except Exception as e:
                print(f"加载配置文件失败: {e}")
                self.config_data = self.get_default_config()
        else:
            self.config_data = self.get_default_config()
            self.save_config()
    
    def save_config(self):
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"保存配置文件失败: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        return self.config_data.get(key, default)
    
    def set(self, key: str, value: Any):
        """设置配置值"""
        self.config_data[key] = value
        self.save_config()
    
    @staticmethod
    def get_default_config() -> Dict:
        """获取默认配置"""
        return {
            "app_name": "CursorUnlimited",
            "version": "0.1.0",
            "database": {
                "type": "sqlite",
                "path": "data/accounts.db"
            },
            "automation": {
                "browser": "chromium",
                "headless": False,
                "timeout": 30000
            },
            "security": {
                "encryption_enabled": True,
                "auto_lock": False
            }
        }
