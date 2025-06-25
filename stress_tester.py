import asyncio
import time
import threading
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import json as json_module
import statistics

try:
    import aiohttp
except ImportError:
    aiohttp = None

class StressTester:
    """API 壓力測試器"""
    
    def __init__(self, data_manager=None):
        self.data_manager = data_manager
        self.active_tests = {}  # 記錄正在執行的測試
    
    async def run_stress_test(self, api_id: str) -> Dict:
        """執行壓力測試"""
        if aiohttp is None:
            raise ImportError("aiohttp is required for stress testing")
            
        api = self.data_manager.get_api_by_id(api_id)
        if not api or not api.get('stress_test'):
            raise ValueError("API 或壓力測試配置不存在")
        
        config = api['stress_test']
        concurrent_requests = config.get('concurrent_requests', 1)
        duration_seconds = config.get('duration_seconds', 10)
        interval_seconds = config.get('interval_seconds', 1.0)
        
        print(f"🔥 開始壓力測試: {api['name']}")
        print(f"   併發請求: {concurrent_requests}, 持續: {duration_seconds}秒, 間隔: {interval_seconds}秒")
        
        # 標記測試開始
        self.active_tests[api_id] = {
            'start_time': datetime.now(),
            'status': 'running'
        }
        
        results = {
            'api_id': api_id,
            'api_name': api['name'],
            'api_url': api['url'],
            'start_time': datetime.now().isoformat(),
            'config': {
                'concurrent_requests': concurrent_requests,
                'duration_seconds': duration_seconds,
                'interval_seconds': interval_seconds
            },
            'requests': [],
            'statistics': {}
        }
        
        try:
            # 執行壓力測試
            start_time = time.time()
            end_time = start_time + duration_seconds
            
            connector = aiohttp.TCPConnector(limit=concurrent_requests * 2)
            async with aiohttp.ClientSession(
                connector=connector,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as session:
                
                while time.time() < end_time:
                    # 創建並發請求任務
                    tasks = []
                    for i in range(concurrent_requests):
                        task = asyncio.create_task(
                            self._make_request(session, api, results)
                        )
                        tasks.append(task)
                    
                    # 等待所有請求完成
                    await asyncio.gather(*tasks, return_exceptions=True)
                    
                    # 檢查是否還有時間進行下一輪
                    if time.time() + interval_seconds < end_time:
                        await asyncio.sleep(interval_seconds)
                    else:
                        break
            
            # 計算統計資料
            results['end_time'] = datetime.now().isoformat()
            results['total_duration'] = time.time() - start_time
            self._calculate_statistics(results)
            
            # 儲存測試結果
            self.data_manager.save_stress_test_result(api_id, results)
            
            print(f"✅ 壓力測試完成: {api['name']}")
            print(f"   總請求數: {len(results['requests'])}")
            print(f"   成功率: {results['statistics']['success_rate']:.1f}%")
            print(f"   平均回應時間: {results['statistics']['avg_response_time']:.3f}s")
            
        except Exception as e:
            results['error'] = str(e)
            results['end_time'] = datetime.now().isoformat()
            print(f"❌ 壓力測試失敗: {api['name']} - {str(e)}")
        
        finally:
            # 移除活動測試記錄
            if api_id in self.active_tests:
                del self.active_tests[api_id]
        
        return results
    
    async def _make_request(self, session, api: Dict, results: Dict):
        """發送單個請求"""
        request_start = time.time()
        request_data = {
            'timestamp': datetime.now().isoformat(),
            'start_time': request_start
        }
        
        try:
            # 準備請求參數
            method = api.get('method', 'GET').upper()
            url = api['url']
            headers = {'User-Agent': 'API-Monitor-StressTester/1.0'}
            
            # 處理請求體
            json_data = None
            if method in ['POST', 'PUT', 'PATCH'] and api.get('request_body'):
                try:
                    json_data = json_module.loads(api['request_body'])
                    
                    # 處理動態時間戳
                    def replace_timestamp(obj):
                        if isinstance(obj, dict):
                            for key, value in obj.items():
                                if key == 'ts' and (value == '{{timestamp}}' or value == 1569221884613):
                                    obj[key] = int(time.time() * 1000)
                                elif isinstance(value, (dict, list)):
                                    replace_timestamp(value)
                        elif isinstance(obj, list):
                            for item in obj:
                                replace_timestamp(item)
                    
                    replace_timestamp(json_data)
                    headers['Content-Type'] = 'application/json'
                    
                except json_module.JSONDecodeError:
                    pass
            
            # 發送請求
            async with session.request(
                method=method,
                url=url,
                headers=headers,
                json=json_data
            ) as response:
                response_time = time.time() - request_start
                response_text = await response.text()
                
                request_data.update({
                    'response_time': response_time,
                    'status_code': response.status,
                    'success': 200 <= response.status < 300,
                    'response_size': len(response_text.encode('utf-8')),
                    'end_time': time.time()
                })
                
                if not request_data['success']:
                    request_data['error'] = f"HTTP {response.status}"
                
        except asyncio.TimeoutError:
            request_data.update({
                'response_time': time.time() - request_start,
                'success': False,
                'error': 'Timeout',
                'end_time': time.time()
            })
        except Exception as e:
            request_data.update({
                'response_time': time.time() - request_start,
                'success': False,
                'error': str(e),
                'end_time': time.time()
            })
        
        # 線程安全地添加結果
        results['requests'].append(request_data)
    
    def _calculate_statistics(self, results: Dict):
        """計算統計資料"""
        requests = results['requests']
        if not requests:
            results['statistics'] = {
                'total_requests': 0,
                'successful_requests': 0,
                'failed_requests': 0,
                'success_rate': 0.0,
                'avg_response_time': 0.0,
                'min_response_time': 0.0,
                'max_response_time': 0.0,
                'median_response_time': 0.0,
                'requests_per_second': 0.0
            }
            return
        
        successful_requests = [r for r in requests if r.get('success', False)]
        failed_requests = [r for r in requests if not r.get('success', False)]
        response_times = [r.get('response_time', 0) for r in requests]
        
        total_duration = results.get('total_duration', 1)
        
        stats = {
            'total_requests': len(requests),
            'successful_requests': len(successful_requests),
            'failed_requests': len(failed_requests),
            'success_rate': (len(successful_requests) / len(requests)) * 100,
            'avg_response_time': statistics.mean(response_times) if response_times else 0,
            'min_response_time': min(response_times) if response_times else 0,
            'max_response_time': max(response_times) if response_times else 0,
            'median_response_time': statistics.median(response_times) if response_times else 0,
            'requests_per_second': len(requests) / total_duration,
            'errors': {}
        }
        
        # 統計錯誤類型
        for request in failed_requests:
            error = request.get('error', 'Unknown Error')
            stats['errors'][error] = stats['errors'].get(error, 0) + 1
        
        results['statistics'] = stats
    
    def run_stress_test_sync(self, api_id: str) -> Dict:
        """同步版本的壓力測試（在新線程中運行）"""
        def run_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self.run_stress_test(api_id))
            finally:
                loop.close()
        
        # 在新線程中運行異步測試
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(run_async)
            return future.result()
    
    def is_test_running(self, api_id: str) -> bool:
        """檢查是否有正在執行的測試"""
        return api_id in self.active_tests
    
    def get_active_tests(self) -> Dict:
        """取得所有活動測試"""
        return self.active_tests.copy()
    
    def calculate_statistics(self, requests_data: List[Dict]) -> Dict:
        """計算統計資料"""
        if not requests_data:
            return {
                'total_requests': 0,
                'successful_requests': 0,
                'failed_requests': 0,
                'success_rate': 0.0,
                'avg_response_time': 0.0,
                'min_response_time': 0.0,
                'max_response_time': 0.0,
                'median_response_time': 0.0
            }
        
        # 根據 status_code 判斷成功失敗
        successful_requests = [r for r in requests_data if 200 <= r.get('status_code', 0) < 300]
        failed_requests = [r for r in requests_data if not (200 <= r.get('status_code', 0) < 300)]
        response_times = [r.get('response_time', 0) for r in requests_data]
        
        return {
            'total_requests': len(requests_data),
            'successful_requests': len(successful_requests),
            'failed_requests': len(failed_requests),
            'success_rate': (len(successful_requests) / len(requests_data)) * 100,
            'avg_response_time': statistics.mean(response_times) if response_times else 0,
            'min_response_time': min(response_times) if response_times else 0,
            'max_response_time': max(response_times) if response_times else 0,
            'median_response_time': statistics.median(response_times) if response_times else 0
        }
    
    def validate_test_config(self, test_config: Dict) -> bool:
        """驗證測試配置"""
        required_fields = ['concurrent_requests', 'duration_seconds']
        for field in required_fields:
            if field not in test_config:
                return False
            if not isinstance(test_config[field], (int, float)) or test_config[field] <= 0:
                return False
        
        # 驗證限制
        if test_config['concurrent_requests'] > 1000:  # 防止過度併發
            return False
        if test_config['duration_seconds'] > 3600:  # 限制最長測試時間
            return False
        
        return True
    
    def stop_test(self, api_id: str) -> bool:
        """停止測試"""
        if api_id in self.active_tests:
            self.active_tests[api_id]['status'] = 'stopped'
            return True
        return False
    
    def get_test_status(self, api_id: str) -> Optional[str]:
        """獲取測試狀態"""
        if api_id in self.active_tests:
            return self.active_tests[api_id]['status']
        return None
    
    def run_single_request(self, api: dict) -> dict:
        """為測試提供的同步單請求方法"""
        import requests
        import time
        
        start_time = time.time()
        try:
            method = api.get('method', 'GET').upper()
            url = api['url']
            headers = api.get('headers', {})
            timeout = api.get('timeout', 10)
            
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                data=api.get('body', ''),
                timeout=timeout
            )
            
            response_time = time.time() - start_time
            
            return {
                'status_code': response.status_code,
                'response_time': response_time,
                'timestamp': time.time(),
                'success': 200 <= response.status_code < 300
            }
            
        except Exception as e:
            return {
                'status_code': 0,
                'response_time': time.time() - start_time,
                'timestamp': time.time(),
                'success': False,
                'error': str(e)
            }
    
    def run_stress_test(self, api: dict, config: dict) -> dict:
        """為測試提供的同步壓力測試方法"""
        import threading
        import time
        import random
        
        concurrent_users = config.get('concurrent_users', 1)
        requests_per_user = config.get('requests_per_user', 1)
        ramp_up_time = config.get('ramp_up_time', 0)
        
        results = {
            'requests': [],
            'summary': {},
            'config': config
        }
        
        def worker():
            """工作線程函數"""
            for _ in range(requests_per_user):
                request_result = self.run_single_request(api)
                results['requests'].append(request_result)
        
        # 創建並啟動線程
        threads = []
        start_time = time.time()
        
        for i in range(concurrent_users):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()
            
            # 漸進啟動
            if ramp_up_time > 0 and i < concurrent_users - 1:
                time.sleep(ramp_up_time / concurrent_users)
        
        # 等待所有線程完成
        for thread in threads:
            thread.join()
        
        # 計算統計信息
        total_requests = len(results['requests'])
        successful_requests = sum(1 for r in results['requests'] if r.get('success', False))
        failed_requests = total_requests - successful_requests
        
        response_times = [r.get('response_time', 0) for r in results['requests']]
        
        results['summary'] = {
            'total_requests': total_requests,
            'successful_requests': successful_requests,
            'failed_requests': failed_requests,
            'average_response_time': sum(response_times) / len(response_times) if response_times else 0,
            'min_response_time': min(response_times) if response_times else 0,
            'max_response_time': max(response_times) if response_times else 0
        }
        
        return results
    
    def calculate_percentiles(self, response_times: list) -> dict:
        """計算百分位數"""
        if not response_times:
            return {'p50': 0, 'p90': 0, 'p95': 0, 'p99': 0}
        
        sorted_times = sorted(response_times)
        n = len(sorted_times)
        
        def percentile(p):
            index = int((p / 100) * (n - 1))
            return sorted_times[min(index, n - 1)]
        
        return {
            'p50': percentile(50),
            'p90': percentile(90),
            'p95': percentile(95),
            'p99': percentile(99)
        }