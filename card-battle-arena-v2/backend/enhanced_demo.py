#!/usr/bin/env python3
"""
卡牌对战竞技场 V2 - 增强版交互式游戏演示
添加了更多动效和视觉效果，让游戏体验更加生动有趣
"""

import sys
import time
import random
from pathlib import Path
from typing import Optional

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from app.game.engine import GameEngine
from app.game.cards import Card, CardType


def clear_screen():
    """清屏"""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')


def animated_print(text, delay=0.03):
    """带动画效果的打印"""
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()


def dramatic_pause(seconds: float = 1):
    """戏剧性暂停"""
    time.sleep(seconds)


def show_damage_effect(damage, target_name):
    """显示伤害效果"""
    effect = f"💥 {target_name} 受到 {damage} 点伤害!"
    animated_print(effect, 0.05)
    dramatic_pause(0.5)


def show_heal_effect(heal_amount, target_name):
    """显示治疗效果"""
    effect = f"💚 {target_name} 恢复 {heal_amount} 点生命值!"
    animated_print(effect, 0.05)
    dramatic_pause(0.5)


def show_card_play_effect(card_name, player_name):
    """显示打牌效果"""
    effect = f"🃏 {player_name} 打出了 {card_name}!"
    animated_print(effect, 0.05)
    dramatic_pause(0.7)


def show_attack_effect(attacker_name, target_name, damage):
    """显示攻击效果"""
    effect = f"⚔️  {attacker_name} 攻击 {target_name}! 造成 {damage} 点伤害!"
    animated_print(effect, 0.05)
    dramatic_pause(0.7)


def show_death_effect(minion_name):
    """显示死亡效果"""
    effect = f"💀 {minion_name} 死亡了!"
    animated_print(effect, 0.05)
    dramatic_pause(0.5)


def show_draw_card_effect(player_name, card_name):
    """显示抽牌效果"""
    effect = f"🎴 {player_name} 抽到了 {card_name}!"
    animated_print(effect, 0.05)
    dramatic_pause(0.3)


def show_mana_restore_effect(player_name, mana_amount):
    """显示法力恢复效果"""
    effect = f"✨ {player_name} 的法力值恢复了 {mana_amount} 点!"
    animated_print(effect, 0.05)
    dramatic_pause(0.5)


def get_card_skills_display(card):
    """获取卡牌技能显示文本"""
    skills = []
    
    # 基础特殊属性
    if card.charge:
        skills.append("⚡冲锋")
    if card.taunt:
        skills.append("🛡️嘲讽")
    if card.divine_shield:
        skills.append("⭐圣盾")
    if card.windfury:
        skills.append("💨风怒")
    if card.stealth:
        skills.append("👤潜行")
    if card.lifelink:
        skills.append("❤️吸血")
    if card.poison:
        skills.append("☠️中毒")
    if card.reborn:
        skills.append("🔥复生")
    if card.echo:
        skills.append("🎯回响")
    if card.rush:
        skills.append("⚔️突袭")
    
    # 基础效果
    if card.battlecry_damage > 0:
        skills.append(f"💥战吼:造成{card.battlecry_damage}点伤害")
    if card.deathrattle_draw > 0:
        skills.append(f"👻亡语:抽{card.deathrattle_draw}张牌")
    if card.damage > 0:
        skills.append(f"🔥伤害:{card.damage}点")
    if card.card_draw > 0:
        skills.append(f"📖抽牌:{card.card_draw}张")
    if card.heal_amount > 0:
        skills.append(f"💚治疗:{card.heal_amount}点")
    if card.spell_damage > 0:
        skills.append(f"🔮法术伤害+{card.spell_damage}")
    if card.mana_gain > 0:
        skills.append(f"💎获得{card.mana_gain}法力")
    
    # 进阶效果
    if card.combo_effect:
        skills.append("🔗连击")
    if card.secret_card:
        skills.append("🔒秘密")
    if card.quest_progress > 0:
        skills.append(f"📜任务进度+{card.quest_progress}")
    if card.aura_effect:
        skills.append("🌟光环")
    
    return skills


