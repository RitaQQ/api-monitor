#!/usr/bin/env python3
"""
Railway 部署初始化腳本
確保數據庫正確初始化並創建管理員用戶
"""

import os
import sys
from database.db_manager import db_manager

def railway_init():
    """Railway 環境初始化"""
    print("🚀 初始化 Railway 部署環境...")
    
    try:
        # 確保數據目錄存在
        os.makedirs('data', exist_ok=True)
        print("📁 數據目錄創建成功")
        
        # 檢查數據庫是否需要初始化
        if not os.path.exists('data/api_monitor.db'):
            print("📊 初始化數據庫...")
            # db_manager 已經會自動初始化數據庫和創建管理員
            try:
                # 觸發數據庫初始化
                users = db_manager.execute_query("SELECT * FROM users WHERE username = 'admin8888'")
                if users:
                    print("✅ 管理員用戶已創建成功")
                    print("   用戶名: admin8888")
                    print("   密碼: admin555333")
                else:
                    print("⚠️ 管理員用戶創建失敗，但繼續部署")
            except Exception as e:
                print(f"⚠️ 數據庫初始化警告: {e}")
                print("🔄 繼續部署，運行時將重新初始化")
        else:
            print("📊 數據庫已存在")
        
        # 執行資料庫遷移
        try:
            print("🔄 執行資料庫遷移...")
            from database.migrate_test_projects import migrate_test_projects_table
            migrate_test_projects_table()
            print("✅ 資料庫遷移完成")
        except Exception as e:
            print(f"⚠️ 資料庫遷移警告: {e}")
            print("🔄 繼續部署，應用將在運行時處理遷移")
        
        # 添加測試資料 (可選)
        try:
            print("🔄 添加測試資料...")
            _create_sample_data()
            print("✅ 測試資料添加完成")
        except Exception as e:
            print(f"⚠️ 測試資料添加警告: {e}")
            print("🔄 繼續部署，不影響核心功能")
        
        print("✅ Railway 環境初始化完成")
        
    except Exception as e:
        print(f"⚠️ 初始化過程中的非致命錯誤: {e}")
        print("🔄 繼續部署，應用將在運行時處理初始化")

def _create_sample_data():
    """創建範例資料以便測試"""
    try:
        from test_case_manager import TestCaseManager
        
        test_manager = TestCaseManager()
        
        # 檢查是否已有測試專案
        existing_projects = test_manager.get_test_projects()
        if existing_projects:
            print("📊 測試專案已存在，跳過範例資料創建")
            return
        
        # 創建範例測試專案
        print("📝 創建範例測試專案...")
        sample_project = test_manager.create_test_project(
            name="範例測試專案",
            description="這是一個範例測試專案，用於演示功能",
            responsible_user_id=None  # 將使用預設管理員
        )
        
        # 創建範例產品標籤
        print("🏷️ 創建範例產品標籤...")
        sample_tags = [
            {"name": "前端功能", "description": "前端相關功能測試", "color": "#007bff"},
            {"name": "後端API", "description": "後端API功能測試", "color": "#28a745"},
            {"name": "資料庫", "description": "資料庫相關測試", "color": "#dc3545"}
        ]
        
        for tag_data in sample_tags:
            try:
                test_manager.create_product_tag(**tag_data)
            except Exception as e:
                print(f"⚠️ 創建標籤 {tag_data['name']} 失敗: {e}")
        
        print(f"✅ 範例資料創建完成，專案ID: {sample_project.get('id') if sample_project else 'None'}")
        
    except Exception as e:
        print(f"⚠️ 創建範例資料時發生錯誤: {e}")
        # 不拋出異常，避免影響部署

if __name__ == "__main__":
    railway_init()