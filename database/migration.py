import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Any
from database.db_manager import db_manager

class DataMigration:
    """資料遷移工具：從 JSON 檔案遷移到 SQLite 資料庫"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.apis_file = os.path.join(data_dir, "apis.json")
        self.users_file = os.path.join(data_dir, "users.json")
        self.test_cases_file = os.path.join(data_dir, "test_cases.json")
        self.test_projects_file = os.path.join(data_dir, "test_projects.json")
        self.product_tags_file = os.path.join(data_dir, "product_tags.json")
        self.user_stories_file = os.path.join(data_dir, "user_stories.json")
    
    def migrate_all(self, backup: bool = True) -> Dict[str, Any]:
        """遷移所有資料"""
        results = {
            'success': True,
            'message': '資料遷移完成',
            'details': {},
            'errors': []
        }
        
        try:
            if backup:
                self._backup_json_files()
            
            # 遷移用戶資料
            users_result = self.migrate_users()
            results['details']['users'] = users_result
            
            # 遷移 API 資料
            apis_result = self.migrate_apis()
            results['details']['apis'] = apis_result
            
            # 遷移產品標籤
            tags_result = self.migrate_product_tags()
            results['details']['product_tags'] = tags_result
            
            # 遷移測試專案
            projects_result = self.migrate_test_projects()
            results['details']['test_projects'] = projects_result
            
            # 遷移測試案例
            test_cases_result = self.migrate_test_cases()
            results['details']['test_cases'] = test_cases_result
            
            # 遷移用戶故事
            user_stories_result = self.migrate_user_stories()
            results['details']['user_stories'] = user_stories_result
            
        except Exception as e:
            results['success'] = False
            results['message'] = f'遷移過程中發生錯誤: {str(e)}'
            results['errors'].append(str(e))
        
        return results
    
    def migrate_users(self) -> Dict[str, Any]:
        """遷移用戶資料"""
        if not os.path.exists(self.users_file):
            return {'migrated': 0, 'message': '用戶檔案不存在，跳過遷移'}
        
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            users = data.get('users', []) if isinstance(data, dict) else data
            migrated_count = 0
            
            for user in users:
                # 檢查用戶是否已存在
                existing_query = "SELECT id FROM users WHERE username = ?"
                existing = db_manager.execute_query(existing_query, (user['username'],))
                
                if not existing:
                    query = """
                        INSERT INTO users (id, username, password_hash, email, role, created_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """
                    
                    # 確保有 ID
                    user_id = user.get('id', str(uuid.uuid4()))
                    created_at = user.get('created_at', datetime.now().isoformat())
                    
                    db_manager.execute_insert(query, (
                        user_id,
                        user['username'],
                        user['password_hash'],
                        user.get('email'),
                        user.get('role', 'user'),
                        created_at
                    ))
                    migrated_count += 1
            
            return {'migrated': migrated_count, 'message': f'成功遷移 {migrated_count} 個用戶'}
            
        except Exception as e:
            return {'migrated': 0, 'message': f'遷移用戶資料時發生錯誤: {str(e)}'}
    
    def migrate_apis(self) -> Dict[str, Any]:
        """遷移 API 資料"""
        if not os.path.exists(self.apis_file):
            return {'migrated': 0, 'message': 'API 檔案不存在，跳過遷移'}
        
        try:
            with open(self.apis_file, 'r', encoding='utf-8') as f:
                apis = json.load(f)
            
            migrated_count = 0
            stress_test_count = 0
            
            for api in apis:
                # 檢查 API 是否已存在
                existing_query = "SELECT id FROM apis WHERE url = ?"
                existing = db_manager.execute_query(existing_query, (api['url'],))
                
                if not existing:
                    query = """
                        INSERT INTO apis (
                            id, name, url, type, method, request_body,
                            status, response_time, last_check, error_count, 
                            last_error, last_response,
                            concurrent_requests, duration_seconds, interval_seconds,
                            created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
                    
                    # 提取壓力測試配置
                    stress_test = api.get('stress_test', {})
                    
                    api_id = api.get('id', str(uuid.uuid4()))
                    created_at = datetime.now().isoformat()
                    
                    db_manager.execute_insert(query, (
                        api_id,
                        api['name'],
                        api['url'],
                        api.get('type', 'REST'),
                        api.get('method', 'GET'),
                        api.get('request_body'),
                        api.get('status', 'unknown'),
                        api.get('response_time', 0),
                        api.get('last_check'),
                        api.get('error_count', 0),
                        api.get('last_error'),
                        api.get('last_response'),
                        stress_test.get('concurrent_requests', 1),
                        stress_test.get('duration_seconds', 10),
                        stress_test.get('interval_seconds', 1.0),
                        created_at
                    ))
                    migrated_count += 1
                    
                    # 遷移壓力測試結果
                    stress_test_count += self._migrate_stress_test_results(api_id, stress_test.get('results', []))
            
            return {
                'migrated': migrated_count, 
                'stress_tests': stress_test_count,
                'message': f'成功遷移 {migrated_count} 個 API 和 {stress_test_count} 個壓力測試結果'
            }
            
        except Exception as e:
            return {'migrated': 0, 'message': f'遷移 API 資料時發生錯誤: {str(e)}'}
    
    def migrate_product_tags(self) -> Dict[str, Any]:
        """遷移產品標籤"""
        if not os.path.exists(self.product_tags_file):
            return {'migrated': 0, 'message': '產品標籤檔案不存在，跳過遷移'}
        
        try:
            with open(self.product_tags_file, 'r', encoding='utf-8') as f:
                tags = json.load(f)
            
            migrated_count = 0
            
            for tag in tags:
                # 檢查標籤是否已存在
                existing_query = "SELECT id FROM product_tags WHERE name = ?"
                existing = db_manager.execute_query(existing_query, (tag['name'],))
                
                if not existing:
                    query = """
                        INSERT INTO product_tags (name, description, color, created_at)
                        VALUES (?, ?, ?, ?)
                    """
                    
                    created_at = tag.get('created_at', datetime.now().isoformat())
                    
                    db_manager.execute_insert(query, (
                        tag['name'],
                        tag.get('description'),
                        tag.get('color', '#007bff'),
                        created_at
                    ))
                    migrated_count += 1
            
            return {'migrated': migrated_count, 'message': f'成功遷移 {migrated_count} 個產品標籤'}
            
        except Exception as e:
            return {'migrated': 0, 'message': f'遷移產品標籤時發生錯誤: {str(e)}'}
    
    def migrate_test_projects(self) -> Dict[str, Any]:
        """遷移測試專案"""
        if not os.path.exists(self.test_projects_file):
            return {'migrated': 0, 'message': '測試專案檔案不存在，跳過遷移'}
        
        try:
            with open(self.test_projects_file, 'r', encoding='utf-8') as f:
                projects = json.load(f)
            
            migrated_count = 0
            
            for project in projects:
                # 檢查專案是否已存在
                existing_query = "SELECT id FROM test_projects WHERE name = ?"
                existing = db_manager.execute_query(existing_query, (project['name'],))
                
                if not existing:
                    query = """
                        INSERT INTO test_projects (name, description, status, responsible_user_id, created_at)
                        VALUES (?, ?, ?, ?, ?)
                    """
                    
                    created_at = project.get('created_at', datetime.now().isoformat())
                    
                    db_manager.execute_insert(query, (
                        project['name'],
                        project.get('description'),
                        project.get('status', 'draft'),
                        project.get('responsible_user_id'),
                        created_at
                    ))
                    migrated_count += 1
            
            return {'migrated': migrated_count, 'message': f'成功遷移 {migrated_count} 個測試專案'}
            
        except Exception as e:
            return {'migrated': 0, 'message': f'遷移測試專案時發生錯誤: {str(e)}'}
    
    def migrate_test_cases(self) -> Dict[str, Any]:
        """遷移測試案例"""
        if not os.path.exists(self.test_cases_file):
            return {'migrated': 0, 'message': '測試案例檔案不存在，跳過遷移'}
        
        try:
            with open(self.test_cases_file, 'r', encoding='utf-8') as f:
                test_cases = json.load(f)
            
            migrated_count = 0
            
            for tc in test_cases:
                # 檢查測試案例是否已存在
                existing_query = "SELECT id FROM test_cases WHERE tc_id = ?"
                existing = db_manager.execute_query(existing_query, (tc['tc_id'],))
                
                if not existing:
                    # 查找專案 ID
                    project_id = None
                    if tc.get('project_name'):
                        project_query = "SELECT id FROM test_projects WHERE name = ?"
                        project_result = db_manager.execute_query(project_query, (tc['project_name'],))
                        if project_result:
                            project_id = project_result[0]['id']
                    
                    query = """
                        INSERT INTO test_cases (
                            tc_id, title, description, acceptance_criteria, priority, status,
                            test_project_id, responsible_user_id, estimated_hours, actual_hours,
                            created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
                    
                    created_at = tc.get('created_at', datetime.now().isoformat())
                    
                    test_case_id = db_manager.execute_insert(query, (
                        tc['tc_id'],
                        tc['title'],
                        tc.get('description'),
                        tc.get('acceptance_criteria'),
                        tc.get('priority', 'medium'),
                        tc.get('status', 'draft'),
                        project_id,
                        tc.get('responsible_user_id'),
                        tc.get('estimated_hours', 0),
                        tc.get('actual_hours', 0),
                        created_at
                    ))
                    
                    # 遷移標籤關聯
                    if tc.get('product_tags'):
                        self._migrate_test_case_tags(int(test_case_id), tc['product_tags'])
                    
                    migrated_count += 1
            
            return {'migrated': migrated_count, 'message': f'成功遷移 {migrated_count} 個測試案例'}
            
        except Exception as e:
            return {'migrated': 0, 'message': f'遷移測試案例時發生錯誤: {str(e)}'}
    
    def migrate_user_stories(self) -> Dict[str, Any]:
        """遷移用戶故事"""
        if not os.path.exists(self.user_stories_file):
            return {'migrated': 0, 'message': '用戶故事檔案不存在，跳過遷移'}
        
        try:
            with open(self.user_stories_file, 'r', encoding='utf-8') as f:
                user_stories = json.load(f)
            
            migrated_count = 0
            
            for story in user_stories:
                query = """
                    INSERT INTO user_stories (title, description, project_name, status, priority, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """
                
                created_at = story.get('created_at', datetime.now().isoformat())
                
                db_manager.execute_insert(query, (
                    story['title'],
                    story.get('description'),
                    story.get('project_name'),
                    story.get('status', 'pending'),
                    story.get('priority', 'medium'),
                    created_at
                ))
                migrated_count += 1
            
            return {'migrated': migrated_count, 'message': f'成功遷移 {migrated_count} 個用戶故事'}
            
        except Exception as e:
            return {'migrated': 0, 'message': f'遷移用戶故事時發生錯誤: {str(e)}'}
    
    def _migrate_stress_test_results(self, api_id: str, results: List[Dict]) -> int:
        """遷移壓力測試結果"""
        migrated_count = 0
        
        for result in results:
            try:
                stats = result.get('statistics', {})
                
                query = """
                    INSERT INTO stress_test_results (
                        api_id, test_name, start_time, end_time,
                        total_requests, successful_requests, failed_requests,
                        success_rate, avg_response_time, min_response_time,
                        max_response_time, requests_per_second,
                        test_config, raw_results
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                
                db_manager.execute_insert(query, (
                    api_id,
                    result.get('test_name', f"Test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
                    result.get('start_time'),
                    result.get('end_time'),
                    stats.get('total_requests', 0),
                    stats.get('successful_requests', 0),
                    stats.get('failed_requests', 0),
                    stats.get('success_rate', 0.0),
                    stats.get('avg_response_time', 0.0),
                    stats.get('min_response_time', 0.0),
                    stats.get('max_response_time', 0.0),
                    stats.get('requests_per_second', 0.0),
                    json.dumps(result.get('config', {})),
                    json.dumps(result)
                ))
                migrated_count += 1
                
            except Exception as e:
                print(f"遷移壓力測試結果時發生錯誤: {e}")
        
        return migrated_count
    
    def _migrate_test_case_tags(self, test_case_id: int, tag_names: List[str]):
        """遷移測試案例標籤關聯"""
        for tag_name in tag_names:
            # 查找標籤 ID
            tag_query = "SELECT id FROM product_tags WHERE name = ?"
            tag_result = db_manager.execute_query(tag_query, (tag_name,))
            
            if tag_result:
                tag_id = tag_result[0]['id']
                
                # 檢查關聯是否已存在
                existing_query = "SELECT 1 FROM test_case_tags WHERE test_case_id = ? AND product_tag_id = ?"
                existing = db_manager.execute_query(existing_query, (test_case_id, tag_id))
                
                if not existing:
                    insert_query = "INSERT INTO test_case_tags (test_case_id, product_tag_id) VALUES (?, ?)"
                    db_manager.execute_insert(insert_query, (test_case_id, tag_id))
    
    def _backup_json_files(self):
        """備份原始 JSON 檔案"""
        backup_dir = os.path.join(self.data_dir, 'backup', datetime.now().strftime('%Y%m%d_%H%M%S'))
        os.makedirs(backup_dir, exist_ok=True)
        
        json_files = [
            self.apis_file, self.users_file, self.test_cases_file,
            self.test_projects_file, self.product_tags_file, self.user_stories_file
        ]
        
        import shutil
        for file_path in json_files:
            if os.path.exists(file_path):
                filename = os.path.basename(file_path)
                backup_path = os.path.join(backup_dir, filename)
                shutil.copy2(file_path, backup_path)
        
        print(f"JSON 檔案已備份到: {backup_dir}")
    
    def check_migration_status(self) -> Dict[str, Any]:
        """檢查遷移狀態"""
        status = {
            'database_exists': db_manager.table_exists('users'),
            'tables': {},
            'data_counts': {}
        }
        
        tables = ['users', 'apis', 'product_tags', 'test_projects', 'test_cases', 'stress_test_results']
        
        for table in tables:
            status['tables'][table] = db_manager.table_exists(table)
            
            if status['tables'][table]:
                count_query = f"SELECT COUNT(*) as count FROM {table}"
                result = db_manager.execute_query(count_query)
                status['data_counts'][table] = result[0]['count'] if result else 0
        
        return status