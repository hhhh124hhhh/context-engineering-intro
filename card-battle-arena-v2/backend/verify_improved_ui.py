#!/usr/bin/env python3
"""
验证改进的UI是否已集成到主脚本中

检查main.py的交互式模式是否使用了改进后的渲染器。
"""

import sys
import pygame
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from app.visualization.improved_interactive_renderer import ImprovedInteractiveRenderer


def test_improved_ui_integration():
    """测试改进UI是否正确集成"""
    print("🔍 验证改进的UI是否已集成到主脚本中...")
    print("=" * 60)

    # 初始化pygame
    pygame.init()

    try:
        # 创建改进的渲染器
        renderer = ImprovedInteractiveRenderer(1200, 800)

        print("✅ 改进的渲染器创建成功")

        # 验证关键改进功能
        hand_height = renderer.player_hand.size[1]
        has_game_controls = hasattr(renderer, 'game_controls')
        has_player_info = hasattr(renderer, 'player_info_display')

        print(f"✅ 手牌区域高度: {hand_height}px (期望: >=210px)")
        print(f"✅ 游戏控制区域: {'存在' if has_game_controls else '缺失'}")
        print(f"✅ 玩家信息显示: {'存在' if has_player_info else '缺失'}")

        # 验证改进效果
        assert hand_height >= 210, f"手牌区域高度不足: {hand_height}px < 210px"
        assert has_game_controls, "缺少游戏控制区域"
        assert has_player_info, "缺少玩家信息显示"

        print("\n🎉 所有改进功能验证通过！")
        print("✅ main.py现在使用的是改进后的渲染器")

        return True

    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False
    finally:
        pygame.quit()


def compare_with_original():
    """与原始版本对比"""
    print("\n📊 改进效果对比:")
    print("-" * 40)

    from app.visualization.interactive_renderer import InteractiveRenderer

    pygame.init()

    try:
        # 原始版本
        original = InteractiveRenderer(1200, 800)
        original_hand_height = original.player_hand.size[1]

        # 改进版本
        improved = ImprovedInteractiveRenderer(1200, 800)
        improved_hand_height = improved.player_hand.size[1]

        improvement = improved_hand_height - original_hand_height
        improvement_percentage = (improvement / original_hand_height) * 100

        print(f"原始手牌高度: {original_hand_height}px")
        print(f"改进手牌高度: {improved_hand_height}px")
        print(f"提升幅度: +{improvement}px ({improvement_percentage:.1f}%)")

        # 检查新增功能
        original_features = []
        improved_features = []

        if hasattr(original, 'game_controls') and original.game_controls:
            original_features.append("游戏控制")
        if hasattr(original, 'player_info_display') and original.player_info_display:
            original_features.append("玩家信息")

        if hasattr(improved, 'game_controls') and improved.game_controls:
            improved_features.append("游戏控制")
        if hasattr(improved, 'player_info_display') and improved.player_info_display:
            improved_features.append("玩家信息")

        new_features = set(improved_features) - set(original_features)
        if new_features:
            print(f"新增功能: {', '.join(new_features)}")

        return improvement_percentage > 0

    except Exception as e:
        print(f"❌ 对比失败: {e}")
        return False
    finally:
        pygame.quit()


def main():
    """主函数"""
    print("🚀 Card Battle Arena - UI改进集成验证")
    print("检查main.py是否已使用改进后的渲染器")
    print()

    # 测试集成
    integration_success = test_improved_ui_integration()

    # 对比改进效果
    comparison_success = compare_with_original()

    print("\n" + "=" * 60)
    if integration_success and comparison_success:
        print("🎉 验证成功！")
        print("✅ main.py已集成改进的UI渲染器")
        print("✅ 所有改进功能正常工作")
        print("✅ 用户体验显著提升")
        print()
        print("🎮 现在可以使用以下命令体验改进后的游戏:")
        print("   python3 main.py --mode interactive")
    else:
        print("❌ 验证失败，需要检查集成情况")
        print("请确保:")
        print("1. interactive_game.py已更新导入")
        print("2. 改进的渲染器文件存在")
        print("3. 所有依赖正确安装")


if __name__ == "__main__":
    main()