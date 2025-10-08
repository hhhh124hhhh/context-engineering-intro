"""
游戏状态管理
"""

import random
import uuid
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field

from .cards import Card, CardType, Weapon, Hero


@dataclass
class PlayResult:
    """游戏动作结果"""
    success: bool
    message: str = ""
    error: str = ""


class Player:
    """玩家状态"""

    def __init__(self, player_id: int, name: str):
        self.player_id = player_id
        self.name = name
        self.hero = Hero(player_id, name, 30)

        # 手牌和牌库
        self.hand: List[Card] = []
        self.deck: List[Card] = []
        self.battlefield: List[Card] = []

        # 法力值
        self.current_mana = 1
        self.max_mana = 1

        # 武器
        self.weapon: Optional[Weapon] = None

        # 游戏标志
        self.used_hero_power = False

    def draw_card(self) -> Optional[Card]:
        """抽牌"""
        if not self.deck:
            # 牌库空了，受到疲劳伤害
            fatigue_damage = len([c for c in self.hand if hasattr(c, 'fatigue_damage')]) + 1
            self.hero.health -= fatigue_damage
            return None

        card = self.deck.pop(0)
        self.hand.append(card)
        return card

    def enforce_hand_limit(self):
        """强制执行手牌上限（7张）"""
        while len(self.hand) > 7:
            # 弃掉多余的牌
            discarded = self.hand.pop()
            print(f"{self.name} 弃掉了 {discarded.name}")

    def take_damage(self, damage: int):
        """受到伤害"""
        # 先扣护甲，再扣生命值
        if self.hero.armor > 0:
            armor_to_take = min(damage, self.hero.armor)
            self.hero.armor -= armor_to_take
            damage -= armor_to_take

        self.hero.health -= damage

    def heal(self, amount: int):
        """治疗"""
        self.hero.health = min(self.hero.health + amount, 30)


class GameState:
    """游戏状态"""

    def __init__(self, player1: Player, player2: Player):
        self.game_id = str(uuid.uuid4())
        self.player1 = player1
        self.player2 = player2

        # 游戏状态
        self.current_player_index = 0  # 0 = player1, 1 = player2
        self.turn_number = 1
        self.phase = "main"  # draw, main, end
        self.game_over = False
        self.winner: Optional[int] = None

        # 游戏历史
        self.history: List[Dict[str, Any]] = []

    @property
    def current_player(self) -> Player:
        """当前玩家"""
        return self.player1 if self.current_player_index == 0 else self.player2

    @property
    def opponent(self) -> Player:
        """对手"""
        return self.player2 if self.current_player_index == 0 else self.player1

    def start_new_turn(self):
        """开始新回合"""
        # 切换玩家
        self.current_player_index = 1 - self.current_player_index
        if self.current_player_index == 0:
            self.turn_number += 1

        current = self.current_player

        # 增加法力值上限（最多10）
        if current.max_mana < 10:
            current.max_mana += 1

        # 恢复法力值
        current.current_mana = current.max_mana

        # 重置英雄技能使用状态
        current.used_hero_power = False

        # 抽牌
        current.draw_card()

        # 战场上的随从可以攻击
        for minion in current.battlefield:
            minion.can_attack = True

        # 记录历史
        self.history.append({
            'action': 'start_turn',
            'player': current.player_id,
            'turn': self.turn_number,
            'mana': current.current_mana
        })

    def end_turn(self):
        """结束回合"""
        current = self.current_player

        # 执行手牌上限检查
        current.enforce_hand_limit()

        # 记录历史
        self.history.append({
            'action': 'end_turn',
            'player': current.player_id,
            'turn': self.turn_number
        })

    def check_win_condition(self):
        """检查胜负条件"""
        if self.player1.hero.health <= 0:
            self.game_over = True
            self.winner = self.player2.player_id
        elif self.player2.hero.health <= 0:
            self.game_over = True
            self.winner = self.player1.player_id

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'game_id': self.game_id,
            'current_player': self.current_player.player_id,
            'turn_number': self.turn_number,
            'phase': self.phase,
            'game_over': self.game_over,
            'winner': self.winner,
            'player1': {
                'player_id': self.player1.player_id,
                'name': self.player1.name,
                'health': self.player1.hero.health,
                'armor': self.player1.hero.armor,
                'current_mana': self.player1.current_mana,
                'max_mana': self.player1.max_mana,
                'hand_count': len(self.player1.hand),
                'battlefield_count': len(self.player1.battlefield),
                'deck_count': len(self.player1.deck),
                'hand': [self._card_to_dict(card) for card in self.player1.hand],
                'battlefield': [self._card_to_dict(card) for card in self.player1.battlefield]
            },
            'player2': {
                'player_id': self.player2.player_id,
                'name': self.player2.name,
                'health': self.player2.hero.health,
                'armor': self.player2.hero.armor,
                'current_mana': self.player2.current_mana,
                'max_mana': self.player2.max_mana,
                'hand_count': len(self.player2.hand),
                'battlefield_count': len(self.player2.battlefield),
                'deck_count': len(self.player2.deck),
                'hand': [self._card_to_dict(card) for card in self.player2.hand],
                'battlefield': [self._card_to_dict(card) for card in self.player2.battlefield]
            }
        }

    def _card_to_dict(self, card: Card) -> Dict[str, Any]:
        """卡牌转字典"""
        return {
            'id': card.id,
            'name': card.name,
            'cost': card.cost,
            'attack': card.attack,
            'health': card.health,
            'type': card.card_type.value,
            'charge': card.charge,
            'taunt': card.taunt,
            'divine_shield': card.divine_shield,
            'can_attack': card.can_attack
        }