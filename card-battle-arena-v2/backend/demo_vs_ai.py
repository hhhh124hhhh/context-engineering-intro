#!/usr/bin/env python3
"""
卡牌对战竞技场 V2 - 玩家 vs AI 演示
自动化演示完整的对战流程
"""

import sys
import time
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from app.game.engine import GameEngine
from app.game.cards import Card, CardType


def print_game_state(game, show_mana_change=False):
    """打印游戏状态"""
    current = game.current_player
    opponent = game.opponent

    print(f"\n{'='*70}")
    print(f"🎮 回合 {game.turn_number} - {current.name}的回合")

    # 法力值显示，带有变化提示
    if show_mana_change:
        print(f"💰 法力值: {current.current_mana}/{current.max_mana} ✨ (法力值已恢复)")
    else:
        print(f"💰 法力值: {current.current_mana}/{current.max_mana}")

    print(f"❤️ {current.name}英雄: {current.hero.health}/30 HP")
    print(f"🗡️ {opponent.name}英雄: {opponent.hero.health}/30 HP")

    print(f"\n🎴 {current.name}的手牌 ({len(current.hand)}张):")
    for i, card in enumerate(current.hand):
        status = ""
        if card.card_type == CardType.MINION:
            status = f"({card.attack}/{card.health})"
        elif card.card_type == CardType.SPELL:
            status = f"(伤害:{getattr(card, 'damage', 0)})"
        elif card.card_type == CardType.WEAPON:
            status = f"({card.attack}/{card.health})"  # 武器的health就是durability

        can_play = "✅" if card.cost <= current.current_mana else "❌"
        print(f"  {i+1}. {can_play} {card.name} - 费用:{card.cost} {status} [{card.card_type.value}]")

    print(f"\n⚔️ {current.name}的战场 ({len(current.battlefield)}张):")
    for i, card in enumerate(current.battlefield):
        attack_status = "🟢可攻击" if card.can_attack else "🔴不可攻击"
        taunt_status = " [嘲讽]" if card.taunt else ""
        divine_status = " [圣盾]" if card.divine_shield else ""
        print(f"  {i+1}. {card.name} - {card.attack}/{card.health} ({attack_status}){taunt_status}{divine_status}")

    print(f"\n🛡️ {opponent.name}的战场 ({len(opponent.battlefield)}张):")
    for i, card in enumerate(opponent.battlefield):
        taunt_status = " [嘲讽]" if card.taunt else ""
        divine_status = " [圣盾]" if card.divine_shield else ""
        print(f"  {i+1}. {card.name} - {card.attack}/{card.health}{taunt_status}{divine_status}")

    if current.weapon:
        print(f"\n🗡️ {current.name}的武器: {current.weapon.name} ({current.weapon.attack}/{current.weapon.durability})")

    print(f"\n⚡ 英雄技能: {'✅可用' if not current.used_hero_power and current.current_mana >= 2 else '❌不可用'}")


def player_turn(engine, game):
    """玩家回合"""
    current = game.current_player
    print(f"\n🎯 {current.name}的回合开始！")
    time.sleep(1)

    # 玩家策略：优先出低费随从
    cards_played = 0
    max_plays = 3  # 最多出3张牌

    # 出牌阶段
    while cards_played < max_plays and current.current_mana > 0:
        # 找到可以打出的卡牌
        playable_cards = [card for card in current.hand if card.cost <= current.current_mana]

        if not playable_cards:
            print(f"💭 {current.name}没有可出的卡牌了")
            break

        # 选择最低费的卡牌
        playable_cards.sort(key=lambda x: x.cost)
        card = playable_cards[0]

        print(f"🎴 {current.name}选择打出 {card.name} (费用:{card.cost})")
        time.sleep(1)

        result = engine.play_card(card)
        if result.success:
            print(f"✅ {current.name}成功打出了 {card.name}！剩余法力: {current.current_mana}/{current.max_mana}")
            cards_played += 1
            time.sleep(1)
        else:
            print(f"❌ {current.name}打出失败: {result.error}")
            break

    # 攻击阶段
    attackable_minions = [m for m in current.battlefield if m.can_attack]
    if attackable_minions and game.opponent.battlefield:
        print(f"\n⚔️ {current.name}考虑攻击...")
        time.sleep(1)

        for attacker in attackable_minions[:2]:  # 最多攻击2次
            # 选择攻击目标（优先攻击低血量随从）
            targets = sorted(game.opponent.battlefield, key=lambda x: x.health)
            if targets:
                target = targets[0]
                print(f"⚔️ {current.name}的 {attacker.name} 攻击 {target.name}")
                time.sleep(1)

                result = engine.attack_with_minion(attacker, target)
                if result.success:
                    print(f"✅ 攻击成功！")
                else:
                    print(f"❌ 攻击失败: {result.error}")

    # 结束回合
    print(f"\n🔄 {current.name}结束回合")
    time.sleep(1)
    engine.end_turn()


