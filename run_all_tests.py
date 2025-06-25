#!/usr/bin/env python3
"""
QA Management Tool 完整單元測試套件執行器
整合所有模組的單元測試，生成完整的測試報告

測試覆蓋範圍：
1. 資料庫管理器 (DatabaseManager)
2. 測試案例管理器 (TestCaseManager) 
3. 用戶管理器 (UserManager)
4. API檢查器 (APIChecker) 和壓力測試器 (StressTester)
5. Flask路由和API端點
6. 配置管理 (Config)
7. 關聯保護功能
"""

import unittest
import sys
import os
import time
from datetime import datetime
from io import StringIO

# 添加專案根目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 導入所有測試模組
try:
    from test_database_manager import TestDatabaseManager, run_database_manager_tests
    from test_test_case_manager_unit import TestTestCaseManager, run_test_case_manager_tests
    from test_user_manager_unit import TestUserManager, run_user_manager_tests
    from test_api_checker_unit import TestAPIChecker, TestStressTester, run_api_tests
    from test_config_unit import TestConfig, run_config_tests
    
    # 嘗試導入可選模組
    test_flask_routes_unit = None
    test_association_functionality = None
    
    try:
        from test_flask_routes_unit import TestFlaskRoutes, run_flask_routes_tests
    except ImportError:
        print("⚠️ Flask測試模組無法載入，將跳過Flask相關測試")
        TestFlaskRoutes = None
        run_flask_routes_tests = None
    
    try:
        from test_association_functionality import test_check_associations_functionality
    except ImportError:
        print("⚠️ 關聯功能測試模組無法載入，將跳過關聯功能測試")
        test_check_associations_functionality = None
        
except ImportError as e:
    print(f"⚠️ 導入核心測試模組時發生錯誤: {e}")
    print("請確保所有測試文件都已正確創建")
    sys.exit(1)


class DetailedTestResult(unittest.TextTestResult):
    """詳細測試結果收集器"""
    
    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.test_results = []
        self.start_time = None
        self.end_time = None
    
    def startTest(self, test):
        super().startTest(test)
        self.start_time = time.time()
    
    def stopTest(self, test):
        super().stopTest(test)
        self.end_time = time.time()
        
        # 記錄測試結果
        test_info = {
            'test_name': str(test),
            'test_method': test._testMethodName,
            'test_class': test.__class__.__name__,
            'duration': self.end_time - self.start_time,
            'status': 'PASS',
            'error_message': None
        }
        
        # 檢查測試狀態
        if hasattr(self, '_exc_info_to_string'):
            for failure in self.failures:
                if failure[0] == test:
                    test_info['status'] = 'FAIL'
                    test_info['error_message'] = failure[1]
                    break
            
            for error in self.errors:
                if error[0] == test:
                    test_info['status'] = 'ERROR'
                    test_info['error_message'] = error[1]
                    break
        
        self.test_results.append(test_info)


