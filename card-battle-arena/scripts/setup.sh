#!/bin/bash

# 卡牌对战竞技场 - 环境设置脚本
# 作者: Card Battle Arena Team
# 版本: 1.0.0

set -e  # 遇到错误时立即退出

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
    echo -e "${PURPLE}[SETUP]${NC} $1"
}

# 检查命令是否存在
check_command() {
    if command -v "$1" >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# 检查并安装工具
install_tool() {
    local tool_name="$1"
    local install_cmd="$2"
    local check_cmd="$3"

    log_header "检查 $tool_name"

    if check_command "$check_cmd"; then
        log_success "$tool_name 已安装"
    else
        log_warning "$tool_name 未安装，尝试安装..."
        if eval "$install_cmd"; then
            log_success "$tool_name 安装成功"
        else
            log_error "$tool_name 安装失败，请手动安装"
            return 1
        fi
    fi
}

# 检查系统要求
check_system_requirements() {
    log_header "检查系统要求"

    # 检查操作系统
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        log_success "操作系统: Linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        log_success "操作系统: macOS"
    else
        log_warning "操作系统: $OSTYPE (可能需要额外配置)"
    fi

    # 检查可用内存
    if check_command "free"; then
        total_mem=$(free -h | awk '/^Mem:/ {print $2}')
        log_info "可用内存: $total_mem"
    fi

    # 检查磁盘空间
    available_space=$(df -h . | awk 'NR==2 {print $4}')
    log_info "可用磁盘空间: $available_space"

    # 检查网络连接
    if ping -c 1 google.com >/dev/null 2>&1; then
        log_success "网络连接正常"
    else
        log_warning "网络连接异常，可能影响依赖安装"
    fi
}

# 安装基础工具
install_basic_tools() {
    log_header "安装基础工具"

    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Ubuntu/Debian
        if check_command "apt-get"; then
            sudo apt-get update
            sudo apt-get install -y curl wget git build-essential
        # CentOS/RHEL
        elif check_command "yum"; then
            sudo yum update -y
            sudo yum groupinstall -y "Development Tools"
            sudo yum install -y curl wget git
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if check_command "brew"; then
            brew update
            brew install curl wget git
        else
            log_warning "建议安装Homebrew: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        fi
    fi
}

# 安装Node.js
install_nodejs() {
    install_tool "Node.js" \
        "curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash - && sudo apt-get install -y nodejs" \
        "node"

    if check_command "node"; then
        node_version=$(node --version)
        log_success "Node.js 版本: $node_version"
    fi

    install_tool "npm" \
        "sudo apt-get install -y npm" \
        "npm"

    if check_command "npm"; then
        npm_version=$(npm --version)
        log_success "npm 版本: $npm_version"
    fi
}

# 安装Python
install_python() {
    install_tool "Python 3" \
        "sudo apt-get install -y python3 python3-pip python3-venv" \
        "python3"

    if check_command "python3"; then
        python_version=$(python3 --version)
        log_success "Python 版本: $python_version"
    fi

    if check_command "pip3"; then
        pip_version=$(pip3 --version)
        log_success "pip 版本: $pip_version"
    fi
}

# 安装Docker
install_docker() {
    install_tool "Docker" \
        "curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh" \
        "docker"

    if check_command "docker"; then
        docker_version=$(docker --version)
        log_success "Docker 版本: $docker_version"

        # 将用户添加到docker组
        if ! groups $USER | grep -q docker; then
            log_info "将用户添加到docker组..."
            sudo usermod -aG docker $USER
            log_warning "请重新登录以使docker组生效"
        fi
    fi

    install_tool "Docker Compose" \
        "sudo curl -L \"https://github.com/docker/compose/releases/latest/download/docker-compose-\$(uname -s)-\$(uname -m)\" -o /usr/local/bin/docker-compose && sudo chmod +x /usr/local/bin/docker-compose" \
        "docker-compose"

    if check_command "docker-compose"; then
        compose_version=$(docker-compose --version)
        log_success "Docker Compose 版本: $compose_version"
    fi
}

# 设置项目环境
setup_project_environment() {
    log_header "设置项目环境"

    # 创建项目根目录
    if [ ! -f "README.md" ]; then
        log_error "请在项目根目录运行此脚本"
        exit 1
    fi

    # 复制环境变量文件
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            log_info "创建 .env 文件..."
            cp .env.example .env
            log_success ".env 文件创建完成"
        else
            log_warning ".env.example 文件不存在"
        fi
    else
        log_info ".env 文件已存在"
    fi

    # 创建日志目录
    if [ ! -d "logs" ]; then
        mkdir -p logs
        log_success "日志目录创建完成"
    fi

    # 创建上传目录
    if [ ! -d "uploads" ]; then
        mkdir -p uploads
        log_success "上传目录创建完成"
    fi
}

# 设置后端环境
setup_backend() {
    log_header "设置后端环境"

    cd backend

    # 创建Python虚拟环境
    if [ ! -d "venv" ]; then
        log_info "创建Python虚拟环境..."
        python3 -m venv venv
        log_success "虚拟环境创建完成"
    else
        log_info "虚拟环境已存在"
    fi

    # 激活虚拟环境
    log_info "激活虚拟环境..."
    source venv/bin/activate

    # 升级pip
    log_info "升级pip..."
    pip install --upgrade pip

    # 安装依赖
    if [ -f "requirements.txt" ]; then
        log_info "安装Python依赖..."
        pip install -r requirements.txt
        log_success "Python依赖安装完成"
    else
        log_warning "requirements.txt 文件不存在"
    fi

    # 安装开发依赖
    if [ -f "requirements-dev.txt" ]; then
        log_info "安装开发依赖..."
        pip install -r requirements-dev.txt
        log_success "开发依赖安装完成"
    fi

    cd ..
}

# 设置前端环境
setup_frontend() {
    log_header "设置前端环境"

    cd frontend

    # 安装依赖
    if [ -f "package.json" ]; then
        log_info "安装前端依赖..."
        npm install
        log_success "前端依赖安装完成"
    else
        log_warning "package.json 文件不存在"
    fi

    cd ..
}

# 初始化数据库
init_database() {
    log_header "初始化数据库"

    # 启动数据库服务
    log_info "启动数据库服务..."
    docker-compose up -d postgres redis

    # 等待数据库启动
    log_info "等待数据库启动..."
    sleep 10

    # 运行数据库迁移
    cd backend
    if [ -d "venv" ]; then
        source venv/bin/activate

        # 检查是否有迁移文件
        if [ -d "migrations" ]; then
            log_info "运行数据库迁移..."
            alembic upgrade head
            log_success "数据库迁移完成"
        fi

        # 初始化基础数据
        if [ -f "../scripts/init-data.py" ]; then
            log_info "初始化基础数据..."
            python ../scripts/init-data.py
            log_success "基础数据初始化完成"
        fi
    fi
    cd ..
}

# 构建Docker镜像
build_docker_images() {
    log_header "构建Docker镜像"

    # 构建开发环境镜像
    log_info "构建开发环境镜像..."
    docker-compose build

    # 构建生产环境镜像
    if [ -f "docker-compose.prod.yml" ]; then
        log_info "构建生产环境镜像..."
        docker-compose -f docker-compose.prod.yml build
    fi

    log_success "Docker镜像构建完成"
}

# 运行测试
run_tests() {
    log_header "运行测试"

    # 后端测试
    cd backend
    if [ -d "venv" ] && [ -d "tests" ]; then
        source venv/bin/activate

        if check_command "pytest"; then
            log_info "运行后端测试..."
            pytest tests/ -v
            log_success "后端测试通过"
        else
            log_warning "pytest未安装，跳过后端测试"
        fi
    fi
    cd ..

    # 前端测试
    cd frontend
    if [ -f "package.json" ]; then
        # 检查是否有测试脚本
        if npm run test --if-present 2>/dev/null; then
            log_info "运行前端测试..."
            npm test -- --watchAll=false
            log_success "前端测试通过"
        else
            log_warning "前端测试脚本不存在，跳过前端测试"
        fi
    fi
    cd ..
}

# 验证安装
verify_installation() {
    log_header "验证安装"

    local errors=0

    # 检查基础工具
    for cmd in git node npm python3 pip docker docker-compose; do
        if check_command "$cmd"; then
            log_success "$cmd 已安装"
        else
            log_error "$cmd 未安装"
            ((errors++))
        fi
    done

    # 检查项目文件
    local required_files=(
        ".env"
        "frontend/node_modules"
        "backend/venv"
        "logs"
        "uploads"
    )

    for file in "${required_files[@]}"; do
        if [ -e "$file" ]; then
            log_success "$file 存在"
        else
            log_error "$file 不存在"
            ((errors++))
        fi
    done

    if [ $errors -eq 0 ]; then
        log_success "安装验证通过！"
        return 0
    else
        log_error "安装验证失败，发现 $errors 个问题"
        return 1
    fi
}

# 显示使用说明
show_usage() {
    log_header "安装完成！"
    echo ""
    log_info "项目已成功设置完成！"
    echo ""
    log_info "使用方法："
    echo "  启动开发环境:     ./scripts/dev-start.sh"
    echo "  停止开发环境:     ./scripts/dev-stop.sh"
    echo "  运行质量检查:     ./scripts/quality-check.sh"
    echo "  部署到生产环境:    ./scripts/deploy.sh"
    echo ""
    log_info "开发环境访问地址："
    echo "  前端应用:         http://localhost:3000"
    echo "  后端API:          http://localhost:8000"
    echo "  API文档:          http://localhost:8000/docs"
    echo ""
    log_info "如需帮助，请查看 DEVELOPMENT.md 文档"
}

# 主函数
main() {
    echo "🚀 卡牌对战竞技场 - 环境设置"
    echo "============================"
    echo ""

    # 解析命令行参数
    local skip_docker=false
    local skip_tests=false

    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-docker)
                skip_docker=true
                shift
                ;;
            --skip-tests)
                skip_tests=true
                shift
                ;;
            --help|-h)
                echo "用法: $0 [选项]"
                echo ""
                echo "选项:"
                echo "  --skip-docker    跳过Docker安装和镜像构建"
                echo "  --skip-tests     跳过测试运行"
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

    # 执行安装步骤
    check_system_requirements
    install_basic_tools
    install_nodejs
    install_python

    if [ "$skip_docker" = false ]; then
        install_docker
    fi

    setup_project_environment
    setup_backend
    setup_frontend

    if [ "$skip_docker" = false ]; then
        init_database
        build_docker_images
    fi

    if [ "$skip_tests" = false ]; then
        run_tests
    fi

    verify_installation
    show_usage
}

# 脚本入口
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi