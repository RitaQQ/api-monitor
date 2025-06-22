#!/usr/bin/env python3
"""
測試專案表結構遷移腳本
為現有的 test_projects 表添加 start_time 和 end_time 欄位
"""

import sqlite3
import os

def migrate_test_projects_table():
    """遷移測試專案表，添加缺失的欄位"""
    db_path = 'data/api_monitor.db'
    
    if not os.path.exists(db_path):
        print("資料庫檔案不存在，跳過遷移")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 檢查欄位是否已存在
        cursor.execute("PRAGMA table_info(test_projects)")
        columns = [column[1] for column in cursor.fetchall()]
        
        migrations_needed = []
        if 'start_time' not in columns:
            migrations_needed.append('start_time')
        if 'end_time' not in columns:
            migrations_needed.append('end_time')
        
        if migrations_needed:
            print(f"需要添加欄位: {migrations_needed}")
            
            for column in migrations_needed:
                alter_sql = f"ALTER TABLE test_projects ADD COLUMN {column} DATETIME"
                cursor.execute(alter_sql)
                print(f"✅ 已添加欄位: {column}")
            
            conn.commit()
            print("🎉 測試專案表遷移完成")
        else:
            print("✅ 測試專案表結構已是最新版本，無需遷移")
        
    except Exception as e:
        print(f"❌ 遷移過程發生錯誤: {e}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    migrate_test_projects_table()