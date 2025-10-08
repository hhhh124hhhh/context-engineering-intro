#!/bin/bash

# 卡牌对战竞技场质量检查脚本
# 作者: Card Battle Arena Team
# 版本: 1.0.0

set -e  # 遇到错误时立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
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
    echo -e "${PURPLE}[CHECK]${NC} $1"
}

# 统计变量
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0

# 检查函数
check() {
    local description="$1"
    local command="$2"

    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

    log_header "$description"

    if eval "$command" > /dev/null 2>&1; then
        log_success "✓ $description"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
        return 0
    else
        log_error "✗ $description"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
        return 1
    fi
}

# 显示检查结果
show_results() {
    echo ""
    log_info "质量检查完成"
    echo "===================="
    echo -e "总检查数: ${BLUE}$TOTAL_CHECKS${NC}"
    echo -e "通过检查: ${GREEN}$PASSED_CHECKS${NC}"
    echo -e "失败检查: ${RED}$FAILED_CHECKS${NC}"

    if [ $FAILED_CHECKS -eq 0 ]; then
        echo ""
        log_success "🎉 所有质量检查都通过了！"
        exit 0
    else
        echo ""
        log_error "❌ 有 $FAILED_CHECKS 项检查失败"
        exit 1
    fi
}

# 检查代码格式
check_code_format() {
    log_info "检查代码格式..."

    # 检查 Python 代码格式
    if command -v black &> /dev/null; then
        check "Python 代码格式 (Black)" "black --check backend/"
    else
        log_warning "Black 未安装，跳过 Python 格式检查"
    fi

    # 检查 TypeScript/JavaScript 代码格式
    if command -v prettier &> /dev/null; then
        check "前端代码格式 (Prettier)" "prettier --check frontend/"
    else
        log_warning "Prettier 未安装，跳过前端格式检查"
    fi
}

# 检查代码质量
check_code_quality() {
    log_info "检查代码质量..."

    # Python 代码质量检查
    if command -v ruff &> /dev/null; then
        check "Python 代码质量 (Ruff)" "ruff check backend/"
    else
        log_warning "Ruff 未安装，跳过 Python 质量检查"
    fi

    # TypeScript 类型检查
    check "TypeScript 类型检查" "cd frontend && npm run type-check"

    # ESLint 检查
    check "JavaScript 代码质量 (ESLint)" "cd frontend && npm run lint"
}

# 运行测试
run_tests() {
    log_info "运行测试套件..."

    # 后端测试
    check "后端单元测试" "cd backend && python run_tests.py test"

    # 前端测试
    check "前端单元测试" "cd frontend && npm test -- --coverage --watchAll=false"

    # 集成测试
    check "集成测试" "cd backend && python run_tests.py integration"
}

# 检查安全性
check_security() {
    log_info "检查安全性..."

    # 检查依赖漏洞
    check "前端依赖安全检查" "cd frontend && npm audit --audit-level moderate"

    # Python 依赖安全检查
    if command -v safety &> /dev/null; then
        check "Python 依赖安全检查 (Safety)" "cd backend && safety check"
    else
        log_warning "Safety 未安装，跳过 Python 安全检查"
    fi

    # 检查敏感信息泄露
    check "敏感信息检查" "! grep -r 'password\\|secret\\|key' --include='*.py' --include='*.ts' --include='*.tsx' --exclude-dir=node_modules --exclude-dir=.git backend/ frontend/ | grep -v 'example\\|test\\|mock' || true"
}

# 检查性能
check_performance() {
    log_info "检查性能..."

    # 检查包大小
    if [ -d "frontend/dist" ]; then
        check "前端包大小检查" "du -sh frontend/dist/ | awk '{print \$1}' | grep -E '^[0-9.]+M$|^[0-9.]+K$'"
    fi

    # 检查未使用的依赖
    check "未使用依赖检查" "cd frontend && npx depcheck || true"
}

