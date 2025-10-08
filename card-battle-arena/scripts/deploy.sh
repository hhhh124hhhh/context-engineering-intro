#!/bin/bash

# 卡牌对战竞技场部署脚本
# 作者: Card Battle Arena Team
# 版本: 1.0.0

set -e  # 遇到错误时立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

# 检查依赖
check_dependencies() {
    log_info "检查系统依赖..."

    # 检查 Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi

    # 检查 Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi

    # 检查 OpenSSL (用于生成证书)
    if ! command -v openssl &> /dev/null; then
        log_error "OpenSSL 未安装，请先安装 OpenSSL"
        exit 1
    fi

    log_success "所有依赖检查通过"
}

# 设置环境变量
setup_environment() {
    log_info "设置环境变量..."

    # 检查 .env 文件是否存在
    if [ ! -f ".env.prod" ]; then
        log_warning ".env.prod 文件不存在，从模板创建..."
        cp .env.prod.example .env.prod

        log_info "请编辑 .env.prod 文件，配置生产环境变量"
        echo "按任意键继续..."
        read -r
    fi

    # 加载环境变量
    export $(cat .env.prod | grep -v '^#' | xargs)

    log_success "环境变量设置完成"
}

# 生成 SSL 证书
generate_ssl_certificates() {
    log_info "生成 SSL 证书..."

    # 创建 SSL 目录
    mkdir -p nginx/ssl

    # 生成自签名证书（生产环境应使用 Let's Encrypt 或购买证书）
    if [ ! -f "nginx/ssl/cert.pem" ] || [ ! -f "nginx/ssl/key.pem" ]; then
        log_info "生成自签名 SSL 证书..."
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout nginx/ssl/key.pem \
            -out nginx/ssl/cert.pem \
            -subj "/C=CN/ST=Beijing/L=Beijing/O=CardBattle/CN=${DOMAIN:-localhost}"

        log_warning "使用自签名证书，浏览器会显示安全警告"
        log_info "生产环境请使用 Let's Encrypt 或购买的有效证书"
    else
        log_info "SSL 证书已存在，跳过生成"
    fi

    log_success "SSL 证书准备完成"
}

# 构建镜像
build_images() {
    log_info "构建 Docker 镜像..."

    # 构建后端镜像
    log_info "构建后端镜像..."
    docker-compose -f docker-compose.prod.yml build backend

    # 构建前端镜像
    log_info "构建前端镜像..."
    docker-compose -f docker-compose.prod.yml build frontend

    log_success "镜像构建完成"
}

# 数据库迁移
run_migrations() {
    log_info "运行数据库迁移..."

    # 启动数据库服务
    docker-compose -f docker-compose.prod.yml up -d postgres redis

    # 等待数据库启动
    log_info "等待数据库启动..."
    sleep 10

    # 运行迁移
    docker-compose -f docker-compose.prod.yml run --rm backend alembic upgrade head

    log_success "数据库迁移完成"
}

# 启动服务
start_services() {
    log_info "启动所有服务..."

    # 启动所有服务
    docker-compose -f docker-compose.prod.yml up -d

    log_info "等待服务启动..."
    sleep 30

    # 检查服务状态
    check_services

    log_success "所有服务启动完成"
}

# 检查服务状态
check_services() {
    log_info "检查服务状态..."

    services=("postgres" "redis" "backend" "frontend" "nginx")

    for service in "${services[@]}"; do
        if docker-compose -f docker-compose.prod.yml ps | grep -q "${service}.*Up"; then
            log_success "${service} 运行正常"
        else
            log_error "${service} 运行异常"
            docker-compose -f docker-compose.prod.yml logs "${service}"
        fi
    done
}

# 健康检查
health_check() {
    log_info "执行健康检查..."

    # 检查后端健康状态
    if curl -f http://localhost:${BACKEND_PORT:-8000}/health &> /dev/null; then
        log_success "后端健康检查通过"
    else
        log_error "后端健康检查失败"
    fi

    # 检查前端健康状态
    if curl -f http://localhost:${FRONTEND_PORT:-3000} &> /dev/null; then
        log_success "前端健康检查通过"
    else
        log_error "前端健康检查失败"
    fi

    # 检查数据库连接
    if docker-compose -f docker-compose.prod.yml exec -T pg_isready -U ${POSTGRES_USER:-cardbattle} &> /dev/null; then
        log_success "数据库连接正常"
    else
        log_error "数据库连接失败"
    fi
}

