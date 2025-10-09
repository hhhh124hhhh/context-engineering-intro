#!/usr/bin/env python3
"""
Card Battle Arena - 卡牌对战竞技场
统一游戏入口脚本

这是游戏的主入口点，提供统一的命令行界面来启动不同的游戏模式。
遵循TDD方法开发，确保代码质量和可靠性。
"""

import sys
import os
import argparse
from pathlib import Path
from typing import Optional

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from cli.parser import main_parser, print_help
from cli.launcher import GameLauncher
from cli.exceptions import (
    GameLauncherError,
    InvalidGameModeError,
    MissingDependencyError,
    PygameInitializationError,
    GameStartupError
)
from config.settings import GameSettings, load_config
from config.game_modes import GameMode


def check_dependencies():
    """
    检查游戏运行所需的依赖

    Raises:
        ImportError: 如果缺少必需的依赖
    """
    required_modules = {
        'pygame': 'Pygame游戏库',
        'random': 'Python随机模块'
    }

    missing_modules = []
    for module_name, description in required_modules.items():
        try:
            __import__(module_name)
        except ImportError:
            missing_modules.append(f"{description} ({module_name})")

    if missing_modules:
        error_msg = "缺少以下必需的依赖:\n"
        error_msg += "\n".join(f"  - {module}" for module in missing_modules)
        error_msg += "\n\n请运行以下命令安装依赖:\n"
        error_msg += "  pip install pygame numpy"

        print("❌ 依赖检查失败")
        print(error_msg)
        raise ImportError(error_msg)


def setup_environment(args: argparse.Namespace) -> GameSettings:
    """
    设置游戏环境

    Args:
        args (argparse.Namespace): 命令行参数

    Returns:
        GameSettings: 游戏设置对象
    """
    print("🔧 正在设置游戏环境...")

    # 加载配置
    settings = GameSettings()

    # 如果指定了配置文件，加载它
    if args.config:
        try:
            settings.load_from_file(args.config)
            print(f"✓ 已加载配置文件: {args.config}")
        except Exception as e:
            print(f"⚠️  加载配置文件失败，使用默认配置: {e}")

    # 应用命令行参数覆盖配置
    overrides = {}

    if args.window_size:
        from cli.parser import parse_window_size
        try:
            width, height = parse_window_size(args.window_size)
            overrides['window_width'] = width
            overrides['window_height'] = height
            print(f"✓ 设置窗口大小: {width}x{height}")
        except ValueError as e:
            print(f"❌ 窗口大小设置错误: {e}")
            sys.exit(1)

    if args.fullscreen:
        overrides['fullscreen'] = True
        print("✓ 启用全屏模式")

    if args.ai_thinking_time:
        overrides['ai_thinking_time'] = args.ai_thinking_time
        print(f"✓ 设置AI思考时间: {args.ai_thinking_time}秒")

    if args.ai_difficulty:
        overrides['ai_difficulty'] = args.ai_difficulty
        print(f"✓ 设置AI难度: {args.ai_difficulty}")

    if args.max_turns:
        overrides['max_turns'] = args.max_turns
        print(f"✓ 设置最大回合数: {args.max_turns}")

    if args.no_sound:
        overrides['sound_enabled'] = False
        print("✓ 禁用声音")

    if args.verbose:
        overrides['verbose_logging'] = True
        print("✓ 启用详细日志")

    if args.debug:
        overrides['debug_mode'] = True
        overrides['show_fps'] = True
        print("✓ 启用调试模式")

    # 应用覆盖设置
    if overrides:
        settings.update_from_dict(overrides)

    print("✓ 游戏环境设置完成")
    return settings


def print_welcome():
    """打印欢迎信息"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                🎮 Card Battle Arena 🎮                       ║
║                     卡牌对战竞技场                           ║
╠══════════════════════════════════════════════════════════════╣
║  策略卡牌对战游戏，与AI或朋友进行激烈对战！                   ║
║  支持多种游戏模式：AI对战、交互式、演示模式                    ║
╚══════════════════════════════════════════════════════════════╝
""")


def print_goodbye():
    """打印告别信息"""
    print("\n感谢游玩 Card Battle Arena!")
    print("再见! 👋")


def handle_exception(e: Exception, args: argparse.Namespace):
    """
    统一异常处理

    Args:
        e (Exception): 异常对象
        args (argparse.Namespace): 命令行参数
    """
    if args.verbose or args.debug:
        import traceback
        print(f"\n❌ 发生异常: {type(e).__name__}")
        print(f"错误信息: {str(e)}")
        print("\n详细错误信息:")
        traceback.print_exc()
    else:
        print(f"\n❌ 游戏启动失败: {str(e)}")
        print("使用 --verbose 获取更多错误信息")

    # 提供解决建议
    if isinstance(e, MissingDependencyError):
        print("\n💡 解决建议:")
        print("  请确保已安装所有必需的依赖库")
        print("  运行: pip install pygame numpy")
    elif isinstance(e, PygameInitializationError):
        print("\n💡 解决建议:")
        print("  请检查显示驱动程序是否正常工作")
        print("  尝试更新显卡驱动程序")
    elif isinstance(e, InvalidGameModeError):
        print("\n💡 解决建议:")
        print("  使用 --help 查看可用的游戏模式")
        print("  使用 --list-modes 查看详细模式信息")
    elif isinstance(e, GameStartupError):
        print("\n💡 解决建议:")
        print("  检查游戏文件是否完整")
        print("  尝试重新安装游戏")


def main(argv: Optional[list] = None) -> int:
    """
    主函数

    Args:
        argv (Optional[list]): 命令行参数列表

    Returns:
        int: 退出代码，0表示成功
    """
    try:
        # 解析命令行参数
        args = main_parser(argv)

        # 特殊参数处理
        if hasattr(args, 'list_modes') and args.list_modes:
            launcher = GameLauncher()
            launcher.list_available_modes()
            return 0

        # 打印欢迎信息（除非是静默模式）
        if not (hasattr(args, 'quiet') and args.quiet):
            print_welcome()

        # 设置游戏环境
        settings = setup_environment(args)

        # 检查依赖（详细模式下显示检查过程）
        if args.verbose:
            print("🔍 正在检查游戏依赖...")
        check_dependencies()
        if args.verbose:
            print("✓ 依赖检查通过")

        # 创建游戏启动器
        launcher = GameLauncher(settings)

        # 启动游戏
        success = launcher.launch(args.mode)

        if success:
            if not (hasattr(args, 'quiet') and args.quiet):
                print_goodbye()
            return 0
        else:
            print("❌ 游戏启动失败")
            return 1

    except KeyboardInterrupt:
        print("\n\n⚠️  游戏被用户中断")
        return 130
    except SystemExit as e:
        return e.code
    except Exception as e:
        args = main_parser(argv) if argv else main_parser()
        handle_exception(e, args)
        return 1


def entry_point():
    """命令行入口点"""
    import sys
    sys.exit(main(sys.argv[1:]))


if __name__ == '__main__':
    # 检查是否直接运行
    if len(sys.argv) == 1:
        # 无参数时显示帮助
        print_welcome()
        print_help()
    else:
        # 有参数时正常启动
        entry_point()