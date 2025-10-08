#!/usr/bin/env python3
"""
卡牌对战竞技场 V2 - 游戏演示
测试游戏引擎是否可以实际游玩
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from app.game.engine import GameEngine
from app.game.cards import Card, CardType


def print_game_state(game):
    """打印游戏状态"""
    current = game.current_player
    opponent = game.opponent

    print(f"\n{'='*60}")
    print(f"回合 {game.turn_number} - {current.name}的回合")
    print(f"当前玩家法力值: {current.current_mana}/{current.max_mana}")
    print(f"对手英雄生命值: {opponent.hero.health}")
    print(f"当前英雄生命值: {current.hero.health}")

    print(f"\n{current.name}的手牌 ({len(current.hand)}张):")
    for i, card in enumerate(current.hand):
        print(f"  {i+1}. {card.name} - 费用:{card.cost} 攻击:{card.attack} 血量:{card.health} 类型:{card.card_type.value}")

    print(f"\n{current.name}的战场 ({len(current.battlefield)}张):")
    for i, card in enumerate(current.battlefield):
        attack_status = "可攻击" if card.can_attack else "不可攻击"
        print(f"  {i+1}. {card.name} - {card.attack}/{card.health} ({attack_status})")

    print(f"\n{opponent.name}的战场 ({len(opponent.battlefield)}张):")
    for i, card in enumerate(opponent.battlefield):
        print(f"  {i+1}. {card.name} - {card.attack}/{card.health}")


def demo_game():
    """演示一局完整的游戏"""
    print("🎮 卡牌对战竞技场 V2 - 游戏演示")
    print("=" * 60)

    # 创建游戏引擎
    engine = GameEngine()

    # 创建新游戏
    game = engine.create_game("玩家1", "玩家2")

    print("✅ 游戏创建成功！")

    # 演示几个回合
    for round_num in range(3):  # 进行3个回合
        print(f"\n🎯 第 {round_num + 1} 回合演示")

        # 玩家1回合
        print_game_state(game)

        # 尝试打出一张卡牌
        current = game.current_player
        if current.hand and current.current_mana >= current.hand[0].cost:
            card_to_play = current.hand[0]
            print(f"\n🎴 {current.name} 打出 {card_to_play.name}")
            result = engine.play_card(card_to_play)
            if result.success:
                print(f"✅ 成功打出 {card_to_play.name}")
            else:
                print(f"❌ 打出失败: {result.error}")

        # 尝试使用英雄技能
        if current.current_mana >= 2 and not current.used_hero_power:
            print(f"\n⚡ {current.name} 使用英雄技能")
            result = engine.use_hero_power()
            if result.success:
                print(f"✅ 英雄技能使用成功")
            else:
                print(f"❌ 英雄技能使用失败: {result.error}")

        # 尝试随从攻击
        for minion in current.battlefield:
            if minion.can_attack:
                print(f"\n⚔️ {minion.name} 攻击对手英雄")
                result = engine.attack_with_minion(minion, game.opponent.hero)
                if result.success:
                    print(f"✅ 攻击成功")
                else:
                    print(f"❌ 攻击失败: {result.error}")
                break  # 只演示一次攻击

        # 结束回合
        print(f"\n🔄 {current.name} 结束回合")
        engine.end_turn()

        # 检查游戏是否结束
        if game.game_over:
            print(f"\n🏆 游戏结束！{game.winner} 获胜！")
            break

    print_game_state(game)

    print(f"\n📊 游戏统计:")
    print(f"总回合数: {game.turn_number}")
    print(f"历史记录数: {len(game.history)}")

    print(f"\n🎉 游戏演示完成！游戏引擎完全可以游玩！")
    return True


def main():
    """主函数"""
    try:
        demo_game()
    except Exception as e:
        print(f"❌ 游戏演示出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()