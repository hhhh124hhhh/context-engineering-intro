"""
游戏引擎核心
实现TDD测试中定义的所有功能
"""

import random
import json
from typing import List, Optional, Dict, Any

from .cards import Card, CardType, create_starter_deck
from .state import GameState, Player, PlayResult


class GameEngine:
    """游戏引擎"""

    def __init__(self):
        self.games: Dict[str, GameState] = {}

    def create_game(self, player1_name: str, player2_name: str) -> GameState:
        """创建新游戏"""
        player1 = Player(1, player1_name)
        player2 = Player(2, player2_name)

        # 创建初始卡组
        deck1 = create_starter_deck()
        deck2 = create_starter_deck()

        # 洗牌
        random.shuffle(deck1)
        random.shuffle(deck2)

        # 设置牌库
        player1.deck = deck1
        player2.deck = deck2

        # 抽起始手牌（3张）
        for _ in range(3):
            player1.draw_card()
            player2.draw_card()

        # 创建游戏状态
        game = GameState(player1, player2)
        self.games[game.game_id] = game

        return game

    def play_card(self, card: Card, target=None) -> PlayResult:
        """打出卡牌"""
        game = self._get_current_game()
        if not game:
            return PlayResult(False, error="No active game")

        current = game.current_player

        # 检查法力值是否足够
        if card.cost > current.current_mana:
            return PlayResult(False, error="Insufficient mana")

        # 检查手牌中是否有这张卡
        if card not in current.hand:
            return PlayResult(False, error="Card not in hand")

        # 检查是否需要目标
        if card.needs_target and target is None:
            return PlayResult(False, error="This card requires a target")

        # 从手牌中移除
        current.hand.remove(card)

        # 消耗法力值
        current.current_mana -= card.cost

        # 根据卡牌类型执行效果
        if card.card_type == CardType.MINION:
            return self._play_minion_card(card, target, game)
        elif card.card_type == CardType.SPELL:
            return self._play_spell_card(card, target, game)
        elif card.card_type == CardType.WEAPON:
            return self._play_weapon_card(card, target, game)

        return PlayResult(True, "Card played successfully")

    def _play_minion_card(self, card: Card, target, game: GameState) -> PlayResult:
        """打出随从卡"""
        current = game.current_player

        # 如果没有冲锋，本回合不能攻击
        if not card.charge:
            card.can_attack = False
        else:
            card.can_attack = True

        # 加入战场
        current.battlefield.append(card)

        # 执行战吼效果
        if card.battlecry_damage > 0 and target:
            target.take_damage(card.battlecry_damage)

        return PlayResult(True, f"Minion {card.name} played")

    def _play_spell_card(self, card: Card, target, game: GameState) -> PlayResult:
        """打出法术卡"""
        # 执行法术效果
        if card.damage > 0 and target:
            if hasattr(target, 'take_damage'):
                target.take_damage(card.damage)
            else:
                # 如果是Hero对象，直接减少生命值
                if hasattr(target, 'health'):
                    target.health -= card.damage

        return PlayResult(True, f"Spell {card.name} cast")

    def _play_weapon_card(self, card: Card, target, game: GameState) -> PlayResult:
        """打出武器卡"""
        current = game.current_player

        # 装备武器
        from .cards import Weapon
        current.weapon = Weapon(card.attack, card.health, card.name)

        return PlayResult(True, f"Weapon {card.name} equipped")

    def attack_with_minion(self, attacker: Card, target) -> PlayResult:
        """随从攻击"""
        game = self._get_current_game()
        if not game:
            return PlayResult(False, error="No active game")

        current = game.current_player

        # 检查随从是否可以攻击
        if attacker not in current.battlefield:
            return PlayResult(False, error="Minion not on battlefield")

        if not attacker.can_attack:
            return PlayResult(False, error="Minion cannot attack this turn")

        # 检查嘲讽机制（只对随从攻击有效）
        if hasattr(target, 'health') and hasattr(target, 'taunt'):  # 攻击随从
            if not target.taunt:
                taunt_minions = [m for m in game.opponent.battlefield if m.taunt]
                if taunt_minions:
                    return PlayResult(False, error="Must attack taunt minion first")

        # 判断攻击目标类型
        if hasattr(target, 'health') and hasattr(target, 'attack'):  # 攻击随从
            return self._minion_attack_minion(attacker, target, game)
        else:  # 攻击英雄
            return self._minion_attack_hero(attacker, target, game)

    def _minion_attack_minion(self, attacker: Card, defender: Card, game: GameState) -> PlayResult:
        """随从攻击随从"""
        # 确保defender是Card对象
        if not isinstance(defender, Card):
            return PlayResult(False, error="Target must be a minion")

        # 处理圣盾
        defender_died = False
        if defender.divine_shield:
            defender.divine_shield = False
        else:
            defender.health -= attacker.attack
            if defender.health <= 0:
                defender_died = True

        attacker_died = False
        if attacker.divine_shield:
            attacker.divine_shield = False
        else:
            attacker.health -= defender.attack
            if attacker.health <= 0:
                attacker_died = True

        # 随从本回合不能再次攻击
        attacker.can_attack = False

        # 移除死亡的随从（只移除真正死亡的）
        if defender_died:
            # 执行亡语效果
            if defender.deathrattle_draw > 0:
                for _ in range(defender.deathrattle_draw):
                    game.opponent.draw_card()

            # 从战场移除
            if defender in game.opponent.battlefield:
                game.opponent.battlefield.remove(defender)

        if attacker_died:
            # 执行亡语效果
            if attacker.deathrattle_draw > 0:
                for _ in range(attacker.deathrattle_draw):
                    game.current_player.draw_card()

            # 从战场移除
            if attacker in game.current_player.battlefield:
                game.current_player.battlefield.remove(attacker)

        return PlayResult(True, "Minion attack completed")

    def _minion_attack_hero(self, attacker: Card, hero, game: GameState) -> PlayResult:
        """随从攻击英雄"""
        # 确保攻击者是随从
        if not isinstance(attacker, Card):
            return PlayResult(False, error="Attacker must be a minion")

        # 攻击英雄
        if hasattr(hero, 'take_damage'):
            hero.take_damage(attacker.attack)
        elif hasattr(hero, 'health'):
            hero.health -= attacker.attack

        attacker.can_attack = False

        return PlayResult(True, "Minion attacked hero")

    def attack_with_hero(self, target) -> PlayResult:
        """英雄攻击"""
        game = self._get_current_game()
        if not game:
            return PlayResult(False, error="No active game")

        current = game.current_player

        if not current.weapon:
            return PlayResult(False, error="No weapon equipped")

        # 确定目标是对手玩家还是随从
        if hasattr(target, 'player_id'):  # 是随从
            # 随从伤害处理
            if hasattr(target, 'divine_shield') and target.divine_shield:
                target.divine_shield = False
            else:
                target.health -= current.weapon.attack
                # 检查随从是否死亡
                if target.health <= 0:
                    # 从战场移除
                    if target in game.opponent.battlefield:
                        game.opponent.battlefield.remove(target)
        else:  # 是英雄
            # 找到拥有这个英雄的玩家
            if target == game.opponent.hero:
                game.opponent.take_damage(current.weapon.attack)
            else:
                current.take_damage(current.weapon.attack)

        current.weapon.durability -= 1

        # 武器耐久度为0时破坏
        if current.weapon.durability <= 0:
            current.weapon = None

        return PlayResult(True, "Hero attack completed")

    def end_turn(self):
        """结束当前回合"""
        game = self._get_current_game()
        if game:
            # 只执行回合结束操作，不立即开始新回合
            game.end_turn()

    def start_turn(self):
        """开始新回合（由游戏流程控制调用）"""
        game = self._get_current_game()
        if game:
            game.start_new_turn()

    def check_win_condition(self):
        """检查胜负条件"""
        game = self._get_current_game()
        if game:
            game.check_win_condition()

    def save_game_state(self) -> Dict[str, Any]:
        """保存游戏状态"""
        game = self._get_current_game()
        if game:
            return game.to_dict()
        return {}

    def load_game_state(self, state_data: Dict[str, Any]) -> GameState:
        """加载游戏状态"""
        # 简化实现，实际需要完整的状态重建
        player1 = Player(1, state_data['player1']['name'])
        player2 = Player(2, state_data['player2']['name'])

        game = GameState(player1, player2)
        game.game_id = state_data['game_id']
        game.current_player_index = 0 if state_data['current_player'] == 1 else 1
        game.turn_number = state_data['turn_number']

        self.games[game.game_id] = game
        return game

    def ai_make_decision(self, player: Player):
        """AI决策"""
        # 简单的AI实现
        possible_actions = []

        # 检查可以打出的卡牌
        for card in player.hand:
            if card.cost <= player.current_mana:
                possible_actions.append({
                    'action': 'play_card',
                    'card': card,
                    'priority': card.cost  # 优先打出低费卡
                })

        # 检查可以攻击的随从
        for minion in player.battlefield:
            if minion.can_attack:
                possible_actions.append({
                    'action': 'attack',
                    'attacker': minion,
                    'priority': minion.attack  # 优先攻击力高的
                })

        # 如果没有可用动作，结束回合
        if not possible_actions:
            return {'action': 'end_turn'}

        # 选择优先级最高的动作
        action = min(possible_actions, key=lambda x: x['priority'])
        return action

    def create_ai_player(self, name: str, difficulty: str = "normal"):
        """创建AI玩家"""
        return Player(999, name)  # 简化实现

    def _get_current_game(self) -> Optional[GameState]:
        """获取当前游戏（简化实现）"""
        if self.games:
            return list(self.games.values())[0]
        return None

    def use_hero_power(self) -> PlayResult:
        """使用英雄技能"""
        game = self._get_current_game()
        if not game:
            return PlayResult(False, error="No active game")

        current = game.current_player

        # 验证使用条件
        if current.used_hero_power:
            return PlayResult(False, error="Hero power already used this turn")

        if current.current_mana < 2:
            return PlayResult(False, error="Insufficient mana for hero power")

        # 消耗法力值
        current.current_mana -= 2
        current.used_hero_power = True

        # 应用英雄技能效果
        self._apply_hero_power_effect(current, game.opponent)

        # 记录历史
        game.history.append({
            'action': 'use_hero_power',
            'player': current.player_id,
            'cost': 2
        })

        return PlayResult(True, "Hero power used successfully")

    def _apply_hero_power_effect(self, player: Player, opponent: Player):
        """应用英雄技能效果"""
        # 基础英雄技能：造成1点伤害
        opponent.hero.health -= 1

        # 记录到历史
        print(f"{player.name} 使用英雄技能，造成1点伤害")

    def _remove_dead_minions(self, game: GameState):
        """移除死亡的随从"""
        for player in [game.player1, game.player2]:
            # 移除死亡的随从
            dead_minions = [m for m in player.battlefield if m.health <= 0]
            for minion in dead_minions:
                # 执行亡语效果
                if minion.deathrattle_draw > 0:
                    for _ in range(minion.deathrattle_draw):
                        player.draw_card()

                # 从战场移除
                player.battlefield.remove(minion)