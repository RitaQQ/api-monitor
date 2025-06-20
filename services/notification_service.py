import time
from typing import Dict

class NotificationService:
    """通知服務"""
    
    def send_error_notification(self, api: Dict) -> None:
        """
        發送錯誤通知
        
        Args:
            api: API 配置字典
        """
        error_msg = self._format_error_message(api)
        
        # 輸出到控制台
        print(error_msg)
        
        # 寫入 log 檔案
        self._write_to_log(error_msg)
        
        # 在這裡可以添加其他通知方式：
        # - 發送郵件
        # - 發送 Slack 訊息
        # - 發送 Discord 訊息
        # - 調用 Webhook
    
    def _format_error_message(self, api: Dict) -> str:
        """格式化錯誤訊息"""
        return f"""
        ⚠️  API 連續錯誤警告 ⚠️
        API 名稱: {api['name']}
        URL: {api['url']}
        連續錯誤次數: {api['error_count']}
        最後錯誤: {api['last_error']}
        最後檢查時間: {api['last_check']}
        """
    
    def _write_to_log(self, message: str) -> None:
        """寫入 log 檔案"""
        try:
            with open('api_monitor.log', 'a', encoding='utf-8') as f:
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"{timestamp} - {message}\n")
        except Exception as e:
            print(f"寫入 log 檔案時發生錯誤: {e}")
    
    def send_success_notification(self, api: Dict) -> None:
        """
        發送成功恢復通知（可選）
        
        Args:
            api: API 配置字典
        """
        success_msg = f"✅ API 已恢復正常: {api['name']} ({api['url']})"
        print(success_msg)
        self._write_to_log(success_msg)