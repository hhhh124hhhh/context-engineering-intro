#!/bin/bash

# 卡牌对战竞技场 - 简化验证脚本
# 适用于没有完整工具链的环境

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
    echo -e "${PURPLE}[VERIFY]${NC} $1"
}

# 验证结果统计
TOTAL_VERIFICATIONS=0
PASSED_VERIFICATIONS=0
FAILED_VERIFICATIONS=0

# 验证函数
verify() {
    local description="$1"
    local command="$2"

    TOTAL_VERIFICATIONS=$((TOTAL_VERIFICATIONS + 1))
    log_header "$description"

    if eval "$command" > /dev/null 2>&1; then
        log_success "✓ $description"
        PASSED_VERIFICATIONS=$((PASSED_VERIFICATIONS + 1))
        return 0
    else
        log_error "✗ $description"
        FAILED_VERIFICATIONS=$((FAILED_VERIFICATIONS + 1))
        return 1
    fi
}

# 显示验证结果
show_verification_results() {
    echo ""
    log_info "验证完成"
    echo "===================="
    echo -e "总验证数: ${BLUE}$TOTAL_VERIFICATIONS${NC}"
    echo -e "通过验证: ${GREEN}$PASSED_VERIFICATIONS${NC}"
    echo -e "失败验证: ${RED}$FAILED_VERIFICATIONS${NC}"

    if [ $FAILED_VERIFICATIONS -eq 0 ]; then
        echo ""
        log_success "🎉 所有验证都通过了！项目结构完整！"
        return 0
    else
        echo ""
        log_warning "⚠️  有 $FAILED_VERIFICATIONS 项验证失败，但项目基本结构完整"
        return 1
    fi
}

# 项目结构验证
verify_project_structure() {
    log_info "验证项目结构完整性"

    # 根目录文件
    verify "README.md 存在" "test -f README.md"
    verify "LICENSE 文件存在" "test -f LICENSE"
    verify ".gitignore 存在" "test -f .gitignore"
    verify "docker-compose.yml 存在" "test -f docker-compose.yml"
    verify "docker-compose.prod.yml 存在" "test -f docker-compose.prod.yml"

    # 环境配置文件
    verify ".env.example 存在" "test -f .env.example"
    verify ".env.prod.example 存在" "test -f .env.prod.example"

    # 前端文件
    verify "前端 package.json 存在" "test -f frontend/package.json"
    verify "前端 tsconfig.json 存在" "test -f frontend/tsconfig.json"
    verify "前端 vite.config.ts 存在" "test -f frontend/vite.config.ts"
    verify "前端 index.html 存在" "test -f frontend/index.html"

    # 后端文件
    verify "后端 requirements.txt 存在" "test -f backend/requirements.txt"
    verify "后端 main.py 存在" "test -f backend/main.py"
    verify "后端 pyproject.toml 存在" "test -f backend/pyproject.toml"

    # 核心目录
    verify "前端 src 目录存在" "test -d frontend/src"
    verify "后端 app 目录存在" "test -d backend/app"
    verify "测试目录存在" "test -d backend/tests"
    verify "部署脚本目录存在" "test -d scripts"
    verify "Nginx 配置目录存在" "test -d nginx"

    # 组件结构
    verify "前端组件目录存在" "test -d frontend/src/components"
    verify "前端页面目录存在" "test -d frontend/src/pages"
    verify "前端类型定义存在" "test -d frontend/src/types"

    # 后端模块
    verify "后端模型目录存在" "test -d backend/app/models"
    verify "后端API路由目录存在" "test -d backend/app/api"
    verify "后端核心模块目录存在" "test -d backend/app/core"
    verify "后端数据库目录存在" "test -d backend/app/database"
}

# 文档验证
verify_documentation() {
    log_info "验证文档完整性"

    verify "API 文档存在" "test -f API_DOCS.md"
    verify "部署指南存在" "test -f DEPLOYMENT.md"
    verify "开发指南存在" "test -f DEVELOPMENT.md"
    verify "项目总结存在" "test -f PROJECT_SUMMARY.md"
    verify "初始需求文档存在" "test -f INITIAL.md"
    verify "PRP 文档存在" "test -f PRP.md"
}

# 配置文件验证
verify_configurations() {
    log_info "验证配置文件完整性"

    verify "GitHub Actions 配置存在" "test -f .github/workflows/ci.yml"
    verify "Docker 配置目录存在" "test -f docker/production/Dockerfile.backend"
    verify "Docker 开发配置存在" "test -f docker/development/Dockerfile.backend"
    verify "监控配置存在" "test -f monitoring/prometheus.yml"
    verify "Grafana 配置目录存在" "test -d monitoring/grafana"
    verify "Nginx 配置文件存在" "test -f nginx/conf.d/default.conf"
}

