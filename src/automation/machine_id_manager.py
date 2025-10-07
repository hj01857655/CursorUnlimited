# -*- coding: utf-8 -*-
"""
Cursor 机器标识管理模块
用于生成、重置和切换机器标识，实现多机器切换
"""

import uuid
import hashlib
import random
import os
from datetime import datetime
from typing import Dict, Optional
from .config_manager import CursorConfigManager
from ..utils.logger import get_logger

logger = get_logger(__name__)


class MachineIdManager:
    """机器标识管理器"""
    
    def __init__(self, config_manager: CursorConfigManager = None):
        self.config_manager = config_manager or CursorConfigManager()
        logger.debug("初始化 MachineIdManager")
    
    @staticmethod
    def generate_uuid() -> str:
        """生成标准UUID"""
        return str(uuid.uuid4())
    
    @staticmethod
    def generate_machine_id() -> str:
        """生成类似Cursor的machineId（SHA256哈希）"""
        random_bytes = os.urandom(32)
        return hashlib.sha256(random_bytes).hexdigest()
    
    @staticmethod
    def generate_mac_machine_id() -> str:
        """生成类似Cursor的macMachineId（长SHA256哈希）"""
        # 生成一个更长的哈希值
        random_bytes = os.urandom(64)
        return hashlib.sha256(random_bytes).hexdigest() + hashlib.sha256(os.urandom(64)).hexdigest()
    
    @staticmethod
    def generate_sqm_id() -> str:
        """生成Windows SQM格式的GUID"""
        guid = str(uuid.uuid4()).upper()
        return f"{{{guid}}}"
    
    def generate_new_machine_ids(self, include_timestamps: bool = False) -> Dict[str, str]:
        """
        生成一套新的机器标识
        
        Args:
            include_timestamps: 是否包含时间戳字段
        
        Returns:
            机器标识字典
        """
        logger.info("生成新的机器标识")
        machine_ids = {
            'serviceMachineId': self.generate_uuid(),
            'machineId': self.generate_machine_id(),
            'macMachineId': self.generate_mac_machine_id(),
            'devDeviceId': self.generate_uuid(),
            'sqmId': self.generate_sqm_id()
        }
        logger.debug(f"生成的机器标识: serviceMachineId={machine_ids['serviceMachineId']}")
        
        # TODO: 时间戳字段暂时不用，因为它们只在 state.vscdb 中
        # if include_timestamps:
        #     current_time = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        #     machine_ids['firstSessionDate'] = current_time
        #     machine_ids['currentSessionDate'] = current_time
        #     machine_ids['lastSessionDate'] = current_time
        
        return machine_ids
    
    def get_current_machine_ids(self, include_timestamps: bool = False) -> Dict[str, str]:
        """
        获取当前的机器标识
        
        Args:
            include_timestamps: 是否包含时间戳字段
        
        Returns:
            机器标识字典
        """
        logger.debug("获取当前机器标识")
        # 从 storage.json 读取机器标识
        storage = self.config_manager.read_storage()
        machine_ids = {
            'serviceMachineId': storage.get('storage.serviceMachineId'),
            'machineId': storage.get('telemetry.machineId'),
            'macMachineId': storage.get('telemetry.macMachineId'),
            'devDeviceId': storage.get('telemetry.devDeviceId'),
            'sqmId': storage.get('telemetry.sqmId')
        }
        
        # TODO: 数据库时间戳暂时不读取
        # if include_timestamps:
        #     machine_ids['firstSessionDate'] = self.config_manager.read_vscdb_value('telemetry.firstSessionDate')
        #     machine_ids['currentSessionDate'] = self.config_manager.read_vscdb_value('telemetry.currentSessionDate')
        #     machine_ids['lastSessionDate'] = self.config_manager.read_vscdb_value('telemetry.lastSessionDate')
        
        return machine_ids
    
    def apply_machine_ids(self, machine_ids: Dict[str, str], sync_to_vscdb: bool = False) -> bool:
        """
        应用机器标识到配置文件
        
        Args:
            machine_ids: 机器标识字典
            sync_to_vscdb: 是否同步到state.vscdb数据库
        
        Returns:
            是否成功
        """
        logger.info("应用机器标识到配置文件")
        # 更新storage.json
        storage = self.config_manager.read_storage()
        
        if 'serviceMachineId' in machine_ids and machine_ids['serviceMachineId']:
            storage['storage.serviceMachineId'] = machine_ids['serviceMachineId']
        if 'machineId' in machine_ids and machine_ids['machineId']:
            storage['telemetry.machineId'] = machine_ids['machineId']
        if 'macMachineId' in machine_ids and machine_ids['macMachineId']:
            storage['telemetry.macMachineId'] = machine_ids['macMachineId']
        if 'devDeviceId' in machine_ids and machine_ids['devDeviceId']:
            storage['telemetry.devDeviceId'] = machine_ids['devDeviceId']
        if 'sqmId' in machine_ids and machine_ids['sqmId']:
            storage['telemetry.sqmId'] = machine_ids['sqmId']
        
        success = self.config_manager.write_storage(storage)
        
        if success:
            logger.info("成功应用机器标识")
        else:
            logger.error("应用机器标识失败")
        
        # TODO: state.vscdb 同步暂时禁用
        # if success and sync_to_vscdb:
        #     for key, value in machine_ids.items():
        #         if value:
        #             # 映射到vscdb中的key格式
        #             if key == 'serviceMachineId':
        #                 vscdb_key = 'storage.serviceMachineId'
        #             elif key == 'machineId':
        #                 vscdb_key = 'telemetry.machineId'
        #             elif key == 'macMachineId':
        #                 vscdb_key = 'telemetry.macMachineId'
        #             elif key == 'devDeviceId':
        #                 vscdb_key = 'telemetry.devDeviceId'
        #             elif key == 'sqmId':
        #                 vscdb_key = 'telemetry.sqmId'
        #             elif key == 'firstSessionDate':
        #                 vscdb_key = 'telemetry.firstSessionDate'
        #             elif key == 'currentSessionDate':
        #                 vscdb_key = 'telemetry.currentSessionDate'
        #             elif key == 'lastSessionDate':
        #                 vscdb_key = 'telemetry.lastSessionDate'
        #             else:
        #                 continue
        #             
        #             self.config_manager.write_vscdb_value(vscdb_key, value)
        
        return success
    
    def reset_machine_ids(self, sync_to_vscdb: bool = False) -> Dict[str, str]:
        """
        重置机器标识为全新的随机值
        
        Args:
            sync_to_vscdb: 是否同步到state.vscdb数据库
        
        Returns:
            新生成的机器标识字典
        """
        logger.info("重置机器标识")
        new_ids = self.generate_new_machine_ids()
        self.apply_machine_ids(new_ids, sync_to_vscdb)
        logger.info("机器标识重置成功")
        return new_ids
    
    def backup_machine_ids(self, backup_name: str) -> Dict[str, str]:
        """
        备份当前的机器标识
        
        Args:
            backup_name: 备份名称
        
        Returns:
            当前的机器标识
        """
        logger.info(f"备份机器标识: {backup_name}")
        current_ids = self.get_current_machine_ids()
        
        # 保存到备份目录
        backup_dir = os.path.join(self.config_manager.backup_dir, backup_name)
        os.makedirs(backup_dir, exist_ok=True)
        
        import json
        backup_file = os.path.join(backup_dir, 'machine_ids.json')
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(current_ids, f, ensure_ascii=False, indent=2)
        
        logger.info(f"机器标识备份成功: {backup_file}")
        return current_ids
    
    def restore_machine_ids(self, backup_name: str, sync_to_vscdb: bool = False) -> bool:
        """
        从备份恢复机器标识
        
        Args:
            backup_name: 备份名称
            sync_to_vscdb: 是否同步到state.vscdb数据库
        
        Returns:
            是否成功
        """
        import json
        backup_file = os.path.join(self.config_manager.backup_dir, backup_name, 'machine_ids.json')
        
            if not os.path.exists(backup_file):
                logger.error(f"备份不存在: {backup_name}")
                return False
        
        try:
            logger.info(f"从备份恢复机器标识: {backup_name}")
            with open(backup_file, 'r', encoding='utf-8') as f:
                machine_ids = json.load(f)
            
            success = self.apply_machine_ids(machine_ids, sync_to_vscdb)
            if success:
                logger.info(f"成功恢复机器标识: {backup_name}")
            else:
                logger.error(f"恢复机器标识失败: {backup_name}")
            return success
        except Exception as e:
            logger.error(f"恢复机器标识失败: {e}")
            return False
    
    def create_machine_profile(self, profile_name: str) -> Dict[str, str]:
        """
        创建一个新的机器配置文件
        
        Args:
            profile_name: 配置文件名称
        
        Returns:
            生成的机器标识
        """
        logger.info(f"创建机器配置文件: {profile_name}")
        machine_ids = self.generate_new_machine_ids()
        
        # 保存配置文件
        profiles_dir = os.path.join(
            os.path.dirname(__file__), '..', '..', 'data', 'machine_profiles'
        )
        os.makedirs(profiles_dir, exist_ok=True)
        
        import json
        profile_file = os.path.join(profiles_dir, f'{profile_name}.json')
        with open(profile_file, 'w', encoding='utf-8') as f:
            json.dump(machine_ids, f, ensure_ascii=False, indent=2)
        
        logger.info(f"成功创建机器配置文件: {profile_file}")
        return machine_ids
    
    def load_machine_profile(self, profile_name: str, apply: bool = True) -> Optional[Dict[str, str]]:
        """
        加载机器配置文件
        
        Args:
            profile_name: 配置文件名称
            apply: 是否立即应用
        
        Returns:
            机器标识字典，如果不存在则返回None
        """
        import json
        profiles_dir = os.path.join(
            os.path.dirname(__file__), '..', '..', 'data', 'machine_profiles'
        )
        profile_file = os.path.join(profiles_dir, f'{profile_name}.json')
        
        if not os.path.exists(profile_file):
            logger.error(f"配置文件不存在: {profile_name}")
            return None
        
        try:
            logger.info(f"加载机器配置文件: {profile_name}")
            with open(profile_file, 'r', encoding='utf-8') as f:
                machine_ids = json.load(f)
            
            if apply:
                logger.debug(f"立即应用配置文件: {profile_name}")
                self.apply_machine_ids(machine_ids)
            
            logger.info(f"成功加载配置文件: {profile_name}")
            return machine_ids
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            return None
    
    def list_machine_profiles(self) -> list:
        """列出所有机器配置文件"""
        profiles_dir = os.path.join(
            os.path.dirname(__file__), '..', '..', 'data', 'machine_profiles'
        )
        
        if not os.path.exists(profiles_dir):
            logger.debug(f"配置文件目录不存在: {profiles_dir}")
            return []
        
        profiles = []
        for filename in os.listdir(profiles_dir):
            if filename.endswith('.json'):
                profiles.append(filename[:-5])  # 去掉.json后缀
        
        logger.debug(f"找到 {len(profiles)} 个机器配置文件")
        return profiles
    
    def delete_machine_profile(self, profile_name: str) -> bool:
        """删除机器配置文件"""
        profiles_dir = os.path.join(
            os.path.dirname(__file__), '..', '..', 'data', 'machine_profiles'
        )
        profile_file = os.path.join(profiles_dir, f'{profile_name}.json')
        
        if not os.path.exists(profile_file):
            logger.warning(f"配置文件不存在，无法删除: {profile_name}")
            return False
        
        try:
            os.remove(profile_file)
            logger.info(f"成功删除配置文件: {profile_name}")
            return True
        except Exception as e:
            logger.error(f"删除配置文件失败: {e}")
            return False
