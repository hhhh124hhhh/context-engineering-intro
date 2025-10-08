#!/usr/bin/env python3
"""
卡牌对战竞技场 V2 - 交互式游戏演示
让玩家可以实际操作一局游戏
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

    print(f"❤️ 你的英雄: {current.hero.health}/30 HP")
    print(f"🗡️ 对手英雄: {opponent.hero.health}/30 HP")

    print(f"\n🎴 你的手牌 ({len(current.hand)}张):")
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

    print(f"\n⚔️ 你的战场 ({len(current.battlefield)}张):")
    for i, card in enumerate(current.battlefield):
        attack_status = "🟢可攻击" if card.can_attack else "🔴不可攻击"
        taunt_status = " [嘲讽]" if card.taunt else ""
        divine_status = " [圣盾]" if card.divine_shield else ""
        print(f"  {i+1}. {card.name} - {card.attack}/{card.health} ({attack_status}){taunt_status}{divine_status}")

    print(f"\n🛡️ 对手战场 ({len(opponent.battlefield)}张):")
    for i, card in enumerate(opponent.battlefield):
        taunt_status = " [嘲讽]" if card.taunt else ""
        divine_status = " [圣盾]" if card.divine_shield else ""
        print(f"  {i+1}. {card.name} - {card.attack}/{card.health}{taunt_status}{divine_status}")

    if current.weapon:
        print(f"\n🗡️ 装备武器: {current.weapon.name} ({current.weapon.attack}/{current.weapon.durability})")

    print(f"\n⚡ 英雄技能: {'✅可用' if not current.used_hero_power and current.current_mana >= 2 else '❌不可用'}")


def get_player_choice():
    """获取玩家选择"""
    while True:
        print(f"\n🎯 请选择行动:")
        print(f"1. 打出手牌")
        print(f"2. 使用英雄技能 (消耗2法力)")
        print(f"3. 随从攻击")
        print(f"4. 英雄攻击")
        print(f"5. 结束回合")
        print(f"6. 查看游戏状态")
        print(f"7. 退出游戏")

        choice = input("请输入选择 (1-7): ").strip()
        if choice in ['1', '2', '3', '4', '5', '6', '7']:
            return choice
        print("❌ 无效选择，请重新输入")


def play_card_interactive(engine, game):
    """交互式打出手牌"""
    current = game.current_player

    if not current.hand:
        print("❌ 你没有手牌！")
        return

    print(f"\n🎴 选择要打出的卡牌:")
    for i, card in enumerate(current.hand):
        print(f"{i+1}. {card.name} (费用:{card.cost})")

    try:
        choice = int(input("请输入卡牌编号: ")) - 1
        if choice < 0 or choice >= len(current.hand):
            print("❌ 无效的卡牌编号！")
            return

        card = current.hand[choice]
        if card.cost > current.current_mana:
            print("❌ 法力值不足！")
            return

        # 检查是否需要目标
        target = None
        if card.card_type == CardType.SPELL and hasattr(card, 'needs_target') and card.needs_target:
            target = choose_target(game)
            if target is None:
                print("❌ 必须选择一个目标！")
                return

        result = engine.play_card(card, target)
        if result.success:
            print(f"✅ 成功打出 {card.name}!")
        else:
            print(f"❌ 打出失败: {result.error}")

    except ValueError:
        print("❌ 请输入有效的数字！")


def choose_target(game):
    """选择目标"""
    opponent = game.opponent

    print(f"\n🎯 选择目标:")
    print(f"1. {opponent.name}的英雄 ({opponent.hero.health} HP)")

    target_index = 2
    minion_targets = {}

    for i, minion in enumerate(opponent.battlefield):
        minion_targets[target_index] = minion
        print(f"{target_index}. {minion.name} ({minion.attack}/{minion.health})")
        target_index += 1

    try:
        choice = int(input("请输入目标编号: "))
        if choice == 1:
            return opponent.hero
        elif choice in minion_targets:
            return minion_targets[choice]
        else:
            print("❌ 无效的目标编号！")
            return None
    except ValueError:
        print("❌ 请输入有效的数字！")
        return None


def use_hero_power_interactive(engine, game):
    """交互式使用英雄技能"""
    current = game.current_player

    if current.used_hero_power:
        print("❌ 本回合已经使用过英雄技能了！")
        return

    if current.current_mana < 2:
        print("❌ 法力值不足！需要2点法力。")
        return

    result = engine.use_hero_power()
    if result.success:
        print("✅ 英雄技能使用成功！")
    else:
        print(f"❌ 英雄技能使用失败: {result.error}")


def attack_with_minion_interactive(engine, game):
    """交互式随从攻击"""
    current = game.current_player

    attackable_minions = [m for m in current.battlefield if m.can_attack]
    if not attackable_minions:
        print("❌ 没有可以攻击的随从！")
        return

    print(f"\n⚔️ 选择攻击的随从:")
    for i, minion in enumerate(attackable_minions):
        print(f"{i+1}. {minion.name} ({minion.attack}/{minion.health})")

    try:
        choice = int(input("请输入随从编号: ")) - 1
        if choice < 0 or choice >= len(attackable_minions):
            print("❌ 无效的随从编号！")
            return

        attacker = attackable_minions[choice]
        target = choose_target(game)

        if target is None:
            print("❌ 必须选择一个目标！")
            return

        result = engine.attack_with_minion(attacker, target)
        if result.success:
            print(f"✅ {attacker.name} 攻击成功！")
        else:
            print(f"❌ 攻击失败: {result.error}")

    except ValueError:
        print("❌ 请输入有效的数字！")


def interactive_game():
    """交互式游戏"""
    print("🎮 卡牌对战竞技场 V2 - 交互式游戏")
    print("=" * 70)

    # 创建游戏引擎
    engine = GameEngine()
    game = engine.create_game("玩家", "电脑")

    print("✅ 游戏创建成功！你是玩家，对手是电脑。")

    # 跟踪是否是新回合开始
    new_turn_starting = True

    while not game.game_over:
        print_game_state(game, show_mana_change=new_turn_starting)
        new_turn_starting = False  # 重置标志

        choice = get_player_choice()

        if choice == '1':  # 打出手牌
            play_card_interactive(engine, game)
        elif choice == '2':  # 使用英雄技能
            use_hero_power_interactive(engine, game)
        elif choice == '3':  # 随从攻击
            attack_with_minion_interactive(engine, game)
        elif choice == '4':  # 英雄攻击
            print("🚧 功能开发中...")
        elif choice == '5':  # 结束回合
            print(f"🔄 {game.current_player.name} 结束回合")
            engine.end_turn()

            # 开始AI对手的回合
            engine.start_turn()

            # 简单的AI对手回合
            ai_turn(engine, game)

            # AI结束回合后，开始玩家的新回合
            engine.start_turn()
            new_turn_starting = True  # 标记新回合开始，显示法力值恢复
            print(f"\n✨ 你的回合开始了！")
        elif choice == '6':  # 查看游戏状态
            print_game_state(game)
        elif choice == '7':  # 退出游戏
            print("👋 游戏结束！")
            break

        # 检查胜负
        engine.check_win_condition()
        if game.game_over:
            winner_name = "玩家" if game.winner == 1 else "电脑"
            print(f"\n🏆 游戏结束！{winner_name} 获胜！")
            break

    print(f"\n📊 游戏统计:")
    print(f"总回合数: {game.turn_number}")
    print(f"历史记录数: {len(game.history)}")


def ai_turn(engine, game):
    """增强的AI回合"""
    print(f"\n🤖 电脑的回合...")
    current = game.current_player

    # 显示AI状态
    print(f"🤖 AI当前法力值: {current.current_mana}/{current.max_mana}")
    print(f"🤖 AI手牌数: {len(current.hand)}")
    time.sleep(1)  # 短暂延迟让用户看清

    # 1. 英雄技能阶段
    if should_use_hero_power(current):
        print(f"🤖 AI正在考虑使用英雄技能...")
        time.sleep(1)
        result = engine.use_hero_power()
        if result.success:
            print(f"🤖 电脑使用了英雄技能！")
        else:
            print(f"🤖 英雄技能使用失败: {result.error}")

    # 2. 出牌阶段（可打多张卡）
    cards_played = 0
    max_cards_per_turn = 3

    print(f"🤖 AI正在考虑出牌（可用法力: {current.current_mana}）...")
    time.sleep(1)

    while cards_played < max_cards_per_turn:
        # 每次出牌前重新计算可出的卡牌（因为法力值会变化）
        playable_cards = [card for card in current.hand if card.cost <= current.current_mana]
        if not playable_cards:
            break

        # 按费用排序，优先出低费卡
        playable_cards.sort(key=lambda x: x.cost)
        card = playable_cards[0]  # 选择最低费的卡

        if can_play_card(card, current, game):
            print(f"🤖 AI选择打出 {card.name} (费用:{card.cost})，剩余法力: {current.current_mana}...")
            time.sleep(1)

            result = play_card_ai(card, engine, game)
            if result.success:
                print(f"🤖 电脑成功打出了 {card.name}！剩余法力: {current.current_mana}/{current.max_mana}")
                cards_played += 1
                # 短暂延迟显示结果
                time.sleep(1)
            else:
                print(f"🤖 打出 {card.name} 失败: {result.error}")
                break  # 如果失败，停止尝试出牌
        else:
            break  # 如果不能出这张卡，停止尝试

    # 3. 攻击阶段
    if has_attackers(current):
        print(f"🤖 AI正在考虑攻击...")
        time.sleep(1)
        perform_attacks_ai(engine, game)

    # 结束回合
    print(f"🤖 电脑结束回合")
    time.sleep(1)
    engine.end_turn()


def should_use_hero_power(player):
    """判断AI是否应该使用英雄技能"""
    # 基础条件：有足够法力且未使用过
    if player.current_mana < 2 or player.used_hero_power:
        return False

    # 策略：法力充裕时使用
    if player.current_mana >= 4:  # 4点法力以上才考虑使用
        return True

    # 如果手牌较少，更倾向于使用英雄技能
    if len(player.hand) <= 2 and player.current_mana >= 2:
        return True

    return False


def can_play_card(card, player, game):
    """判断AI是否可以打出这张卡"""
    if card.card_type == CardType.MINION:
        return True  # 随从卡总是可以打
    elif card.card_type == CardType.SPELL:
        # 法术卡需要目标
        return hasattr(card, 'needs_target') and choose_target_ai(card, game) is not None
    elif card.card_type == CardType.WEAPON:
        return player.weapon is None  # 没有武器时才打武器卡
    return False


def play_card_ai(card, engine, game):
    """AI打卡逻辑"""
    if card.card_type == CardType.SPELL and hasattr(card, 'needs_target'):
        target = choose_target_ai(card, game)
        return engine.play_card(card, target)
    else:
        return engine.play_card(card)


def choose_target_ai(card, game):
    """AI为目标法术选择目标"""
    opponent = game.opponent

    # 简单策略：优先攻击对手英雄
    if hasattr(card, 'damage') and card.damage > 0:
        return opponent.hero

    # 如果有随从，优先攻击威胁随从
    if opponent.battlefield:
        # 选择攻击力最高的随从作为目标
        threat_minions = sorted(opponent.battlefield, key=lambda x: x.attack, reverse=True)
        return threat_minions[0]

    return opponent.hero


def has_attackers(player):
    """检查是否有可攻击的单位"""
    # 检查随从
    for minion in player.battlefield:
        if minion.can_attack:
            return True

    # 检查英雄武器
    if player.weapon and player.weapon.durability > 0:
        return True

    return False


def perform_attacks_ai(engine, game):
    """AI攻击阶段"""
    current = game.current_player
    opponent = game.opponent

    attacks_made = 0

    # 随从攻击
    for minion in current.battlefield:
        if minion.can_attack and attacks_made < 2:  # 限制攻击次数
            target = choose_attack_target_ai(minion, game)
            if target:
                print(f"🤖 {minion.name} 准备攻击 {get_target_name(target)}...")
                time.sleep(1)

                result = engine.attack_with_minion(minion, target)
                if result.success:
                    print(f"🤖 {minion.name} 攻击了 {get_target_name(target)}！")
                    attacks_made += 1
                else:
                    print(f"🤖 {minion.name} 攻击失败: {result.error}")

    # 英雄攻击（如果有武器）
    if current.weapon and current.weapon.durability > 0 and attacks_made < 2:
        target = choose_attack_target_ai(None, game)  # 英雄攻击
        if target:
            print(f"🤖 英雄准备使用 {current.weapon.name} 攻击 {get_target_name(target)}...")
            time.sleep(1)

            result = engine.attack_with_hero(target)
            if result.success:
                print(f"🤖 英雄攻击了 {get_target_name(target)}！")
            else:
                print(f"🤖 英雄攻击失败: {result.error}")


def choose_attack_target_ai(attacker, game):
    """AI选择攻击目标"""
    opponent = game.opponent

    # 如果有嘲讽随从，必须先攻击嘲讽
    taunt_minions = [m for m in opponent.battlefield if m.taunt]
    if taunt_minions:
        # 选择攻击力最低的嘲讽随从
        return min(taunt_minions, key=lambda x: x.attack)

    # 英雄攻击策略：优先攻击英雄
    if attacker is None:  # 英雄攻击
        return opponent.hero

    # 随从攻击策略：
    # 1. 如果能安全消灭敌方随从，优先交换
    for minion in opponent.battlefield:
        if attacker.attack >= minion.health:
            return minion

    # 2. 否则攻击英雄脸
    return opponent.hero


def get_target_name(target):
    """获取目标名称"""
    if hasattr(target, 'name'):
        return target.name
    elif hasattr(target, 'player_id'):
        return f"英雄({target.player_id})"
    else:
        return "未知目标"


def main():
    """主函数"""
    try:
        interactive_game()
    except KeyboardInterrupt:
        print("\n👋 游戏被中断")
    except Exception as e:
        print(f"❌ 游戏出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()