#!/bin/bash

# 卡牌对战竞技场 - 健康检查脚本
# 作者: Card Battle Arena Team
# 版本: 1.0.0

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_header() {
    echo -e "${PURPLE}[HEALTH]${NC} $1"
}

# 配置
FRONTEND_URL=${FRONTEND_URL:-"http://localhost:3000"}
BACKEND_URL=${BACKEND_URL:-"http://localhost:8000"}
WEBSOCKET_URL=${WEBSOCKET_URL:-"ws://localhost:8000/ws"}

# 健康检查统计
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0

# 检查函数
health_check() {
    local description="$1"
    local check_command="$2"

    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    log_header "$description"

    if eval "$check_command" > /dev/null 2>&1; then
        log_success "✓ $description"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
        return 0
    else
        log_error "✗ $description"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
        return 1
    fi
}

# 检查HTTP服务
check_http_service() {
    local url="$1"
    local service_name="$2"
    local expected_status="${3:-200}"

    health_check "$service_name HTTP服务" "curl -f -s -o /dev/null -w '%{http_code}' '$url' | grep -q '$expected_status'"
}

# 检查数据库连接
check_database() {
    health_check "PostgreSQL数据库连接" "docker exec postgres-container pg_isready -U cardbattle -d cardbattle_dev"
}

# 检查Redis连接
check_redis() {
    health_check "Redis缓存连接" "docker exec redis-container redis-cli ping | grep -q PONG"
}

# 检查Docker服务
check_docker_service() {
    local service_name="$1"
    health_check "Docker服务: $service_name" "docker ps --format '{{.Names}}' | grep -q '$service_name'"
}

# 检查系统资源
check_system_resources() {
    log_header "系统资源检查"

    # 检查内存使用率
    if command -v free >/dev/null 2>&1; then
        memory_usage=$(free | awk 'NR==2{printf "%.1f", $3*100/$2}')
        if (( $(echo "$memory_usage < 80" | bc -l) )); then
            log_success "✓ 内存使用率: ${memory_usage}%"
            PASSED_CHECKS=$((PASSED_CHECKS + 1))
        else
            log_warning "⚠ 内存使用率较高: ${memory_usage}%"
        fi
        TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    fi

    # 检查磁盘使用率
    if command -v df >/dev/null 2>&1; then
        disk_usage=$(df . | awk 'NR==2 {print $5}' | sed 's/%//')
        if [ "$disk_usage" -lt 80 ]; then
            log_success "✓ 磁盘使用率: ${disk_usage}%"
            PASSED_CHECKS=$((PASSED_CHECKS + 1))
        else
            log_warning "⚠ 磁盘使用率较高: ${disk_usage}%"
        fi
        TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    fi

    # 检查CPU负载
    if command -v uptime >/dev/null 2>&1; then
        load_avg=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | sed 's/,//')
        log_info "CPU负载: $load_avg"
        TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    fi
}

# 检查端口占用
check_port() {
    local port="$1"
    local service="$2"

    if command -v netstat >/dev/null 2>&1; then
        health_check "端口 $port ($service)" "netstat -tuln | grep -q ':$port '"
    elif command -v ss >/dev/null 2>&1; then
        health_check "端口 $port ($service)" "ss -tuln | grep -q ':$port '"
    fi
}

# 检查进程
check_process() {
    local process_name="$1"
    local service_name="$2"

    health_check "进程: $service_name" "pgrep -f '$process_name' > /dev/null"
}

# 检查日志错误
check_log_errors() {
    log_header "日志错误检查"

    local error_count=0

    # 检查应用日志
    if [ -d "logs" ]; then
        error_count=$(find logs -name "*.log" -exec grep -l "ERROR\|FATAL" {} \; | wc -l)
        if [ "$error_count" -eq 0 ]; then
            log_success "✓ 应用日志无错误"
            PASSED_CHECKS=$((PASSED_CHECKS + 1))
        else
            log_warning "⚠ 发现 $error_count 个日志文件包含错误"
        fi
        TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    fi

    # 检查Docker容器日志
    if command -v docker >/dev/null 2>&1; then
        docker_error_count=$(docker ps --format "{{.Names}}" | xargs -I {} sh -c 'docker logs {} 2>&1 | grep -c "ERROR\|FATAL"' | paste -sd+ | bc)
        if [ "$docker_error_count" -eq 0 ]; then
            log_success "✓ Docker日志无错误"
            PASSED_CHECKS=$((PASSED_CHECKS + 1))
        else
            log_warning "⚠ Docker日志中发现 $docker_error_count 个错误"
        fi
        TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    fi
}

