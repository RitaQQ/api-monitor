#!/bin/bash

# Docker 構建和管理腳本
# 確保資料分離和乾淨構建

set -e

# 顏色輸出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 函數：打印彩色訊息
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 檢查 Docker 是否運行
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker 未運行！請啟動 Docker Desktop"
        exit 1
    fi
    print_success "Docker 狀態正常"
}

# 清理函數
cleanup_build() {
    print_info "清理構建快取..."
    docker builder prune -f
    print_success "構建快取清理完成"
}

# 開發環境構建
build_dev() {
    print_info "構建開發環境..."
    
    # 確保沒有本地資料洩漏
    if [ -d "data" ] && [ "$(ls -A data 2>/dev/null)" ]; then
        print_warning "檢測到本地 data/ 目錄有檔案"
        print_info "這些檔案不會包含在 Docker 映像中 (已被 .dockerignore 排除)"
    fi
    
    docker-compose -f docker-compose.dev.yml build --no-cache
    print_success "開發環境構建完成"
}

# 生產環境構建
build_prod() {
    print_info "構建生產環境..."
    
    # 使用乾淨的 Dockerfile
    docker build -f Dockerfile.clean -t api-monitor:prod --no-cache .
    print_success "生產環境構建完成"
}

# 啟動開發環境
start_dev() {
    print_info "啟動開發環境..."
    docker-compose -f docker-compose.dev.yml up -d
    
    # 等待服務啟動
    print_info "等待服務啟動..."
    sleep 10
    
    # 檢查健康狀態
    if curl -f http://localhost:5001/health >/dev/null 2>&1; then
        print_success "開發環境啟動成功！"
        print_info "訪問地址: http://localhost:5001"
        print_info "預設帳號: admin / admin123"
    else
        print_warning "服務可能還在啟動中，請稍後檢查"
    fi
}

# 停止所有服務
stop_all() {
    print_info "停止所有服務..."
    docker-compose -f docker-compose.dev.yml down
    docker-compose -f docker-compose.yml down 2>/dev/null || true
    print_success "所有服務已停止"
}

# 查看日誌
view_logs() {
    print_info "查看開發環境日誌..."
    docker-compose -f docker-compose.dev.yml logs -f api-monitor-dev
}

# 資料管理
manage_data() {
    echo "資料管理選項："
    echo "1. 查看資料 volumes"
    echo "2. 備份開發資料"
    echo "3. 清理所有資料 (危險)"
    read -p "請選擇 (1-3): " choice
    
    case $choice in
        1)
            print_info "Docker Volumes:"
            docker volume ls | grep api_monitor
            ;;
        2)
            timestamp=$(date +%Y%m%d_%H%M%S)
            backup_name="api_monitor_backup_${timestamp}"
            docker run --rm -v dev_api_monitor_data:/data -v $(pwd):/backup alpine tar czf /backup/${backup_name}.tar.gz -C /data .
            print_success "備份完成: ${backup_name}.tar.gz"
            ;;
        3)
            read -p "確定要刪除所有開發資料嗎？(y/N): " confirm
            if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
                docker volume rm dev_api_monitor_data dev_api_monitor_logs 2>/dev/null || true
                print_success "開發環境資料已清理"
            fi
            ;;
        *)
            print_error "無效選擇"
            ;;
    esac
}

# 主選單
show_menu() {
    echo ""
    echo "🐳 API Monitor Docker 管理工具"
    echo "================================"
    echo "1. 構建開發環境"
    echo "2. 構建生產環境"
    echo "3. 啟動開發環境"
    echo "4. 停止所有服務"
    echo "5. 查看日誌"
    echo "6. 資料管理"
    echo "7. 清理構建快取"
    echo "8. 檢查狀態"
    echo "0. 退出"
    echo ""
}

# 檢查狀態
check_status() {
    print_info "檢查服務狀態..."
    echo ""
    echo "Docker Compose 服務:"
    docker-compose -f docker-compose.dev.yml ps
    echo ""
    echo "Docker Volumes:"
    docker volume ls | grep api_monitor || echo "無相關 volumes"
    echo ""
    if curl -s http://localhost:5001/health >/dev/null; then
        print_success "API 服務運行正常"
    else
        print_warning "API 服務未運行或無法訪問"
    fi
}

# 主程式
main() {
    check_docker
    
    if [ $# -eq 0 ]; then
        # 互動模式
        while true; do
            show_menu
            read -p "請選擇操作 (0-8): " choice
            
            case $choice in
                1) build_dev ;;
                2) build_prod ;;
                3) start_dev ;;
                4) stop_all ;;
                5) view_logs ;;
                6) manage_data ;;
                7) cleanup_build ;;
                8) check_status ;;
                0) 
                    print_info "再見！"
                    exit 0
                    ;;
                *)
                    print_error "無效選擇，請重試"
                    ;;
            esac
            
            echo ""
            read -p "按 Enter 鍵繼續..."
        done
    else
        # 命令列模式
        case $1 in
            "build-dev") build_dev ;;
            "build-prod") build_prod ;;
            "start-dev") start_dev ;;
            "stop") stop_all ;;
            "logs") view_logs ;;
            "status") check_status ;;
            "clean") cleanup_build ;;
            *)
                echo "用法: $0 [build-dev|build-prod|start-dev|stop|logs|status|clean]"
                echo "或不帶參數進入互動模式"
                exit 1
                ;;
        esac
    fi
}

main "$@"