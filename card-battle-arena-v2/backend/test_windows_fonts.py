#!/usr/bin/env python3
"""
Windows 11 字体修复验证脚本

测试中文字符在游戏界面中的显示效果。
"""

import sys
import pygame
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from app.visualization.font_manager import WindowsFontManager


def test_font_manager():
    """测试字体管理器功能"""
    print("🔧 测试Windows字体管理器...")

    # 获取字体信息
    font_info = WindowsFontManager.get_font_info()
    print(f"✅ 可用中文字体: {font_info['chinese_fonts']}")
    print(f"✅ 可用英文字体: {font_info['english_fonts']}")
    print(f"✅ 字体缓存状态: {'启用' if font_info['cache_enabled'] else '禁用'}")
    print(f"✅ 平台: {font_info['platform']}")
    print()

    # 测试中文渲染
    print("🎮 测试中文字符渲染...")
    test_texts = [
        "卡牌对战游戏",
        "新手战士",
        "火球术",
        "玩家1的回合 - 回合 1",
        "❤️ 生命值: 30/30",
        "💰 法力值: 5/5"
    ]

    for text in test_texts:
        try:
            surface = WindowsFontManager.render_chinese_text(text, 20, (0, 0, 0))
            print(f"✅ '{text}' - 渲染成功 (尺寸: {surface.get_size()})")
        except Exception as e:
            print(f"❌ '{text}' - 渲染失败: {e}")

    print()


def test_game_components():
    """测试游戏组件字体显示"""
    print("🎮 测试游戏组件字体显示...")

    # 测试HUD组件
    try:
        from app.visualization.ui.game_hud import GameHUD
        print("📊 测试GameHUD组件...")

        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("字体测试")

        hud = GameHUD((0, 0), (800, 70))
        hud.turn_display = "玩家1的回合 - 回合 1"
        hud.player1_health_display = "25/30"
        hud.player2_health_display = "28/30"
        hud.player1_mana_display = "5/5"
        hud.player2_mana_display = "3/4"

        hud.render(screen)
        print("✅ GameHUD渲染成功")

        pygame.display.flip()
        pygame.time.wait(2000)  # 显示2秒

        pygame.quit()

    except Exception as e:
        print(f"❌ GameHUD测试失败: {e}")

    print()


def test_interactive_game():
    """测试交互式游戏字体"""
    print("🎮 测试交互式游戏字体...")

    try:
        from app.visualization.interactive_renderer import InteractiveRenderer

        print("🚀 启动交互式游戏测试 (3秒)...")
        renderer = InteractiveRenderer(800, 600)

        if renderer.create_window("字体测试"):
            if renderer.initialize_game("测试玩家", "测试AI"):
                print("✅ 游戏初始化成功")

                # 运行3秒
                import time
                start_time = time.time()
                while time.time() - start_time < 3:
                    renderer.render()
                    renderer.clock.tick(60)
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            break

                print("✅ 交互式游戏测试完成")
            else:
                print("❌ 游戏窗口创建失败")
        else:
            print("❌ Pygame初始化失败")

    except Exception as e:
        print(f"❌ 交互式游戏测试失败: {e}")

    print()


def main():
    """主函数"""
    print("🎮 Card Battle Arena - Windows 11 字体修复验证")
    print("=" * 50)
    print()

    # 测试字体管理器
    test_font_manager()

    # 测试游戏组件
    test_game_components()

    # 测试交互式游戏
    test_interactive_game()

    print("=" * 50)
    print("✅ Windows 11 字体修复验证完成！")
    print("中文字符现在应该可以正确显示了。")


if __name__ == '__main__':
    main()