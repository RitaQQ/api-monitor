import json
import os
from typing import List, Dict, Optional, Any
from datetime import datetime
from models import TestCase, ProductTag, TestProject, TestResult, TestStatistics, TestStatus, ProjectStatus, generate_id

class TestCaseManager:
    """測試案例管理器"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.test_cases_file = os.path.join(data_dir, "test_cases.json")
        self.product_tags_file = os.path.join(data_dir, "product_tags.json")
        self.test_projects_file = os.path.join(data_dir, "test_projects.json")
        
        # 確保資料目錄存在
        os.makedirs(data_dir, exist_ok=True)
        
        # 初始化檔案
        self._init_files()
    
    def _init_files(self):
        """初始化資料檔案"""
        for file_path in [self.test_cases_file, self.product_tags_file, self.test_projects_file]:
            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump([], f, ensure_ascii=False, indent=2)
    
    def _load_json(self, file_path: str) -> List[Dict]:
        """載入JSON檔案"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_json(self, file_path: str, data: List[Dict]):
        """儲存JSON檔案"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    # ========== Product Tags 管理 ==========
    
    def get_product_tags(self) -> List[ProductTag]:
        """取得所有產品標籤"""
        data = self._load_json(self.product_tags_file)
        return [ProductTag.from_dict(item) for item in data]
    
    def create_product_tag(self, name: str, description: Optional[str] = None) -> ProductTag:
        """建立產品標籤"""
        tag = ProductTag(
            id=generate_id(),
            name=name,
            description=description
        )
        
        tags = self._load_json(self.product_tags_file)
        tags.append(tag.to_dict())
        self._save_json(self.product_tags_file, tags)
        
        return tag
    
    def update_product_tag(self, tag_id: str, name: Optional[str] = None, 
                          description: Optional[str] = None) -> Optional[ProductTag]:
        """更新產品標籤"""
        tags = self._load_json(self.product_tags_file)
        
        for i, tag_data in enumerate(tags):
            if tag_data['id'] == tag_id:
                if name is not None:
                    tag_data['name'] = name
                if description is not None:
                    tag_data['description'] = description
                
                tags[i] = tag_data
                self._save_json(self.product_tags_file, tags)
                return ProductTag.from_dict(tag_data)
        
        return None
    
    def delete_product_tag(self, tag_id: str) -> bool:
        """刪除產品標籤（同時從測試案例中移除關聯）"""
        tags = self._load_json(self.product_tags_file)
        original_length = len(tags)
        
        tags = [tag for tag in tags if tag['id'] != tag_id]
        
        if len(tags) < original_length:
            # 保存更新後的標籤列表
            self._save_json(self.product_tags_file, tags)
            
            # 從所有測試案例中移除此標籤的關聯
            test_cases = self._load_json(self.test_cases_file)
            updated = False
            for test_case in test_cases:
                if 'product_tags' in test_case and tag_id in test_case['product_tags']:
                    test_case['product_tags'].remove(tag_id)
                    test_case['updated_at'] = datetime.now().isoformat()
                    updated = True
            
            if updated:
                self._save_json(self.test_cases_file, test_cases)
            
            return True
        
        return False
    
    # ========== Test Cases 管理 ==========
    
    def get_test_cases(self) -> List[TestCase]:
        """取得所有測試案例"""
        data = self._load_json(self.test_cases_file)
        return [TestCase.from_dict(item) for item in data]
    
    def get_test_case(self, case_id: str) -> Optional[TestCase]:
        """取得特定測試案例"""
        data = self._load_json(self.test_cases_file)
        for item in data:
            if item['id'] == case_id:
                return TestCase.from_dict(item)
        return None
    
    def create_test_case(self, title: str, user_role: str, feature_description: str,
                        acceptance_criteria: List[str], test_notes: Optional[str] = None,
                        product_tags: Optional[List[str]] = None) -> TestCase:
        """建立測試案例"""
        test_case = TestCase(
            id=generate_id(),
            title=title,
            user_role=user_role,
            feature_description=feature_description,
            acceptance_criteria=acceptance_criteria,
            test_notes=test_notes,
            product_tags=product_tags or []
        )
        
        cases = self._load_json(self.test_cases_file)
        cases.append(test_case.to_dict())
        self._save_json(self.test_cases_file, cases)
        
        return test_case
    
    def update_test_case(self, case_id: str, **kwargs) -> Optional[TestCase]:
        """更新測試案例"""
        cases = self._load_json(self.test_cases_file)
        
        for i, case_data in enumerate(cases):
            if case_data['id'] == case_id:
                # 更新允許的欄位
                allowed_fields = ['title', 'user_role', 'feature_description', 
                                'acceptance_criteria', 'test_notes', 'product_tags']
                
                for field, value in kwargs.items():
                    if field in allowed_fields and value is not None:
                        case_data[field] = value
                
                case_data['updated_at'] = datetime.now().isoformat()
                cases[i] = case_data
                self._save_json(self.test_cases_file, cases)
                return TestCase.from_dict(case_data)
        
        return None
    
    def delete_test_case(self, case_id: str) -> bool:
        """刪除測試案例"""
        cases = self._load_json(self.test_cases_file)
        original_length = len(cases)
        
        cases = [case for case in cases if case['id'] != case_id]
        
        if len(cases) < original_length:
            self._save_json(self.test_cases_file, cases)
            return True
        
        return False
    
    def batch_update_test_cases(self, updates: List[Dict[str, Any]]) -> List[TestCase]:
        """批量更新測試案例"""
        cases = self._load_json(self.test_cases_file)
        updated_cases = []
        
        for update in updates:
            case_id = update.get('id')
            if not case_id:
                continue
                
            for i, case_data in enumerate(cases):
                if case_data['id'] == case_id:
                    # 更新允許的欄位
                    allowed_fields = ['title', 'user_role', 'feature_description', 
                                    'acceptance_criteria', 'test_notes', 'product_tags']
                    
                    for field, value in update.items():
                        if field in allowed_fields and field != 'id':
                            case_data[field] = value
                    
                    case_data['updated_at'] = datetime.now().isoformat()
                    cases[i] = case_data
                    updated_cases.append(TestCase.from_dict(case_data))
                    break
        
        self._save_json(self.test_cases_file, cases)
        return updated_cases
    
    # ========== Test Projects 管理 ==========
    
    def get_test_projects(self) -> List[TestProject]:
        """取得所有測試專案"""
        data = self._load_json(self.test_projects_file)
        return [TestProject.from_dict(item) for item in data]
    
    def get_test_project(self, project_id: str) -> Optional[TestProject]:
        """取得特定測試專案"""
        data = self._load_json(self.test_projects_file)
        for item in data:
            if item['id'] == project_id:
                return TestProject.from_dict(item)
        return None
    
    def create_test_project(self, name: str, responsible_user: str,
                           selected_test_cases: List[str], start_time: Optional[datetime] = None,
                           end_time: Optional[datetime] = None) -> TestProject:
        """建立測試專案"""
        project = TestProject(
            id=generate_id(),
            name=name,
            responsible_user=responsible_user,
            selected_test_cases=selected_test_cases,
            start_time=start_time,
            end_time=end_time
        )
        
        projects = self._load_json(self.test_projects_file)
        projects.append(project.to_dict())
        self._save_json(self.test_projects_file, projects)
        
        return project
    
    def update_test_project(self, project_id: str, **kwargs) -> Optional[TestProject]:
        """更新測試專案"""
        projects = self._load_json(self.test_projects_file)
        
        for i, project_data in enumerate(projects):
            if project_data['id'] == project_id:
                # 更新允許的欄位
                allowed_fields = ['name', 'start_time', 'end_time', 'responsible_user', 
                                'selected_test_cases', 'status']
                
                for field, value in kwargs.items():
                    if field in allowed_fields and value is not None:
                        if field in ['start_time', 'end_time'] and isinstance(value, datetime):
                            project_data[field] = value.isoformat()
                        elif field == 'status' and isinstance(value, ProjectStatus):
                            project_data[field] = value.value
                        else:
                            project_data[field] = value
                
                project_data['updated_at'] = datetime.now().isoformat()
                projects[i] = project_data
                self._save_json(self.test_projects_file, projects)
                return TestProject.from_dict(project_data)
        
        return None
    
    def update_test_result(self, project_id: str, test_case_id: str, 
                          status: TestStatus, notes: Optional[str] = None,
                          known_issues: Optional[str] = None,
                          blocked_reason: Optional[str] = None) -> Optional[TestProject]:
        """更新測試結果"""
        projects = self._load_json(self.test_projects_file)
        
        for i, project_data in enumerate(projects):
            if project_data['id'] == project_id:
                test_result = TestResult(
                    test_case_id=test_case_id,
                    status=status,
                    notes=notes,
                    known_issues=known_issues,
                    blocked_reason=blocked_reason
                )
                
                if 'test_results' not in project_data:
                    project_data['test_results'] = {}
                
                project_data['test_results'][test_case_id] = test_result.to_dict()
                project_data['updated_at'] = datetime.now().isoformat()
                
                projects[i] = project_data
                self._save_json(self.test_projects_file, projects)
                return TestProject.from_dict(project_data)
        
        return None
    
    def delete_test_project(self, project_id: str) -> bool:
        """刪除測試專案"""
        projects = self._load_json(self.test_projects_file)
        original_length = len(projects)
        
        projects = [project for project in projects if project['id'] != project_id]
        
        if len(projects) < original_length:
            self._save_json(self.test_projects_file, projects)
            return True
        
        return False
    
    # ========== 統計功能 ==========
    
    def get_project_statistics(self, project_id: str) -> Optional[TestStatistics]:
        """取得專案統計"""
        project = self.get_test_project(project_id)
        if not project:
            return None
        
        test_cases = {case.id: case for case in self.get_test_cases() 
                     if case.id in project.selected_test_cases}
        product_tags = {tag.id: tag for tag in self.get_product_tags()}
        
        total_cases = len(project.selected_test_cases)
        passed_cases = sum(1 for result in project.test_results.values() 
                          if result.status == TestStatus.PASS)
        failed_cases = sum(1 for result in project.test_results.values() 
                          if result.status == TestStatus.FAIL)
        blocked_cases = sum(1 for result in project.test_results.values() 
                           if result.status == TestStatus.BLOCKED)
        not_tested_cases = total_cases - len(project.test_results)
        
        pass_rate = (passed_cases / total_cases * 100) if total_cases > 0 else 0
        fail_rate = (failed_cases / total_cases * 100) if total_cases > 0 else 0
        
        # 計算各產品標籤的統計
        product_stats = {}
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
            tag_blocked = sum(1 for case in tag_cases 
                            if case.id in project.test_results and 
                            project.test_results[case.id].status == TestStatus.BLOCKED)
            tag_pass_rate = (tag_passed / tag_total * 100) if tag_total > 0 else 0
            
            product_stats[tag.name] = {
                'total': tag_total,
                'passed': tag_passed,
                'failed': tag_failed,
                'blocked': tag_blocked,
                'not_tested': tag_total - tag_passed - tag_failed - tag_blocked,
                'pass_rate': round(tag_pass_rate, 2)
            }
        
        return TestStatistics(
            total_cases=total_cases,
            passed_cases=passed_cases,
            failed_cases=failed_cases,
            blocked_cases=blocked_cases,
            not_tested_cases=not_tested_cases,
            pass_rate=round(pass_rate, 2),
            fail_rate=round(fail_rate, 2),
            product_stats=product_stats
        )