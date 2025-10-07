"""
账号切换管理器模块
实现账号的快速切换、状态备份和恢复
"""

import os
import time
import json
from typing import Optional, Dict, Any, Tuple
from datetime import datetime

from src.database.database_manager import DatabaseManager
from src.database.models import Account
from src.automation.auth_manager import AuthManager
from src.automation.machine_id_manager import MachineIdManager
from src.automation.cursor_manager import CursorManager
from src.utils.logger import Logger

class AccountSwitcher:
    """账号切换管理器，协调各个组件实现账号切换"""
    
    def __init__(self):
        """初始化账号切换管理器"""
        self.logger = Logger(__name__)
        
        # 初始化各个管理器
        self.db_manager = DatabaseManager()
        self.auth_manager = AuthManager()
        self.machine_id_manager = MachineIdManager()
        self.cursor_manager = CursorManager()
        
        self.logger.info("账号切换管理器初始化完成")
    
    def get_current_account_info(self) -> Dict[str, Any]:
        """
        获取当前登录的账号信息
        
        Returns:
            包含当前账号信息的字典
        """
        self.logger.info("获取当前账号信息")
        
        try:
            # 获取当前认证信息
            auth_info = self.auth_manager.get_auth_info()
            
            # 获取当前机器标识
            machine_ids = self.machine_id_manager.get_machine_ids()
            
            current_info = {
                'auth_tokens': auth_info,
                'machine_ids': machine_ids,
                'timestamp': datetime.now().isoformat()
            }
            
            # 尝试从auth_info中提取邮箱
            email = None
            if auth_info:
                # 这里需要根据实际的token结构来提取邮箱
                # 暂时使用一个占位逻辑
                for key, value in auth_info.items():
                    if 'email' in str(value).lower():
                        # 尝试解析JWT或其他格式的token来获取邮箱
                        pass
            
            current_info['email'] = email
            
            self.logger.debug(f"当前账号信息: {current_info}")
            return current_info
            
        except Exception as e:
            self.logger.error(f"获取当前账号信息失败: {e}")
            return {}
    
    def backup_current_account(self, nickname: str = None, notes: str = None) -> Optional[Account]:
        """
        备份当前登录的账号信息到数据库
        
        Args:
            nickname: 账号昵称
            notes: 备注信息
        
        Returns:
            保存成功的Account对象，失败返回None
        """
        self.logger.info("开始备份当前账号")
        
        try:
            # 获取当前账号信息
            current_info = self.get_current_account_info()
            
            if not current_info or not current_info.get('auth_tokens'):
                self.logger.warning("无法获取当前账号认证信息")
                return None
            
            # 获取机器标识
            machine_ids = current_info.get('machine_ids', {})
            
            # 创建或更新账号记录
            # 这里需要一个方法来识别账号（比如从token中提取邮箱）
            email = current_info.get('email')
            
            if not email:
                # 如果无法自动获取邮箱，使用时间戳作为临时标识
                email = f"account_{datetime.now().strftime('%Y%m%d_%H%M%S')}@cursor.local"
                self.logger.warning(f"无法获取账号邮箱，使用临时标识: {email}")
            
            # 检查账号是否已存在
            existing_account = self.db_manager.get_account(email=email)
            
            if existing_account:
                # 更新现有账号
                success = self.db_manager.update_account(
                    email=email,
                    auth_tokens=current_info['auth_tokens'],
                    machine_id=machine_ids.get('machineId'),
                    telemetry_id=machine_ids.get('telemetryMachineId'),
                    sqm_id=machine_ids.get('sqmId'),
                    dev_device_id=machine_ids.get('devDeviceId'),
                    mac_machine_id=machine_ids.get('macMachineId'),
                    nickname=nickname or existing_account.nickname,
                    notes=notes or existing_account.notes,
                    is_active=True
                )
                
                if success:
                    self.logger.info(f"成功更新账号备份: {email}")
                    return self.db_manager.get_account(email=email)
                else:
                    self.logger.error("更新账号备份失败")
                    return None
            else:
                # 创建新账号
                account = self.db_manager.add_account(
                    email=email,
                    password="",  # 密码字段暂时为空
                    auth_tokens=current_info['auth_tokens'],
                    machine_id=machine_ids.get('machineId'),
                    telemetry_id=machine_ids.get('telemetryMachineId'),
                    sqm_id=machine_ids.get('sqmId'),
                    dev_device_id=machine_ids.get('devDeviceId'),
                    mac_machine_id=machine_ids.get('macMachineId'),
                    nickname=nickname or email.split('@')[0],
                    notes=notes,
                    is_active=True
                )
                
                if account:
                    self.logger.info(f"成功创建账号备份: {email}")
                    return account
                else:
                    self.logger.error("创建账号备份失败")
                    return None
                    
        except Exception as e:
            self.logger.error(f"备份账号失败: {e}")
            return None
    
    def switch_account(self, 
                       account_id: int = None, 
                       email: str = None,
                       backup_current: bool = True) -> Tuple[bool, str]:
        """
        切换到指定账号
        
        Args:
            account_id: 目标账号ID
            email: 目标账号邮箱
            backup_current: 是否备份当前账号
        
        Returns:
            (成功标志, 消息)
        """
        self.logger.info(f"开始切换账号: ID={account_id}, Email={email}")
        
        try:
            # 获取目标账号
            target_account = self.db_manager.get_account(account_id=account_id, email=email)
            
            if not target_account:
                msg = f"目标账号不存在: ID={account_id}, Email={email}"
                self.logger.error(msg)
                return False, msg
            
            # 检查Cursor是否正在运行
            if self.cursor_manager.is_running():
                self.logger.info("Cursor正在运行，准备关闭")
                if not self.cursor_manager.kill_all():
                    msg = "无法关闭Cursor进程"
                    self.logger.error(msg)
                    return False, msg
                
                # 等待进程完全关闭
                time.sleep(3)
            
            # 备份当前账号（如果需要）
            if backup_current:
                self.logger.info("备份当前账号信息")
                self.backup_current_account(notes="自动备份于账号切换")
            
            # 获取目标账号的认证信息和机器标识
            auth_tokens = self.db_manager.get_tokens(target_account)
            
            if not auth_tokens:
                msg = f"目标账号没有有效的认证信息: {target_account.email}"
                self.logger.error(msg)
                return False, msg
            
            # 准备机器标识数据
            machine_ids = {}
            if target_account.machine_id:
                machine_ids['machineId'] = target_account.machine_id
            if target_account.telemetry_id:
                machine_ids['telemetryMachineId'] = target_account.telemetry_id
            if target_account.sqm_id:
                machine_ids['sqmId'] = target_account.sqm_id
            if target_account.dev_device_id:
                machine_ids['devDeviceId'] = target_account.dev_device_id
            if target_account.mac_machine_id:
                machine_ids['macMachineId'] = target_account.mac_machine_id
            
            # 写入认证信息
            self.logger.info("写入目标账号认证信息")
            if not self.auth_manager.set_auth_info(auth_tokens):
                msg = "写入认证信息失败"
                self.logger.error(msg)
                return False, msg
            
            # 写入机器标识
            if machine_ids:
                self.logger.info("写入目标账号机器标识")
                if not self.machine_id_manager.set_machine_ids(machine_ids):
                    msg = "写入机器标识失败"
                    self.logger.error(msg)
                    # 机器标识写入失败不算致命错误，继续执行
            
            # 更新账号状态
            self.db_manager.set_active_account(account_id=target_account.id)
            self.db_manager.update_last_used(account_id=target_account.id)
            
            # 启动Cursor
            self.logger.info("启动Cursor")
            if self.cursor_manager.start():
                msg = f"成功切换到账号: {target_account.email}"
                self.logger.info(msg)
                return True, msg
            else:
                msg = "启动Cursor失败，但账号信息已切换"
                self.logger.warning(msg)
                return True, msg
                
        except Exception as e:
            msg = f"切换账号失败: {e}"
            self.logger.error(msg)
            return False, msg
    
    def quick_switch(self, account_id: int = None, email: str = None) -> Tuple[bool, str]:
        """
        快速切换账号（自动备份当前账号）
        
        Args:
            account_id: 目标账号ID
            email: 目标账号邮箱
        
        Returns:
            (成功标志, 消息)
        """
        return self.switch_account(account_id, email, backup_current=True)
    
    def restore_account(self, account_id: int = None, email: str = None) -> Tuple[bool, str]:
        """
        恢复账号（不备份当前账号）
        
        Args:
            account_id: 目标账号ID
            email: 目标账号邮箱
        
        Returns:
            (成功标志, 消息)
        """
        return self.switch_account(account_id, email, backup_current=False)
    
    def list_available_accounts(self) -> list:
        """
        列出所有可用账号
        
        Returns:
            账号列表
        """
        accounts = self.db_manager.get_all_accounts()
        
        account_list = []
        for account in accounts:
            account_list.append({
                'id': account.id,
                'email': account.email,
                'nickname': account.nickname,
                'is_active': account.is_active,
                'last_used': account.last_used.isoformat() if account.last_used else None,
                'tags': account.tags,
                'notes': account.notes
            })
        
        return account_list
    
    def export_all_accounts(self, export_path: str = None) -> bool:
        """
        导出所有账号数据
        
        Args:
            export_path: 导出文件路径
        
        Returns:
            成功返回True，否则False
        """
        return self.db_manager.export_accounts(export_path, include_sensitive=True)
    
    def import_accounts(self, import_path: str) -> int:
        """
        导入账号数据
        
        Args:
            import_path: 导入文件路径
        
        Returns:
            成功导入的账号数量
        """
        return self.db_manager.import_accounts(import_path)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取账号统计信息
        
        Returns:
            统计信息字典
        """
        return self.db_manager.get_statistics()
    
    def cleanup(self):
        """清理资源"""
        try:
            self.db_manager.close()
            self.logger.info("账号切换管理器资源已清理")
        except Exception as e:
            self.logger.error(f"清理资源失败: {e}")


# 测试代码
if __name__ == "__main__":
    import sys
    
    switcher = AccountSwitcher()
    
    # 测试命令行界面
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "list":
            # 列出所有账号
            accounts = switcher.list_available_accounts()
            print("\n可用账号列表:")
            print("-" * 60)
            for acc in accounts:
                status = "✓" if acc['is_active'] else " "
                print(f"[{status}] ID: {acc['id']:<3} | {acc['email']:<30} | {acc['nickname']:<15}")
                if acc['last_used']:
                    print(f"    最后使用: {acc['last_used']}")
                if acc['notes']:
                    print(f"    备注: {acc['notes']}")
                print("-" * 60)
        
        elif command == "current":
            # 显示当前账号信息
            info = switcher.get_current_account_info()
            print("\n当前账号信息:")
            print(json.dumps(info, indent=2, ensure_ascii=False))
        
        elif command == "backup":
            # 备份当前账号
            nickname = input("请输入账号昵称（可选）: ").strip() or None
            notes = input("请输入备注信息（可选）: ").strip() or None
            
            account = switcher.backup_current_account(nickname, notes)
            if account:
                print(f"✓ 账号备份成功: {account.email}")
            else:
                print("✗ 账号备份失败")
        
        elif command == "switch":
            # 切换账号
            if len(sys.argv) > 2:
                target = sys.argv[2]
                
                # 判断是ID还是邮箱
                if target.isdigit():
                    success, msg = switcher.quick_switch(account_id=int(target))
                else:
                    success, msg = switcher.quick_switch(email=target)
                
                if success:
                    print(f"✓ {msg}")
                else:
                    print(f"✗ {msg}")
            else:
                print("用法: python account_switcher.py switch <账号ID或邮箱>")
        
        elif command == "export":
            # 导出账号
            path = sys.argv[2] if len(sys.argv) > 2 else None
            if switcher.export_all_accounts(path):
                print("✓ 账号导出成功")
            else:
                print("✗ 账号导出失败")
        
        elif command == "import":
            # 导入账号
            if len(sys.argv) > 2:
                path = sys.argv[2]
                count = switcher.import_accounts(path)
                print(f"✓ 成功导入 {count} 个账号")
            else:
                print("用法: python account_switcher.py import <文件路径>")
        
        elif command == "stats":
            # 显示统计信息
            stats = switcher.get_statistics()
            print("\n账号统计信息:")
            print(f"  总账号数: {stats['total_accounts']}")
            print(f"  激活账号: {stats['active_accounts']}")
            print(f"  未激活账号: {stats['inactive_accounts']}")
            if stats['recent_account']:
                print(f"  最近使用: {stats['recent_account']}")
                print(f"  使用时间: {stats['recent_used_time']}")
        
        else:
            print("未知命令:", command)
            print("\n可用命令:")
            print("  list    - 列出所有账号")
            print("  current - 显示当前账号信息")
            print("  backup  - 备份当前账号")
            print("  switch  - 切换到指定账号")
            print("  export  - 导出所有账号")
            print("  import  - 导入账号数据")
            print("  stats   - 显示统计信息")
    else:
        # 交互式测试
        print("\n=== 账号切换管理器测试 ===\n")
        
        # 显示当前账号信息
        print("当前账号信息:")
        current = switcher.get_current_account_info()
        print(json.dumps(current, indent=2, ensure_ascii=False))
        
        # 列出可用账号
        print("\n可用账号:")
        accounts = switcher.list_available_accounts()
        for acc in accounts:
            print(f"  [{acc['id']}] {acc['email']} ({acc['nickname']})")
        
        # 显示统计
        print("\n统计信息:")
        stats = switcher.get_statistics()
        print(f"  总计: {stats['total_accounts']} 个账号")
        print(f"  激活: {stats['active_accounts']} 个")
    
    # 清理资源
    switcher.cleanup()