def print_game_state(game, show_mana_change=False):
    """打印游戏状态（增强版）"""
    current = game.current_player
    opponent = game.opponent

    # 清屏并显示标题
    clear_screen()
    print("🎮" + "="*68 + "🎮")
    title = f"卡牌对战竞技场 V2 - 回合 {game.turn_number}"
    print(f"{title:^70}")
    print("🎮" + "="*68 + "🎮")
    
    print(f"\n{'🔵 ' + current.name + '的回合' if game.current_player_index == 0 else '🔴 ' + current.name + '的回合':^70}")

    # 法力值显示，带有变化提示
    mana_bar = "🔷" * current.current_mana + "🔹" * (current.max_mana - current.current_mana)
    if show_mana_change:
        print(f"💰 法力值: {current.current_mana}/{current.max_mana} {mana_bar} ✨ (法力值已恢复)")
    else:
        print(f"💰 法力值: {current.current_mana}/{current.max_mana} {mana_bar}")

    # 英雄状态
    print(f"\n{'❤️ 你的英雄:':<30}{'🗡️ 对手英雄:'}")
    print(f"  {current.hero.health}/30 HP{'':<15}{opponent.hero.health}/30 HP")
    
    # 生命值条
    player_health_bar = "🟥" * (current.hero.health // 3) + "⬜" * (10 - current.hero.health // 3)
    opponent_health_bar = "🟥" * (opponent.hero.health // 3) + "⬜" * (10 - opponent.hero.health // 3)
    print(f"  {player_health_bar:<15}{'':<10}{opponent_health_bar}")

    # 手牌区域
    print(f"\n🎴 你的手牌 ({len(current.hand)}张):")
    if current.hand:
        for i, card in enumerate(current.hand):
            status = ""
            if card.card_type == CardType.MINION:
                status = f"({card.attack}/{card.health})"
            elif card.card_type == CardType.SPELL:
                status = f"(伤害:{getattr(card, 'damage', 0)})"
            elif card.card_type == CardType.WEAPON:
                status = f"({card.attack}/{card.health})"  # 武器的health就是durability

            can_play = "✅" if card.cost <= current.current_mana else "❌"
            cost_color = "🟡" * card.cost
            
            # 显示卡牌技能
            skills = get_card_skills_display(card)
            skills_display = ""
            if skills:
                if len(skills) <= 2:
                    skills_display = " [" + ", ".join(skills) + "]"
                else:
                    skills_display = " [" + ", ".join(skills[:2]) + ", ...]"
            
            print(f"  {i+1}. {can_play} {card.name} - {cost_color} {status} [{card.card_type.value}]{skills_display}")
    else:
        print("  (空)")

    # 战场区域
    print(f"\n⚔️ 你的战场 ({len(current.battlefield)}张):")
    if current.battlefield:
        for i, card in enumerate(current.battlefield):
            attack_status = "🟢可攻击" if card.can_attack else "🔴不可攻击"
            taunt_status = " [🛡️嘲讽]" if card.taunt else ""
            divine_status = " [⭐圣盾]" if card.divine_shield else ""
            
            # 显示卡牌技能
            skills = get_card_skills_display(card)
            skills_display = ""
            if skills:
                if len(skills) <= 1:
                    skills_display = " [" + ", ".join(skills) + "]"
                else:
                    skills_display = " [" + skills[0] + ", ...]"
            
            print(f"  {i+1}. {card.name} - {card.attack}/{card.health} ({attack_status}){taunt_status}{divine_status}{skills_display}")
    else:
        print("  (无随从)")

    print(f"\n🛡️ 对手战场 ({len(opponent.battlefield)}张):")
    if opponent.battlefield:
        for i, card in enumerate(opponent.battlefield):
            taunt_status = " [🛡️嘲讽]" if card.taunt else ""
            divine_status = " [⭐圣盾]" if card.divine_shield else ""
            
            # 显示卡牌技能
            skills = get_card_skills_display(card)
            skills_display = ""
            if skills:
                if len(skills) <= 1:
                    skills_display = " [" + ", ".join(skills) + "]"
                else:
                    skills_display = " [" + skills[0] + ", ...]"
            
            print(f"  {i+1}. {card.name} - {card.attack}/{card.health}{taunt_status}{divine_status}{skills_display}")
    else:
        print("  (无随从)")

    # 武器装备
    if current.weapon:
        print(f"\n🗡️ 装备武器: {current.weapon.name} ({current.weapon.attack}/{current.weapon.durability})")

    # 英雄技能
    hero_power_status = "✅可用" if not current.used_hero_power and current.current_mana >= 2 else "❌不可用"
    print(f"\n⚡ 英雄技能: {hero_power_status} (消耗2法力)")


def get_player_choice():
    """获取玩家选择（增强版）"""
    print(f"\n🎯 请选择行动:")
    print(f"1. 🃏 打出手牌")
    print(f"2. ⚡ 使用英雄技能 (消耗2法力)")
    print(f"3. ⚔️ 随从攻击")
    print(f"4. 👑 英雄攻击")
    print(f"5. 🔄 结束回合")
    print(f"6. 🔍 查看游戏状态")
    print(f"7. 🚪 退出游戏")

    while True:
        choice = input("\n请输入选择 (1-7): ").strip()
        if choice in ['1', '2', '3', '4', '5', '6', '7']:
            return choice
        print("❌ 无效选择，请重新输入")


def play_card_interactive(engine, game):
    """交互式打出手牌（增强版）"""
    current = game.current_player

    if not current.hand:
        print("❌ 你没有手牌！")
        dramatic_pause(1)
        return

    print(f"\n🎴 选择要打出的卡牌:")
    for i, card in enumerate(current.hand):
        cost_color = "🟡" * card.cost
        print(f"{i+1}. {card.name} ({cost_color})")

    try:
        choice = int(input("请输入卡牌编号: ")) - 1
        if choice < 0 or choice >= len(current.hand):
            print("❌ 无效的卡牌编号！")
            dramatic_pause(1)
            return

        card = current.hand[choice]
        if card.cost > current.current_mana:
            print("❌ 法力值不足！")
            dramatic_pause(1)
            return

        # 检查是否需要目标
        target = None
        if card.card_type == CardType.SPELL and hasattr(card, 'needs_target') and card.needs_target:
            target = choose_target(game)
            if target is None:
                print("❌ 必须选择一个目标！")
                dramatic_pause(1)
                return

        result = engine.play_card(card, target)
        if result.success:
            show_card_play_effect(card.name, current.name)
            # 特殊效果显示
            if hasattr(card, 'damage') and card.damage > 0:
                if target:
                    target_name = getattr(target, 'name', '对手英雄')
                    show_damage_effect(card.damage, target_name)
            if hasattr(card, 'heal_amount') and card.heal_amount > 0:
                show_heal_effect(card.heal_amount, current.name)
            if hasattr(card, 'card_draw') and card.card_draw > 0:
                for _ in range(card.card_draw):
                    if current.deck:
                        drawn_card = current.deck.pop()
                        current.hand.append(drawn_card)
                        show_draw_card_effect(current.name, drawn_card.name)
        else:
            print(f"❌ 打出失败: {result.error}")

        dramatic_pause(1)

    except ValueError:
        print("❌ 请输入有效的数字！")
        dramatic_pause(1)


def choose_target(game):
    """选择目标（增强版）"""
    opponent = game.opponent

    print(f"\n🎯 选择目标:")
    print(f"1. 🎯 {opponent.name}的英雄 ({opponent.hero.health} HP)")

    target_index = 2
    minion_targets = {}

    for i, minion in enumerate(opponent.battlefield):
        minion_targets[target_index] = minion
        print(f"{target_index}. 🛡️ {minion.name} ({minion.attack}/{minion.health})")
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
    """交互式使用英雄技能（增强版）"""
    current = game.current_player

    if current.used_hero_power:
        print("❌ 本回合已经使用过英雄技能了！")
        dramatic_pause(1)
        return

    if current.current_mana < 2:
        print("❌ 法力值不足！需要2点法力。")
        dramatic_pause(1)
        return

    # 英雄技能动画
    print("⚡ 英雄技能准备中...")
    for i in range(3):
        print(".", end="", flush=True)
        time.sleep(0.5)
    print()

    result = engine.use_hero_power()
    if result.success:
        animated_print("✅ 英雄技能使用成功！", 0.05)
        show_damage_effect(1, game.opponent.name + "的英雄")
        dramatic_pause(1)
    else:
        print(f"❌ 英雄技能使用失败: {result.error}")
        dramatic_pause(1)


def attack_with_minion_interactive(engine, game):
    """交互式随从攻击（增强版）"""
    current = game.current_player

    attackable_minions = [m for m in current.battlefield if m.can_attack]
    if not attackable_minions:
        print("❌ 没有可以攻击的随从！")
        dramatic_pause(1)
        return

    print(f"\n⚔️ 选择攻击的随从:")
    for i, minion in enumerate(attackable_minions):
        print(f"{i+1}. {minion.name} ({minion.attack}/{minion.health})")

    try:
        choice = int(input("请输入随从编号: ")) - 1
        if choice < 0 or choice >= len(attackable_minions):
            print("❌ 无效的随从编号！")
            dramatic_pause(1)
            return

        attacker = attackable_minions[choice]
        target = choose_target(game)

        if target is None:
            print("❌ 必须选择一个目标！")
            dramatic_pause(1)
            return

        # 攻击动画
        print(f"\n⚔️ {attacker.name} 准备攻击...")
        dramatic_pause(0.5)
        
        result = engine.attack_with_minion(attacker, target)
        if result.success:
            target_name = getattr(target, 'name', '对手英雄')
            show_attack_effect(attacker.name, target_name, attacker.attack)
            
            # 检查目标是否死亡
            if hasattr(target, 'health') and target.health <= 0:
                show_death_effect(target_name)
            
            # 检查攻击者是否死亡
            if hasattr(attacker, 'health') and attacker.health <= 0:
                show_death_effect(attacker.name)
                
            print(f"✅ {attacker.name} 攻击成功！")
        else:
            print(f"❌ 攻击失败: {result.error}")

        dramatic_pause(1)

    except ValueError:
        print("❌ 请输入有效的数字！")
        dramatic_pause(1)


def attack_with_hero_interactive(engine, game):
    """交互式英雄攻击（增强版）"""
    current = game.current_player

    if not current.weapon:
        print("❌ 你没有装备武器！")
        dramatic_pause(1)
        return

    if current.weapon.durability <= 0:
        print("❌ 你的武器已经损坏！")
        dramatic_pause(1)
        return

    target = choose_target(game)
    if target is None:
        print("❌ 必须选择一个目标！")
        dramatic_pause(1)
        return

    # 英雄攻击动画
    print(f"\n👑 {current.name} 准备使用 {current.weapon.name} 攻击...")
    dramatic_pause(0.5)
    
    result = engine.attack_with_hero(target)
    if result.success:
        target_name = getattr(target, 'name', '对手英雄')
        show_attack_effect(f"{current.name}(英雄)", target_name, current.weapon.attack)
        
        # 检查目标是否死亡
        if hasattr(target, 'health') and target.health <= 0:
            show_death_effect(target_name)
            
        print(f"✅ 英雄攻击成功！")
        
        # 显示武器耐久度
        if current.weapon:
            print(f"🗡️ {current.weapon.name} 剩余耐久度: {current.weapon.durability}")
            
        # 检查武器是否损坏
        if current.weapon and current.weapon.durability <= 0:
            print(f"💥 {current.weapon.name} 已损坏！")
            current.weapon = None
    else:
        print(f"❌ 英雄攻击失败: {result.error}")

    dramatic_pause(1)


def interactive_game():
    """交互式游戏（增强版）"""
    # 开场动画
    clear_screen()
    animated_print("🎮 欢迎来到卡牌对战竞技场 V2!", 0.05)
    animated_print("🔥 准备进入史诗级对决...", 0.05)
    dramatic_pause(1)
    
    # 创建游戏引擎
    engine = GameEngine()
    game = engine.create_game("玩家", "电脑")

    animated_print("✅ 游戏创建成功！你是玩家，对手是电脑。", 0.05)
    dramatic_pause(1)

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
            attack_with_hero_interactive(engine, game)
        elif choice == '5':  # 结束回合
            print(f"🔄 {game.current_player.name} 结束回合")
            dramatic_pause(1)
            engine.end_turn()

            # 开始AI对手的回合
            engine.start_turn()

            # 简单的AI对手回合
            ai_turn(engine, game)

            # AI结束回合后，开始玩家的新回合
            engine.start_turn()
            new_turn_starting = True  # 标记新回合开始，显示法力值恢复
            animated_print("✨ 你的回合开始了！", 0.05)
            show_mana_restore_effect(game.current_player.name, game.current_player.max_mana)
            dramatic_pause(1)
        elif choice == '6':  # 查看游戏状态
            print_game_state(game)
            dramatic_pause(1)
        elif choice == '7':  # 退出游戏
            print("👋 游戏结束！")
            break

        # 检查胜负
        engine.check_win_condition()
        if game.game_over:
            winner_name = "玩家" if game.winner == 1 else "电脑"
            clear_screen()
            victory_text = f"🏆 游戏结束！{winner_name} 获胜！"
            animated_print("="*50, 0.02)
            animated_print(victory_text, 0.05)
            animated_print("="*50, 0.02)
            break

    print(f"\n📊 游戏统计:")
    print(f"总回合数: {game.turn_number}")
    print(f"历史记录数: {len(game.history)}")
    input("\n按回车键退出...")


def ai_turn(engine, game):
    """增强的AI回合（带动画效果）"""
    print(f"\n🤖 电脑的回合...")
    current = game.current_player

    # 显示AI状态
    print(f"🤖 AI当前法力值: {current.current_mana}/{current.max_mana}")
    print(f"🤖 AI手牌数: {len(current.hand)}")
    dramatic_pause(1)  # 短暂延迟让用户看清

    # 1. 英雄技能阶段
    if should_use_hero_power(current):
        animated_print("🤖 AI正在考虑使用英雄技能...", 0.05)
        dramatic_pause(1)
        result = engine.use_hero_power()
        if result.success:
            animated_print("🤖 电脑使用了英雄技能！", 0.05)
            show_damage_effect(1, "玩家的英雄")
        else:
            print(f"🤖 英雄技能使用失败: {result.error}")

    # 2. 出牌阶段（可打多张卡）
    cards_played = 0
    max_cards_per_turn = 3

    animated_print(f"🤖 AI正在考虑出牌（可用法力: {current.current_mana}）...", 0.05)
    dramatic_pause(1)

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
            dramatic_pause(1)

            result = play_card_ai(card, engine, game)
            if result.success:
                show_card_play_effect(card.name, current.name)
                print(f"🤖 电脑成功打出了 {card.name}！剩余法力: {current.current_mana}/{current.max_mana}")
                cards_played += 1
                # 短暂延迟显示结果
                dramatic_pause(1)
            else:
                print(f"🤖 打出 {card.name} 失败: {result.error}")
                break  # 如果失败，停止尝试出牌
        else:
            break  # 如果不能出这张卡，停止尝试

    # 3. 攻击阶段
    if has_attackers(current):
        animated_print("🤖 AI正在考虑攻击...", 0.05)
        dramatic_pause(1)
        perform_attacks_ai(engine, game)

    # 结束回合
    animated_print("🤖 电脑结束回合", 0.05)
    dramatic_pause(1)
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
                target_name = getattr(target, 'name', '对手英雄')
                print(f"🤖 {minion.name} 准备攻击 {target_name}...")
                dramatic_pause(1)

                result = engine.attack_with_minion(minion, target)
                if result.success:
                    show_attack_effect(minion.name, target_name, minion.attack)
                    print(f"🤖 {minion.name} 攻击了 {target_name}！")
                    attacks_made += 1
                else:
                    print(f"🤖 {minion.name} 攻击失败: {result.error}")

    # 英雄攻击（如果有武器）
    if current.weapon and current.weapon.durability > 0 and attacks_made < 2:
        target = choose_attack_target_ai(None, game)  # 英雄攻击
        if target:
            target_name = getattr(target, 'name', '对手英雄')
            print(f"🤖 英雄准备使用 {current.weapon.name} 攻击 {target_name}...")
            dramatic_pause(1)

            result = engine.attack_with_hero(target)
            if result.success:
                show_attack_effect("英雄", target_name, current.weapon.attack)
                print(f"🤖 英雄攻击了 {target_name}！")
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