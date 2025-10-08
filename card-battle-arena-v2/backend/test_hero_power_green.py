#!/usr/bin/env python3
"""
英雄技能测试脚本 - 演示TDD的GREEN阶段
"""

import sys
import traceback
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from app.game.engine import GameEngine


def test_hero_power_usage():
    """测试英雄技能使用 - 应该成功"""
    engine = GameEngine()
    game = engine.create_game("Player1", "Player2")

    current = game.current_player

    # 初始状态：没有使用过英雄技能
    assert not current.used_hero_power

    # 给玩家足够的法力值来使用英雄技能
    current.current_mana = 2
    current.max_mana = 2

    # 使用英雄技能
    result = engine.use_hero_power()

    # 验证结果
    assert result.success
    assert current.used_hero_power
    assert current.current_mana == 0  # 2 - 2 = 0
    assert result.message == "Hero power used successfully"

    print("✅ 英雄技能基本使用测试通过")
    return True


def test_hero_power_insufficient_mana():
    """测试法力值不足"""
    engine = GameEngine()
    game = engine.create_game("Player1", "Player2")

    current = game.current_player
    # 法力值设为1（不够使用英雄技能）
    current.current_mana = 1

    # 尝试使用英雄技能
    result = engine.use_hero_power()

    assert not result.success
    assert "Insufficient mana" in result.error
    assert not current.used_hero_power

    print("✅ 法力值不足测试通过")
    return True


def test_hero_power_cannot_use_twice():
    """测试不能重复使用英雄技能"""
    engine = GameEngine()
    game = engine.create_game("Player1", "Player2")

    current = game.current_player
    current.current_mana = 2
    current.max_mana = 2

    # 使用英雄技能
    result1 = engine.use_hero_power()
    assert result1.success

    # 尝试再次使用
    result2 = engine.use_hero_power()
    assert not result2.success
    assert "already used" in result2.error.lower()

    print("✅ 重复使用测试通过")
    return True


def test_hero_power_deals_damage():
    """测试英雄技能造成伤害"""
    engine = GameEngine()
    game = engine.create_game("Player1", "Player2")

    current = game.current_player
    current.current_mana = 2

    original_health = game.opponent.hero.health

    # 使用英雄技能
    result = engine.use_hero_power()

    assert result.success
    assert game.opponent.hero.health == original_health - 1

    print("✅ 伤害效果测试通过")
    return True


def main():
    """主函数"""
    print("🟢 TDD GREEN阶段: 英雄技能基本实现")
    print("=" * 50)

    try:
        test_hero_power_usage()
        test_hero_power_insufficient_mana()
        test_hero_power_cannot_use_twice()
        test_hero_power_deals_damage()

        print("\n🎉 GREEN阶段成功 - 所有测试通过！")
        print("✅ 英雄技能基本功能已实现")

    except Exception as e:
        print(f"❌ GREEN阶段测试失败: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()