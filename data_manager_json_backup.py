import json
import os
import uuid
from datetime import datetime
from typing import List, Dict, Optional

class DataManager:
    def __init__(self, data_file: str):
        self.data_file = data_file
        self.ensure_data_file()
    
    def ensure_data_file(self):
        """確保資料檔案存在"""
        if not os.path.exists(self.data_file):
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            self.save_apis([])
    
    def load_apis(self) -> List[Dict]:
        """載入 API 清單"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def save_apis(self, apis: List[Dict]):
        """儲存 API 清單"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(apis, f, ensure_ascii=False, indent=2)
    
    def add_api(self, name: str, url: str, api_type: str = "REST", method: str = "GET", request_body: str = None, 
                concurrent_requests: int = 1, duration_seconds: int = 10, interval_seconds: float = 1.0) -> Dict:
        """新增 API"""
        apis = self.load_apis()
        new_api = {
            "id": str(uuid.uuid4()),
            "name": name,
            "url": url,
            "type": api_type,
            "method": method,
            "request_body": request_body,
            "status": "unknown",
            "response_time": 0,
            "last_check": None,
            "error_count": 0,
            "last_error": None,
            "stress_test": {
                "concurrent_requests": concurrent_requests,
                "duration_seconds": duration_seconds,
                "interval_seconds": interval_seconds,
                "enabled": False,
                "last_test": None,
                "results": []
            }
        }
        apis.append(new_api)
        self.save_apis(apis)
        return new_api
    
    def delete_api(self, api_id: str) -> bool:
        """刪除 API"""
        apis = self.load_apis()
        original_count = len(apis)
        apis = [api for api in apis if api.get("id") != api_id]
        if len(apis) < original_count:
            self.save_apis(apis)
            return True
        return False
    
    def update_api_status(self, api_id: str, status: str, response_time: float = 0, error_msg: str = None, response_data: str = None):
        """更新 API 狀態"""
        apis = self.load_apis()
        for api in apis:
            if api.get("id") == api_id:
                api["status"] = status
                api["response_time"] = response_time
                api["last_check"] = datetime.now().isoformat()
                api["last_response"] = response_data
                
                if status == "unhealthy":
                    api["error_count"] += 1
                    api["last_error"] = error_msg
                else:
                    api["error_count"] = 0
                    api["last_error"] = None
                break
        
        self.save_apis(apis)
    
    def get_api_by_id(self, api_id: str) -> Optional[Dict]:
        """根據 ID 取得特定 API"""
        apis = self.load_apis()
        for api in apis:
            if api.get("id") == api_id:
                return api
        return None
    
    def update_stress_test_config(self, api_id: str, concurrent_requests: int, duration_seconds: int, interval_seconds: float, enabled: bool = False):
        """更新壓力測試配置"""
        apis = self.load_apis()
        for api in apis:
            if api.get("id") == api_id:
                if "stress_test" not in api:
                    api["stress_test"] = {"results": []}
                
                api["stress_test"].update({
                    "concurrent_requests": concurrent_requests,
                    "duration_seconds": duration_seconds,
                    "interval_seconds": interval_seconds,
                    "enabled": enabled
                })
                break
        self.save_apis(apis)
    
    def save_stress_test_result(self, api_id: str, result: Dict):
        """儲存壓力測試結果"""
        apis = self.load_apis()
        for api in apis:
            if api.get("id") == api_id:
                if "stress_test" not in api:
                    api["stress_test"] = {"results": []}
                elif "results" not in api["stress_test"]:
                    api["stress_test"]["results"] = []
                
                api["stress_test"]["results"].append(result)
                api["stress_test"]["last_test"] = datetime.now().isoformat()
                
                # 只保留最近 10 次測試結果
                if len(api["stress_test"]["results"]) > 10:
                    api["stress_test"]["results"] = api["stress_test"]["results"][-10:]
                break
        self.save_apis(apis)
    
    def update_api(self, api_id: str, name: str, url: str, api_type: str = "REST", method: str = "GET", 
                   request_body: str = None, concurrent_requests: int = 1, duration_seconds: int = 10, 
                   interval_seconds: float = 1.0) -> bool:
        """更新 API 資訊"""
        apis = self.load_apis()
        for api in apis:
            if api.get("id") == api_id:
                # 更新基本資訊
                api["name"] = name
                api["url"] = url
                api["type"] = api_type
                api["method"] = method
                api["request_body"] = request_body
                
                # 更新壓力測試配置
                if "stress_test" not in api:
                    api["stress_test"] = {"results": []}
                
                api["stress_test"].update({
                    "concurrent_requests": concurrent_requests,
                    "duration_seconds": duration_seconds,
                    "interval_seconds": interval_seconds
                })
                
                # 重置監控狀態 (因為 URL 或配置可能有變更)
                api["status"] = "unknown"
                api["response_time"] = 0
                api["last_check"] = None
                api["error_count"] = 0
                api["last_error"] = None
                
                self.save_apis(apis)
                return True
        return False