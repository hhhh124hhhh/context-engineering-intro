#!/usr/bin/env python3
"""
游戏字体测试脚本

测试游戏组件中的中文字体显示效果。
"""

import sys
import pygame
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from app.visualization.font_manager import WindowsFontManager, render_text_safely
from app.visualization.ui.game_hud import GameHUD
from app.visualization.ui.card_component import InteractiveCard
from app.visualization.ui.hand_area import HandArea
from app.visualization.ui.battlefield import BattlefieldZone


def test_game_hud_chinese():
    """测试GameHUD中文显示"""
    print("🎮 测试GameHUD中文显示...")

    pygame.init()
    screen = pygame.display.set_mode((1200, 100))
    pygame.display.set_caption("GameHUD Font Test")

    # 创建HUD组件
    hud = GameHUD((0, 0), (1200, 80))

    # 设置中文文本
    hud.turn_display = "玩家1的回合 - 回合 1"
    hud.player1_health_display = "25/30"
    hud.player2_health_display = "28/30"
    hud.player1_mana_display = "5/5"
    hud.player2_mana_display = "3/4"

    # 渲染HUD
    hud.render(screen)

    # 保存截图
    pygame.image.save(screen, "test_hud_output.png")
    print("✅ GameHUD中文渲染成功，截图保存为 test_hud_output.png")

    pygame.quit()


def test_card_component_chinese():
    """测试卡牌组件中文显示"""
    print("🃏 测试卡牌组件中文显示...")

    pygame.init()
    screen = pygame.display.set_mode((800, 300))
    pygame.display.set_caption("Card Component Font Test")

    # 创建测试卡牌
    from app.game.cards import Card, CardType

    # 创建一张中文卡牌
    test_card = Card(
        id=1,
        name="火球术",
        cost=3,
        attack=0,
        health=0,
        card_type=CardType.SPELL,
        damage=4
    )

    # 创建卡牌组件
    card = InteractiveCard(
        card=test_card,
        position=(50, 50),
        size=(120, 160)
    )

    # 渲染卡牌
    card.render(screen)

    # 保存截图
    pygame.image.save(screen, "test_card_output.png")
    print("✅ 卡牌组件中文渲染成功，截图保存为 test_card_output.png")

    pygame.quit()


def test_hand_area_chinese():
    """测试手牌区域中文显示"""
    print("👋 测试手牌区域中文显示...")

    pygame.init()
    screen = pygame.display.set_mode((1000, 250))
    pygame.display.set_caption("Hand Area Font Test")

    # 创建手牌区域
    hand_area = HandArea((0, 50), (1000, 180))

    # 添加几张测试卡牌
    from app.game.cards import Card, CardType

    cards = [
        Card(1, "新手战士", 1, 2, 3, CardType.MINION),
        Card(2, "火球术", 3, 0, 0, CardType.SPELL, damage=4),
        Card(3, "治疗术", 2, 0, 0, CardType.SPELL, damage=-3)
    ]

    for card in cards:
        hand_area.add_card(card)

    # 渲染手牌区域
    hand_area.render(screen)

    # 保存截图
    pygame.image.save(screen, "test_hand_output.png")
    print("✅ 手牌区域中文渲染成功，截图保存为 test_hand_output.png")

    pygame.quit()


def test_battlefield_chinese():
    """测试战场区域中文显示"""
    print("⚔️ 测试战场区域中文显示...")

    pygame.init()
    screen = pygame.display.set_mode((900, 250))
    pygame.display.set_caption("Battlefield Font Test")

    # 创建战场区域
    battlefield = BattlefieldZone((50, 50), (800, 150))

    # 添加测试随从
    from app.game.cards import Card, CardType

    minion = Card(1, "石元素", 4, 2, 7, CardType.MINION, taunt=True)
    minion.attack = 2
    minion.health = 7
    minion.taunt = True

    battlefield.add_minion(minion)

    # 渲染战场
    battlefield.render(screen)

    # 保存截图
    pygame.image.save(screen, "test_battlefield_output.png")
    print("✅ 战场区域中文渲染成功，截图保存为 test_battlefield_output.png")

    pygame.quit()


def test_font_info():
    """测试字体信息"""
    print("🔍 测试字体信息...")

    font_info = WindowsFontManager.get_font_info()
    print(f"✅ 平台: {font_info['platform']}")
    print(f"✅ 可用中文字体: {font_info['chinese_fonts'][:5]}...")  # 只显示前5个
    print(f"✅ 字体缓存状态: {'启用' if font_info['cache_enabled'] else '禁用'}")
    print()


def main():
    """主函数"""
    print("🎮 Card Battle Arena - 游戏字体测试")
    print("=" * 50)
    print()

    # 测试字体信息
    test_font_info()

    # 测试各个组件的中文显示
    try:
        test_game_hud_chinese()
    except Exception as e:
        print(f"❌ GameHUD测试失败: {e}")

    try:
        test_card_component_chinese()
    except Exception as e:
        print(f"❌ 卡牌组件测试失败: {e}")

    try:
        test_hand_area_chinese()
    except Exception as e:
        print(f"❌ 手牌区域测试失败: {e}")

    try:
        test_battlefield_chinese()
    except Exception as e:
        print(f"❌ 战场区域测试失败: {e}")

    print("=" * 50)
    print("✅ 游戏字体测试完成！")
    print("所有测试截图已保存到当前目录。")


if __name__ == '__main__':
    main()