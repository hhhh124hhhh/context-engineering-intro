"""
命令行参数解析器

定义统一的命令行接口，支持多种游戏模式和配置选项。
"""

import argparse
import sys
from typing import List, Optional


def create_parser() -> argparse.ArgumentParser:
    """
    创建命令行参数解析器

    Returns:
        argparse.ArgumentParser: 配置好的参数解析器
    """
    parser = argparse.ArgumentParser(
        prog='card-battle-arena',
        description='🎮 Card Battle Arena - 策略卡牌对战游戏',
        epilog='''
使用示例:
  %(prog)s                           # 默认AI对战模式
  %(prog)s --mode ai                 # AI对战模式
  %(prog)s --mode interactive        # 交互式模式
  %(prog)s --mode demo               # 演示模式
  %(prog)s --config custom.json      # 使用自定义配置
  %(prog)s --verbose                 # 显示详细输出
        '''.strip(),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # 游戏模式参数
    parser.add_argument(
        '--mode', '-m',
        choices=['ai-vs-player', 'ai', 'interactive', 'demo'],
        default='ai-vs-player',
        help='选择游戏模式 (默认: ai-vs-player)'
    )

    # 配置文件参数
    parser.add_argument(
        '--config', '-c',
        type=str,
        metavar='FILE',
        help='指定配置文件路径 (JSON格式)'
    )

    # 详细输出参数
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='启用详细输出模式'
    )

    # 版本信息
    parser.add_argument(
        '--version',
        action='version',
        version='Card Battle Arena 1.0.0'
    )

    # 调试参数
    parser.add_argument(
        '--debug',
        action='store_true',
        help='启用调试模式'
    )

    # 窗口设置参数
    parser.add_argument(
        '--fullscreen',
        action='store_true',
        help='全屏模式'
    )

    parser.add_argument(
        '--window-size',
        type=str,
        metavar='WIDTHxHEIGHT',
        help='设置窗口大小 (例如: 1920x1080)'
    )

    # AI设置参数
    parser.add_argument(
        '--ai-thinking-time',
        type=float,
        metavar='SECONDS',
        help='AI思考时间 (秒)'
    )

    parser.add_argument(
        '--ai-difficulty',
        choices=['easy', 'normal', 'hard'],
        default='normal',
        help='AI难度级别 (默认: normal)'
    )

    # 游戏设置参数
    parser.add_argument(
        '--max-turns',
        type=int,
        metavar='NUMBER',
        help='最大回合数'
    )

    parser.add_argument(
        '--no-sound',
        action='store_true',
        help='禁用声音'
    )

    return parser


def parse_window_size(window_size_str: str) -> tuple[int, int]:
    """
    解析窗口大小字符串

    Args:
        window_size_str (str): 窗口大小字符串 (例如: "1920x1080")

    Returns:
        tuple[int, int]: (宽度, 高度) 元组

    Raises:
        ValueError: 如果格式不正确
    """
    try:
        width, height = map(int, window_size_str.lower().split('x'))
        if width <= 0 or height <= 0:
            raise ValueError("窗口尺寸必须为正数")
        return width, height
    except (ValueError, AttributeError) as e:
        raise ValueError(f"无效的窗口大小格式: {window_size_str}。请使用 WIDTHxHEIGHT 格式，例如: 1920x1080") from e


def validate_arguments(args: argparse.Namespace) -> List[str]:
    """
    验证命令行参数

    Args:
        args (argparse.Namespace): 解析后的参数

    Returns:
        List[str]: 错误信息列表，空列表表示验证通过
    """
    errors = []

    # 验证窗口大小
    if args.window_size:
        try:
            parse_window_size(args.window_size)
        except ValueError as e:
            errors.append(str(e))

    # 验证AI思考时间
    if args.ai_thinking_time is not None:
        if args.ai_thinking_time <= 0:
            errors.append("AI思考时间必须大于0秒")

    # 验证最大回合数
    if args.max_turns is not None:
        if args.max_turns <= 0:
            errors.append("最大回合数必须大于0")

    # 验证配置文件
    if args.config:
        import os
        if not os.path.exists(args.config):
            errors.append(f"配置文件不存在: {args.config}")

    return errors


def print_help() -> None:
    """打印帮助信息"""
    parser = create_parser()
    parser.print_help()


def print_version() -> None:
    """打印版本信息"""
    print("Card Battle Arena 1.0.0")


def print_available_modes() -> None:
    """打印可用的游戏模式"""
    modes = [
        ("ai-vs-player", "AI对战模式 - 与AI进行对战"),
        ("ai", "简化AI模式 - 快速AI对战"),
        ("interactive", "交互式模式 - 手动操作"),
        ("demo", "演示模式 - 展示游戏功能")
    ]

    print("可用的游戏模式:")
    print("-" * 40)
    for mode_id, description in modes:
        print(f"  {mode_id:15} - {description}")


def main_parser(args: Optional[List[str]] = None) -> argparse.Namespace:
    """
    主解析函数

    Args:
        args (Optional[List[str]]): 命令行参数列表，None表示使用sys.argv

    Returns:
        argparse.Namespace: 解析后的参数

    Raises:
        SystemExit: 如果参数解析失败
    """
    parser = create_parser()

    if args is None:
        args = sys.argv[1:]

    parsed_args = parser.parse_args(args)

    # 验证参数
    errors = validate_arguments(parsed_args)
    if errors:
        print("参数错误:")
        for error in errors:
            print(f"  - {error}")
        parser.print_help()
        sys.exit(1)

    return parsed_args


if __name__ == '__main__':
    # 如果直接运行此脚本，显示帮助信息
    if len(sys.argv) == 1:
        print_help()
    else:
        try:
            args = main_parser()
            print("参数解析成功:")
            print(f"  模式: {args.mode}")
            print(f"  配置文件: {args.config}")
            print(f"  详细输出: {args.verbose}")
        except SystemExit:
            pass