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
    
    def add_api(self, name: str, url: str, api_type: str = "REST", method: str = "GET", request_body: str = None) -> Dict:
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
            "last_error": None
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