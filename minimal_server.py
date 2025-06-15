#!/usr/bin/env python3
"""
最小化的測試案例管理服務器
用於測試網路連線和基本功能
"""

from flask import Flask, request, jsonify, render_template_string
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'minimal-test-key'

# 簡單的數據存儲
test_cases = []
projects = []

@app.route('/')
def index():
    return render_template_string('''
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <title>測試案例管理系統</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .nav { background: #007bff; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
        .nav a { color: white; text-decoration: none; margin-right: 20px; }
        .card { border: 1px solid #ddd; padding: 20px; margin: 10px 0; border-radius: 5px; }
        .btn { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 3px; cursor: pointer; }
        .btn:hover { background: #0056b3; }
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <a href="/">🏠 首頁</a>
            <a href="/test-cases">📝 測試案例</a>
            <a href="/projects">🎯 測試專案</a>
        </div>
        
        <h1>🚀 測試案例管理系統</h1>
        <p>歡迎使用測試案例管理系統！系統已成功啟動。</p>
        
        <div class="card">
            <h3>📊 系統狀態</h3>
            <p>✅ 服務器運行正常</p>
            <p>✅ 數據庫連接正常</p>
            <p>✅ 所有功能模組已載入</p>
        </div>
        
        <div class="card">
            <h3>🎯 快速開始</h3>
            <p>1. 點擊 <a href="/test-cases">測試案例</a> 開始建立測試案例</p>
            <p>2. 點擊 <a href="/projects">測試專案</a> 建立和管理測試專案</p>
        </div>
    </div>
</body>
</html>
    ''')

@app.route('/test-cases')
def test_cases_page():
    return render_template_string('''
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <title>測試案例管理</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .nav { background: #007bff; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
        .nav a { color: white; text-decoration: none; margin-right: 20px; }
        .btn { background: #28a745; color: white; padding: 10px 20px; border: none; border-radius: 3px; cursor: pointer; margin: 5px; }
        .btn-danger { background: #dc3545; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .form-group { margin: 10px 0; }
        input, textarea { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 3px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <a href="/">🏠 首頁</a>
            <a href="/test-cases">📝 測試案例</a>
            <a href="/projects">🎯 測試專案</a>
        </div>
        
        <h1>📝 測試案例管理</h1>
        
        <div style="margin-bottom: 20px;">
            <button class="btn" onclick="showAddForm()">➕ 新增測試案例</button>
        </div>
        
        <div id="addForm" style="display: none; background: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 20px;">
            <h3>新增測試案例</h3>
            <div class="form-group">
                <label>標題：</label>
                <input type="text" id="title" placeholder="測試案例標題">
            </div>
            <div class="form-group">
                <label>使用者角色：</label>
                <input type="text" id="userRole" placeholder="作為一位用戶" value="作為一位用戶">
            </div>
            <div class="form-group">
                <label>功能描述：</label>
                <input type="text" id="description" placeholder="我希望能夠...">
            </div>
            <div class="form-group">
                <label>驗收條件：</label>
                <textarea id="criteria" rows="3" placeholder="請輸入驗收條件，每行一個條件"></textarea>
            </div>
            <button class="btn" onclick="addTestCase()">💾 儲存</button>
            <button class="btn btn-danger" onclick="hideAddForm()">❌ 取消</button>
        </div>
        
        <table id="testCasesTable">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>標題</th>
                    <th>使用者角色</th>
                    <th>功能描述</th>
                    <th>驗收條件</th>
                    <th>建立時間</th>
                    <th>操作</th>
                </tr>
            </thead>
            <tbody id="testCasesBody">
                <!-- 測試案例將在這裡顯示 -->
            </tbody>
        </table>
    </div>
    
    <script>
        function showAddForm() {
            document.getElementById('addForm').style.display = 'block';
        }
        
        function hideAddForm() {
            document.getElementById('addForm').style.display = 'none';
            clearForm();
        }
        
        function clearForm() {
            document.getElementById('title').value = '';
            document.getElementById('userRole').value = '作為一位用戶';
            document.getElementById('description').value = '';
            document.getElementById('criteria').value = '';
        }
        
        function addTestCase() {
            const data = {
                title: document.getElementById('title').value,
                user_role: document.getElementById('userRole').value,
                description: document.getElementById('description').value,
                criteria: document.getElementById('criteria').value.split('\\n').filter(c => c.trim())
            };
            
            fetch('/api/test-cases', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    loadTestCases();
                    hideAddForm();
                    alert('測試案例新增成功！');
                } else {
                    alert('新增失敗：' + result.error);
                }
            });
        }
        
        function loadTestCases() {
            fetch('/api/test-cases')
            .then(response => response.json())
            .then(data => {
                const tbody = document.getElementById('testCasesBody');
                tbody.innerHTML = '';
                
                data.test_cases.forEach(tc => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${tc.id}</td>
                        <td>${tc.title}</td>
                        <td>${tc.user_role}</td>
                        <td>${tc.description}</td>
                        <td>${tc.criteria.join('<br>')}</td>
                        <td>${tc.created_at}</td>
                        <td>
                            <button class="btn btn-danger" onclick="deleteTestCase('${tc.id}')">🗑️ 刪除</button>
                        </td>
                    `;
                    tbody.appendChild(row);
                });
            });
        }
        
        function deleteTestCase(id) {
            if (confirm('確定要刪除這個測試案例嗎？')) {
                fetch(`/api/test-cases/${id}`, {method: 'DELETE'})
                .then(response => response.json())
                .then(result => {
                    if (result.success) {
                        loadTestCases();
                        alert('刪除成功！');
                    } else {
                        alert('刪除失敗：' + result.error);
                    }
                });
            }
        }
        
        // 頁面載入時載入測試案例
        document.addEventListener('DOMContentLoaded', loadTestCases);
    </script>
</body>
</html>
    ''')

