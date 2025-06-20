#!/usr/bin/env python3
"""
資料遷移腳本：從 JSON 檔案遷移到 SQLite 資料庫
"""

import os
import sys
from database.migration import DataMigration
from database.db_manager import db_manager

def main():
    print("🔄 開始從 JSON 遷移到 SQLite 資料庫...")
    print("=" * 60)
    
    # 檢查是否存在 JSON 檔案
    data_dir = "data"
    json_files = [
        "apis.json", "users.json", "test_cases.json",
        "test_projects.json", "product_tags.json", "user_stories.json"
    ]
    
    existing_files = []
    for file_name in json_files:
        file_path = os.path.join(data_dir, file_name)
        if os.path.exists(file_path):
            existing_files.append(file_name)
    
    if not existing_files:
        print("📝 沒有找到 JSON 資料檔案，跳過遷移")
        print("✅ SQLite 資料庫已就緒，可以開始使用")
        return
    
    print(f"📁 找到以下 JSON 檔案: {', '.join(existing_files)}")
    
    # 檢查資料庫狀態
    migration = DataMigration(data_dir)
    status = migration.check_migration_status()
    
    print(f"🗄️  資料庫狀態:")
    print(f"   - 資料庫存在: {'是' if status['database_exists'] else '否'}")
    
    for table, exists in status['tables'].items():
        count = status['data_counts'].get(table, 0)
        print(f"   - {table}: {'存在' if exists else '不存在'} ({count} 筆資料)")
    
    # 詢問是否繼續遷移
    if any(count > 0 for count in status['data_counts'].values()):
        print("\n⚠️  資料庫中已有資料，繼續遷移可能會有重複資料")
        response = input("是否繼續遷移？(y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("❌ 遷移已取消")
            return
    
    # 執行遷移
    print("\n🚀 開始遷移...")
    results = migration.migrate_all(backup=True)
    
    print("\n📊 遷移結果:")
    print("=" * 60)
    
    if results['success']:
        print("✅ 遷移成功完成！")
        
        for data_type, result in results['details'].items():
            if isinstance(result, dict) and 'migrated' in result:
                migrated_count = result['migrated']
                message = result['message']
                print(f"   {data_type}: {migrated_count} 筆資料 - {message}")
        
        # 顯示最終統計
        final_status = migration.check_migration_status()
        print(f"\n📈 最終資料統計:")
        for table, count in final_status['data_counts'].items():
            if count > 0:
                print(f"   - {table}: {count} 筆資料")
        
        print(f"\n🎉 遷移完成！現在可以使用 SQLite 資料庫版本的應用程式")
        print(f"💾 原始 JSON 檔案已備份到 data/backup/ 目錄")
        
    else:
        print("❌ 遷移失敗！")
        print(f"錯誤訊息: {results['message']}")
        if results['errors']:
            print("詳細錯誤:")
            for error in results['errors']:
                print(f"   - {error}")
        
        sys.exit(1)

if __name__ == "__main__":
    main()