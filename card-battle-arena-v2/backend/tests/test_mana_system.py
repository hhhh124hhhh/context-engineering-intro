"""
费用系统测试
测试法力值增长、消耗和恢复机制
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.game.engine import GameEngine
from app.game.cards import Card, CardType


class TestManaSystem:
    """费用系统测试类"""

    def test_mana_growth_per_turn(self):
        """测试每回合法力值增长"""
        engine = GameEngine()
        game = engine.create_game("Player1", "Player2")

        # 第1回合 - 玩家1
        current = game.current_player
        assert current.player_id == 1
        assert current.current_mana == 1
        assert current.max_mana == 1

        # 玩家1结束回合
        engine.end_turn()

        # 开始玩家2的回合
        engine.start_turn()

        # 第1回合 - 玩家2 (后手有优势，获得2点法力值)
        current = game.current_player
        assert current.player_id == 2
        assert current.current_mana == 2  # 后手玩家第1回合获得2点法力值（平衡性设计）
        assert current.max_mana == 2

        # 玩家2结束回合
        engine.end_turn()

        # 开始玩家1的第2回合
        engine.start_turn()

        # 第2回合 - 玩家1
        current = game.current_player
        assert current.player_id == 1
        assert current.current_mana == 2  # 法力值增长到2
        assert current.max_mana == 2

        print("✅ 法力值增长测试通过")

    def test_mana_consumption(self):
        """测试法力值消耗"""
        engine = GameEngine()
        game = engine.create_game("Player1", "Player2")

        current = game.current_player

        # 给玩家更多法力值用于测试
        current.current_mana = 5
        current.max_mana = 5

        # 创建一张2费卡牌
        card = Card(1, "Test Minion", 2, 3, 3, CardType.MINION)
        current.hand.append(card)

        initial_mana = current.current_mana

        # 打出卡牌
        result = engine.play_card(card)

        assert result.success
        assert current.current_mana == initial_mana - 2  # 消耗2点法力值
        assert current.max_mana == 5  # 最大法力值不变

        print("✅ 法力值消耗测试通过")

    def test_mana_recovery_on_turn_start(self):
        """测试回合开始时法力值恢复"""
        engine = GameEngine()
        game = engine.create_game("Player1", "Player2")

        current = game.current_player

        # 消耗一些法力值
        current.current_mana = 0  # 假设法力值被消耗完

        # 结束回合并开始新回合
        engine.end_turn()
        engine.start_turn()  # 对手回合
        engine.end_turn()
        engine.start_turn()  # 回到玩家回合，第2回合

        # 法力值应该恢复到最大值
        current = game.current_player
        assert current.player_id == 1
        assert current.current_mana == 2  # 第2回合，法力值恢复到2
        assert current.max_mana == 2

        print("✅ 法力值恢复测试通过")

    def test_hero_power_mana_cost(self):
        """测试英雄技能的法力值消耗"""
        engine = GameEngine()
        game = engine.create_game("Player1", "Player2")

        current = game.current_player

        # 给玩家足够法力值
        current.current_mana = 3
        current.max_mana = 3

        initial_mana = current.current_mana

        # 使用英雄技能
        result = engine.use_hero_power()

        assert result.success
        assert current.current_mana == initial_mana - 2  # 消耗2点法力值
        assert current.used_hero_power == True

        print("✅ 英雄技能法力消耗测试通过")

    def test_max_mana_limit(self):
        """测试最大法力值限制（10点）"""
        engine = GameEngine()
        game = engine.create_game("Player1", "Player2")

        current = game.current_player

        # 模拟游戏进行到第10回合之后
        for turn in range(1, 12):  # 进行到第11回合
            engine.end_turn()
            engine.start_turn()  # 对手回合
            engine.end_turn()
            engine.start_turn()  # 玩家回合

        # 法力值应该限制在10点
        assert current.max_mana == 10
        assert current.current_mana == 10

        print("✅ 最大法力值限制测试通过")

    def test_insufficient_mana_prevents_action(self):
        """测试法力值不足时阻止行动"""
        engine = GameEngine()
        game = engine.create_game("Player1", "Player2")

        current = game.current_player

        # 确保法力值不足
        current.current_mana = 1

        # 创建一张高费卡牌
        expensive_card = Card(1, "Expensive Card", 5, 5, 5, CardType.MINION)
        current.hand.append(expensive_card)

        # 尝试打出卡牌应该失败
        result = engine.play_card(expensive_card)
        assert not result.success
        assert "Insufficient mana" in result.error

        # 尝试使用英雄技能应该失败
        current.current_mana = 1  # 确保1点法力值
        result = engine.use_hero_power()
        assert not result.success
        assert "Insufficient mana" in result.error

        print("✅ 法力值不足阻止行动测试通过")


def run_all_mana_tests():
    """运行所有费用系统测试"""
    print("🧮 开始费用系统测试...")
    print("=" * 50)

    test_instance = TestManaSystem()

    tests = [
        test_instance.test_mana_growth_per_turn,
        test_instance.test_mana_consumption,
        test_instance.test_mana_recovery_on_turn_start,
        test_instance.test_hero_power_mana_cost,
        test_instance.test_max_mana_limit,
        test_instance.test_insufficient_mana_prevents_action
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ 测试失败: {test.__name__}")
            print(f"   错误: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("=" * 50)
    print(f"📊 测试结果: {passed} 通过, {failed} 失败")

    if failed == 0:
        print("🎉 所有费用系统测试通过！")
    else:
        print("⚠️ 有测试失败，需要修复")

    return failed == 0


if __name__ == "__main__":
    success = run_all_mana_tests()
    sys.exit(0 if success else 1)