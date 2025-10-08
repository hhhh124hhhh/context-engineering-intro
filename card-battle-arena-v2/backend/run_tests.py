#!/usr/bin/env python3
"""
简单的测试运行器
在没有pytest的情况下运行基础测试
"""

import sys
import traceback
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from app.game.engine import GameEngine
from app.game.cards import Card, CardType


class SimpleTestRunner:
    """简单测试运行器"""

    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0

    def run_test(self, test_name, test_func):
        """运行单个测试"""
        self.tests_run += 1
        print(f"Running {test_name}... ", end="")

        try:
            test_func()
            self.tests_passed += 1
            print("✅ PASS")
        except Exception as e:
            self.tests_failed += 1
            print(f"❌ FAIL")
            print(f"  Error: {e}")
            traceback.print_exc()

    def assert_equal(self, actual, expected, message=""):
        """断言相等"""
        if actual != expected:
            error_msg = f"Expected {expected}, got {actual}"
            if message:
                error_msg = f"{message}: {error_msg}"
            raise AssertionError(error_msg)

    def assert_true(self, condition, message=""):
        """断言为真"""
        if not condition:
            error_msg = "Expected True, got False"
            if message:
                error_msg = f"{message}: {error_msg}"
            raise AssertionError(error_msg)

    def assert_false(self, condition, message=""):
        """断言为假"""
        if condition:
            error_msg = "Expected False, got True"
            if message:
                error_msg = f"{message}: {error_msg}"
            raise AssertionError(error_msg)

    def print_summary(self):
        """打印测试总结"""
        print(f"\n{'='*50}")
        print(f"测试总结:")
        print(f"总测试数: {self.tests_run}")
        print(f"通过: {self.tests_passed}")
        print(f"失败: {self.tests_failed}")
        print(f"成功率: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "0%")
        print(f"{'='*50}")


# 测试用例
def test_game_creation():
    """测试游戏创建"""
    runner = SimpleTestRunner()

    def test_create_game():
        engine = GameEngine()
        game = engine.create_game("Player1", "Player2")

        runner.assert_equal(game.player1.name, "Player1")
        runner.assert_equal(game.player2.name, "Player2")
        runner.assert_equal(game.current_player.player_id, 1)
        runner.assert_equal(game.turn_number, 1)
        runner.assert_false(game.game_over)

    runner.run_test("test_create_game", test_create_game)
    return runner


def test_mana_system():
    """测试法力值系统"""
    runner = SimpleTestRunner()

    def test_initial_mana():
        engine = GameEngine()
        game = engine.create_game("Player1", "Player2")

        current = game.current_player
        runner.assert_equal(current.current_mana, 1)
        runner.assert_equal(current.max_mana, 1)

    def test_mana_consumption():
        engine = GameEngine()
        game = engine.create_game("Player1", "Player2")

        # 创建一个1费随从
        card = Card(1, "Test Minion", 1, 1, 1, CardType.MINION)
        game.current_player.hand.append(card)

        # 打出卡牌
        result = engine.play_card(card, target=None)
        runner.assert_true(result.success)
        runner.assert_equal(game.current_player.current_mana, 0)

    def test_insufficient_mana():
        engine = GameEngine()
        game = engine.create_game("Player1", "Player2")

        # 创建一个5费卡牌，但只有1点法力值
        expensive_card = Card(5, "Expensive Card", 5, 5, 5, CardType.MINION)
        game.current_player.hand.append(expensive_card)

        # 尝试打出卡牌
        result = engine.play_card(expensive_card, target=None)
        runner.assert_false(result.success)

    runner.run_test("test_initial_mana", test_initial_mana)
    runner.run_test("test_mana_consumption", test_mana_consumption)
    runner.run_test("test_insufficient_mana", test_insufficient_mana)
    return runner


def test_card_playing():
    """测试出牌功能"""
    runner = SimpleTestRunner()

    def test_play_minion():
        engine = GameEngine()
        game = engine.create_game("Player1", "Player2")

        # 创建一个1费随从
        minion_card = Card(1, "Test Minion", 1, 2, 1, CardType.MINION)
        game.current_player.hand.append(minion_card)

        # 打出随从
        result = engine.play_card(minion_card, target=None)

        runner.assert_true(result.success)
        runner.assert_equal(len(game.current_player.battlefield), 1)
        runner.assert_equal(game.current_player.current_mana, 0)
        runner.assert_equal(minion_card not in game.current_player.hand, True)

    def test_play_spell():
        engine = GameEngine()
        game = engine.create_game("Player1", "Player2")

        # 创建一个1费法术卡（造成3点伤害）
        spell_card = Card(2, "Fireball", 1, 0, 0, CardType.SPELL)
        spell_card.damage = 3
        game.current_player.hand.append(spell_card)

        original_health = game.opponent.hero.health

        # 打出法术卡攻击对手英雄
        result = engine.play_card(spell_card, target=game.opponent.hero)

        print(f"    Debug: spell result success={result.success}, error={result.error}")
        print(f"    Debug: opponent health={game.opponent.hero.health}, original={original_health}")
        runner.assert_true(result.success, f"Spell casting failed: {result.error}")
        runner.assert_equal(game.opponent.hero.health, original_health - 3)
        runner.assert_equal(game.current_player.current_mana, 0)

    runner.run_test("test_play_minion", test_play_minion)
    runner.run_test("test_play_spell", test_play_spell)
    return runner


def test_combat():
    """测试战斗系统"""
    runner = SimpleTestRunner()

    def test_minion_attack_hero():
        engine = GameEngine()
        game = engine.create_game("Player1", "Player2")

        # 在场上放一个攻击力为2的随从
        minion = Card(1, "Attacker", 1, 2, 3, CardType.MINION)
        minion.can_attack = True
        game.current_player.battlefield.append(minion)

        original_health = game.opponent.hero.health

        # 随从攻击对手英雄
        result = engine.attack_with_minion(minion, target=game.opponent.hero)

        print(f"    Debug: attack result success={result.success}, error={result.error}")
        runner.assert_true(result.success, f"Attack failed: {result.error}")
        runner.assert_equal(game.opponent.hero.health, original_health - 2)
        runner.assert_false(minion.can_attack)

    def test_minion_attack_minion():
        engine = GameEngine()
        game = engine.create_game("Player1", "Player2")

        # 攻击方随从 (3血量，避免死亡)
        attacker = Card(2, "Attacker", 2, 3, 3, CardType.MINION)
        attacker.can_attack = True
        game.current_player.battlefield.append(attacker)

        # 防守方随从 (1血量，应该死亡)
        defender = Card(3, "Defender", 1, 2, 1, CardType.MINION)
        game.opponent.battlefield.append(defender)

        # 随从攻击随从
        result = engine.attack_with_minion(attacker, target=defender)

        print(f"    Debug: attack result success={result.success}, error={result.error}")
        print(f"    Debug: attacker health={attacker.health}, defender health={defender.health}")
        runner.assert_true(result.success, f"Attack failed: {result.error}")
        runner.assert_equal(attacker.health, 1)  # 3 - 2 = 1
        runner.assert_equal(defender.health, -2)  # 1 - 3 = -2 (死亡)

    runner.run_test("test_minion_attack_hero", test_minion_attack_hero)
    runner.run_test("test_minion_attack_minion", test_minion_attack_minion)
    return runner


def test_game_rules():
    """测试游戏规则"""
    runner = SimpleTestRunner()

    def test_turn_sequence():
        engine = GameEngine()
        game = engine.create_game("Player1", "Player2")

        # 初始回合
        runner.assert_equal(game.current_player.player_id, 1)
        runner.assert_equal(game.turn_number, 1)

        # 结束当前回合
        engine.end_turn()

        # 结束回合后不应该自动切换玩家，需要手动开始新回合
        runner.assert_equal(game.current_player.player_id, 1)  # 还是玩家1
        runner.assert_equal(game.turn_number, 1)

        # 开始对手的回合
        engine.start_turn()

        # 现在切换到对手回合
        runner.assert_equal(game.current_player.player_id, 2)
        runner.assert_equal(game.turn_number, 1)

    def test_win_condition():
        engine = GameEngine()
        game = engine.create_game("Player1", "Player2")

        # 将对手英雄生命值降至0
        game.opponent.hero.health = 0

        # 检查游戏结束状态
        engine.check_win_condition()

        runner.assert_true(game.game_over)
        runner.assert_equal(game.winner, game.current_player.player_id)

    runner.run_test("test_turn_sequence", test_turn_sequence)
    runner.run_test("test_win_condition", test_win_condition)
    return runner


def main():
    """主函数"""
    print("🧮 卡牌对战竞技场 V2 - 游戏引擎测试")
    print("=" * 50)

    # 运行所有测试套件
    all_runners = []

    try:
        all_runners.append(test_game_creation())
        all_runners.append(test_mana_system())
        all_runners.append(test_card_playing())
        all_runners.append(test_combat())
        all_runners.append(test_game_rules())
    except Exception as e:
        print(f"❌ 测试运行出错: {e}")
        traceback.print_exc()
        return 1

    # 统计结果
    total_tests = sum(runner.tests_run for runner in all_runners)
    total_passed = sum(runner.tests_passed for runner in all_runners)
    total_failed = sum(runner.tests_failed for runner in all_runners)

    print(f"\n{'='*50}")
    print(f"📊 总体测试结果:")
    print(f"总测试数: {total_tests}")
    print(f"通过: {total_passed}")
    print(f"失败: {total_failed}")
    print(f"成功率: {(total_passed/total_tests*100):.1f}%" if total_tests > 0 else "0%")

    if total_failed == 0:
        print(f"\n🎉 所有测试通过！游戏引擎基本功能正常工作。")
        print(f"✅ TDD方法验证成功 - 先定义测试，再实现功能。")
    else:
        print(f"\n⚠️  有 {total_failed} 个测试失败，需要修复。")
        print(f"🔧 这正是TDD的价值 - 立即发现并修复问题。")

    print("=" * 50)
    return 0 if total_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())