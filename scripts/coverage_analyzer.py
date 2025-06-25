#!/usr/bin/env python3
"""
測試覆蓋率分析器
分析當前項目的測試覆蓋情況，包括檔案覆蓋率、功能覆蓋率和代碼行覆蓋率
"""

import os
import sys
import ast
from pathlib import Path
from typing import Dict, List, Set, Tuple
import re

class CoverageAnalyzer:
    """測試覆蓋率分析器"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.source_files = []
        self.test_files = []
        self.coverage_data = {}
        
    def scan_files(self):
        """掃描專案文件"""
        print("🔍 掃描專案文件...")
        
        # 排除的目錄和模式
        exclude_patterns = [
            'venv', '.venv', 'env', '.env',  # 虛擬環境
            '.git', '.pytest_cache', '__pycache__',  # 隱藏目錄
            'node_modules', 'build', 'dist',  # 構建目錄
            'scripts', 'tests'  # 腳本和測試目錄
        ]
        
        # 掃描源文件
        for py_file in self.project_root.rglob("*.py"):
            # 檢查是否在排除路徑中
            should_exclude = False
            for part in py_file.parts:
                if part in exclude_patterns or part.startswith('.'):
                    should_exclude = True
                    break
            
            if should_exclude:
                continue
                
            # 排除測試文件和特定文件
            if (py_file.name.startswith('test_') or 
                py_file.name.startswith('_') or
                'test_' in py_file.name):
                if py_file.name.startswith('test_'):
                    self.test_files.append(py_file)
                continue
            else:
                self.source_files.append(py_file)
        
        # 單獨掃描測試文件
        for py_file in self.project_root.rglob("test_*.py"):
            if py_file not in self.test_files:
                self.test_files.append(py_file)
        
        print(f"   📁 源文件: {len(self.source_files)}")
        print(f"   🧪 測試文件: {len(self.test_files)}")
    
    def analyze_file_coverage(self) -> Dict:
        """分析文件級別的覆蓋率"""
        print("\n📊 分析文件覆蓋率...")
        
        covered_files = set()
        uncovered_files = set()
        
        # 分析哪些源文件有對應的測試
        for source_file in self.source_files:
            source_name = source_file.stem
            has_test = False
            
            # 檢查是否有對應的測試文件
            for test_file in self.test_files:
                if source_name in test_file.name or self._is_testing_file(test_file, source_file):
                    covered_files.add(source_file)
                    has_test = True
                    break
            
            if not has_test:
                uncovered_files.add(source_file)
        
        coverage_rate = len(covered_files) / len(self.source_files) * 100 if self.source_files else 0
        
        return {
            'total_files': len(self.source_files),
            'covered_files': len(covered_files),
            'uncovered_files': len(uncovered_files),
            'coverage_rate': coverage_rate,
            'covered_list': list(covered_files),
            'uncovered_list': list(uncovered_files)
        }
    
    def _is_testing_file(self, test_file: Path, source_file: Path) -> bool:
        """檢查測試文件是否測試了指定的源文件"""
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # 檢查import語句
                source_module = source_file.stem
                import_patterns = [
                    f"from {source_module} import",
                    f"import {source_module}",
                    f"from .{source_module} import",
                    f"import .{source_module}"
                ]
                
                for pattern in import_patterns:
                    if pattern in content:
                        return True
                        
        except Exception:
            pass
        return False
    
    def analyze_function_coverage(self) -> Dict:
        """分析函數級別的覆蓋率"""
        print("📊 分析函數覆蓋率...")
        
        function_stats = {}
        
        for source_file in self.source_files:
            try:
                functions = self._extract_functions(source_file)
                tested_functions = self._find_tested_functions(source_file)
                
                total_functions = len(functions)
                covered_functions = len(tested_functions)
                coverage_rate = (covered_functions / total_functions * 100) if total_functions > 0 else 0
                
                function_stats[str(source_file.relative_to(self.project_root))] = {
                    'total_functions': total_functions,
                    'covered_functions': covered_functions,
                    'coverage_rate': coverage_rate,
                    'functions': functions,
                    'tested_functions': list(tested_functions)
                }
                
            except Exception as e:
                print(f"   ⚠️ 分析 {source_file} 時發生錯誤: {e}")
        
        return function_stats
    
    def _extract_functions(self, file_path: Path) -> List[str]:
        """提取文件中的函數名"""
        functions = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
                
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    # 提取類中的方法
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            functions.append(f"{node.name}.{item.name}")
                            
        except Exception as e:
            print(f"   ⚠️ 解析 {file_path} 失敗: {e}")
        
        return functions
    
    def _find_tested_functions(self, source_file: Path) -> Set[str]:
        """查找被測試的函數"""
        tested_functions = set()
        source_module = source_file.stem
        
        for test_file in self.test_files:
            if source_module in test_file.name or self._is_testing_file(test_file, source_file):
                try:
                    with open(test_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 使用正則表達式查找測試的函數
                    patterns = [
                        r'def test_(\w+)',  # test_function_name
                        r'\.(\w+)\(',       # object.method()
                        r'(\w+)\(',         # function()
                    ]
                    
                    for pattern in patterns:
                        matches = re.findall(pattern, content)
                        tested_functions.update(matches)
                        
                except Exception:
                    continue
        
        return tested_functions
    
    def analyze_test_quality(self) -> Dict:
        """分析測試質量"""
        print("📊 分析測試質量...")
        
        test_stats = {}
        total_tests = 0
        total_assertions = 0
        
        for test_file in self.test_files:
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 統計測試方法數量
                test_methods = len(re.findall(r'def test_\w+', content))
                
                # 統計斷言數量
                assertion_patterns = [
                    r'self\.assert\w+',
                    r'assert\s+',
                    r'self\.fail',
                    r'self\.assertTrue',
                    r'self\.assertFalse',
                    r'self\.assertEqual',
                    r'self\.assertIn',
                    r'self\.assertIsNone'
                ]
                
                assertions = 0
                for pattern in assertion_patterns:
                    assertions += len(re.findall(pattern, content))
                
                total_tests += test_methods
                total_assertions += assertions
                
                test_stats[str(test_file.relative_to(self.project_root))] = {
                    'test_methods': test_methods,
                    'assertions': assertions,
                    'assertions_per_test': assertions / test_methods if test_methods > 0 else 0
                }
                
            except Exception as e:
                print(f"   ⚠️ 分析 {test_file} 時發生錯誤: {e}")
        
        return {
            'test_files': test_stats,
            'total_tests': total_tests,
            'total_assertions': total_assertions,
            'avg_assertions_per_test': total_assertions / total_tests if total_tests > 0 else 0
        }
    
    def generate_coverage_report(self) -> Dict:
        """生成完整的覆蓋率報告"""
        print("📋 生成覆蓋率報告...")
        
        file_coverage = self.analyze_file_coverage()
        function_coverage = self.analyze_function_coverage()
        test_quality = self.analyze_test_quality()
        
        # 計算整體函數覆蓋率
        total_functions = sum(stats['total_functions'] for stats in function_coverage.values())
        covered_functions = sum(stats['covered_functions'] for stats in function_coverage.values())
        overall_function_coverage = (covered_functions / total_functions * 100) if total_functions > 0 else 0
        
        return {
            'file_coverage': file_coverage,
            'function_coverage': function_coverage,
            'overall_function_coverage': overall_function_coverage,
            'test_quality': test_quality,
            'summary': {
                'file_coverage_rate': file_coverage['coverage_rate'],
                'function_coverage_rate': overall_function_coverage,
                'total_source_files': len(self.source_files),
                'total_test_files': len(self.test_files),
                'total_tests': test_quality['total_tests'],
                'test_to_source_ratio': len(self.test_files) / len(self.source_files) if self.source_files else 0
            }
        }
    
    def print_detailed_report(self, report: Dict):
        """打印詳細報告"""
        print("\n" + "=" * 80)
        print("📊 測試覆蓋率詳細報告")
        print("=" * 80)
        
        summary = report['summary']
        file_cov = report['file_coverage']
        
        # 總覽
        print(f"\n📋 總覽:")
        print(f"   📁 源文件數量: {summary['total_source_files']}")
        print(f"   🧪 測試文件數量: {summary['total_test_files']}")
        print(f"   📊 測試/源文件比例: {summary['test_to_source_ratio']:.2f}")
        print(f"   🎯 總測試數量: {summary['total_tests']}")
        
        # 文件覆蓋率
        print(f"\n📊 文件覆蓋率: {file_cov['coverage_rate']:.1f}%")
        print(f"   ✅ 有測試的文件: {file_cov['covered_files']}/{file_cov['total_files']}")
        print(f"   ❌ 無測試的文件: {file_cov['uncovered_files']}/{file_cov['total_files']}")
        
        # 函數覆蓋率
        func_cov_rate = report['overall_function_coverage']
        print(f"\n📊 函數覆蓋率: {func_cov_rate:.1f}%")
        
        # 測試質量
        test_quality = report['test_quality']
        print(f"\n📊 測試質量:")
        print(f"   🧪 平均每個測試的斷言數: {test_quality['avg_assertions_per_test']:.1f}")
        print(f"   📝 總斷言數: {test_quality['total_assertions']}")
        
        # 未覆蓋的文件
        if file_cov['uncovered_list']:
            print(f"\n❌ 缺少測試的文件:")
            for file in file_cov['uncovered_list']:
                print(f"   - {file.relative_to(self.project_root)}")
        
        # 覆蓋率評級
        print(f"\n📈 覆蓋率評級:")
        file_grade = self._get_coverage_grade(file_cov['coverage_rate'])
        func_grade = self._get_coverage_grade(func_cov_rate)
        print(f"   📁 文件覆蓋率: {file_grade}")
        print(f"   🔧 函數覆蓋率: {func_grade}")
        
        # 改進建議
        print(f"\n💡 改進建議:")
        self._print_recommendations(report)
    
    def _get_coverage_grade(self, coverage_rate: float) -> str:
        """獲取覆蓋率評級"""
        if coverage_rate >= 90:
            return f"{coverage_rate:.1f}% - 🟢 優秀"
        elif coverage_rate >= 80:
            return f"{coverage_rate:.1f}% - 🟡 良好"
        elif coverage_rate >= 70:
            return f"{coverage_rate:.1f}% - 🟠 一般"
        elif coverage_rate >= 60:
            return f"{coverage_rate:.1f}% - 🔴 偏低"
        else:
            return f"{coverage_rate:.1f}% - ⚫ 嚴重不足"
    
    def _print_recommendations(self, report: Dict):
        """打印改進建議"""
        file_rate = report['file_coverage']['coverage_rate']
        func_rate = report['overall_function_coverage']
        test_quality = report['test_quality']
        
        recommendations = []
        
        if file_rate < 80:
            recommendations.append("為缺少測試的文件添加單元測試")
        
        if func_rate < 70:
            recommendations.append("增加函數級別的測試覆蓋")
        
        if test_quality['avg_assertions_per_test'] < 2:
            recommendations.append("增加測試的斷言數量，提高測試的深度")
        
        if report['summary']['test_to_source_ratio'] < 0.5:
            recommendations.append("增加測試文件數量，建議測試文件與源文件比例至少為1:2")
        
        if len(report['file_coverage']['uncovered_list']) > 5:
            recommendations.append("優先為核心業務邏輯文件添加測試")
        
        if not recommendations:
            recommendations.append("當前測試覆蓋率良好，建議維持現有質量標準")
        
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")

def main():
    """主函數"""
    print("🚀 開始測試覆蓋率分析...")
    
    analyzer = CoverageAnalyzer()
    analyzer.scan_files()
    
    report = analyzer.generate_coverage_report()
    analyzer.print_detailed_report(report)
    
    # 保存報告到文件
    import json
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"coverage_report_{timestamp}.json"
    
    # 轉換Path對象為字符串以便JSON序列化
    json_report = {}
    for key, value in report.items():
        if key == 'file_coverage':
            json_report[key] = {
                **value,
                'covered_list': [str(p.relative_to(Path("."))) for p in value['covered_list']],
                'uncovered_list': [str(p.relative_to(Path("."))) for p in value['uncovered_list']]
            }
        else:
            json_report[key] = value
    
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(json_report, f, indent=2, ensure_ascii=False)
        print(f"\n📁 詳細報告已保存到: {report_file}")
    except Exception as e:
        print(f"⚠️ 保存報告失敗: {e}")
    
    # 返回覆蓋率分數
    overall_score = (report['summary']['file_coverage_rate'] + report['summary']['function_coverage_rate']) / 2
    print(f"\n🎯 總體覆蓋率分數: {overall_score:.1f}%")
    
    return 0 if overall_score >= 80 else 1

if __name__ == "__main__":
    sys.exit(main())