import sqlite3

db_path = r'C:\Users\12925\AppData\Roaming\Cursor\User\globalStorage\state.vscdb'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 80)
print("state.vscdb 中所有账号认证相关的字段")
print("=" * 80)

# 搜索所有可能与账号认证相关的key
patterns = [
    '%cursor%',
    '%auth%',
    '%token%',
    '%email%',
    '%user%',
    '%account%',
    '%login%',
    '%session%'
]

all_keys = set()
for pattern in patterns:
    cursor.execute(f"SELECT key FROM ItemTable WHERE key LIKE ?", (pattern,))
    results = cursor.fetchall()
    for row in results:
        all_keys.add(row[0])

# 排序并显示
sorted_keys = sorted(all_keys)

print(f"\n找到 {len(sorted_keys)} 个相关键:\n")

for key in sorted_keys:
    cursor.execute("SELECT value FROM ItemTable WHERE key = ?", (key,))
    result = cursor.fetchone()
    value = result[0] if result else '(无值)'
    
    # 对长值进行截断显示
    if isinstance(value, str) and len(value) > 60:
        display_value = f"{value[:30]}...{value[-20:]}"
    else:
        display_value = value
    
    print(f"{key:50s}: {display_value}")

conn.close()

print("\n" + "=" * 80)