def ai_turn(engine, game):
    """AI回合"""
    current = game.current_player
    print(f"\n🤖 {current.name}的回合开始！")
    time.sleep(1)

    # AI策略
    cards_played = 0
    max_plays = 3

    # 出牌阶段
    while cards_played < max_plays and current.current_mana > 0:
        playable_cards = [card for card in current.hand if card.cost <= current.current_mana]

        if not playable_cards:
            print(f"💭 {current.name}没有可出的卡牌了")
            break

        # AI选择策略：优先高攻击力随从
        if any(card.card_type == CardType.MINION for card in playable_cards):
            minion_cards = [card for card in playable_cards if card.card_type == CardType.MINION]
            minion_cards.sort(key=lambda x: x.attack, reverse=True)
            card = minion_cards[0]
        else:
            playable_cards.sort(key=lambda x: x.cost)
            card = playable_cards[0]

        print(f"🤖 {current.name}选择打出 {card.name} (费用:{card.cost})")
        time.sleep(1)

        result = engine.play_card(card)
        if result.success:
            print(f"✅ {current.name}成功打出了 {card.name}！剩余法力: {current.current_mana}/{current.max_mana}")
            cards_played += 1
            time.sleep(1)
        else:
            print(f"❌ {current.name}打出失败: {result.error}")
            break

    # 攻击阶段
    attackable_minions = [m for m in current.battlefield if m.can_attack]
    if attackable_minions:
        print(f"\n⚔️ {current.name}考虑攻击...")
        time.sleep(1)

        for attacker in attackable_minions[:2]:
            # AI攻击策略：优先攻击敌方英雄
            targets = [game.opponent.hero] + game.opponent.battlefield

            for target in targets:
                print(f"⚔️ {current.name}的 {attacker.name} 攻击 {target.name if hasattr(target, 'name') else '英雄'}")
                time.sleep(1)

                result = engine.attack_with_minion(attacker, target)
                if result.success:
                    print(f"✅ 攻击成功！")
                    break
                else:
                    print(f"❌ 攻击失败: {result.error}")

    # 结束回合
    print(f"\n🔄 {current.name}结束回合")
    time.sleep(1)
    engine.end_turn()


def demo_game():
    """演示游戏"""
    print("🎮 卡牌对战竞技场 V2 - 玩家 vs AI 演示")
    print("=" * 70)
    print("🎯 玩家控制蓝色方，AI控制红色方")
    print("🤖 演示将自动进行，展示完整的对战流程")
    print("=" * 70)

    # 创建游戏引擎
    engine = GameEngine()
    game = engine.create_game("玩家", "AI电脑")

    print("✅ 游戏创建成功！")
    time.sleep(2)

    turn_count = 0
    max_turns = 10  # 最多进行10个回合

    while not game.game_over and turn_count < max_turns:
        turn_count += 1

        # 开始新回合
        engine.start_turn()
        print_game_state(game, show_mana_change=True)

        # 判断当前玩家
        if game.current_player.name == "玩家":
            player_turn(engine, game)
        else:
            ai_turn(engine, game)

        # 检查游戏是否结束
        engine.check_win_condition()

        if game.game_over:
            break

        # 切换到下一个玩家
        engine.start_turn()

    # 显示游戏结果
    print("\n" + "=" * 70)
    if game.game_over:
        winner_name = "玩家" if game.winner == 1 else "AI电脑"
        print(f"🏆 游戏结束！{winner_name} 获胜！")

        print(f"\n📊 最终统计:")
        print(f"  - 总回合数: {game.turn_number}")
        print(f"  - 玩家血量: {game.player1.hero.health}/30")
        print(f"  - AI血量: {game.player2.hero.health}/30")
        print(f"  - 玩家战场: {len(game.player1.battlefield)}张随从")
        print(f"  - AI战场: {len(game.player2.battlefield)}张随从")
    else:
        print("⏰ 演示时间结束，游戏仍在进行中...")

    print("\n🎉 演示完成！")
    print("💡 这展示了完整的玩家vs AI对战系统")
    print("🎮 你可以运行 interactive_demo.py 进行手动对战")


def main():
    """主函数"""
    try:
        demo_game()
    except KeyboardInterrupt:
        print("\n👋 演示被中断")
    except Exception as e:
        print(f"❌ 演示出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()