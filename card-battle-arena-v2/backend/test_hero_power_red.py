#!/usr/bin/env python3
"""
英雄技能测试脚本 - 演示TDD的RED阶段
"""

import sys
import traceback
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from app.game.engine import GameEngine


def test_hero_power_usage():
    """测试英雄技能使用 - 应该失败因为方法不存在"""
    engine = GameEngine()
    game = engine.create_game("Player1", "Player2")

    current = game.current_player

    # 初始状态：没有使用过英雄技能
    assert not current.used_hero_power

    # 给玩家足够的法力值来使用英雄技能
    current.current_mana = 2
    current.max_mana = 2

    # 尝试使用英雄技能 - 应该失败因为方法不存在
    try:
        result = engine.use_hero_power()
        # 如果方法存在，检查结果
        assert result.success
        assert current.used_hero_power
        assert current.current_mana == current.max_mana - 2

        # 不能重复使用
        result2 = engine.use_hero_power()
        assert not result2.success
        assert "already used" in result2.error.lower()
        print("✅ 英雄技能测试通过")
    except AttributeError as e:
        print(f"❌ RED阶段测试失败: {e}")
        print("这是预期的 - use_hero_power方法尚未实现")
        return False

    return True


def main():
    """主函数"""
    print("🔴 TDD RED阶段: 英雄技能测试")
    print("=" * 50)

    try:
        success = test_hero_power_usage()
        if success:
            print("测试意外通过了 - 检查实现")
        else:
            print("✅ RED阶段成功 - 测试失败，需要实现功能")
    except Exception as e:
        print(f"❌ 测试执行出错: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()