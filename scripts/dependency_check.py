#!/usr/bin/env python3
"""
依賴檢查和管理腳本
確保所有必要的依賴都正確安裝，並檢查版本相容性
"""

import sys
import subprocess
from typing import Dict, List, Tuple
import importlib

# 嘗試導入pkg_resources，如果失敗則使用替代方案
try:
    import pkg_resources
    HAS_PKG_RESOURCES = True
except ImportError:
    HAS_PKG_RESOURCES = False

# 定義項目依賴
REQUIRED_DEPENDENCIES = {
    # 核心依賴（必須）
    'core': {
        'sqlite3': None,  # 內建模組
        'json': None,     # 內建模組
        'datetime': None, # 內建模組
        'typing': None,   # 內建模組
    },
    
    # 可選依賴（建議）
    'optional': {
        'requests': '>=2.25.0',
        'flask': '>=2.0.0',
    },
    
    # 開發依賴（測試和開發用）
    'development': {
        'unittest': None,  # 內建模組
    },
    
    # 高級功能依賴（特定功能需要）
    'advanced': {
        'aiohttp': '>=3.8.0',
        'asyncio': None,  # 內建模組（Python 3.7+）
    }
}

class DependencyChecker:
    """依賴檢查器"""
    
    def __init__(self):
        self.results = {
            'core': {'missing': [], 'installed': [], 'version_mismatch': []},
            'optional': {'missing': [], 'installed': [], 'version_mismatch': []},
            'development': {'missing': [], 'installed': [], 'version_mismatch': []},
            'advanced': {'missing': [], 'installed': [], 'version_mismatch': []}
        }
    
    def check_module_import(self, module_name: str) -> bool:
        """檢查模組是否可以導入"""
        try:
            importlib.import_module(module_name)
            return True
        except ImportError:
            return False
    
    def check_package_version(self, package_name: str, version_requirement: str = None) -> Tuple[bool, str]:
        """檢查包版本是否符合要求"""
        try:
            if version_requirement is None:
                # 對於內建模組，只檢查是否可導入
                return self.check_module_import(package_name), "內建模組"
            
            if not HAS_PKG_RESOURCES:
                # 如果沒有pkg_resources，只檢查是否可以導入
                can_import = self.check_module_import(package_name)
                return can_import, "已安裝（無法檢查版本）" if can_import else "未安裝"
            
            # 檢查已安裝的版本
            installed_version = pkg_resources.get_distribution(package_name).version
            
            # 檢查版本要求
            try:
                pkg_resources.require(f"{package_name}{version_requirement}")
                return True, installed_version
            except pkg_resources.VersionConflict:
                return False, installed_version
                
        except (pkg_resources.DistributionNotFound if HAS_PKG_RESOURCES else ImportError):
            return False, "未安裝"
    
    def check_dependency_category(self, category: str, dependencies: Dict[str, str]):
        """檢查特定類別的依賴"""
        print(f"\n📦 檢查 {category} 依賴...")
        
        for package, version_req in dependencies.items():
            is_ok, version_info = self.check_package_version(package, version_req)
            
            if is_ok:
                self.results[category]['installed'].append(package)
                print(f"✅ {package}: {version_info}")
            else:
                if version_info == "未安裝":
                    self.results[category]['missing'].append(package)
                    print(f"❌ {package}: 未安裝")
                else:
                    self.results[category]['version_mismatch'].append((package, version_info, version_req))
                    print(f"⚠️ {package}: 版本不符 (已安裝: {version_info}, 需要: {version_req})")
    
    def run_full_check(self):
        """執行完整的依賴檢查"""
        print("🔍 開始依賴檢查...")
        print("=" * 60)
        
        for category, dependencies in REQUIRED_DEPENDENCIES.items():
            self.check_dependency_category(category, dependencies)
        
        return self.results
    
    def generate_report(self, results: Dict) -> Dict[str, any]:
        """生成檢查報告"""
        report = {
            'total_missing': 0,
            'total_version_mismatch': 0,
            'critical_issues': [],
            'recommendations': []
        }
        
        print("\n" + "=" * 60)
        print("📊 依賴檢查報告")
        print("=" * 60)
        
        for category, result in results.items():
            missing = len(result['missing'])
            mismatch = len(result['version_mismatch'])
            installed = len(result['installed'])
            
            report['total_missing'] += missing
            report['total_version_mismatch'] += mismatch
            
            print(f"\n📋 {category.upper()} 依賴:")
            print(f"   ✅ 已安裝: {installed}")
            print(f"   ❌ 缺失: {missing}")
            print(f"   ⚠️ 版本不符: {mismatch}")
            
            # 記錄關鍵問題
            if category == 'core' and (missing > 0 or mismatch > 0):
                report['critical_issues'].append(f"核心依賴問題: {missing}個缺失, {mismatch}個版本不符")
            
            # 顯示缺失的包
            if result['missing']:
                print(f"   缺失的包: {', '.join(result['missing'])}")
                
                # 生成安裝建議
                if category == 'core':
                    report['critical_issues'].append(f"必須安裝: {', '.join(result['missing'])}")
                elif category == 'optional':
                    report['recommendations'].append(f"建議安裝: {', '.join(result['missing'])}")
        
        return report
    
    def generate_install_commands(self, results: Dict) -> List[str]:
        """生成安裝命令建議"""
        commands = []
        
        # 收集需要安裝的包
        to_install = []
        
        for category, result in results.items():
            if category == 'core':
                # 核心依賴必須安裝
                to_install.extend(result['missing'])
            elif category == 'optional':
                # 可選依賴建議安裝
                to_install.extend(result['missing'])
        
        if to_install:
            # 過濾掉內建模組
            external_packages = [pkg for pkg in to_install if pkg not in ['sqlite3', 'json', 'datetime', 'typing', 'unittest', 'asyncio']]
            
            if external_packages:
                commands.append(f"pip3 install {' '.join(external_packages)}")
        
        return commands

