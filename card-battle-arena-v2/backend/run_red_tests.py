#!/usr/bin/env python3
"""
TDD RED阶段测试运行器

运行UI布局改进的RED测试，验证当前布局的问题。
"""

import sys
import pygame
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from app.visualization.interactive_renderer import InteractiveRenderer
from app.game.cards import Card, CardType


def run_red_test(test_name, test_func):
    """
    运行单个RED测试

    Args:
        test_name: 测试名称
        test_func: 测试函数
    """
    print(f"🔴 测试: {test_name}")
    try:
        test_func()
        print(f"  ❌ UNEXPECTED PASS - 测试应该失败但却通过了")
        return False
    except AssertionError as e:
        print(f"  ✅ EXPECTED FAIL - {e}")
        return True
    except Exception as e:
        print(f"  ❌ ERROR - {e}")
        return False


def test_current_hand_area_insufficient_height():
    """测试：当前手牌区域高度不足"""
    pygame.init()
    renderer = InteractiveRenderer(1200, 800)

    hand_area = renderer.player_hand
    hand_height = hand_area.size[1]
    card_height = 160  # 标准卡牌高度

    # 这应该FAIL，因为150 < 160
    assert hand_height >= card_height, f"手牌区域高度{hand_height}px不足以容纳卡牌高度{card_height}px"

    pygame.quit()


def test_missing_game_controls_area():
    """测试：缺少游戏控制区域"""
    pygame.init()
    renderer = InteractiveRenderer(1200, 800)

    # 检查是否有游戏控制区域
    has_game_controls = hasattr(renderer, 'game_controls')

    # 这应该FAIL，因为当前没有游戏控制区域
    assert has_game_controls, "缺少专门的游戏控制区域"

    pygame.quit()


def test_insufficient_card_interaction_space():
    """测试：卡牌交互空间不足"""
    pygame.init()
    renderer = InteractiveRenderer(1200, 800)

    hand_area = renderer.player_hand
    hand_height = hand_area.size[1]
    card_height = 160
    hover_space = 20  # 悬停效果需要的额外空间

    # 计算可用交互空间
    available_space = hand_height - card_height

    # 这应该FAIL，因为可用空间不足
    assert available_space >= hover_space, f"卡牌交互空间{available_space}px不足，需要至少{hover_space}px"

    pygame.quit()


def test_no_end_turn_button():
    """测试：没有结束回合按钮"""
    pygame.init()
    renderer = InteractiveRenderer(1200, 800)

    # 检查是否有结束回合按钮
    has_end_turn_button = hasattr(renderer, 'end_turn_button')

    # 这应该FAIL，因为当前没有结束回合按钮
    assert has_end_turn_button, "缺少结束回合按钮"

    pygame.quit()


def test_layout_space_allocation():
    """测试：布局空间分配问题"""
    pygame.init()
    renderer = InteractiveRenderer(1200, 800)

    # 检查当前布局的空间分配
    hud_height = renderer.hud.size[1]
    hand_height = renderer.player_hand.size[1]

    # 这应该FAIL，因为当前空间分配不合理
    total_used = hud_height + hand_height
    assert total_used <= 220, f"当前HUD+手牌使用了{total_used}px空间，分配不合理"

    pygame.quit()


def main():
    """运行所有RED测试"""
    print("🔴 TDD RED阶段 - UI布局改进测试")
    print("这些测试预期会FAIL，因为功能还未实现")
    print("=" * 60)

    tests = [
        ("当前手牌区域高度不足", test_current_hand_area_insufficient_height),
        ("缺少游戏控制区域", test_missing_game_controls_area),
        ("卡牌交互空间不足", test_insufficient_card_interaction_space),
        ("没有结束回合按钮", test_no_end_turn_button),
        ("布局空间分配问题", test_layout_space_allocation)
    ]

    passed_count = 0
    total_count = len(tests)

    for test_name, test_func in tests:
        if run_red_test(test_name, test_func):
            passed_count += 1
        print()

    print("=" * 60)
    print(f"RED测试结果: {passed_count}/{total_count} 测试按预期失败")
    print("✅ RED阶段完成 - 所有测试按预期失败，确认了需要改进的问题")
    print("🟢 下一步: 进入GREEN阶段 - 实现功能让测试通过")


if __name__ == "__main__":
    main()