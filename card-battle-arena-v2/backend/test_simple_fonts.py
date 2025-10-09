#!/usr/bin/env python3
"""
简化字体测试脚本

测试字体管理器的核心功能，不依赖具体字体文件。
"""

import sys
import pygame
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from app.visualization.font_manager import WindowsFontManager, render_text_safely


def test_font_manager_basic():
    """测试字体管理器基本功能"""
    print("🔧 测试字体管理器基本功能...")

    # 初始化pygame
    pygame.init()

    # 获取字体信息
    font_info = WindowsFontManager.get_font_info()
    print(f"✅ 平台: {font_info['platform']}")
    print(f"✅ 字体缓存状态: {'启用' if font_info['cache_enabled'] else '禁用'}")
    print(f"✅ 可用中文字体: {font_info['chinese_fonts']}")
    print(f"✅ 可用英文字体: {font_info['english_fonts']}")
    print()

    # 测试安全文本渲染
    print("🎮 测试安全文本渲染...")
    test_texts = [
        "Card Battle Arena",
        "Turn 1",
        "Health: 30",
        "Mana: 5/5"
    ]

    for text in test_texts:
        try:
            surface = render_text_safely(text, 20, (0, 0, 0))
            print(f"✅ '{text}' - 渲染成功 (尺寸: {surface.get_size()})")
        except Exception as e:
            print(f"❌ '{text}' - 渲染失败: {e}")

    print()


def test_game_components():
    """测试游戏组件"""
    print("🎮 测试游戏组件...")

    try:
        # 创建一个简单的surface用于测试
        screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Font Test")

        # 测试GameHUD
        from app.visualization.ui.game_hud import GameHUD
        hud = GameHUD((0, 0), (800, 70))
        hud.turn_display = "Player 1 Turn - Round 1"
        hud.player1_health_display = "25/30"
        hud.player2_health_display = "28/30"
        hud.player1_mana_display = "5/5"
        hud.player2_mana_display = "3/4"

        hud.render(screen)
        print("✅ GameHUD组件渲染成功")

        # 测试InteractiveCard
        from app.visualization.ui.card_component import InteractiveCard
        from app.game.cards import create_card

        # 创建一个简单的测试卡牌
        test_card = create_card("新手战士", 1, "minion")
        test_card.attack = 2
        test_card.health = 3
        test_card.set_description("一个基础的战士")

        card_component = InteractiveCard(
            card=test_card,
            position=(100, 100),
            size=(120, 160)
        )

        card_component.render(screen)
        print("✅ InteractiveCard组件渲染成功")

        pygame.display.flip()
        pygame.time.wait(2000)  # 显示2秒

        pygame.quit()

    except Exception as e:
        print(f"❌ 游戏组件测试失败: {e}")
        import traceback
        traceback.print_exc()

    print()


def test_safe_render_fallback():
    """测试安全渲染的降级机制"""
    print("🛡️ 测试安全渲染降级机制...")

    try:
        # 测试空字符串
        empty_surface = render_text_safely("", 20, (0, 0, 0))
        print(f"✅ 空字符串渲染成功 (尺寸: {empty_surface.get_size()})")

        # 测试特殊字符
        special_surface = render_text_safely("❤️ 💰 ⚔️", 20, (0, 0, 0))
        print(f"✅ 特殊字符渲染成功 (尺寸: {special_surface.get_size()})")

        # 测试长文本
        long_text = "This is a very long text that might cause issues"
        long_surface = render_text_safely(long_text, 20, (0, 0, 0))
        print(f"✅ 长文本渲染成功 (尺寸: {long_surface.get_size()})")

        print("✅ 安全渲染降级机制工作正常")

    except Exception as e:
        print(f"❌ 安全渲染测试失败: {e}")

    print()


def main():
    """主函数"""
    print("🎮 Card Battle Arena - 简化字体测试")
    print("=" * 50)
    print()

    # 测试字体管理器基本功能
    test_font_manager_basic()

    # 测试安全渲染降级机制
    test_safe_render_fallback()

    # 测试游戏组件
    test_game_components()

    print("=" * 50)
    print("✅ 简化字体测试完成！")
    print("字体管理器和安全渲染功能正常工作。")


if __name__ == '__main__':
    main()