from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from data_manager import DataManager
from scheduler import APIScheduler
from config import Config
import os

app = Flask(__name__)
config = Config()
app.config.from_object(config)

# 初始化組件
data_manager = DataManager(config.DATA_FILE)
scheduler = APIScheduler()

@app.route('/')
def index():
    """主監控頁面"""
    apis = data_manager.load_apis()
    
    # 計算統計資料
    stats = {
        'total': len(apis),
        'healthy': len([api for api in apis if api.get('status') == 'healthy']),
        'unhealthy': len([api for api in apis if api.get('status') == 'unhealthy']),
        'unknown': len([api for api in apis if api.get('status') == 'unknown'])
    }
    
    return render_template('index.html', apis=apis, stats=stats)

@app.route('/admin')
def admin():
    """管理後台頁面"""
    apis = data_manager.load_apis()
    return render_template('admin.html', apis=apis)

@app.route('/admin/add', methods=['POST'])
def add_api():
    """新增 API"""
    name = request.form.get('name', '').strip()
    url = request.form.get('url', '').strip()
    api_type = request.form.get('type', 'REST').strip()
    
    if not name or not url:
        flash('請填寫完整的 API 名稱和 URL', 'error')
        return redirect(url_for('admin'))
    
    # 檢查 URL 是否已存在
    existing_apis = data_manager.load_apis()
    if any(api.get('url') == url for api in existing_apis):
        flash('這個 URL 已經存在於監控清單中', 'error')
        return redirect(url_for('admin'))
    
    try:
        new_api = data_manager.add_api(name, url, api_type)
        flash(f'成功新增 API: {name}', 'success')
        
        # 立即檢查新增的 API
        scheduler.check_now()
        
    except Exception as e:
        flash(f'新增 API 時發生錯誤: {str(e)}', 'error')
    
    return redirect(url_for('admin'))

@app.route('/admin/delete/<api_id>', methods=['POST'])
def delete_api(api_id):
    """刪除 API"""
    try:
        if data_manager.delete_api(api_id):
            flash('API 已成功刪除', 'success')
        else:
            flash('找不到要刪除的 API', 'error')
    except Exception as e:
        flash(f'刪除 API 時發生錯誤: {str(e)}', 'error')
    
    return redirect(url_for('admin'))

@app.route('/check-now')
def check_now():
    """立即執行檢查"""
    try:
        scheduler.check_now()
        flash('已執行立即檢查，結果將在下次頁面更新時顯示', 'success')
    except Exception as e:
        flash(f'執行檢查時發生錯誤: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/api/status')
def api_status():
    """提供 JSON 格式的 API 狀態資料"""
    apis = data_manager.load_apis()
    stats = {
        'total': len(apis),
        'healthy': len([api for api in apis if api.get('status') == 'healthy']),
        'unhealthy': len([api for api in apis if api.get('status') == 'unhealthy']),
        'unknown': len([api for api in apis if api.get('status') == 'unknown'])
    }
    
    return jsonify({
        'apis': apis,
        'stats': stats,
        'scheduler': scheduler.get_scheduler_status()
    })

@app.route('/health')
def health_check():
    """應用程式本身的健康檢查端點"""
    return jsonify({
        'status': 'healthy',
        'message': 'API Monitor is running',
        'scheduler_running': scheduler.scheduler.running
    })

if __name__ == '__main__':
    # 啟動排程器
    scheduler.start()
    
    # 初始化時執行一次檢查
    print("正在執行初始 API 檢查...")
    scheduler.check_now()
    
    print("API 監控系統已啟動!")
    print("訪問 http://127.0.0.1:3000 查看監控頁面")
    print("訪問 http://127.0.0.1:3000/admin 管理 API")
    
    # 啟動 Flask 應用程式
    app.run(debug=True, host='127.0.0.1', port=3000)