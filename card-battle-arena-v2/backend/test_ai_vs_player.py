#!/usr/bin/env python3
"""
测试AI vs 玩家对战功能
验证AI是否能正确执行操作
"""

import sys
import time
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from app.game.engine import GameEngine
from app.game.cards import Card, CardType


def test_ai_vs_player():
    """测试AI vs 玩家对战"""
    print("🧪 开始测试AI vs 玩家对战功能")
    print("=" * 50)

    # 创建游戏引擎
    engine = GameEngine()
    game = engine.create_game("玩家", "AI电脑")

    print("✅ 游戏创建成功")

    # 测试几个回合
    for turn in range(1, 6):  # 测试5个回合
        print(f"\n📊 回合 {turn}")
        print("-" * 30)

        # 开始当前玩家回合
        engine.start_turn()
        current = game.current_player
        opponent = game.opponent

        print(f"👤 当前玩家: {current.name}")
        print(f"💰 法力值: {current.current_mana}/{current.max_mana}")
        print(f"❤️ 生命值: {current.hero.health}/30")
        print(f"🎴 手牌数量: {len(current.hand)}")

        if current.name == "AI电脑":
            # AI回合
            print("\n🤖 AI回合开始")

            # AI出牌
            cards_played = 0
            while cards_played < 2 and current.current_mana > 0:
                playable_cards = [card for card in current.hand if card.cost <= current.current_mana]

                if not playable_cards:
                    print("💭 AI没有可出的卡牌了")
                    break

                # AI选择卡牌
                card = playable_cards[0]  # 简单策略：选第一张
                print(f"🎴 AI选择: {card.name} (费用:{card.cost})")

                result = engine.play_card(card)
                if result.success:
                    print(f"✅ AI成功打出 {card.name}")
                    cards_played += 1
                else:
                    print(f"❌ AI出牌失败: {result.error}")
                    break

            # AI攻击
            attackable = [m for m in current.battlefield if m.can_attack]
            if attackable:
                print(f"⚔️ AI有 {len(attackable)} 个随从可以攻击")
                # 简单攻击第一个目标
                attacker = attackable[0]
                target = opponent.hero
                result = engine.attack_with_minion(attacker, target)
                if result.success:
                    print(f"✅ AI {attacker.name} 攻击英雄")
                else:
                    print(f"❌ AI攻击失败: {result.error}")

        # 结束回合
        print(f"🔄 {current.name} 结束回合")
        engine.end_turn()

        # 检查游戏是否结束
        engine.check_win_condition()
        if game.game_over:
            winner = "玩家" if game.winner == 1 else "AI电脑"
            print(f"\n🏆 游戏结束！{winner} 获胜！")
            break

        # 切换玩家
        engine.start_turn()

    print("\n✅ AI vs 玩家对战测试完成")

    # 显示最终状态
    print(f"\n📊 最终状态:")
    print(f"  玩家生命值: {game.player1.hero.health}/30")
    print(f"  AI生命值: {game.player2.hero.health}/30")
    print(f"  玩家战场: {len(game.player1.battlefield)}张随从")
    print(f"  AI战场: {len(game.player2.battlefield)}张随从")


if __name__ == "__main__":
    try:
        test_ai_vs_player()
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()