def check_python_version():
    """檢查Python版本"""
    print("🐍 檢查Python版本...")
    version = sys.version_info
    
    if version >= (3, 7):
        print(f"✅ Python版本: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python版本過舊: {version.major}.{version.minor}.{version.micro}")
        print("   建議使用Python 3.7或更新版本")
        return False

def check_virtual_environment():
    """檢查是否在虛擬環境中"""
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    
    if in_venv:
        print("✅ 運行在虛擬環境中")
    else:
        print("⚠️ 未使用虛擬環境 - 建議使用虛擬環境隔離依賴")
    
    return in_venv

def main():
    """主函數"""
    print("🚀 開始依賴管理檢查...")
    print("=" * 80)
    
    # 檢查Python版本
    python_ok = check_python_version()
    
    # 檢查虛擬環境
    venv_info = check_virtual_environment()
    
    if not python_ok:
        print("\n❌ Python版本不符合要求，請升級Python版本")
        return 1
    
    # 執行依賴檢查
    checker = DependencyChecker()
    results = checker.run_full_check()
    
    # 生成報告
    report = checker.generate_report(results)
    
    # 生成安裝建議
    install_commands = checker.generate_install_commands(results)
    
    # 顯示總結和建議
    print("\n" + "=" * 60)
    print("💡 總結和建議")
    print("=" * 60)
    
    if report['critical_issues']:
        print("\n🚨 關鍵問題:")
        for issue in report['critical_issues']:
            print(f"   - {issue}")
    
    if install_commands:
        print("\n📦 安裝建議:")
        for cmd in install_commands:
            print(f"   {cmd}")
    
    if report['recommendations']:
        print("\n💡 其他建議:")
        for rec in report['recommendations']:
            print(f"   - {rec}")
    
    # 返回狀態
    if report['critical_issues']:
        print(f"\n❌ 發現 {len(report['critical_issues'])} 個關鍵問題")
        return 1
    else:
        print("\n✅ 所有核心依賴都已滿足")
        return 0

if __name__ == "__main__":
    sys.exit(main())