# -*- coding: utf-8 -*-
"""
综合测试脚本 - 测试账号管理系统的完整功能
"""

import sys
import os
import time
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.database_manager import DatabaseManager
from src.services.account_switcher import AccountSwitcher
from src.models.account import AccountStatus


def print_section(title):
    """打印分节标题"""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def test_database_manager():
    """测试数据库管理器"""
    print_section("测试数据库管理器")
    
    # 使用测试数据库
    db = DatabaseManager("data/test_full_system.db")
    
    # 1. 添加测试账号
    print("\n1. 添加测试账号...")
    test_accounts = [
        {
            "email": "test1@example.com",
            "password": "password1",
            "username": "TestUser1",
            "access_token": "token_test1_access",
            "refresh_token": "token_test1_refresh",
            "notes": "测试账号1"
        },
        {
            "email": "test2@example.com", 
            "password": "password2",
            "username": "TestUser2",
            "access_token": "token_test2_access",
            "refresh_token": "token_test2_refresh",
            "notes": "测试账号2",
            "is_active": True
        },
        {
            "email": "test3@example.com",
            "password": "password3",
            "username": "TestUser3",
            "access_token": "token_test3_access",
            "refresh_token": "token_test3_refresh",
            "notes": "测试账号3 - 禁用",
            "is_active": False
        }
    ]
    
    created_accounts = []
    for acc_data in test_accounts:
        account = db.add_account(**acc_data)
        if account:
            created_accounts.append(account)
            print(f"   ✓ 添加账号: {account.email} (ID: {account.id})")
        else:
            print(f"   ✗ 添加失败: {acc_data['email']}")
    
    # 2. 设置主账号
    print("\n2. 设置主账号...")
    if created_accounts:
        success = db.set_primary_account(created_accounts[0].id)
        if success:
            print(f"   ✓ 设置 {created_accounts[0].email} 为主账号")
    
    # 3. 查询账号
    print("\n3. 查询账号...")
    all_accounts = db.get_all_accounts()
    print(f"   总账号数: {len(all_accounts)}")
    
    active_accounts = db.get_all_accounts(active_only=True)
    print(f"   活跃账号数: {len(active_accounts)}")
    
    # 4. 更新账号信息
    print("\n4. 更新账号信息...")
    if created_accounts:
        success = db.update_account(
            created_accounts[1].id,
            status=AccountStatus.ACTIVE,
            total_quota=100.0,
            used_quota=25.5
        )
        if success:
            print(f"   ✓ 更新账号 {created_accounts[1].email} 的状态和配额")
    
    # 5. 更新Token
    print("\n5. 更新Token...")
    if created_accounts:
        success = db.update_account_tokens(
            created_accounts[1].id,
            "new_access_token_" + str(int(time.time())),
            "new_refresh_token_" + str(int(time.time()))
        )
        if success:
            print(f"   ✓ 更新账号 {created_accounts[1].email} 的Token")
    
    # 6. 添加使用日志
    print("\n6. 添加使用日志...")
    if created_accounts:
        for i, account in enumerate(created_accounts[:2]):
            log = db.add_usage_log(
                account.id,
                action='login' if i == 0 else 'switch',
                success=True,
                details=f"测试日志 {i+1}"
            )
            if log:
                print(f"   ✓ 添加日志: {account.email} - {log.action}")
    
    # 7. 获取统计信息
    print("\n7. 统计信息...")
    stats = db.get_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    return db, created_accounts


def test_account_switcher(db, accounts):
    """测试账号切换器"""
    print_section("测试账号切换器")
    
    switcher = AccountSwitcher(db)
    
    # 1. 获取当前账号
    print("\n1. 获取当前账号...")
    current = switcher.get_current_account()
    if current:
        print(f"   当前账号: {current.email}")
    else:
        print("   无当前账号")
    
    # 2. 同步当前账号
    print("\n2. 同步当前账号...")
    success, message = switcher.sync_current_account()
    print(f"   结果: {message}")
    
    # 3. 切换账号（不关闭Cursor）
    if accounts and len(accounts) > 1:
        print("\n3. 切换账号测试...")
        target = accounts[1]
        print(f"   切换到: {target.email}")
        success, message = switcher.switch_account(target.id, kill_cursor=False)
        print(f"   结果: {message}")
        
        # 验证切换结果
        time.sleep(1)
        current = switcher.get_current_account()
        if current:
            print(f"   当前账号确认: {current.email}")


def test_import_export(db):
    """测试导入导出功能"""
    print_section("测试导入导出")
    
    # 1. 导出账号
    print("\n1. 导出账号...")
    accounts_data = db.export_accounts()
    print(f"   导出 {len(accounts_data)} 个账号")
    
    # 2. 模拟导入（到新数据库）
    print("\n2. 模拟导入到新数据库...")
    new_db = DatabaseManager("data/test_import.db")
    
    # 准备导入数据（只导入邮箱不同的）
    import_data = [
        {
            "email": "imported1@example.com",
            "password": "pass1",
            "username": "ImportUser1",
            "access_token": "import_token1",
            "notes": "导入的账号1"
        },
        {
            "email": "imported2@example.com",
            "password": "pass2",
            "username": "ImportUser2",
            "access_token": "import_token2",
            "notes": "导入的账号2"
        }
    ]
    
    imported_count = new_db.import_accounts(import_data)
    print(f"   成功导入 {imported_count} 个账号")
    
    # 验证导入
    imported_accounts = new_db.get_all_accounts()
    print(f"   新数据库账号总数: {len(imported_accounts)}")
    for acc in imported_accounts:
        print(f"     - {acc.email}")


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("  CursorUnlimited 综合测试")
    print("=" * 60)
    print(f"\n测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 测试数据库管理
        db, accounts = test_database_manager()
        
        # 测试账号切换
        test_account_switcher(db, accounts)
        
        # 测试导入导出
        test_import_export(db)
        
        print_section("测试完成")
        print("\n✓ 所有测试成功完成！")
        
    except Exception as e:
        print_section("测试失败")
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)