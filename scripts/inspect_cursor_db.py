# -*- coding: utf-8 -*-
"""
查看Cursor数据库结构
"""

import sqlite3
import os

db_path = r"C:\Users\12925\AppData\Roaming\Cursor\User\globalStorage\state.vscdb"

if not os.path.exists(db_path):
    print(f"数据库文件不存在: {db_path}")
    exit(1)

print(f"数据库文件大小: {os.path.getsize(db_path) / (1024*1024):.2f} MB\n")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 获取所有表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print(f"共有 {len(tables)} 个表:\n")
    
    for table in tables:
        table_name = table[0]
        print(f"表名: {table_name}")
        
        # 获取表结构
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        print("  字段:")
        for col in columns:
            col_id, col_name, col_type, not_null, default_val, pk = col
            print(f"    - {col_name} ({col_type})" + (" PRIMARY KEY" if pk else ""))
        
        # 获取记录数
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"  记录数: {count}")
        
        # 如果记录数不多，显示一些示例数据
        if count > 0 and count <= 10:
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
            rows = cursor.fetchall()
            if rows:
                print(f"  示例数据:")
                for row in rows:
                    print(f"    {row}")
        
        print()
    
    conn.close()
    print("查询完成！")
    
except Exception as e:
    print(f"错误: {e}")
