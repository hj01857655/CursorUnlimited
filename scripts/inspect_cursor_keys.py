# -*- coding: utf-8 -*-
"""
查看Cursor数据库中的key
"""

import sqlite3

db_path = r"C:\Users\12925\AppData\Roaming\Cursor\User\globalStorage\state.vscdb"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=== ItemTable 表的 keys ===\n")
cursor.execute("SELECT key FROM ItemTable LIMIT 20")
for row in cursor.fetchall():
    print(f"  - {row[0]}")

print("\n=== cursorDiskKV 表的 keys (前50个) ===\n")
cursor.execute("SELECT key FROM cursorDiskKV LIMIT 50")
for row in cursor.fetchall():
    print(f"  - {row[0]}")

# 查找包含特定关键词的key
print("\n=== 包含 'account' 或 'user' 或 'auth' 的 keys ===\n")
cursor.execute("""
    SELECT key FROM ItemTable WHERE key LIKE '%account%' OR key LIKE '%user%' OR key LIKE '%auth%'
    UNION
    SELECT key FROM cursorDiskKV WHERE key LIKE '%account%' OR key LIKE '%user%' OR key LIKE '%auth%'
    LIMIT 30
""")
for row in cursor.fetchall():
    print(f"  - {row[0]}")

conn.close()
