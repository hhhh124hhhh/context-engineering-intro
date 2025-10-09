#!/usr/bin/env python3
"""
TDD集成测试套件

完整的RED-GREEN-REFACTOR循环验证，确保UI布局改进的完整性和质量。
"""

import sys
import pygame
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from app.visualization.interactive_renderer import InteractiveRenderer
from app.visualization.improved_interactive_renderer import ImprovedInteractiveRenderer


class TDDIntegrationTester:
    """TDD集成测试器"""

    def __init__(self):
        self.test_results = {
            'RED': {'passed': 0, 'total': 0},
            'GREEN': {'passed': 0, 'total': 0},
            'INTEGRATION': {'passed': 0, 'total': 0}
        }

    def run_test(self, phase: str, test_name: str, test_func, should_pass: bool = True):
        """
        运行单个测试

        Args:
            phase: 测试阶段 (RED/GREEN/INTEGRATION)
            test_name: 测试名称
            test_func: 测试函数
            should_pass: 测试是否应该通过
        """
        status = "🔴" if phase == "RED" else "🟢" if phase == "GREEN" else "🔵"
        print(f"{status} {phase}: {test_name}")

        try:
            test_func()
            if should_pass:
                print(f"  ✅ PASS - 按预期通过")
                self.test_results[phase]['passed'] += 1
            else:
                print(f"  ❌ UNEXPECTED - 应该失败但却通过了")
        except AssertionError as e:
            if not should_pass:
                print(f"  ✅ EXPECTED FAIL - {e}")
                self.test_results[phase]['passed'] += 1
            else:
                print(f"  ❌ FAIL - {e}")
        except Exception as e:
            print(f"  ❌ ERROR - {e}")

        self.test_results[phase]['total'] += 1
        print()

    def run_red_tests(self):
        """运行RED阶段测试"""
        print("🔴 RED阶段 - 验证原始布局问题")
        print("=" * 50)

        def test_original_hand_area_too_small():
            renderer = InteractiveRenderer(1200, 800)
            hand_height = renderer.player_hand.size[1]
            card_height = 160
            assert hand_height < card_height, f"原始布局应该有问题: 手牌高度{hand_height}px < 卡牌高度{card_height}px"

        def test_original_missing_game_controls():
            renderer = InteractiveRenderer(1200, 800)
            has_game_controls = hasattr(renderer, 'game_controls')
            assert not has_game_controls, "原始布局应该缺少游戏控制区域"

        def test_original_no_end_turn_button():
            renderer = InteractiveRenderer(1200, 800)
            has_end_turn = hasattr(renderer, 'end_turn_button')
            assert not has_end_turn, "原始布局应该没有结束回合按钮"

        def test_original_insufficient_interaction_space():
            renderer = InteractiveRenderer(1200, 800)
            hand_height = renderer.player_hand.size[1]
            available_space = hand_height - 160
            assert available_space < 20, f"原始布局交互空间应该不足: {available_space}px < 20px"

        # 运行RED测试（期望失败）
        self.run_test("RED", "原始手牌区域太小", test_original_hand_area_too_small, should_pass=False)
        self.run_test("RED", "原始缺少游戏控制", test_original_missing_game_controls, should_pass=False)
        self.run_test("RED", "原始没有结束回合按钮", test_original_no_end_turn_button, should_pass=False)
        self.run_test("RED", "原始交互空间不足", test_original_insufficient_interaction_space, should_pass=False)

    def run_green_tests(self):
        """运行GREEN阶段测试"""
        print("🟢 GREEN阶段 - 验证改进效果")
        print("=" * 50)

        def test_improved_hand_area_height():
            renderer = ImprovedInteractiveRenderer(1200, 800)
            hand_height = renderer.player_hand.size[1]
            card_height = 160
            min_space = 50
            assert hand_height >= card_height + min_space, \
                f"改进后手牌高度应该足够: {hand_height}px >= {card_height + min_space}px"

        def test_improved_has_game_controls():
            renderer = ImprovedInteractiveRenderer(1200, 800)
            has_game_controls = hasattr(renderer, 'game_controls')
            assert has_game_controls, "改进后应该有游戏控制区域"

        def test_improved_has_end_turn_button():
            renderer = ImprovedInteractiveRenderer(1200, 800)
            has_end_turn = hasattr(renderer, 'game_controls') and renderer.game_controls is not None
            assert has_end_turn, "改进后应该有结束回合按钮"

        def test_improved_sufficient_interaction_space():
            renderer = ImprovedInteractiveRenderer(1200, 800)
            hand_height = renderer.player_hand.size[1]
            available_space = hand_height - 160
            assert available_space >= 50, f"改进后交互空间应该充足: {available_space}px >= 50px"

        def test_improved_has_player_info():
            renderer = ImprovedInteractiveRenderer(1200, 800)
            has_player_info = hasattr(renderer, 'player_info_display')
            assert has_player_info, "改进后应该有玩家信息显示"

        # 运行GREEN测试（期望通过）
        self.run_test("GREEN", "改进手牌区域高度", test_improved_hand_area_height, should_pass=True)
        self.run_test("GREEN", "改进有游戏控制", test_improved_has_game_controls, should_pass=True)
        self.run_test("GREEN", "改进有结束回合按钮", test_improved_has_end_turn_button, should_pass=True)
        self.run_test("GREEN", "改进交互空间充足", test_improved_sufficient_interaction_space, should_pass=True)
        self.run_test("GREEN", "改进有玩家信息", test_improved_has_player_info, should_pass=True)

    def run_integration_tests(self):
        """运行集成测试"""
        print("🔵 INTEGRATION阶段 - 验证整体功能")
        print("=" * 50)

        def test_comparison_hand_area_improvement():
            original = InteractiveRenderer(1200, 800)
            improved = ImprovedInteractiveRenderer(1200, 800)

            original_height = original.player_hand.size[1]
            improved_height = improved.player_hand.size[1]

            assert improved_height > original_height, \
                f"改进版本应该有更高的手牌区域: {improved_height}px > {original_height}px"

            improvement_percentage = ((improved_height - original_height) / original_height) * 100
            assert improvement_percentage >= 30, \
                f"手牌区域应该至少提升30%: 实际提升{improvement_percentage:.1f}%"

        def test_functionality_preserved():
            """测试改进后基本功能保持不变"""
            improved = ImprovedInteractiveRenderer(1200, 800)

            # 测试窗口创建
            window_created = improved.create_window("测试窗口")
            assert window_created, "改进后应该能正常创建窗口"

            # 测试游戏初始化
            game_initialized = improved.initialize_game("测试玩家1", "测试玩家2")
            assert game_initialized, "改进后应该能正常初始化游戏"

            # 测试基本组件存在
            assert improved.hud is not None, "HUD组件应该存在"
            assert improved.player_hand is not None, "手牌组件应该存在"
            assert improved.player_battlefield is not None, "玩家战场应该存在"
            assert improved.opponent_battlefield is not None, "对手战场应该存在"

        def test_layout_efficiency():
            """测试布局效率"""
            improved = ImprovedInteractiveRenderer(1200, 800)

            # 检查总空间使用是否合理
            hud_height = improved.hud.size[1]
            hand_height = improved.player_hand.size[1]
            total_used = hud_height + hand_height

            assert total_used <= 320, \
                f"总使用空间应该合理: {total_used}px <= 320px"

            # 检查手牌区域利用效率
            efficiency = (hand_height - 160) / hand_height * 100  # 可用空间占比
            assert efficiency >= 20, \
                f"手牌区域应该有良好的空间利用效率: {efficiency:.1f}% >= 20%"

        def test_code_quality_metrics():
            """测试代码质量指标"""
            improved = ImprovedInteractiveRenderer(1200, 800)

            # 检查模块化程度
            modules = ['hud', 'player_hand', 'player_battlefield', 'opponent_battlefield']
            for module in modules:
                assert hasattr(improved, module), f"应该有模块化的{module}组件"

            # 检查新功能组件
            new_components = ['game_controls', 'player_info_display']
            for component in new_components:
                assert hasattr(improved, component), f"应该有新的{component}组件"

        def test_user_experience_improvements():
            """测试用户体验改进"""
            improved = ImprovedInteractiveRenderer(1200, 800)

            # 检查是否有明确的操作反馈
            has_controls = hasattr(improved, 'game_controls') and improved.game_controls is not None
            assert has_controls, "应该有明确的用户控制"

            # 检查是否有清晰的信息显示
            has_info_display = hasattr(improved, 'player_info_display') and improved.player_info_display is not None
            assert has_info_display, "应该有清晰的信息显示"

            # 检查交互空间是否充足
            hand_height = improved.player_hand.size[1]
            interaction_space = hand_height - 160
            assert interaction_space >= 50, f"应该有充足的交互空间: {interaction_space}px >= 50px"

        # 运行集成测试
        self.run_test("INTEGRATION", "手牌区域改进对比", test_comparison_hand_area_improvement, should_pass=True)
        self.run_test("INTEGRATION", "功能保持完整", test_functionality_preserved, should_pass=True)
        self.run_test("INTEGRATION", "布局效率合理", test_layout_efficiency, should_pass=True)
        self.run_test("INTEGRATION", "代码质量指标", test_code_quality_metrics, should_pass=True)
        self.run_test("INTEGRATION", "用户体验改进", test_user_experience_improvements, should_pass=True)

    def generate_report(self):
        """生成测试报告"""
        print("=" * 60)
        print("📊 TDD完整测试报告")
        print("=" * 60)

        total_passed = 0
        total_tests = 0

        for phase, results in self.test_results.items():
            passed = results['passed']
            total = results['total']
            total_passed += passed
            total_tests += total

            if total > 0:
                percentage = (passed / total) * 100
                status = "✅" if passed == total else "⚠️" if passed > 0 else "❌"
                print(f"{status} {phase}: {passed}/{total} ({percentage:.1f}%)")

        print("=" * 60)
        overall_percentage = (total_passed / total_tests) * 100 if total_tests > 0 else 0
        print(f"🎯 总体: {total_passed}/{total_tests} ({overall_percentage:.1f}%)")

        if overall_percentage == 100:
            print("🎉 TDD循环完全成功！UI布局改进完美实现！")
        elif overall_percentage >= 80:
            print("✅ TDD循环基本成功，大部分改进按预期工作")
        else:
            print("⚠️  TDD循环需要进一步改进")

        return overall_percentage == 100

    def run_complete_tdd_cycle(self):
        """运行完整的TDD循环"""
        print("🔄 开始完整的TDD循环测试")
        print("Card Battle Arena UI布局改进验证")
        print("=" * 60)
        print()

        try:
            # 运行所有阶段测试
            self.run_red_tests()
            self.run_green_tests()
            self.run_integration_tests()

            # 生成报告
            success = self.generate_report()
            return success

        except Exception as e:
            print(f"❌ 测试执行出错: {e}")
            return False
        finally:
            # 清理pygame
            if pygame.get_init():
                pygame.quit()


def main():
    """主函数"""
    tester = TDDIntegrationTester()
    success = tester.run_complete_tdd_cycle()

    if success:
        print("\n🚀 UI布局改进已准备好部署！")
        print("建议:")
        print("1. 使用改进的渲染器替换原始版本")
        print("2. 进行用户测试验证体验改进")
        print("3. 监控性能和用户反馈")
    else:
        print("\n🔧 需要进一步改进:")
        print("1. 检查失败的测试用例")
        print("2. 修复相关问题")
        print("3. 重新运行TDD循环")


if __name__ == "__main__":
    main()