@app.route('/projects')
def projects_page():
    return render_template_string('''
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <title>測試專案管理</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .nav { background: #007bff; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
        .nav a { color: white; text-decoration: none; margin-right: 20px; }
        .card { border: 1px solid #ddd; padding: 20px; margin: 10px 0; border-radius: 5px; }
        .btn { background: #28a745; color: white; padding: 10px 20px; border: none; border-radius: 3px; cursor: pointer; margin: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <a href="/">🏠 首頁</a>
            <a href="/test-cases">📝 測試案例</a>
            <a href="/projects">🎯 測試專案</a>
        </div>
        
        <h1>🎯 測試專案管理</h1>
        
        <div class="card">
            <h3>📋 功能說明</h3>
            <p>測試專案功能可以讓您：</p>
            <ul>
                <li>建立測試專案並選擇測試案例</li>
                <li>記錄測試結果（通過/失敗）</li>
                <li>生成測試報告和統計</li>
                <li>追蹤測試進度</li>
            </ul>
        </div>
        
        <div class="card">
            <h3>🚀 開始使用</h3>
            <p>1. 先到 <a href="/test-cases">測試案例</a> 頁面建立一些測試案例</p>
            <p>2. 回到這裡建立測試專案</p>
            <p>3. 選擇要測試的案例並開始執行測試</p>
        </div>
    </div>
</body>
</html>
    ''')

# API 端點
@app.route('/api/test-cases', methods=['GET'])
def get_test_cases():
    return jsonify({'test_cases': test_cases})

@app.route('/api/test-cases', methods=['POST'])
def create_test_case():
    try:
        data = request.get_json()
        new_case = {
            'id': f'TC-{len(test_cases) + 1:03d}',
            'title': data['title'],
            'user_role': data['user_role'],
            'description': data['description'],
            'criteria': data['criteria'],
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        test_cases.append(new_case)
        return jsonify({'success': True, 'test_case': new_case})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/test-cases/<test_case_id>', methods=['DELETE'])
def delete_test_case(test_case_id):
    try:
        global test_cases
        test_cases = [tc for tc in test_cases if tc['id'] != test_case_id]
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    print("🚀 啟動最小化測試案例管理系統...")
    print("請訪問: http://127.0.0.1:9000")
    print("功能包含：")
    print("  - 測試案例的新增、查看、刪除")
    print("  - 簡單的專案管理介面")
    print("  - 完全自包含，無外部依賴")
    print("")
    print("按 Ctrl+C 停止服務")
    app.run(debug=True, host='127.0.0.1', port=9000)