# 脚本验证
verify_scripts() {
    log_info "验证脚本完整性"

    verify "Linux 部署脚本存在" "test -f scripts/deploy.sh"
    verify "Windows 部署脚本存在" "test -f scripts/deploy-windows.ps1"
    verify "质量检查脚本存在" "test -f scripts/quality-check.sh"
    verify "Windows 质量检查脚本存在" "test -f scripts/quality-check.ps1"
    verify "设置脚本存在" "test -f scripts/setup.sh"
    verify "数据初始化脚本存在" "test -f scripts/init-data.py"
    verify "健康检查脚本存在" "test -f scripts/health-check.sh"
}

# 测试文件验证
verify_tests() {
    log_info "验证测试文件完整性"

    verify "游戏引擎测试存在" "test -f backend/tests/test_game_engine.py"
    verify "匹配系统测试存在" "test -f backend/tests/test_matchmaking.py"
    verify "用户系统测试存在" "test -f backend/tests/test_auth.py"
    verify "WebSocket测试存在" "test -f backend/tests/test_websocket.py"
    verify "卡牌测试存在" "test -f backend/tests/test_cards.py"
}

# 统计项目信息
generate_project_stats() {
    log_info "生成项目统计信息"

    echo ""
    log_header "项目统计信息"

    # 文件统计
    total_files=$(find . -type f | grep -v node_modules | grep -v __pycache__ | grep -v .git | wc -l)
    python_files=$(find . -name "*.py" | wc -l)
    ts_files=$(find . -name "*.ts" -o -name "*.tsx" | wc -l)
    js_files=$(find . -name "*.js" -o -name "*.jsx" | wc -l)

    echo -e "总文件数: ${BLUE}$total_files${NC}"
    echo -e "Python 文件: ${BLUE}$python_files${NC}"
    echo -e "TypeScript 文件: ${BLUE}$ts_files${NC}"
    echo -e "JavaScript 文件: ${BLUE}$js_files${NC}"

    # 代码行数统计（近似）
    if command -v find >/dev/null 2>&1; then
        backend_lines=0
        if [ -d "backend" ]; then
            backend_lines=$(find backend -name "*.py" -exec wc -l {} + 2>/dev/null | tail -1 | awk '{print $1}' || echo "0")
        fi

        frontend_lines=0
        if [ -d "frontend/src" ]; then
            frontend_lines=$(find frontend/src -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" -exec wc -l {} + 2>/dev/null | tail -1 | awk '{print $1}' || echo "0")
        fi

        echo -e "后端代码行数: ${BLUE}$backend_lines${NC}"
        echo -e "前端代码行数: ${BLUE}$frontend_lines${NC}"
    fi

    # 目录结构
    echo ""
    log_header "主要目录结构"
    if command -v tree >/dev/null 2>&1; then
        tree -I 'node_modules|.git|__pycache__|*.pyc|coverage|dist' --dirsfirst -L 2
    else
        ls -la
    fi
}

# 主函数
main() {
    echo "🔍 卡牌对战竞技场 - 简化验证"
    echo "============================="
    echo ""
    echo "项目: Card Battle Arena"
    echo "版本: 1.0.0"
    echo "时间: $(date)"
    echo "环境: 简化验证模式"
    echo ""

    # 执行验证
    verify_project_structure
    verify_documentation
    verify_configurations
    verify_scripts
    verify_tests

    echo ""
    # 生成统计信息
    generate_project_stats

    # 显示结果
    show_verification_results

    echo ""
    log_info "验证完成！"
    echo ""
    log_info "下一步操作建议："
    echo "1. 在有完整工具链的环境中运行完整验证："
    echo "   ./scripts/final-verification.sh"
    echo ""
    echo "2. 安装依赖并运行测试："
    echo "   cd frontend && npm install && npm test"
    echo "   cd backend && pip install -r requirements.txt && python -m pytest"
    echo ""
    echo "3. 构建和部署："
    echo "   docker-compose build"
    echo "   ./scripts/deploy.sh"
}

# 脚本入口
if [ "${1:-}" = "--help" ] || [ "${1:-}" = "-h" ]; then
    echo "卡牌对战竞技场 - 简化验证脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  --help, -h    显示帮助信息"
    echo ""
    echo "此脚本适用于没有完整工具链的环境，主要验证项目结构完整性。"
    exit 0
fi

main