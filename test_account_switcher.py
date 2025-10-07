# -*- coding: utf-8 -*-
"""
测试AccountSwitcher服务
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.database_manager import DatabaseManager
from src.services.account_switcher import AccountSwitcher
from src.models.account import AccountStatus


def test_account_switcher():
    """测试AccountSwitcher服务"""
    print("=" * 60)
    print("测试AccountSwitcher服务")
    print("=" * 60)
    
    # 初始化数据库管理器
    db_manager = DatabaseManager("data/test_accounts.db")
    
    # 初始化账号切换服务
    switcher = AccountSwitcher(db_manager)
    
    # 测试1：获取当前账号
    print("\n1. 获取当前账号...")
    current_account = switcher.get_current_account()
    if current_account:
        print(f"   当前账号: {current_account.email}")
        print(f"   账号ID: {current_account.id}")
        print(f"   状态: {current_account.status.value if current_account.status else 'unknown'}")
    else:
        print("   未检测到当前账号")
    
    # 测试2：同步当前账号到数据库
    print("\n2. 同步当前账号到数据库...")
    success, message = switcher.sync_current_account()
    print(f"   结果: {message}")
    
    # 测试3：查看所有账号
    print("\n3. 查看数据库中的所有账号...")
    accounts = db_manager.get_all_accounts()
    for acc in accounts:
        print(f"   - {acc.email} (ID:{acc.id}, 状态:{acc.status.value if acc.status else 'unknown'}, 启用:{acc.is_active})")
    
    # 测试4：如果有多个账号，尝试切换
    if len(accounts) > 1:
        print("\n4. 尝试切换账号...")
        # 找一个不是当前账号的
        target_account = None
        for acc in accounts:
            if current_account and acc.id != current_account.id and acc.is_active:
                target_account = acc
                break
        
        if target_account:
            print(f"   切换到: {target_account.email}")
            success, message = switcher.switch_account(target_account.id, kill_cursor=False)
            print(f"   结果: {message}")
    
    # 测试5：获取统计信息
    print("\n5. 获取统计信息...")
    stats = db_manager.get_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # 测试6：获取使用日志
    print("\n6. 获取最近的使用日志...")
    logs = db_manager.get_usage_logs(limit=10)
    if logs:
        for log in logs[:5]:  # 只显示前5条
            print(f"   [{log.timestamp}] {log.action} - 成功:{log.success}")
            if log.error_message:
                print(f"     错误: {log.error_message}")
    else:
        print("   暂无使用日志")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_account_switcher()
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()