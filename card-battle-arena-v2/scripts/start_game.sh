#!/bin/bash
#
# Card Battle Arena 游戏启动脚本
#
# 使用方法:
#   ./scripts/start_game.sh [参数]
#
# 示例:
#   ./scripts/start_game.sh --mode demo
#   ./scripts/start_game.sh --mode interactive --verbose
#   ./scripts/start_game.sh --config custom.json

# 脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# 项目根目录
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 切换到项目根目录
cd "$PROJECT_ROOT"

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到Python3"
    exit 1
fi

# 检查是否安装了必要的依赖
echo "🔍 检查依赖..."
python3 -c "import pygame, numpy" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  警告：缺少游戏依赖库"
    echo "   请运行: pip install pygame numpy"
    echo "   继续启动可能会失败..."
fi

# 启动游戏
echo "🎮 启动 Card Battle Arena..."
echo "================================"

# 传递所有参数给main.py
python3 main.py "$@"

# 获取退出代码
EXIT_CODE=$?

echo "================================"
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ 游戏正常退出"
else
    echo "❌ 游戏异常退出 (代码: $EXIT_CODE)"
fi

exit $EXIT_CODE