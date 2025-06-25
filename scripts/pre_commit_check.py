#!/usr/bin/env python3
"""
Pre-commit 檢查腳本
在每次提交前自動運行品質檢查，防止問題代碼進入版本控制
"""

import sys
import subprocess
import os
from pathlib import Path

def run_command(cmd, description):
    """執行命令並返回結果"""
    print(f"🔍 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} 通過")
            return True
        else:
            print(f"❌ {description} 失敗:")
            print(result.stdout)
            print(result.stderr)
            return False
    except Exception as e:
        print(f"💥 {description} 執行錯誤: {e}")
        return False

def check_python_syntax():
    """檢查Python語法"""
    python_files = []
    for ext in ['*.py']:
        python_files.extend(Path('.').rglob(ext))
    
    for file in python_files:
        if not run_command(f"python3 -m py_compile {file}", f"語法檢查 {file}"):
            return False
    return True

def run_unit_tests():
    """執行單元測試"""
    # 只運行快速的核心測試
    core_tests = [
        'test_database_manager.py',
        'test_config_unit.py'
    ]
    
    for test in core_tests:
        if os.path.exists(test):
            if not run_command(f"python3 {test}", f"單元測試 {test}"):
                return False
    return True

def check_import_dependencies():
    """檢查導入依賴"""
    return run_command("python3 -c 'import sys; sys.path.insert(0, \".\"); import config, user_manager, test_case_manager'", "導入依賴檢查")

def validate_database_schema():
    """驗證資料庫Schema一致性"""
    schema_file = "database/schema.sql"
    if os.path.exists(schema_file):
        # 簡化驗證：只檢查資料庫管理器是否可以正常導入和初始化
        return run_command(f"python3 -c 'from database.db_manager import db_manager; print(\"資料庫管理器載入成功\")'", "資料庫Schema驗證")
    return True

def check_test_coverage():
    """檢查測試覆蓋率（簡化版）"""
    # 統計測試文件和源文件比例
    test_files = list(Path('.').glob('test_*.py'))
    source_files = list(Path('.').glob('*.py'))
    source_files = [f for f in source_files if not f.name.startswith('test_')]
    
    if len(source_files) > 0:
        coverage_ratio = len(test_files) / len(source_files)
        print(f"📊 測試文件覆蓋率: {coverage_ratio:.1%} ({len(test_files)}/{len(source_files)})")
        
        if coverage_ratio < 0.5:  # 至少50%的文件有測試
            print("⚠️ 測試覆蓋率偏低，建議增加測試文件")
            return False
    
    return True

def main():
    """主檢查流程"""
    print("🚀 開始 Pre-commit 品質檢查...")
    print("=" * 50)
    
    checks = [
        ("Python語法檢查", check_python_syntax),
        ("導入依賴檢查", check_import_dependencies), 
        ("資料庫Schema驗證", validate_database_schema),
        ("核心單元測試", run_unit_tests),
        ("測試覆蓋率檢查", check_test_coverage)
    ]
    
    failed_checks = []
    
    for check_name, check_func in checks:
        print(f"\n📋 執行 {check_name}")
        if not check_func():
            failed_checks.append(check_name)
    
    print("\n" + "=" * 50)
    print("📊 Pre-commit 檢查結果:")
    
    if failed_checks:
        print("❌ 以下檢查失敗:")
        for check in failed_checks:
            print(f"   - {check}")
        print("\n🔧 請修復上述問題後重新提交")
        return 1
    else:
        print("✅ 所有檢查通過！代碼品質良好，可以提交。")
        return 0

if __name__ == "__main__":
    sys.exit(main())