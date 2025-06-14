import requests
import time
from typing import Tuple
from data_manager import DataManager
from config import Config

class APIChecker:
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
        self.config = Config()
    
    def check_single_api(self, api: dict) -> Tuple[str, float, str, str]:
        """
        檢查單一 API 的健康狀態
        返回: (status, response_time, error_message, response_data)
        """
        try:
            start_time = time.time()
            method = api.get('method', 'GET').upper()
            headers = {'User-Agent': 'API-Monitor/1.0'}
            
            # 根據不同的 HTTP 方法發送請求
            if method == 'GET':
                response = requests.get(
                    api['url'], 
                    timeout=self.config.REQUEST_TIMEOUT,
                    headers=headers
                )
            elif method == 'POST':
                headers['Content-Type'] = 'application/json'
                
                # 檢查是否有自訂的 request body
                if api.get('request_body'):
                    try:
                        # 嘗試解析 JSON 格式的 request body
                        import json as json_module
                        test_payload = json_module.loads(api['request_body'])
                        
                        # 如果包含時間戳變數，動態替換
                        if isinstance(test_payload, dict):
                            def update_timestamps(obj):
                                if isinstance(obj, dict):
                                    for key, value in obj.items():
                                        if key == 'ts' and (value == '{{timestamp}}' or value == 1569221884613):
                                            obj[key] = int(time.time() * 1000)
                                        elif isinstance(value, (dict, list)):
                                            update_timestamps(value)
                                elif isinstance(obj, list):
                                    for item in obj:
                                        update_timestamps(item)
                            update_timestamps(test_payload)
                    except json_module.JSONDecodeError:
                        # 如果不是有效的 JSON，使用原始字串
                        response = requests.post(
                            api['url'], 
                            data=api['request_body'],
                            timeout=self.config.REQUEST_TIMEOUT,
                            headers=headers
                        )
                        response_time = time.time() - start_time
                        response_data = response.text[:2000] if response.text else f"狀態碼: {response.status_code}"
                        if 200 <= response.status_code < 300:
                            return "healthy", response_time, None, response_data
                        else:
                            return "unhealthy", response_time, f"HTTP {response.status_code}", response_data
                elif 'ionex' in api['url'].lower() and 'boundingBox' in api['url']:
                    # IONEX boundingBox API 的預設 payload
                    test_payload = {
                        "topRight": {
                            "lat": 25.098480744152837,
                            "lon": 121.63874437309272
                        },
                        "bottomLeft": {
                            "lat": 25.015207286647275,
                            "lon": 121.58853342033387
                        },
                        "location": {
                            "lat": 25.015207286647275,
                            "lon": 121.58853342033387
                        },
                        "from": 0,
                        "size": 200,
                        "lang": "en",
                        "stationTypes": [
                            "ENERGY",
                            "RENTAL"
                        ],
                        "app": "com.noodoe.nex.user.dev",
                        "dn": "70C21539-18B2-4399-A1CC-C8718AE7966C",
                        "dm": "iPhone14,2",
                        "vn": "1.0.0",
                        "ts": int(time.time() * 1000),
                        "tz": 480,
                        "cn": "TW"
                    }
                else:
                    # 一般測試 payload
                    test_payload = {
                        "test": True,
                        "timestamp": time.time()
                    }
                
                response = requests.post(
                    api['url'], 
                    json=test_payload,
                    timeout=self.config.REQUEST_TIMEOUT,
                    headers=headers
                )
            elif method == 'PUT':
                response = requests.put(
                    api['url'], 
                    timeout=self.config.REQUEST_TIMEOUT,
                    headers=headers
                )
            elif method == 'DELETE':
                response = requests.delete(
                    api['url'], 
                    timeout=self.config.REQUEST_TIMEOUT,
                    headers=headers
                )
            else:
                return "unhealthy", 0, f"不支援的 HTTP 方法: {method}"
                
            response_time = time.time() - start_time
            
            # 捕獲回應內容
            try:
                # 限制回應內容長度以避免記憶體問題
                response_text = response.text[:2000] if response.text else ""
                # 嘗試格式化 JSON 回應
                if response.headers.get('content-type', '').startswith('application/json'):
                    import json as json_module
                    try:
                        response_data = json_module.dumps(json_module.loads(response_text), indent=2, ensure_ascii=False)
                    except:
                        response_data = response_text
                else:
                    response_data = response_text
            except:
                response_data = f"狀態碼: {response.status_code}"
            
            if 200 <= response.status_code < 300:
                return "healthy", response_time, None, response_data
            else:
                return "unhealthy", response_time, f"HTTP {response.status_code}", response_data
                
        except requests.exceptions.Timeout:
            return "unhealthy", self.config.REQUEST_TIMEOUT, "請求超時", None
        except requests.exceptions.ConnectionError:
            return "unhealthy", 0, "連線失敗", None
        except requests.exceptions.RequestException as e:
            return "unhealthy", 0, f"請求錯誤: {str(e)}", None
        except Exception as e:
            return "unhealthy", 0, f"未知錯誤: {str(e)}", None
    
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
        """發送通知（這裡用 log 模擬）"""
        error_msg = f"""
        ⚠️  API 連續錯誤警告 ⚠️
        API 名稱: {api['name']}
        URL: {api['url']}
        連續錯誤次數: {api['error_count']}
        最後錯誤: {api['last_error']}
        最後檢查時間: {api['last_check']}
        """
        
        print(error_msg)
        
        # 也可以寫入 log 檔案
        with open('api_monitor.log', 'a', encoding='utf-8') as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {error_msg}\n")