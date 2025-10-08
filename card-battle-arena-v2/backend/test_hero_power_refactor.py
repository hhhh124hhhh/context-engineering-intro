#!/usr/bin/env python3
"""
英雄技能测试脚本 - 演示TDD的REFACTOR阶段
"""

import sys
import traceback
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from app.game.engine import GameEngine


def test_refactored_hero_power():
    """测试重构后的英雄技能功能"""
    engine = GameEngine()
    game = engine.create_game("Player1", "Player2")

    current = game.current_player
    current.current_mana = 2
    current.max_mana = 2

    original_health = game.opponent.hero.health
    original_history_length = len(game.history)

    # 使用英雄技能
    result = engine.use_hero_power()

    # 验证基本功能
    assert result.success
    assert current.used_hero_power
    assert current.current_mana == 0
    assert game.opponent.hero.health == original_health - 1

    # 验证历史记录
    assert len(game.history) == original_history_length + 1
    last_action = game.history[-1]
    assert last_action['action'] == 'use_hero_power'
    assert last_action['player'] == current.player_id
    assert last_action['cost'] == 2

    print("✅ 重构后的英雄技能测试通过")
    return True


def test_all_hero_power_conditions():
    """测试所有英雄技能使用条件"""
    engine = GameEngine()
    game = engine.create_game("Player1", "Player2")

    current = game.current_player

    # 测试法力值不足
    current.current_mana = 1
    result = engine.use_hero_power()
    assert not result.success
    assert "Insufficient mana" in result.error

    # 测试重复使用
    current.current_mana = 2
    result1 = engine.use_hero_power()
    assert result1.success

    result2 = engine.use_hero_power()
    assert not result2.success
    assert "already used" in result2.error.lower()

    print("✅ 所有英雄技能条件测试通过")
    return True


def test_hero_power_with_turn_system():
    """测试英雄技能与回合系统的集成"""
    engine = GameEngine()
    game = engine.create_game("Player1", "Player2")

    current = game.current_player
    current.current_mana = 2

    # 使用英雄技能
    result1 = engine.use_hero_power()
    assert result1.success
    assert current.used_hero_power

    # 结束回合
    engine.end_turn()

    # 回到玩家回合，英雄技能状态应该重置
    engine.end_turn()  # 结束对手回合

    assert not current.used_hero_power
    # 应该可以再次使用英雄技能
    result2 = engine.use_hero_power()
    assert result2.success

    print("✅ 英雄技能与回合系统集成测试通过")
    return True


def main():
    """主函数"""
    print("🔄 TDD REFACTOR阶段: 英雄技能重构优化")
    print("=" * 50)

    try:
        test_refactored_hero_power()
        test_all_hero_power_conditions()
        test_hero_power_with_turn_system()

        print("\n🎉 REFACTOR阶段成功 - 重构完成，所有功能正常！")
        print("✅ 代码结构更清晰，更易扩展")
        print("✅ 历史记录功能已添加")
        print("✅ 英雄技能效果已分离到独立方法")

    except Exception as e:
        print(f"❌ REFACTOR阶段测试失败: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()