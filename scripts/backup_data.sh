#!/bin/bash

# 🔐 API Monitor 資料備份腳本
# 用途：在 git push 或部署前備份生產環境資料

set -e  # 遇到錯誤立即退出

# ========== 配置 ==========
BACKUP_DIR="/var/backups/api-monitor"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="api_monitor_backup_${TIMESTAMP}"

# Docker 資料路徑
DATA_PATH="/opt/api-monitor/data"
LOGS_PATH="/opt/api-monitor/logs"

# 備份保留天數
RETENTION_DAYS=30

# ========== 函數定義 ==========
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

check_prerequisites() {
    log "檢查備份前置條件..."
    
    # 檢查是否為 root 或有 sudo 權限
    if [[ $EUID -ne 0 ]] && ! sudo -n true 2>/dev/null; then
        log "錯誤：需要 root 權限或 sudo 權限來備份資料"
        exit 1
    fi
    
    # 檢查資料目錄是否存在
    if [[ ! -d "$DATA_PATH" ]]; then
        log "警告：資料目錄 $DATA_PATH 不存在"
    fi
    
    # 創建備份目錄
    sudo mkdir -p "$BACKUP_DIR"
    log "備份目錄已準備：$BACKUP_DIR"
}

backup_database() {
    log "開始備份資料庫..."
    
    if [[ -f "$DATA_PATH/api_monitor.db" ]]; then
        # 使用 SQLite 的 .backup 命令創建一致性備份
        sudo sqlite3 "$DATA_PATH/api_monitor.db" ".backup $BACKUP_DIR/${BACKUP_NAME}_database.db"
        log "✅ 資料庫備份完成：${BACKUP_NAME}_database.db"
    else
        log "⚠️ 資料庫檔案不存在，跳過資料庫備份"
    fi
}

backup_files() {
    log "開始備份檔案..."
    
    # 備份整個 data 目錄
    if [[ -d "$DATA_PATH" ]]; then
        sudo tar -czf "$BACKUP_DIR/${BACKUP_NAME}_data.tar.gz" -C "$(dirname "$DATA_PATH")" "$(basename "$DATA_PATH")"
        log "✅ 資料檔案備份完成：${BACKUP_NAME}_data.tar.gz"
    fi
    
    # 備份日誌檔案（可選）
    if [[ -d "$LOGS_PATH" ]] && [[ -n "$(ls -A "$LOGS_PATH" 2>/dev/null)" ]]; then
        sudo tar -czf "$BACKUP_DIR/${BACKUP_NAME}_logs.tar.gz" -C "$(dirname "$LOGS_PATH")" "$(basename "$LOGS_PATH")"
        log "✅ 日誌檔案備份完成：${BACKUP_NAME}_logs.tar.gz"
    fi
}

create_backup_manifest() {
    log "創建備份清單..."
    
    MANIFEST_FILE="$BACKUP_DIR/${BACKUP_NAME}_manifest.txt"
    {
        echo "API Monitor 資料備份清單"
        echo "備份時間: $(date)"
        echo "備份名稱: $BACKUP_NAME"
        echo "==============================="
        echo ""
        echo "檔案列表:"
        ls -la "$BACKUP_DIR"/${BACKUP_NAME}_* 2>/dev/null || echo "無備份檔案"
        echo ""
        echo "資料庫資訊:"
        if [[ -f "$DATA_PATH/api_monitor.db" ]]; then
            echo "資料庫大小: $(sudo du -h "$DATA_PATH/api_monitor.db" | cut -f1)"
            echo "資料庫修改時間: $(sudo stat -c %y "$DATA_PATH/api_monitor.db")"
        else
            echo "資料庫不存在"
        fi
    } | sudo tee "$MANIFEST_FILE" > /dev/null
    
    log "✅ 備份清單已創建：${BACKUP_NAME}_manifest.txt"
}

cleanup_old_backups() {
    log "清理舊備份檔案（保留 $RETENTION_DAYS 天）..."
    
    # 刪除超過保留期限的備份檔案
    sudo find "$BACKUP_DIR" -name "api_monitor_backup_*" -type f -mtime +$RETENTION_DAYS -delete 2>/dev/null || true
    
    log "✅ 舊備份清理完成"
}

# ========== 主要執行流程 ==========
main() {
    log "🔄 開始 API Monitor 資料備份"
    
    check_prerequisites
    backup_database
    backup_files
    create_backup_manifest
    cleanup_old_backups
    
    log "🎉 資料備份完成！備份檔案："
    sudo ls -la "$BACKUP_DIR"/${BACKUP_NAME}_* 2>/dev/null || echo "無備份檔案生成"
    
    echo ""
    echo "📋 備份檔案位置：$BACKUP_DIR"
    echo "📋 備份名稱：$BACKUP_NAME"
    echo "📋 要恢復資料，請執行：./scripts/restore_data.sh $BACKUP_NAME"
}

# 執行主函數
main "$@"