# 备份数据库
backup_database() {
    log_info "备份数据库..."

    backup_dir="backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"

    # 导出数据库
    docker-compose -f docker-compose.prod.yml exec -T postgres pg_dump -U ${POSTGRES_USER:-cardbattle} ${POSTGRES_DB:-cardbattle_prod} > "$backup_dir/database.sql"

    log_success "数据库备份完成: $backup_dir"
}

# 清理旧镜像
cleanup_images() {
    log_info "清理旧的 Docker 镜像..."

    # 清理悬空镜像
    docker image prune -f

    # 清理旧的应用镜像（保留最近3个版本）
    docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.ID}}" | grep "cardbattle" | \
    tail -n +4 | awk '{print $3}' | xargs -r docker rmi -f 2>/dev/null || true

    log_success "镜像清理完成"
}

# 更新服务
update_services() {
    log_info "更新服务..."

    # 备份数据库
    backup_database

    # 拉取最新代码
    log_info "拉取最新代码..."
    git pull origin main

    # 重新构建和部署
    build_images
    run_migrations
    docker-compose -f docker-compose.prod.yml up -d

    # 清理旧镜像
    cleanup_images

    log_success "服务更新完成"
}

# 回滚服务
rollback_services() {
    log_info "回滚服务到上一个版本..."

    # 获取上一个版本
    previous_version=$(git describe --tags --abbrev=0 HEAD~1 2>/dev/null || echo "HEAD~1")

    log_info "回滚到版本: $previous_version"

    # 切换到上一个版本
    git checkout "$previous_version"

    # 重新构建和部署
    build_images
    docker-compose -f docker-compose.prod.yml up -d

    log_success "服务回滚完成"
}

# 显示日志
show_logs() {
    local service=${1:-""}

    if [ -n "$service" ]; then
        log_info "显示 $service 服务日志..."
        docker-compose -f docker-compose.prod.yml logs -f "$service"
    else
        log_info "显示所有服务日志..."
        docker-compose -f docker-compose.prod.yml logs -f
    fi
}

# 停止服务
stop_services() {
    log_info "停止所有服务..."

    docker-compose -f docker-compose.prod.yml down

    log_success "所有服务已停止"
}

# 完全清理
cleanup_all() {
    log_warning "这将删除所有容器、镜像和数据卷，确定继续吗？(y/N)"
    read -r response

    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        log_info "清理所有资源..."

        docker-compose -f docker-compose.prod.yml down -v --rmi all
        docker system prune -af

        log_success "清理完成"
    else
        log_info "取消清理操作"
    fi
}

# 显示帮助信息
show_help() {
    echo "卡牌对战竞技场部署脚本"
    echo ""
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  deploy      完整部署（推荐首次使用）"
    echo "  update      更新服务"
    echo "  rollback    回滚服务"
    echo "  start       启动服务"
    echo "  stop        停止服务"
    echo "  restart     重启服务"
    echo "  status      查看服务状态"
    echo "  logs [服务] 查看日志"
    echo "  health      健康检查"
    echo "  backup      备份数据库"
    echo "  cleanup     清理资源"
    echo "  help        显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 deploy     # 完整部署"
    echo "  $0 update     # 更新服务"
    echo "  $0 logs backend # 查看后端日志"
}

# 主函数
main() {
    case "${1:-}" in
        "deploy")
            check_dependencies
            setup_environment
            generate_ssl_certificates
            build_images
            run_migrations
            start_services
            health_check
            ;;
        "update")
            check_dependencies
            setup_environment
            update_services
            health_check
            ;;
        "rollback")
            check_dependencies
            rollback_services
            health_check
            ;;
        "start")
            start_services
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            stop_services
            start_services
            ;;
        "status")
            check_services
            ;;
        "logs")
            show_logs "${2:-}"
            ;;
        "health")
            health_check
            ;;
        "backup")
            backup_database
            ;;
        "cleanup")
            cleanup_all
            ;;
        "help"|"--help"|"-h")
            show_help
            ;;
        *)
            log_error "未知命令: $1"
            show_help
            exit 1
            ;;
    esac
}

# 脚本入口
main "$@"