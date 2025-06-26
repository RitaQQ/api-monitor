#!/bin/bash

# 🚀 API Monitor 安全部署腳本
# 用途：在保護生產環境資料的前提下進行部署

set -e  # 遇到錯誤立即退出

# ========== 配置 ==========
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BACKUP_ENABLED=true
ENVIRONMENT="production"

# ========== 函數定義 ==========
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

show_usage() {
    echo "用法: $0 [選項]"
    echo ""
    echo "選項:"
    echo "  -e, --environment ENV    部署環境 (development|production)，預設: production"
    echo "  --no-backup             跳過資料備份"
    echo "  --force                 強制部署，跳過確認"
    echo "  -h, --help              顯示此幫助訊息"
    echo ""
    echo "範例:"
    echo "  $0                      # 生產環境部署（含備份）"
    echo "  $0 -e development       # 開發環境部署"
    echo "  $0 --no-backup          # 部署但不備份"
}

parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -e|--environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            --no-backup)
                BACKUP_ENABLED=false
                shift
                ;;
            --force)
                FORCE_DEPLOY=true
                shift
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            *)
                echo "未知選項: $1"
                show_usage
                exit 1
                ;;
        esac
    done
}

check_prerequisites() {
    log "檢查部署前置條件..."
    
    # 檢查必要工具
    local required_tools=("git" "docker" "docker-compose")
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            log "錯誤：找不到必要工具 '$tool'"
            exit 1
        fi
    done
    
    # 檢查 Docker 是否運行
    if ! docker info &> /dev/null; then
        log "錯誤：Docker 服務未運行"
        exit 1
    fi
    
    # 檢查是否在正確的專案目錄
    if [[ ! -f "$PROJECT_DIR/simple_app.py" ]]; then
        log "錯誤：不在正確的專案目錄中"
        exit 1
    fi
    
    log "✅ 前置條件檢查通過"
}

backup_current_data() {
    if [[ "$BACKUP_ENABLED" == "true" ]] && [[ "$ENVIRONMENT" == "production" ]]; then
        log "開始備份當前資料..."
        
        if [[ -f "$SCRIPT_DIR/backup_data.sh" ]]; then
            bash "$SCRIPT_DIR/backup_data.sh"
            log "✅ 資料備份完成"
        else
            log "⚠️ 備份腳本不存在，跳過備份"
        fi
    else
        log "跳過資料備份（$ENVIRONMENT 環境或已禁用備份）"
    fi
}

pull_latest_code() {
    log "拉取最新代碼..."
    
    cd "$PROJECT_DIR"
    
    # 檢查是否有未提交的變更
    if [[ -n "$(git status --porcelain)" ]]; then
        log "⚠️ 發現未提交的變更："
        git status --short
        
        if [[ "$FORCE_DEPLOY" != "true" ]]; then
            read -p "繼續部署會忽略這些變更，確定繼續嗎？(y/N): " confirm
            if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
                log "部署已取消"
                exit 0
            fi
        fi
    fi
    
    # 拉取最新代碼
    git fetch origin
    git reset --hard origin/main
    
    log "✅ 代碼更新完成"
}

deploy_application() {
    log "開始部署應用..."
    
    cd "$PROJECT_DIR"
    
    if [[ "$ENVIRONMENT" == "production" ]]; then
        # 生產環境部署
        log "使用生產環境配置部署..."
        
        # 確保生產環境資料目錄存在
        sudo mkdir -p /opt/api-monitor/{data,logs}
        sudo chown -R 1000:1000 /opt/api-monitor/
        
        # 使用生產環境配置
        docker-compose -f docker-compose.prod.yml down || true
        docker-compose -f docker-compose.prod.yml build --no-cache
        docker-compose -f docker-compose.prod.yml up -d
        
    else
        # 開發環境部署
        log "使用開發環境配置部署..."
        
        # 確保開發環境資料目錄存在
        mkdir -p docker_data/{data,logs,uploads,backups}
        
        docker-compose down || true
        docker-compose build --no-cache
        docker-compose up -d
    fi
    
    log "✅ 應用部署完成"
}

wait_for_services() {
    log "等待服務啟動..."
    
    local max_attempts=30
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        if curl -s http://localhost:5001/health &>/dev/null; then
            log "✅ 服務啟動成功"
            return 0
        fi
        
        log "等待服務啟動... ($attempt/$max_attempts)"
        sleep 5
        ((attempt++))
    done
    
    log "⚠️ 服務啟動超時，請手動檢查"
    return 1
}

verify_deployment() {
    log "驗證部署結果..."
    
    # 檢查容器狀態
    local containers
    if [[ "$ENVIRONMENT" == "production" ]]; then
        containers=$(docker-compose -f docker-compose.prod.yml ps -q)
    else
        containers=$(docker-compose ps -q)
    fi
    
    for container in $containers; do
        if [[ -n "$container" ]]; then
            local status=$(docker inspect --format='{{.State.Status}}' "$container")
            local name=$(docker inspect --format='{{.Name}}' "$container" | sed 's/^\/*//')
            
            if [[ "$status" == "running" ]]; then
                log "✅ 容器 $name 運行正常"
            else
                log "❌ 容器 $name 狀態異常: $status"
            fi
        fi
    done
    
    # 檢查健康狀態
    if wait_for_services; then
        log "✅ 部署驗證成功"
    else
        log "❌ 部署驗證失敗"
        exit 1
    fi
}

show_deployment_info() {
    log "部署完成資訊："
    echo ""
    echo "🎉 API Monitor 部署成功！"
    echo ""
    echo "📋 部署環境: $ENVIRONMENT"
    echo "📋 訪問地址: http://localhost:5001"
    echo "📋 健康檢查: http://localhost:5001/health"
    
    if [[ "$ENVIRONMENT" == "production" ]]; then
        echo "📋 資料目錄: /opt/api-monitor/data"
        echo "📋 日誌目錄: /opt/api-monitor/logs"
    else
        echo "📋 資料目錄: ./docker_data/data"
        echo "📋 日誌目錄: ./docker_data/logs"
    fi
    
    if [[ "$BACKUP_ENABLED" == "true" ]]; then
        echo "📋 備份目錄: /var/backups/api-monitor"
    fi
    
    echo ""
    echo "🔧 管理命令:"
    if [[ "$ENVIRONMENT" == "production" ]]; then
        echo "  查看日誌: docker-compose -f docker-compose.prod.yml logs -f"
        echo "  停止服務: docker-compose -f docker-compose.prod.yml down"
    else
        echo "  查看日誌: docker-compose logs -f"
        echo "  停止服務: docker-compose down"
    fi
}

# ========== 主要執行流程 ==========
main() {
    log "🚀 開始 API Monitor 安全部署"
    
    parse_arguments "$@"
    check_prerequisites
    backup_current_data
    pull_latest_code
    deploy_application
    verify_deployment
    show_deployment_info
    
    log "🎉 部署流程完成！"
}

# 執行主函數
main "$@"