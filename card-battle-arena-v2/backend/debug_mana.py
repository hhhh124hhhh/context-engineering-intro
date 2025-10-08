#!/usr/bin/env python3
"""
调试法力值增长问题
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from app.game.engine import GameEngine


def debug_mana_growth():
    """调试法力值增长"""
    engine = GameEngine()
    game = engine.create_game("Player1", "Player2")

    print("=== 初始状态 ===")
    print(f"当前玩家: {game.current_player.name} (ID: {game.current_player.player_id})")
    print(f"法力值: {game.current_player.current_mana}/{game.current_player.max_mana}")
    print(f"对手: {game.opponent.name} (ID: {game.opponent.player_id})")
    print(f"法力值: {game.opponent.current_mana}/{game.opponent.max_mana}")

    print("\n=== 玩家1结束回合 ===")
    engine.end_turn()

    print("=== 开始玩家2回合 ===")
    engine.start_turn()

    current = game.current_player
    print(f"当前玩家: {current.name} (ID: {current.player_id})")
    print(f"法力值: {current.current_mana}/{current.max_mana}")

    print("\n=== 玩家2结束回合 ===")
    engine.end_turn()

    print("=== 开始玩家1第2回合 ===")
    engine.start_turn()

    current = game.current_player
    print(f"当前玩家: {current.name} (ID: {current.player_id})")
    print(f"法力值: {current.current_mana}/{current.max_mana}")


if __name__ == "__main__":
    debug_mana_growth()