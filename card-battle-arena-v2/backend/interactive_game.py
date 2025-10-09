#!/usr/bin/env python3
"""
卡牌对战竞技场 V2 - 交互式游戏

真正的可玩卡牌游戏，支持鼠标点击和拖拽操作。
"""

import sys
import time
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from app.visualization.improved_interactive_renderer import ImprovedInteractiveRenderer as InteractiveRenderer
from app.visualization.window_manager import WindowConfig


def main():
    """主函数"""
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║                🎮 卡牌对战竞技场 V2 🎮                       ║")
    print("║                    交互式游戏模式                            ║")
    print("╠══════════════════════════════════════════════════════════════╣")
    print("║ 操作说明:                                                   ║")
    print("║ • 鼠标左键点击: 选择/取消选择卡牌                           ║")
    print("║ • 鼠标拖拽: 将手牌拖拽到战场出牌                           ║")
    print("║ • 空格键: 结束回合                                         ║")
    print("║ • ESC键: 取消选择                                         ║")
    print("║ • M键: 显示游戏菜单                                       ║")
    print("║ • 数字键1-7: 快速执行对应操作                              ║")
    print("║ • 关闭窗口: 退出游戏                                       ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()

    # 从环境变量获取窗口设置
    import os
    width = int(os.environ.get('WINDOW_WIDTH', 1200))
    height = int(os.environ.get('WINDOW_HEIGHT', 800))
    fullscreen = os.environ.get('FULLSCREEN', 'false').lower() == 'true'

    try:
        # 创建窗口配置
        window_config = WindowConfig(width=width, height=height, fullscreen=fullscreen)

        # 创建交互式渲染器
        renderer = InteractiveRenderer(width=width, height=height, window_config=window_config)

        # 初始化游戏
        if not renderer.initialize_game("玩家", "AI电脑"):
            print("❌ 游戏初始化失败")
            return 1

        print(f"✅ 游戏初始化成功 (窗口: {width}x{height})")
        print("🎮 开始游戏...")
        print()

        # 运行游戏
        exit_code = renderer.run()

        if exit_code == 0:
            print("\n✅ 游戏正常退出")
        else:
            print(f"\n❌ 游戏异常退出 (代码: {exit_code})")

        return exit_code

    except KeyboardInterrupt:
        print("\n\n⚠️  游戏被用户中断")
        return 130
    except Exception as e:
        print(f"\n❌ 游戏运行时发生错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())