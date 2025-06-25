import time
import requests
from typing import Tuple, Dict, Optional
from data_manager import DataManager
from config import Config
import config as config_module

class APIChecker:
    def __init__(self, data_manager=None):
        self.data_manager = data_manager
        self.timeout = getattr(config_module, 'REQUEST_TIMEOUT', 10)
        self.max_error_count = getattr(config_module, 'MAX_ERROR_COUNT', 3)
    
    def check_single_api(self, api: dict) -> Tuple[str, float, str, str]:
        """
        檢查單一 API 的健康狀態
        返回: (status, response_time, error_message, response_data)
        """
        return self.make_request(api)
    
    def make_request(self, api: dict) -> Tuple[str, float, str, str]:
        """
        發送 HTTP 請求並返回結果
        返回: (status, response_time, error_message, response_data)
        """
        try:
            start_time = time.time()
            method = api.get('method', 'GET').upper()
            url = api['url']
            headers = api.get('headers', {})
            
            # 發送請求
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=self.timeout)
            elif method == 'POST':
                data = api.get('request_body', '')
                response = requests.post(url, data=data, headers=headers, timeout=self.timeout)
            elif method == 'PUT':
                data = api.get('request_body', '')
                response = requests.put(url, data=data, headers=headers, timeout=self.timeout)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=self.timeout)
            else:
                return 'unhealthy', 0.0, f'不支援的方法: {method}', ''
            
            response_time = time.time() - start_time
            
            # 檢查狀態碼
            if 200 <= response.status_code < 300:
                status = 'healthy'
                error_message = ''
            else:
                status = 'unhealthy'
                error_message = f'HTTP {response.status_code}'
            
            return status, response_time, error_message, response.text[:1000]
            
        except requests.exceptions.Timeout:
            return 'unhealthy', self.timeout, '請求超時', ''
        except requests.exceptions.ConnectionError:
            return 'unhealthy', 0.0, '連接錯誤', ''
        except Exception as e:
            return 'unhealthy', 0.0, str(e), ''
    
    def validate_api_config(self, api_config: dict) -> bool:
        """
        驗證 API 配置
        """
        required_fields = ['url']
        for field in required_fields:
            if field not in api_config or not api_config[field]:
                return False
        
        # 驗證 URL 格式
        url = api_config['url']
        if not url.startswith(('http://', 'https://')):
            return False
        
        # 驗證方法
        method = api_config.get('method', 'GET').upper()
        valid_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']
        if method not in valid_methods:
            return False
        
        return True
    
    def get_timeout(self) -> float:
        """獲取超時設定"""
        return self.timeout
    
    def set_timeout(self, timeout: float):
        """設定超時時間"""
        if timeout > 0:
            self.timeout = timeout
    
    def check_all_apis(self):
        """檢查所有 API 的健康狀態"""
        if not self.data_manager:
            return
            
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
                if updated_api and updated_api['error_count'] >= self.max_error_count:
                    self.send_notification(updated_api)
            
            print(f"  狀態: {status}, 回應時間: {response_time:.3f}s")
            if error_msg:
                print(f"  錯誤: {error_msg}")
    
    def send_notification(self, api: dict):
        """發送通知"""
        print(f"⚠️ 發送通知: API {api['name']} 連續失敗 {api.get('error_count', 0)} 次")