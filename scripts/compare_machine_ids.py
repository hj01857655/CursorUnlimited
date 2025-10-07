import json
import sqlite3

# 读取 storage.json
storage_json_path = r'C:\Users\12925\AppData\Roaming\Cursor\User\globalStorage\storage.json'
with open(storage_json_path, 'r', encoding='utf-8') as f:
    storage_data = json.load(f)

# 读取 state.vscdb
db_path = r'C:\Users\12925\AppData\Roaming\Cursor\User\globalStorage\state.vscdb'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 机器标识字段列表
fields = [
    'storage.serviceMachineId',
    'telemetry.machineId',
    'telemetry.macMachineId',
    'telemetry.devDeviceId',
    'telemetry.sqmId',
    'telemetry.firstSessionDate',
    'telemetry.currentSessionDate',
    'telemetry.lastSessionDate'
]

print("=" * 80)
print("对比 storage.json 和 state.vscdb 中的机器标识")
print("=" * 80)

for field in fields:
    storage_value = storage_data.get(field, '(不存在)')
    
    cursor.execute("SELECT value FROM ItemTable WHERE key = ?", (field,))
    result = cursor.fetchone()
    db_value = result[0] if result else '(不存在)'
    
    match = "✓" if storage_value == db_value else "✗"
    
    print(f"\n{field}:")
    print(f"  storage.json: {storage_value[:80] if isinstance(storage_value, str) else storage_value}")
    print(f"  state.vscdb:  {db_value[:80] if isinstance(db_value, str) else db_value}")
    print(f"  匹配: {match}")

conn.close()

print("\n" + "=" * 80)
print("总结：哪些字段需要同时更新")
print("=" * 80)
