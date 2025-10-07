import sqlite3
import json

db_path = r'C:\Users\12925\AppData\Roaming\Cursor\User\globalStorage\state.vscdb'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=== 遥测和机器ID相关的keys ===\n")
rows = cursor.execute("""
    SELECT key, value FROM ItemTable 
    WHERE key LIKE '%telemetry%' 
    OR key LIKE '%machine%' 
    OR key LIKE '%device%'
    OR key LIKE '%sqm%'
    OR key LIKE '%storage.service%'
    OR key LIKE '%uuid%'
    OR key LIKE '%guid%'
    OR key LIKE '%id%'
""").fetchall()

print(f"找到 {len(rows)} 个相关键\n")

for key, value in rows:
    if len(value) > 200:
        print(f"{key}: {value[:200]}...")
    else:
        print(f"{key}: {value}")
    print()

conn.close()