# 检查文档
check_documentation() {
    log_info "检查文档..."

    # 检查 README 存在
    check "README 文档存在" "test -f README.md"

    # 检查 API 文档生成
    check "API 文档配置" "test -f backend/app/main.py && grep -q 'docs_url' backend/app/main.py"

    # 检查组件文档
    check "组件文档覆盖" "find frontend/src/components -name '*.tsx' -exec grep -l '\/\*\*' {} \; | wc -l | grep -qE '^[1-9]+$' || true"
}

# 检查构建
check_build() {
    log_info "检查构建..."

    # 前端构建
    check "前端构建" "cd frontend && npm run build"

    # 检查构建产物
    check "前端构建产物" "test -d frontend/dist && test -f frontend/dist/index.html"

    # 后端打包检查
    check "后端依赖打包" "cd backend && pip freeze > requirements.txt && test -s requirements.txt"
}

# 检查环境配置
check_environment() {
    log_info "检查环境配置..."

    # 检查环境变量文件
    check "环境变量模板" "test -f .env.prod.example"

    # 检查 Docker 配置
    check "Docker Compose 配置" "test -f docker-compose.yml && docker-compose config > /dev/null"

    check "生产 Docker 配置" "test -f docker-compose.prod.yml && docker-compose -f docker-compose.prod.yml config > /dev/null"
}

# 检查版本管理
check_versioning() {
    log_info "检查版本管理..."

    # 检查版本标签
    check "版本标签一致性" "grep -q 'version.*1.0.0' frontend/package.json && grep -q 'version.*1.0.0' backend/pyproject.toml 2>/dev/null || grep -q 'version.*1.0.0' backend/setup.py"

    # 检查 Git 状态
    check "Git 工作区干净" "git diff --quiet && git diff --cached --quiet"
}

# 检查许可证
check_licenses() {
    log_info "检查许可证..."

    # 检查许可证文件
    check "许可证文件存在" "test -f LICENSE"

    # 检查前端依赖许可证
    check "前端依赖许可证" "cd frontend && npx license-checker --summary --excludePrivatePackages | grep -E '(MIT|Apache|BSD|ISC)' || true"
}

# 生成质量报告
generate_report() {
    log_info "生成质量报告..."

    report_dir="quality-reports/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$report_dir"

    # 生成测试覆盖率报告
    cd backend && python run_tests.py coverage > "$report_dir/backend-coverage.txt" 2>&1 || true
    cd ../frontend && npm run test:coverage > "$report_dir/frontend-coverage.txt" 2>&1 || true
    cd ..

    # 生成代码质量报告
    if command -v ruff &> /dev/null; then
        cd backend && ruff check . --output-format=json > "$report_dir/backend-quality.json" 2>/dev/null || true
        cd ..
    fi

    # 生成依赖报告
    cd frontend && npm list --depth=0 > "$report_dir/dependencies.txt" 2>&1 || true
    cd ..

    log_success "质量报告生成完成: $report_dir"
}

# 主函数
main() {
    echo "🔍 卡牌对战竞技场质量检查"
    echo "=========================="
    echo ""

    # 基础检查
    check_environment
    check_versioning
    check_licenses

    # 代码质量检查
    check_code_format
    check_code_quality

    # 测试检查
    run_tests

    # 安全性检查
    check_security

    # 性能检查
    check_performance

    # 文档检查
    check_documentation

    # 构建检查
    check_build

    # 生成报告
    generate_report

    # 显示结果
    show_results
}

# 脚本入口
if [ "${1:-}" = "--help" ] || [ "${1:-}" = "-h" ]; then
    echo "卡牌对战竞技场质量检查脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  --help, -h    显示帮助信息"
    echo "  --report      只生成报告"
    echo "  --code        只检查代码质量"
    echo "  --security    只检查安全性"
    echo "  --tests       只运行测试"
    echo ""
    echo "示例:"
    echo "  $0           # 运行所有检查"
    echo "  $0 --code    # 只检查代码质量"
    exit 0
fi

# 检查特定模块
case "${1:-}" in
    "--report")
        generate_report
        exit 0
        ;;
    "--code")
        check_code_format
        check_code_quality
        show_results
        exit 0
        ;;
    "--security")
        check_security
        show_results
        exit 0
        ;;
    "--tests")
        run_tests
        show_results
        exit 0
        ;;
    *)
        main
        ;;
esac