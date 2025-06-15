import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from models import TestProject, TestCase, ProductTag, TestStatistics, TestStatus
from test_case_manager import TestCaseManager

@dataclass
class ProductStats:
    """產品統計資料"""
    product_name: str
    total_cases: int
    passed_cases: int
    failed_cases: int
    not_tested_cases: int
    pass_rate: float
    fail_rate: float
    critical_failures: List[str]  # 重要失敗項目

@dataclass
class ProjectReport:
    """專案報告"""
    project: TestProject
    statistics: TestStatistics
    product_stats: List[ProductStats]
    test_case_details: List[Dict[str, Any]]
    summary: Dict[str, Any]

class ReportGenerator:
    """報告生成器"""
    
    def __init__(self, test_case_manager: TestCaseManager):
        self.manager = test_case_manager
    
    def generate_project_report(self, project_id: str) -> Optional[ProjectReport]:
        """生成專案報告"""
        project = self.manager.get_test_project(project_id)
        if not project:
            return None
        
        # 取得相關資料
        test_cases = {tc.id: tc for tc in self.manager.get_test_cases() 
                     if tc.id in project.selected_test_cases}
        product_tags = {tag.id: tag for tag in self.manager.get_product_tags()}
        
        # 計算統計資料
        statistics = self._calculate_statistics(project, test_cases, product_tags)
        
        # 計算產品統計
        product_stats = self._calculate_product_stats(project, test_cases, product_tags)
        
        # 生成測試案例詳情
        test_case_details = self._generate_test_case_details(project, test_cases, product_tags)
        
        # 生成摘要
        summary = self._generate_summary(project, statistics, product_stats)
        
        return ProjectReport(
            project=project,
            statistics=statistics,
            product_stats=product_stats,
            test_case_details=test_case_details,
            summary=summary
        )
    
    def _calculate_statistics(self, project: TestProject, test_cases: Dict[str, TestCase], 
                            product_tags: Dict[str, ProductTag]) -> TestStatistics:
        """計算統計資料"""
        total_cases = len(project.selected_test_cases)
        passed_cases = sum(1 for result in project.test_results.values() 
                          if result.status == TestStatus.PASS)
        failed_cases = sum(1 for result in project.test_results.values() 
                          if result.status == TestStatus.FAIL)
        not_tested_cases = total_cases - len(project.test_results)
        
        pass_rate = (passed_cases / total_cases * 100) if total_cases > 0 else 0
        fail_rate = (failed_cases / total_cases * 100) if total_cases > 0 else 0
        
        # 計算各產品標籤的統計
        product_stats_dict = {}
        for tag_id, tag in product_tags.items():
            tag_cases = [case for case in test_cases.values() 
                        if tag_id in case.product_tags]
            
            if not tag_cases:
                continue
            
            tag_total = len(tag_cases)
            tag_passed = sum(1 for case in tag_cases 
                           if case.id in project.test_results and 
                           project.test_results[case.id].status == TestStatus.PASS)
            tag_failed = sum(1 for case in tag_cases 
                           if case.id in project.test_results and 
                           project.test_results[case.id].status == TestStatus.FAIL)
            tag_pass_rate = (tag_passed / tag_total * 100) if tag_total > 0 else 0
            
            product_stats_dict[tag.name] = {
                'total': tag_total,
                'passed': tag_passed,
                'failed': tag_failed,
                'not_tested': tag_total - tag_passed - tag_failed,
                'pass_rate': round(tag_pass_rate, 2)
            }
        
        return TestStatistics(
            total_cases=total_cases,
            passed_cases=passed_cases,
            failed_cases=failed_cases,
            not_tested_cases=not_tested_cases,
            pass_rate=round(pass_rate, 2),
            fail_rate=round(fail_rate, 2),
            product_stats=product_stats_dict
        )
    
    def _calculate_product_stats(self, project: TestProject, test_cases: Dict[str, TestCase], 
                               product_tags: Dict[str, ProductTag]) -> List[ProductStats]:
        """計算產品統計"""
        product_stats = []
        
        for tag_id, tag in product_tags.items():
            tag_cases = [case for case in test_cases.values() 
                        if tag_id in case.product_tags]
            
            if not tag_cases:
                continue
            
            total = len(tag_cases)
            passed = sum(1 for case in tag_cases 
                        if case.id in project.test_results and 
                        project.test_results[case.id].status == TestStatus.PASS)
            failed = sum(1 for case in tag_cases 
                        if case.id in project.test_results and 
                        project.test_results[case.id].status == TestStatus.FAIL)
            not_tested = total - passed - failed
            
            pass_rate = (passed / total * 100) if total > 0 else 0
            fail_rate = (failed / total * 100) if total > 0 else 0
            
            # 找出重要失敗項目
            critical_failures = []
            for case in tag_cases:
                if (case.id in project.test_results and 
                    project.test_results[case.id].status == TestStatus.FAIL):
                    result = project.test_results[case.id]
                    failure_info = f"{case.title}"
                    if result.known_issues:
                        failure_info += f" - {result.known_issues}"
                    critical_failures.append(failure_info)
            
            product_stats.append(ProductStats(
                product_name=tag.name,
                total_cases=total,
                passed_cases=passed,
                failed_cases=failed,
                not_tested_cases=not_tested,
                pass_rate=round(pass_rate, 2),
                fail_rate=round(fail_rate, 2),
                critical_failures=critical_failures
            ))
        
        # 按通過率排序
        product_stats.sort(key=lambda x: x.pass_rate, reverse=True)
        return product_stats
    
    def _generate_test_case_details(self, project: TestProject, test_cases: Dict[str, TestCase], 
                                  product_tags: Dict[str, ProductTag]) -> List[Dict[str, Any]]:
        """生成測試案例詳情"""
        details = []
        
        for case_id in project.selected_test_cases:
            case = test_cases.get(case_id)
            if not case:
                continue
            
            result = project.test_results.get(case_id)
            
            # 產品標籤名稱
            tag_names = [product_tags[tag_id].name for tag_id in case.product_tags 
                        if tag_id in product_tags]
            
            detail = {
                'id': case.id,
                'title': case.title,
                'user_role': case.user_role,
                'feature_description': case.feature_description,
                'acceptance_criteria': case.acceptance_criteria,
                'test_notes': case.test_notes,
                'product_tags': tag_names,
                'status': result.status.value if result else 'not_tested',
                'status_text': self._get_status_text(result.status if result else TestStatus.NOT_TESTED),
                'test_result_notes': result.notes if result else '',
                'known_issues': result.known_issues if result else '',
                'tested_at': result.tested_at.isoformat() if result and result.tested_at else None
            }
            
            details.append(detail)
        
        return details
    
    def _generate_summary(self, project: TestProject, statistics: TestStatistics, 
                         product_stats: List[ProductStats]) -> Dict[str, Any]:
        """生成摘要"""
        # 找出問題產品
        problematic_products = [ps for ps in product_stats if ps.fail_rate > 0 or ps.not_tested_cases > 0]
        
        # 找出完全通過的產品
        perfect_products = [ps for ps in product_stats if ps.pass_rate == 100.0 and ps.total_cases > 0]
        
        # 計算專案狀態建議
        if statistics.not_tested_cases > 0:
            project_status_suggestion = "測試尚未完成，建議繼續進行測試。"
        elif statistics.fail_rate == 0:
            project_status_suggestion = "所有測試案例均已通過，專案可進入下一階段。"
        elif statistics.fail_rate <= 10:
            project_status_suggestion = "測試通過率良好，建議修復失敗項目後發布。"
        elif statistics.fail_rate <= 25:
            project_status_suggestion = "測試通過率中等，需要重點關注失敗項目。"
        else:
            project_status_suggestion = "測試通過率偏低，建議延期發布並修復主要問題。"
        
        # 風險評估
        risk_level = "低"
        if statistics.fail_rate > 25:
            risk_level = "高"
        elif statistics.fail_rate > 10:
            risk_level = "中"
        
        return {
            'project_status_suggestion': project_status_suggestion,
            'risk_level': risk_level,
            'problematic_products': [{'name': ps.product_name, 'fail_rate': ps.fail_rate, 
                                    'critical_failures': ps.critical_failures} for ps in problematic_products],
            'perfect_products': [ps.product_name for ps in perfect_products],
            'completion_rate': round((len(project.test_results) / len(project.selected_test_cases) * 100) 
                                   if project.selected_test_cases else 0, 2),
            'top_issues': self._get_top_issues(project, statistics),
            'recommendations': self._generate_recommendations(statistics, product_stats)
        }
    
    def _get_status_text(self, status: TestStatus) -> str:
        """取得狀態文字"""
        status_map = {
            TestStatus.PASS: '通過',
            TestStatus.FAIL: '失敗',
            TestStatus.NOT_TESTED: '待測試'
        }
        return status_map.get(status, '未知')
    
    def _get_top_issues(self, project: TestProject, statistics: TestStatistics) -> List[Dict[str, Any]]:
        """取得主要問題"""
        issues = []
        
        # 失敗的測試案例
        failed_results = [(case_id, result) for case_id, result in project.test_results.items() 
                         if result.status == TestStatus.FAIL]
        
        for case_id, result in failed_results:
            issues.append({
                'type': '測試失敗',
                'description': result.known_issues if result.known_issues else '測試案例執行失敗',
                'test_case_id': case_id
            })
        
        # 未完成的測試
        if statistics.not_tested_cases > 0:
            issues.append({
                'type': '測試未完成',
                'description': f'還有 {statistics.not_tested_cases} 個測試案例尚未執行',
                'test_case_id': None
            })
        
        return issues[:5]  # 只返回前5個問題
    
    def _generate_recommendations(self, statistics: TestStatistics, 
                                product_stats: List[ProductStats]) -> List[str]:
        """生成建議"""
        recommendations = []
        
        if statistics.not_tested_cases > 0:
            recommendations.append(f"完成剩餘的 {statistics.not_tested_cases} 個測試案例")
        
        if statistics.fail_rate > 0:
            recommendations.append("優先修復失敗的測試案例")
        
        # 針對產品的建議
        for ps in product_stats:
            if ps.fail_rate > 50:
                recommendations.append(f"重點關注 {ps.product_name} 產品的品質問題")
            elif ps.not_tested_cases > ps.total_cases * 0.3:
                recommendations.append(f"加快 {ps.product_name} 產品的測試進度")
        
        if statistics.pass_rate >= 95:
            recommendations.append("測試結果優秀，可以考慮提前發布")
        elif statistics.pass_rate >= 80:
            recommendations.append("測試結果良好，修復小問題後即可發布")
        else:
            recommendations.append("測試結果需要改善，建議延期發布")
        
        return recommendations
    
    def export_to_dict(self, report: ProjectReport) -> Dict[str, Any]:
        """將報告匯出為字典格式"""
        return {
            'project': {
                'id': report.project.id,
                'name': report.project.name,
                'test_date': report.project.test_date.isoformat(),
                'responsible_user': report.project.responsible_user,
                'status': report.project.status.value,
                'created_at': report.project.created_at.isoformat(),
                'updated_at': report.project.updated_at.isoformat()
            },
            'statistics': report.statistics.to_dict(),
            'product_stats': [
                {
                    'product_name': ps.product_name,
                    'total_cases': ps.total_cases,
                    'passed_cases': ps.passed_cases,
                    'failed_cases': ps.failed_cases,
                    'not_tested_cases': ps.not_tested_cases,
                    'pass_rate': ps.pass_rate,
                    'fail_rate': ps.fail_rate,
                    'critical_failures': ps.critical_failures
                } for ps in report.product_stats
            ],
            'test_case_details': report.test_case_details,
            'summary': report.summary,
            'generated_at': datetime.now().isoformat()
        }
    
    def generate_comparison_report(self, project_ids: List[str]) -> Dict[str, Any]:
        """生成多專案比較報告"""
        reports = []
        
        for project_id in project_ids:
            report = self.generate_project_report(project_id)
            if report:
                reports.append(report)
        
        if not reports:
            return {}
        
        # 比較統計
        comparison_stats = {
            'projects': [],
            'overall_trends': {},
            'product_comparison': {},
            'recommendations': []
        }
        
        # 整理各專案統計
        for report in reports:
            comparison_stats['projects'].append({
                'name': report.project.name,
                'test_date': report.project.test_date.isoformat(),
                'pass_rate': report.statistics.pass_rate,
                'fail_rate': report.statistics.fail_rate,
                'completion_rate': report.summary['completion_rate']
            })
        
        # 計算趨勢
        pass_rates = [report.statistics.pass_rate for report in reports]
        comparison_stats['overall_trends'] = {
            'average_pass_rate': round(sum(pass_rates) / len(pass_rates), 2),
            'best_project': max(reports, key=lambda r: r.statistics.pass_rate).project.name,
            'worst_project': min(reports, key=lambda r: r.statistics.pass_rate).project.name,
            'improvement_trend': self._calculate_trend(reports)
        }
        
        return comparison_stats
    
    def _calculate_trend(self, reports: List[ProjectReport]) -> str:
        """計算改善趨勢"""
        if len(reports) < 2:
            return "資料不足"
        
        # 按測試日期排序
        sorted_reports = sorted(reports, key=lambda r: r.project.test_date)
        
        # 計算通過率趨勢
        pass_rates = [report.statistics.pass_rate for report in sorted_reports]
        
        if len(pass_rates) >= 2:
            if pass_rates[-1] > pass_rates[0]:
                return "改善中"
            elif pass_rates[-1] < pass_rates[0]:
                return "退步中"
            else:
                return "穩定"
        
        return "無法判斷"