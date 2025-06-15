import json
import os
from datetime import datetime
import uuid

class UserStoryManager:
    def __init__(self, data_file='data/user_stories.json'):
        self.data_file = data_file
        self.ensure_data_directory()
        self.init_data_file()
    
    def ensure_data_directory(self):
        """確保 data 目錄存在"""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
    
    def init_data_file(self):
        """初始化資料檔案，如果不存在則創建並添加範例 User Story"""
        if not os.path.exists(self.data_file):
            # 創建範例 User Story
            sample_stories = [
                {
                    "id": str(uuid.uuid4()),
                    "project_name": "機車租借系統",
                    "title": "搜尋地圖上的可用機車",
                    "user_role": "使用者",
                    "feature_description": "我希望在搜尋機車時，能夠在地圖上看到可用車輛",
                    "acceptance_criteria": [
                        "能夠在地圖上顯示可用機車位置",
                        "機車圖示顯示電量狀態",
                        "點擊機車可查看詳細資訊",
                        "支援依距離篩選機車"
                    ],
                    "test_result": "Pass",
                    "test_notes": "所有功能正常運作，地圖載入速度良好",
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    "created_by": "系統初始化"
                },
                {
                    "id": str(uuid.uuid4()),
                    "project_name": "機車租借系統",
                    "title": "機車預約功能",
                    "user_role": "使用者",
                    "feature_description": "我希望能夠預約指定時間的機車",
                    "acceptance_criteria": [
                        "可選擇預約時間（最多提前24小時）",
                        "顯示機車預約狀態",
                        "可取消預約",
                        "預約到期自動釋放"
                    ],
                    "test_result": "Pending",
                    "test_notes": "待開發完成後進行測試",
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    "created_by": "系統初始化"
                },
                {
                    "id": str(uuid.uuid4()),
                    "project_name": "API 監控系統",
                    "title": "API 異常通知管理",
                    "user_role": "管理者",
                    "feature_description": "我希望能夠收到 API 異常通知",
                    "acceptance_criteria": [
                        "API 回應時間超過 5 秒時發送通知",
                        "API 回傳錯誤狀態碼時發送通知",
                        "通知包含錯誤詳細資訊",
                        "支援多種通知方式（Email、簡訊、Slack）"
                    ],
                    "test_result": "Fail",
                    "test_notes": "Email 通知功能尚未實作完成",
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    "created_by": "系統初始化"
                },
                {
                    "id": str(uuid.uuid4()),
                    "project_name": "API 監控系統",
                    "title": "壓力測試報告生成",
                    "user_role": "測試人員",
                    "feature_description": "我希望能夠產生詳細的壓力測試報告",
                    "acceptance_criteria": [
                        "包含測試時間、請求數量統計",
                        "顯示成功率和回應時間分析",
                        "可匯出為 PDF 或 Excel 格式",
                        "支援歷史報告比較"
                    ],
                    "test_result": "Pass",
                    "test_notes": "報告功能完整，匯出格式正確",
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    "created_by": "系統初始化"
                }
            ]
            
            data = {
                "user_stories": sample_stories,
                "created_at": datetime.now().isoformat(),
                "version": "1.0"
            }
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"🔧 創建 User Story 資料檔案: {self.data_file}")
    
    def load_user_stories(self):
        """載入所有 User Story"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('user_stories', [])
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            print(f"錯誤：無法解析 User Story 檔案 {self.data_file}")
            return []
    
    def save_user_stories(self, user_stories):
        """保存 User Story 列表"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {"created_at": datetime.now().isoformat(), "version": "1.0"}
        
        data['user_stories'] = user_stories
        data['updated_at'] = datetime.now().isoformat()
        
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def get_user_story_by_id(self, story_id):
        """根據 ID 獲取 User Story"""
        user_stories = self.load_user_stories()
        for story in user_stories:
            if story.get('id') == story_id:
                return story
        return None
    
    def create_user_story(self, project_names, title, user_role, feature_description, purpose,
                         acceptance_criteria, test_result="Pending", test_notes="", created_by="Unknown"):
        """創建新的 User Story"""
        user_stories = self.load_user_stories()
        
        # 處理專案名稱，支援字串或列表
        if isinstance(project_names, str):
            project_names = [project_names.strip()]
        else:
            project_names = [name.strip() for name in project_names if name.strip()]
        
        new_story = {
            "id": str(uuid.uuid4()),
            "project_names": project_names,
            "title": title.strip(),
            "user_role": user_role.strip(),
            "feature_description": feature_description.strip(),
            "purpose": purpose.strip(),
            "acceptance_criteria": [criterion.strip() for criterion in acceptance_criteria if criterion.strip()],
            "test_result": test_result,
            "test_notes": test_notes.strip(),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "created_by": created_by
        }
        
        user_stories.append(new_story)
        self.save_user_stories(user_stories)
        
        return new_story
    
    def update_user_story(self, story_id, **kwargs):
        """更新 User Story"""
        user_stories = self.load_user_stories()
        
        for i, story in enumerate(user_stories):
            if story.get('id') == story_id:
                # 允許更新的欄位
                allowed_fields = ['project_names', 'title', 'user_role', 'feature_description', 'purpose',
                                'acceptance_criteria', 'test_result', 'test_notes']
                
                for field in allowed_fields:
                    if field in kwargs:
                        if field == 'acceptance_criteria':
                            # 處理驗收條件列表
                            story[field] = [criterion.strip() for criterion in kwargs[field] if criterion.strip()]
                        elif field == 'project_names':
                            # 處理專案名稱列表
                            if isinstance(kwargs[field], str):
                                story[field] = [kwargs[field].strip()]
                            else:
                                story[field] = [name.strip() for name in kwargs[field] if name.strip()]
                        else:
                            story[field] = kwargs[field].strip() if isinstance(kwargs[field], str) else kwargs[field]
                
                story['updated_at'] = datetime.now().isoformat()
                user_stories[i] = story
                self.save_user_stories(user_stories)
                return True
        
        return False
    
    def delete_user_story(self, story_id):
        """刪除 User Story"""
        user_stories = self.load_user_stories()
        original_count = len(user_stories)
        
        user_stories = [story for story in user_stories if story.get('id') != story_id]
        
        if len(user_stories) < original_count:
            self.save_user_stories(user_stories)
            return True
        
        return False
    
    def get_statistics(self):
        """獲取統計資訊"""
        user_stories = self.load_user_stories()
        return {
            'total': len(user_stories),
            'pass': len([s for s in user_stories if s.get('test_result') == 'Pass']),
            'fail': len([s for s in user_stories if s.get('test_result') == 'Fail']),
            'pending': len([s for s in user_stories if s.get('test_result') == 'Pending'])
        }
    
    def get_user_stories_by_result(self, test_result):
        """根據測試結果篩選 User Story"""
        user_stories = self.load_user_stories()
        return [story for story in user_stories if story.get('test_result') == test_result]
    
    def get_all_projects(self):
        """獲取所有測試專案名稱"""
        user_stories = self.load_user_stories()
        projects = set()
        for story in user_stories:
            # 支援舊格式（project_name）和新格式（project_names）
            if 'project_names' in story:
                projects.update(story['project_names'])
            elif 'project_name' in story:
                projects.add(story['project_name'])
            else:
                projects.add('未分類專案')
        return sorted(list(projects))
    
    def get_user_stories_by_project(self, project_name):
        """根據專案名稱獲取 User Story"""
        user_stories = self.load_user_stories()
        result = []
        for story in user_stories:
            # 支援舊格式（project_name）和新格式（project_names）
            if 'project_names' in story:
                if project_name in story['project_names']:
                    result.append(story)
            elif story.get('project_name') == project_name:
                result.append(story)
        return result
    
    def get_project_statistics(self, project_name):
        """獲取指定專案的統計資訊"""
        project_stories = self.get_user_stories_by_project(project_name)
        total = len(project_stories)
        
        if total == 0:
            return {
                'total': 0,
                'pass': 0,
                'fail': 0,
                'pending': 0,
                'pass_rate': 0.0,
                'tested': 0
            }
        
        pass_count = len([s for s in project_stories if s.get('test_result') == 'Pass'])
        fail_count = len([s for s in project_stories if s.get('test_result') == 'Fail'])
        pending_count = len([s for s in project_stories if s.get('test_result') == 'Pending'])
        
        # 計算通過率（僅考慮已測試的案例）
        tested_count = pass_count + fail_count
        pass_rate = (pass_count / tested_count * 100) if tested_count > 0 else 0.0
        
        return {
            'total': total,
            'pass': pass_count,
            'fail': fail_count,
            'pending': pending_count,
            'pass_rate': round(pass_rate, 1),
            'tested': tested_count
        }
    
    def get_projects_overview(self):
        """獲取所有專案的總覽統計"""
        projects = self.get_all_projects()
        overview = []
        
        for project in projects:
            stats = self.get_project_statistics(project)
            overview.append({
                'project_name': project,
                'stats': stats
            })
        
        return overview
    
    def generate_project_report(self, project_name):
        """產生指定專案的測試報告"""
        project_stories = self.get_user_stories_by_project(project_name)
        stats = self.get_project_statistics(project_name)
        
        report = {
            'project_name': project_name,
            'generated_at': datetime.now().isoformat(),
            'statistics': stats,
            'user_stories': project_stories
        }
        
        return report
    
    def delete_project(self, project_name):
        """刪除專案並從所有測試案例中移除該專案的關聯"""
        if not project_name.strip():
            return False
        
        project_name = project_name.strip()
        user_stories = self.load_user_stories()
        modified = False
        
        # 從所有測試案例中移除該專案
        for i, story in enumerate(user_stories):
            # 處理新格式（project_names）
            if 'project_names' in story and project_name in story['project_names']:
                story['project_names'].remove(project_name)
                story['updated_at'] = datetime.now().isoformat()
                user_stories[i] = story
                modified = True
            
            # 處理舊格式（project_name）- 轉換為新格式
            elif 'project_name' in story and story['project_name'] == project_name:
                # 將舊格式轉換為新格式，並移除該專案
                story['project_names'] = []  # 移除該專案後變成空陣列
                del story['project_name']  # 刪除舊欄位
                story['updated_at'] = datetime.now().isoformat()
                user_stories[i] = story
                modified = True
        
        # 移除沒有任何專案關聯的測試案例（可選）
        # user_stories = [story for story in user_stories 
        #                if not (('project_names' in story and not story['project_names']) or 
        #                       ('project_names' not in story and 'project_name' not in story))]
        
        if modified:
            self.save_user_stories(user_stories)
            return True
        
        return False
    
    def get_project_test_cases_count(self, project_name):
        """獲取指定專案的測試案例數量"""
        return len(self.get_user_stories_by_project(project_name))