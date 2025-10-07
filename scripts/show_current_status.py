import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from automation.auth_manager import CursorAuthManager
from automation.machine_id_manager import MachineIdManager

print("=" * 80)
print("Cursor 当前状态")
print("=" * 80)

# 1. 账号信息 - storage.json
print("\n【账号信息 - storage.json】")
print("-" * 80)

auth_manager = CursorAuthManager()
config = auth_manager.config_manager
storage = config.read_storage()

auth_fields = [
    'cursorAuth/accessToken',
    'cursorAuth/cachedEmail',
    'cursorAuth/refreshToken',
    'cursorAuth/cachedSignUpType'
]

for field in auth_fields:
    value = storage.get(field, '(未设置)')
    if isinstance(value, str) and len(value) > 60:
        # 长字符串显示前后部分
        display_value = f"{value[:30]}...{value[-30:]}"
    else:
        display_value = value
    print(f"{field:30s}: {display_value}")

# 1.2 账号信息 - state.vscdb
print("\n【账号信息 - state.vscdb】")
print("-" * 80)

for field in auth_fields:
    value = config.read_vscdb_value(field)
    if value is None:
        display_value = '(未设置)'
    elif isinstance(value, str) and len(value) > 60:
        display_value = f"{value[:30]}...{value[-30:]}"
    else:
        display_value = value
    print(f"{field:30s}: {display_value}")

# 对比
print("\n【同步状态】")
print("-" * 80)
for field in auth_fields:
    storage_val = storage.get(field)
    vscdb_val = config.read_vscdb_value(field)
    
    if storage_val == vscdb_val:
        status = "✓ 一致"
    else:
        status = "✗ 不一致"
    print(f"{field:30s}: {status}")

# 2. 机器标识信息
print("\n【机器标识信息】")
print("-" * 80)

machine_manager = MachineIdManager()
machine_ids = machine_manager.get_current_machine_ids()

print(f"storage.serviceMachineId: {machine_ids.get('serviceMachineId', '(未设置)')}")
print(f"telemetry.machineId:      {machine_ids.get('machineId', '(未设置)')}")
print(f"telemetry.devDeviceId:    {machine_ids.get('devDeviceId', '(未设置)')}")
print(f"telemetry.sqmId:          {machine_ids.get('sqmId', '(未设置)')}")

mac_machine_id = machine_ids.get('macMachineId', '(未设置)')
if len(str(mac_machine_id)) > 80:
    print(f"telemetry.macMachineId:   {mac_machine_id[:40]}...")
    print(f"                          {mac_machine_id[40:80]}...")
    if len(mac_machine_id) > 80:
        print(f"                          {mac_machine_id[80:]}")
else:
    print(f"telemetry.macMachineId:   {mac_machine_id}")

# 3. Windows 系统标识
print("\n【Windows 系统标识】")
print("-" * 80)

import winreg

try:
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography")
    win_machine_guid, _ = winreg.QueryValueEx(key, "MachineGuid")
    winreg.CloseKey(key)
    print(f"Windows MachineGuid:      {win_machine_guid}")
    
    # 对比
    if machine_ids.get('serviceMachineId') == win_machine_guid:
        print("  → 与 storage.serviceMachineId 一致 ✓")
    else:
        print("  → 与 storage.serviceMachineId 不一致 ✗")
except Exception as e:
    print(f"Windows MachineGuid:      读取失败 - {e}")

try:
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\SQMClient")
    win_sqm_id, _ = winreg.QueryValueEx(key, "MachineId")
    winreg.CloseKey(key)
    print(f"Windows SQM MachineId:    {win_sqm_id}")
    
    # 对比
    if machine_ids.get('sqmId') == win_sqm_id:
        print("  → 与 telemetry.sqmId 一致 ✓")
    else:
        print("  → 与 telemetry.sqmId 不一致 ✗")
except Exception as e:
    print(f"Windows SQM MachineId:    不存在或读取失败")

# 4. account.json 账号列表
print("\n【account.json 账号列表】")
print("-" * 80)

accounts = auth_manager.get_account_list()
if accounts:
    print(f"共有 {len(accounts)} 个账号:")
    for i, acc in enumerate(accounts, 1):
        current_mark = " ← 当前" if acc.get('is_current', False) else ""
        print(f"  {i}. {acc['email']}{current_mark}")
        if acc.get('created_at'):
            print(f"     创建时间: {acc['created_at']}")
else:
    print("(无账号)")

print("\n" + "=" * 80)
