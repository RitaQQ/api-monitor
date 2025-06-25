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
            
            # 處理請求體和動態變數
            data = api.get('body', api.get('request_body', ''))
            if data and '{{timestamp}}' in data:
                current_timestamp = str(int(time.time()))
                data = data.replace('{{timestamp}}', current_timestamp)
            
            # 使用統一的 requests.request 方法
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                data=data,
                timeout=api.get('timeout', self.timeout)
            )
            
            response_time = time.time() - start_time
            
            # 檢查狀態碼（保持原有逻輯）
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
    
    def check_api(self, api: dict) -> dict:
        """為測試提供的統一接口方法，返回字典格式結果"""
        import time
        
        # 直接做 HTTP 請求，而不通過 check_single_api
        try:
            start_time = time.time()
            method = api.get('method', 'GET').upper()
            url = api['url']
            headers = api.get('headers', {})
            timeout = api.get('timeout', self.timeout)
            
            # 處理請求體和動態變數
            data = api.get('body', api.get('request_body', ''))
            if data and '{{timestamp}}' in data:
                current_timestamp = str(int(time.time()))
                data = data.replace('{{timestamp}}', current_timestamp)
            
            # 發送請求
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                data=data,
                timeout=timeout
            )
            
            response_time = time.time() - start_time
            
            # 處理特殊的狀態碼需求
            expected_status = api.get('expected_status', 200)
            if response.status_code == expected_status:
                status = 'healthy'
                error_message = ''
            else:
                status = 'unhealthy'
                error_message = f'HTTP {response.status_code}'
            
            result = {
                'status': status,
                'response_time': response_time,
                'timestamp': time.time(),
                'response_content': response.text[:1000],
                'status_code': response.status_code
            }
            
            if error_message:
                result['error_message'] = error_message
            
            # 檢查內容匹配
            expected_content = api.get('expected_content')
            if expected_content and response.text:
                result['content_match'] = expected_content in response.text
                if not result['content_match'] and status == 'healthy':
                    result['status'] = 'unhealthy'
                    result['error_message'] = f'Expected content "{expected_content}" not found in response'
            
            return result
            
        except requests.exceptions.Timeout:
            return {
                'status': 'unhealthy',
                'response_time': timeout,
                'timestamp': time.time(),
                'response_content': '',
                'status_code': 0,
                'error_message': 'Request timeout'
            }
        except requests.exceptions.ConnectionError:
            return {
                'status': 'unhealthy',
                'response_time': 0.0,
                'timestamp': time.time(),
                'response_content': '',
                'status_code': 0,
                'error_message': 'Connection failed'
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'response_time': 0.0,
                'timestamp': time.time(),
                'response_content': '',
                'status_code': 0,
                'error_message': str(e)
            }