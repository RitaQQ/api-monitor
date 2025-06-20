from typing import Tuple
from data_manager import DataManager
from config import Config
from services.api_request_handler import APIRequestHandler
from services.notification_service import NotificationService

class APIChecker:
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
        self.config = Config()
        self.request_handler = APIRequestHandler()
        self.notification_service = NotificationService()
    
    def check_single_api(self, api: dict) -> Tuple[str, float, str, str]:
        """
        檢查單一 API 的健康狀態
        返回: (status, response_time, error_message, response_data)
        """
        return self.request_handler.make_request(api)
    
    def check_all_apis(self):
        """檢查所有 API 的健康狀態"""
        apis = self.data_manager.load_apis()
        
        for api in apis:
            print(f"檢查 API: {api['name']} ({api['url']})")
            
            status, response_time, error_msg, response_data = self.check_single_api(api)
            
            # 更新 API 狀態
            self.data_manager.update_api_status(
                api['id'], 
                status, 
                response_time, 
                error_msg,
                response_data
            )
            
            # 檢查是否需要發送通知
            if status == "unhealthy":
                updated_api = self.data_manager.get_api_by_id(api['id'])
                if updated_api and updated_api['error_count'] >= self.config.MAX_ERROR_COUNT:
                    self.send_notification(updated_api)
            
            print(f"  狀態: {status}, 回應時間: {response_time:.3f}s")
            if error_msg:
                print(f"  錯誤: {error_msg}")
    
    def send_notification(self, api: dict):
        """發送通知"""
        self.notification_service.send_error_notification(api)