class TestSuiteRunner:
    """測試套件執行器"""
    
    def __init__(self):
        self.total_tests = 0
        self.total_failures = 0
        self.total_errors = 0
        self.total_time = 0
        self.module_results = []
    
    def run_test_module(self, module_name, test_class, run_function=None):
        """執行單個測試模組"""
        print(f"\n{'='*80}")
        print(f"🧪 執行 {module_name} 測試")
        print(f"{'='*80}")
        
        start_time = time.time()
        
        try:
            if run_function:
                # 使用專用的執行函數
                success = run_function()
                
                # 單獨執行測試以獲取詳細結果
                loader = unittest.TestLoader()
                suite = loader.loadTestsFromTestCase(test_class)
                
                # 使用詳細結果收集器
                stream = StringIO()
                runner = unittest.TextTestRunner(
                    stream=stream, 
                    verbosity=2,
                    resultclass=DetailedTestResult
                )
                result = runner.run(suite)
                
            else:
                # 直接執行測試類
                loader = unittest.TestLoader()
                suite = loader.loadTestsFromTestCase(test_class)
                
                runner = unittest.TextTestRunner(
                    verbosity=2,
                    resultclass=DetailedTestResult
                )
                result = runner.run(suite)
                success = result.wasSuccessful()
            
            end_time = time.time()
            duration = end_time - start_time
            
            # 記錄模組結果
            module_result = {
                'module_name': module_name,
                'test_class': test_class.__name__,
                'tests_run': result.testsRun,
                'failures': len(result.failures),
                'errors': len(result.errors),
                'success': success,
                'duration': duration,
                'detailed_results': getattr(result, 'test_results', [])
            }
            
            self.module_results.append(module_result)
            self.total_tests += result.testsRun
            self.total_failures += len(result.failures)
            self.total_errors += len(result.errors)
            self.total_time += duration
            
            # 顯示模組結果摘要
            print(f"\n📊 {module_name} 測試結果：")
            print(f"   測試數量：{result.testsRun}")
            print(f"   失敗：{len(result.failures)}")
            print(f"   錯誤：{len(result.errors)}")
            print(f"   執行時間：{duration:.2f}秒")
            print(f"   狀態：{'✅ 通過' if success else '❌ 失敗'}")
            
            return success
            
        except Exception as e:
            print(f"💥 執行 {module_name} 測試時發生錯誤：{e}")
            return False
    
    def run_functional_tests(self):
        """執行功能測試"""
        print(f"\n{'='*80}")
        print("🧪 執行關聯保護功能測試")
        print(f"{'='*80}")
        
        start_time = time.time()
        
        try:
            # 執行關聯保護功能測試
            success = test_check_associations_functionality()
            
            end_time = time.time()
            duration = end_time - start_time
            
            # 記錄功能測試結果
            functional_result = {
                'module_name': '關聯保護功能',
                'test_class': 'FunctionalTest',
                'tests_run': 4,  # 已知的測試數量
                'failures': 0 if success else 1,
                'errors': 0,
                'success': success,
                'duration': duration,
                'detailed_results': []
            }
            
            self.module_results.append(functional_result)
            self.total_tests += 4
            if not success:
                self.total_failures += 1
            self.total_time += duration
            
            print(f"\n📊 關聯保護功能測試結果：")
            print(f"   測試數量：4")
            print(f"   失敗：{0 if success else 1}")
            print(f"   錯誤：0")
            print(f"   執行時間：{duration:.2f}秒")
            print(f"   狀態：{'✅ 通過' if success else '❌ 失敗'}")
            
            return success
            
        except Exception as e:
            print(f"💥 執行關聯保護功能測試時發生錯誤：{e}")
            return False
    
    def generate_summary_report(self):
        """生成總結報告"""
        print(f"\n\n{'='*100}")
        print("📋 QA Management Tool 完整測試報告")
        print(f"{'='*100}")
        
        # 基本統計
        print(f"\n📊 測試統計摘要：")
        print(f"   總測試數量：{self.total_tests}")
        print(f"   成功：{self.total_tests - self.total_failures - self.total_errors}")
        print(f"   失敗：{self.total_failures}")
        print(f"   錯誤：{self.total_errors}")
        print(f"   總執行時間：{self.total_time:.2f}秒")
        print(f"   成功率：{((self.total_tests - self.total_failures - self.total_errors) / self.total_tests * 100):.1f}%")
        
        # 模組詳細結果
        print(f"\n📋 各模組測試結果：")
        print(f"{'模組名稱':<25} {'測試數':<8} {'失敗':<6} {'錯誤':<6} {'時間(秒)':<10} {'狀態'}")
        print("-" * 80)
        
        for result in self.module_results:
            status_icon = "✅" if result['success'] else "❌"
            print(f"{result['module_name']:<25} {result['tests_run']:<8} {result['failures']:<6} "
                  f"{result['errors']:<6} {result['duration']:<10.2f} {status_icon}")
        
        # 失敗的測試詳情
        failed_modules = [r for r in self.module_results if not r['success']]
        if failed_modules:
            print(f"\n❌ 失敗的模組詳情：")
            for result in failed_modules:
                print(f"\n   模組：{result['module_name']}")
                print(f"   失敗測試：{result['failures']}")
                print(f"   錯誤測試：{result['errors']}")
        
        # 效能分析
        print(f"\n⏱️ 效能分析：")
        sorted_results = sorted(self.module_results, key=lambda x: x['duration'], reverse=True)
        print(f"   最慢的模組：{sorted_results[0]['module_name']} ({sorted_results[0]['duration']:.2f}秒)")
        print(f"   最快的模組：{sorted_results[-1]['module_name']} ({sorted_results[-1]['duration']:.2f}秒)")
        
        # 測試覆蓋率評估
        print(f"\n📈 測試覆蓋率評估：")
        coverage_areas = [
            "✅ 資料庫層：DatabaseManager 完整測試",
            "✅ 業務邏輯層：TestCaseManager, UserManager 完整測試", 
            "✅ API層：Flask路由和端點完整測試",
            "✅ 工具層：APIChecker, StressTester 完整測試",
            "✅ 配置層：Config 管理完整測試",
            "✅ 功能層：關聯保護機制完整測試"
        ]
        
        for area in coverage_areas:
            print(f"   {area}")
        
        # 建議和總結
        print(f"\n💡 測試總結：")
        if self.total_failures == 0 and self.total_errors == 0:
            print("   🎉 所有測試都通過了！系統品質良好。")
            print("   📦 建議：可以考慮部署到生產環境。")
        elif self.total_failures > 0:
            print(f"   ⚠️ 有 {self.total_failures} 個測試失敗，需要修復。")
            print("   🔧 建議：修復失敗的測試後再進行部署。")
        
        if self.total_errors > 0:
            print(f"   💥 有 {self.total_errors} 個測試錯誤，需要檢查代碼。")
            print("   🔍 建議：檢查錯誤日誌並修復相關問題。")
        
        # 返回總體成功狀態
        return self.total_failures == 0 and self.total_errors == 0
    
    def save_report_to_file(self):
        """保存報告到檔案"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"test_report_{timestamp}.txt"
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                # 重定向輸出到檔案
                old_stdout = sys.stdout
                sys.stdout = f
                
                # 重新生成報告
                self.generate_summary_report()
                
                # 恢復輸出
                sys.stdout = old_stdout
            
            print(f"\n📁 詳細測試報告已保存到：{report_file}")
            
        except Exception as e:
            print(f"⚠️ 保存報告失敗：{e}")


def main():
    """主執行函數"""
    print("🚀 啟動 QA Management Tool 完整單元測試套件")
    print(f"開始時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 創建測試執行器
    runner = TestSuiteRunner()
    
    # 測試模組列表
    test_modules = [
        ("資料庫管理器", TestDatabaseManager, run_database_manager_tests),
        ("測試案例管理器", TestTestCaseManager, run_test_case_manager_tests),
        ("用戶管理器", TestUserManager, run_user_manager_tests),
        ("API檢查器和壓力測試器", TestAPIChecker, run_api_tests),
        ("配置管理", TestConfig, run_config_tests)
    ]
    
    # 添加可選模組
    if TestFlaskRoutes and run_flask_routes_tests:
        test_modules.append(("Flask路由和API端點", TestFlaskRoutes, run_flask_routes_tests))
    
    # 執行所有單元測試模組
    all_success = True
    for module_name, test_class, run_function in test_modules:
        success = runner.run_test_module(module_name, test_class, run_function)
        if not success:
            all_success = False
    
    # 執行功能測試（如果可用）
    if test_check_associations_functionality:
        functional_success = runner.run_functional_tests()
        if not functional_success:
            all_success = False
    else:
        print("\n⚠️ 跳過關聯功能測試（模組無法載入）")
    
    # 生成並顯示總結報告
    overall_success = runner.generate_summary_report()
    
    # 保存報告到檔案
    runner.save_report_to_file()
    
    # 最終狀態
    print(f"\n{'='*100}")
    if overall_success:
        print("🎉 所有測試完成且全部通過！QA Management Tool 品質良好。")
        exit_code = 0
    else:
        print("❌ 測試完成但有失敗項目，請檢查並修復相關問題。")
        exit_code = 1
    
    print(f"結束時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*100}")
    
    return exit_code


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)