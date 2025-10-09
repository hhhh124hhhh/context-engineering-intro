#!/usr/bin/env python3
"""
TDD GREEN阶段测试运行器

验证UI布局改进是否成功解决了RED阶段发现的问题。
"""

import sys
import pygame
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from app.visualization.improved_interactive_renderer import ImprovedInteractiveRenderer


def run_green_test(test_name, test_func):
    """
    运行单个GREEN测试

    Args:
        test_name: 测试名称
        test_func: 测试函数
    """
    print(f"🟢 测试: {test_name}")
    try:
        test_func()
        print(f"  ✅ PASS - 改进成功")
        return True
    except AssertionError as e:
        print(f"  ❌ FAIL - {e}")
        return False
    except Exception as e:
        print(f"  ❌ ERROR - {e}")
        return False


def test_improved_hand_area_height():
    """测试：改进的手牌区域高度"""
    pygame.init()
    renderer = ImprovedInteractiveRenderer(1200, 800)

    hand_area = renderer.player_hand
    hand_height = hand_area.size[1]
    card_height = 160  # 标准卡牌高度
    min_required_space = 50  # 最小操作空间

    # 这应该PASS，因为改进后的高度应该足够
    assert hand_height >= card_height + min_required_space, \
        f"手牌区域高度{hand_height}px不足，需要至少{card_height + min_required_space}px"

    print(f"    手牌区域高度: {hand_height}px (卡牌: {card_height}px + 操作空间: {min_required_space}px)")

    pygame.quit()


def test_game_controls_area_exists():
    """测试：游戏控制区域存在"""
    pygame.init()
    renderer = ImprovedInteractiveRenderer(1200, 800)

    # 检查是否有游戏控制区域
    has_game_controls = hasattr(renderer, 'game_controls')

    # 这应该PASS，因为改进后添加了游戏控制区域
    assert has_game_controls, "应该有专门的游戏控制区域"

    # 检查游戏控制区域是否正确初始化
    if has_game_controls:
        assert renderer.game_controls is not None, "游戏控制区域应该正确初始化"

    pygame.quit()


def test_sufficient_card_interaction_space():
    """测试：充足的卡牌交互空间"""
    pygame.init()
    renderer = ImprovedInteractiveRenderer(1200, 800)

    hand_area = renderer.player_hand
    hand_height = hand_area.size[1]
    card_height = 160
    hover_space = 20  # 悬停效果需要的额外空间

    # 计算可用交互空间
    available_space = hand_height - card_height

    # 这应该PASS，因为改进后应该有足够的交互空间
    assert available_space >= hover_space, \
        f"卡牌交互空间{available_space}px不足，需要至少{hover_space}px"

    print(f"    可用交互空间: {available_space}px (需要: {hover_space}px)")

    pygame.quit()


def test_end_turn_button_exists():
    """测试：结束回合按钮存在"""
    pygame.init()
    renderer = ImprovedInteractiveRenderer(1200, 800)

    # 检查是否有结束回合按钮
    has_end_turn_button = False
    if hasattr(renderer, 'game_controls') and renderer.game_controls:
        has_end_turn_button = True

    # 这应该PASS，因为改进后添加了结束回合按钮
    assert has_end_turn_button, "应该有结束回合按钮"

    # 检查按钮是否正确配置
    if has_end_turn_button:
        button_rect = renderer.game_controls.rect
        assert button_rect.width > 0 and button_rect.height > 0, "结束回合按钮应该有正确的尺寸"

    pygame.quit()


def test_layout_space_allocation():
    """测试：合理的布局空间分配"""
    pygame.init()
    renderer = ImprovedInteractiveRenderer(1200, 800)

    # 检查改进后的布局空间分配
    hud_height = renderer.hud.size[1]
    hand_height = renderer.player_hand.size[1]

    # 这应该PASS，因为改进后的空间分配应该更合理
    total_used = hud_height + hand_height
    max_reasonable = 300  # HUD + 手牌的合理最大使用空间

    assert total_used <= max_reasonable, \
        f"HUD+手牌使用了{total_used}px空间，超过了合理的{max_reasonable}px"

    print(f"    HUD高度: {hud_height}px")
    print(f"    手牌高度: {hand_height}px")
    print(f"    总使用: {total_used}px")

    pygame.quit()


def test_player_info_display_exists():
    """测试：玩家信息显示存在"""
    pygame.init()
    renderer = ImprovedInteractiveRenderer(1200, 800)

    # 检查是否有玩家信息显示
    has_player_info = hasattr(renderer, 'player_info_display')

    # 这应该PASS，因为改进后添加了玩家信息显示
    assert has_player_info, "应该有玩家信息显示区域"

    pygame.quit()


def test_improved_layout_functionality():
    """测试：改进布局的功能性"""
    pygame.init()
    renderer = ImprovedInteractiveRenderer(1200, 800)

    # 测试游戏是否能正常初始化
    success = renderer.initialize_game("测试玩家", "测试AI")

    # 这应该PASS，因为改进不应该破坏基本功能
    assert success, "改进后的布局应该能正常初始化游戏"

    # 测试基本组件是否存在
    assert renderer.hud is not None, "HUD组件应该存在"
    assert renderer.player_hand is not None, "手牌组件应该存在"
    assert renderer.player_battlefield is not None, "玩家战场组件应该存在"
    assert renderer.opponent_battlefield is not None, "对手战场组件应该存在"

    pygame.quit()


def main():
    """运行所有GREEN测试"""
    print("🟢 TDD GREEN阶段 - 验证UI布局改进")
    print("这些测试应该PASS，验证改进是否成功解决了RED阶段的问题")
    print("=" * 70)

    tests = [
        ("改进的手牌区域高度", test_improved_hand_area_height),
        ("游戏控制区域存在", test_game_controls_area_exists),
        ("充足的卡牌交互空间", test_sufficient_card_interaction_space),
        ("结束回合按钮存在", test_end_turn_button_exists),
        ("合理的布局空间分配", test_layout_space_allocation),
        ("玩家信息显示存在", test_player_info_display_exists),
        ("改进布局的功能性", test_improved_layout_functionality)
    ]

    passed_count = 0
    total_count = len(tests)

    for test_name, test_func in tests:
        if run_green_test(test_name, test_func):
            passed_count += 1
        print()

    print("=" * 70)
    print(f"GREEN测试结果: {passed_count}/{total_count} 测试通过")

    if passed_count == total_count:
        print("🎉 GREEN阶段成功 - 所有改进都按预期工作！")
        print("🔵 下一步: 进入REFACTOR阶段 - 优化代码质量")
    else:
        print(f"⚠️  还有 {total_count - passed_count} 个测试未通过，需要继续改进")


if __name__ == "__main__":
    main()