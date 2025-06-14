from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from api_checker import APIChecker
from data_manager import DataManager
from config import Config
import atexit

class APIScheduler:
    def __init__(self):
        self.config = Config()
        self.data_manager = DataManager(self.config.DATA_FILE)
        self.api_checker = APIChecker(self.data_manager)
        self.scheduler = BackgroundScheduler()
        self.setup_scheduler()
    
    def setup_scheduler(self):
        """設定排程器"""
        # 每 60 秒檢查一次所有 API
        self.scheduler.add_job(
            func=self.api_checker.check_all_apis,
            trigger=IntervalTrigger(seconds=self.config.CHECK_INTERVAL),
            id='api_health_check',
            name='API 健康檢查',
            replace_existing=True
        )
        
        # 註冊程式結束時停止排程器
        atexit.register(lambda: self.scheduler.shutdown())
    
    def start(self):
        """啟動排程器"""
        if not self.scheduler.running:
            self.scheduler.start()
            print(f"排程器已啟動，每 {self.config.CHECK_INTERVAL} 秒檢查一次 API")
    
    def stop(self):
        """停止排程器"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            print("排程器已停止")
    
    def check_now(self):
        """立即執行一次檢查"""
        self.api_checker.check_all_apis()
    
    def get_scheduler_status(self):
        """取得排程器狀態"""
        return {
            'running': self.scheduler.running,
            'jobs': [
                {
                    'id': job.id,
                    'name': job.name,
                    'next_run': job.next_run_time.isoformat() if job.next_run_time else None
                }
                for job in self.scheduler.get_jobs()
            ]
        }