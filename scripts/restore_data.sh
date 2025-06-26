#!/bin/bash

# 🔄 API Monitor 資料恢復腳本
# 用途：從備份恢復生產環境資料

set -e  # 遇到錯誤立即退出

# ========== 配置 ==========
BACKUP_DIR="/var/backups/api-monitor"
DATA_PATH="/opt/api-monitor/data"
LOGS_PATH="/opt/api-monitor/logs"

# ========== 函數定義 ==========
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

show_usage() {
    echo "用法: $0 <備份名稱>"
    echo ""
    echo "範例: $0 api_monitor_backup_20250625_143022"
    echo ""
    echo "可用備份："
    ls -1 "$BACKUP_DIR"/api_monitor_backup_*_manifest.txt 2>/dev/null | sed 's/.*backup_/  /' | sed 's/_manifest.txt//' || echo "  無可用備份"
}

check_prerequisites() {
    log "檢查恢復前置條件..."
    
    # 檢查參數
    if [[ $# -ne 1 ]]; then
        show_usage
        exit 1
    fi
    
    BACKUP_NAME="$1"
    
    # 檢查是否為 root 或有 sudo 權限
    if [[ $EUID -ne 0 ]] && ! sudo -n true 2>/dev/null; then
        log "錯誤：需要 root 權限或 sudo 權限來恢復資料"
        exit 1
    fi
    
    # 檢查備份檔案是否存在
    if [[ ! -f "$BACKUP_DIR/${BACKUP_NAME}_manifest.txt" ]]; then
        log "錯誤：找不到備份 $BACKUP_NAME"
        show_usage
        exit 1
    fi
    
    log "備份名稱：$BACKUP_NAME"
}

show_backup_info() {
    log "備份資訊："
    sudo cat "$BACKUP_DIR/${BACKUP_NAME}_manifest.txt"
    echo ""
}

confirm_restore() {
    echo "⚠️  警告：這將會覆蓋當前的生產環境資料！"
    echo ""
    echo "當前資料狀態："
    if [[ -f "$DATA_PATH/api_monitor.db" ]]; then
        echo "  - 資料庫: $(sudo du -h "$DATA_PATH/api_monitor.db" | cut -f1) (修改時間: $(sudo stat -c %y "$DATA_PATH/api_monitor.db"))"
    else
        echo "  - 資料庫: 不存在"
    fi
    
    echo ""
    read -p "確定要從備份 '$BACKUP_NAME' 恢復資料嗎？(輸入 'yes' 確認): " confirm
    
    if [[ "$confirm" != "yes" ]]; then
        log "取消恢復操作"
        exit 0
    fi
}

stop_services() {
    log "停止相關服務..."
    
    # 停止 Docker 服務
    if command -v docker-compose &> /dev/null; then
        if [[ -f "docker-compose.prod.yml" ]]; then
            docker-compose -f docker-compose.prod.yml down || true
        elif [[ -f "docker-compose.yml" ]]; then
            docker-compose down || true
        fi
    fi
    
    log "✅ 服務已停止"
}

restore_database() {
    log "恢復資料庫..."
    
    if [[ -f "$BACKUP_DIR/${BACKUP_NAME}_database.db" ]]; then
        # 確保資料目錄存在
        sudo mkdir -p "$DATA_PATH"
        
        # 備份當前資料庫（如果存在）
        if [[ -f "$DATA_PATH/api_monitor.db" ]]; then
            sudo mv "$DATA_PATH/api_monitor.db" "$DATA_PATH/api_monitor.db.backup.$(date +%s)"
            log "當前資料庫已備份"
        fi
        
        # 恢復資料庫
        sudo cp "$BACKUP_DIR/${BACKUP_NAME}_database.db" "$DATA_PATH/api_monitor.db"
        sudo chown 1000:1000 "$DATA_PATH/api_monitor.db" 2>/dev/null || true
        
        log "✅ 資料庫恢復完成"
    else
        log "⚠️ 沒有找到資料庫備份檔案"
    fi
}

restore_files() {
    log "恢復檔案..."
    
    if [[ -f "$BACKUP_DIR/${BACKUP_NAME}_data.tar.gz" ]]; then
        # 備份當前資料目錄（如果存在）
        if [[ -d "$DATA_PATH" ]]; then
            sudo mv "$DATA_PATH" "${DATA_PATH}.backup.$(date +%s)"
            log "當前資料目錄已備份"
        fi
        
        # 恢復資料檔案
        sudo mkdir -p "$(dirname "$DATA_PATH")"
        sudo tar -xzf "$BACKUP_DIR/${BACKUP_NAME}_data.tar.gz" -C "$(dirname "$DATA_PATH")"
        sudo chown -R 1000:1000 "$DATA_PATH" 2>/dev/null || true
        
        log "✅ 資料檔案恢復完成"
    else
        log "⚠️ 沒有找到資料檔案備份"
    fi
}

start_services() {
    log "啟動服務..."
    
    # 啟動 Docker 服務
    if command -v docker-compose &> /dev/null; then
        if [[ -f "docker-compose.prod.yml" ]]; then
            docker-compose -f docker-compose.prod.yml up -d
        elif [[ -f "docker-compose.yml" ]]; then
            docker-compose up -d
        fi
    fi
    
    log "✅ 服務已啟動"
}

verify_restore() {
    log "驗證恢復結果..."
    
    # 等待服務啟動
    sleep 10
    
    # 檢查資料庫是否可訪問
    if [[ -f "$DATA_PATH/api_monitor.db" ]]; then
        if sudo sqlite3 "$DATA_PATH/api_monitor.db" "SELECT COUNT(*) FROM sqlite_master;" &>/dev/null; then
            log "✅ 資料庫驗證成功"
        else
            log "⚠️ 資料庫驗證失敗"
        fi
    fi
    
    # 檢查服務是否正常
    if curl -s http://localhost:5001/health &>/dev/null; then
        log "✅ 服務健康檢查通過"
    else
        log "⚠️ 服務健康檢查失敗，請手動檢查"
    fi
}

# ========== 主要執行流程 ==========
main() {
    log "🔄 開始 API Monitor 資料恢復"
    
    check_prerequisites "$@"
    show_backup_info
    confirm_restore
    stop_services
    restore_database
    restore_files
    start_services
    verify_restore
    
    log "🎉 資料恢復完成！"
    echo ""
    echo "📋 恢復的備份：$BACKUP_NAME"
    echo "📋 如有問題，請檢查備份檔案：$DATA_PATH.backup.*"
}

# 執行主函數
main "$@"