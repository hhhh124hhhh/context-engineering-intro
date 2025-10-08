#!/usr/bin/env python3
"""
调试战斗系统
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from app.game.engine import GameEngine
from app.game.cards import Card, CardType


def debug_combat():
    """调试随从战斗"""
    engine = GameEngine()
    game = engine.create_game("Player1", "Player2")

    # 创建随从
    attacker = Card(2, "Attacker", 2, 3, 2, CardType.MINION)
    attacker.can_attack = True
    game.current_player.battlefield.append(attacker)

    defender = Card(3, "Defender", 1, 2, 1, CardType.MINION)
    game.opponent.battlefield.append(defender)

    print(f"攻击前: attacker.health={attacker.health}, defender.health={defender.health}")
    print(f"attacker在战场: {attacker in game.current_player.battlefield}")
    print(f"defender在战场: {defender in game.opponent.battlefield}")

    # 执行攻击
    result = engine.attack_with_minion(attacker, target=defender)
    print(f"攻击结果: {result.success}")

    print(f"攻击后: attacker.health={attacker.health}, defender.health={defender.health}")
    print(f"attacker在战场: {attacker in game.current_player.battlefield}")
    print(f"defender在战场: {defender in game.opponent.battlefield}")
    print(f"attacker.can_attack={attacker.can_attack}")


if __name__ == "__main__":
    debug_combat()