# 检查SSL证书
check_ssl_certificate() {
    if [[ "$BACKEND_URL" == https://* ]]; then
        local domain=$(echo "$BACKEND_URL" | sed 's|https://||')
        health_check "SSL证书有效性" "echo | openssl s_client -servername '$domain' -connect '$domain:443' 2>/dev/null | openssl x509 -noout -dates | grep -q 'notAfter'"
    fi
}

# 检查API响应时间
check_api_response_time() {
    log_header "API响应时间检查"

    if command -v curl >/dev/null 2>&1; then
        local response_time=$(curl -o /dev/null -s -w '%{time_total}' "$BACKEND_URL/health" 2>/dev/null)
        if [ -n "$response_time" ]; then
            if (( $(echo "$response_time < 1.0" | bc -l) )); then
                log_success "✓ API响应时间: ${response_time}s"
                PASSED_CHECKS=$((PASSED_CHECKS + 1))
            else
                log_warning "⚠ API响应时间较慢: ${response_time}s"
            fi
            TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
        fi
    fi
}

# 显示健康检查结果
show_health_results() {
    echo ""
    log_info "健康检查完成"
    echo "===================="
    echo -e "总检查数: ${BLUE}$TOTAL_CHECKS${NC}"
    echo -e "通过检查: ${GREEN}$PASSED_CHECKS${NC}"
    echo -e "失败检查: ${RED}$FAILED_CHECKS${NC}"

    if [ $FAILED_CHECKS -eq 0 ]; then
        echo ""
        log_success "🎉 所有健康检查都通过了！系统运行正常。"
        return 0
    else
        echo ""
        log_warning "⚠️  有 $FAILED_CHECKS 项检查失败，请检查相关服务"
        return 1
    fi
}

# 生成健康报告
generate_health_report() {
    local report_file="reports/health-$(date +%Y%m%d_%H%M%S).json"
    mkdir -p reports

    local report=$(cat <<EOF
{
    "timestamp": "$(date -Iseconds)",
    "total_checks": $TOTAL_CHECKS,
    "passed_checks": $PASSED_CHECKS,
    "failed_checks": $FAILED_CHECKS,
    "status": "$([ $FAILED_CHECKS -eq 0 ] && echo "healthy" || echo "unhealthy")",
    "services": {
        "frontend": {
            "url": "$FRONTEND_URL",
            "status": "running"
        },
        "backend": {
            "url": "$BACKEND_URL",
            "status": "running"
        }
    }
}
EOF
)

    echo "$report" > "$report_file"
    log_success "健康报告已生成: $report_file"
}

# 主函数
main() {
    echo "🏥 卡牌对战竞技场 - 健康检查"
    echo "=============================="
    echo ""

    # 解析命令行参数
    local detailed=false
    local generate_report=false

    while [[ $# -gt 0 ]]; do
        case $1 in
            --detailed|-d)
                detailed=true
                shift
                ;;
            --report|-r)
                generate_report=true
                shift
                ;;
            --help|-h)
                echo "用法: $0 [选项]"
                echo ""
                echo "选项:"
                echo "  --detailed, -d   运行详细健康检查"
                echo "  --report, -r     生成健康报告"
                echo "  --help, -h       显示帮助信息"
                echo ""
                exit 0
                ;;
            *)
                log_error "未知选项: $1"
                exit 1
                ;;
        esac
    done

    # 基础检查
    log_info "运行基础健康检查..."

    # 检查端口
    check_port 3000 "前端服务"
    check_port 8000 "后端服务"

    # 检查HTTP服务
    check_http_service "$FRONTEND_URL" "前端应用"
    check_http_service "$BACKEND_URL/health" "后端健康检查"

    # 检查Docker服务
    if command -v docker >/dev/null 2>&1; then
        check_docker_service "postgres-container"
        check_docker_service "redis-container"
        check_docker_service "backend-container"
        check_docker_service "frontend-container"
    fi

    # 检查数据库
    check_database
    check_redis

    # 系统资源检查
    check_system_resources

    # 详细检查
    if [ "$detailed" = true ]; then
        log_info "运行详细健康检查..."

        # 检查API响应时间
        check_api_response_time

        # 检查SSL证书
        check_ssl_certificate

        # 检查日志错误
        check_log_errors
    fi

    # 显示结果
    show_health_results

    # 生成报告
    if [ "$generate_report" = true ]; then
        generate_health_report
    fi

    echo ""
    log_info "健康检查完成！"
}

# 脚本入口
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi