from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
import structlog
from datetime import datetime, timezone

logger = structlog.get_logger()


class CardType(Enum):
    """卡牌类型"""
    MINION = "minion"
    SPELL = "spell"
    WEAPON = "weapon"
    HERO_POWER = "hero_power"


class CardRarity(Enum):
    """卡牌稀有度"""
    COMMON = "common"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


class CardClass(Enum):
    """卡牌职业"""
    WARRIOR = "warrior"
    MAGE = "mage"
    HUNTER = "hunter"
    ROGUE = "rogue"
    PRIEST = "priest"
    WARLOCK = "warlock"
    SHAMAN = "shaman"
    PALADIN = "paladin"
    DRUID = "druid"
    NEUTRAL = "neutral"


class GamePhase(Enum):
    """游戏阶段"""
    MULLIGAN = "mulligan"
    MAIN = "main"
    END = "end"


class TurnPhase(Enum):
    """回合阶段"""
    DRAW = "draw"
    MAIN = "main"
    END = "end"


@dataclass
class Card:
    """游戏中的卡牌"""
    id: int
    instance_id: str
    name: str
    card_type: CardType
    rarity: CardRarity
    card_class: CardClass
    cost: int
    attack: Optional[int] = None
    defense: Optional[int] = None
    durability: Optional[int] = None
    mechanics: List[str] = field(default_factory=list)
    effects: List[str] = field(default_factory=list)

    # 动态属性
    current_cost: int = field(init=False)
    current_attack: Optional[int] = field(init=False)
    current_defense: Optional[int] = field(init=False)
    current_durability: Optional[int] = field(init=False)
    is_dormant: bool = False
    is_silenced: bool = False
    is_frozen: bool = False
    attack_count: int = 0
    summoning_sickness: bool = True
    enchantments: List[Dict[str, Any]] = field(default_factory=list)

    # 位置信息
    location: str = "deck"  # deck, hand, battlefield, graveyard, secret, removed
    position: Optional[int] = None
    controller: Optional[int] = None

    def __post_init__(self):
        self.current_cost = self.cost
        self.current_attack = self.attack
        self.current_defense = self.defense
        self.current_durability = self.durability
        self.instance_id = self.instance_id or str(uuid.uuid4())

    @property
    def is_minion(self) -> bool:
        return self.card_type == CardType.MINION

    @property
    def is_spell(self) -> bool:
        return self.card_type == CardType.SPELL

    @property
    def is_weapon(self) -> bool:
        return self.card_type == CardType.WEAPON

    @property
    def effective_attack(self) -> int:
        return self.current_attack or 0

    @property
    def effective_defense(self) -> int:
        return self.current_defense or 0

    @property
    def effective_durability(self) -> int:
        return self.current_durability or 0

    @property
    def effective_cost(self) -> int:
        return max(0, self.current_cost)

    def can_attack(self) -> bool:
        """检查是否可以攻击"""
        if not self.is_minion or self.is_dormant or self.is_frozen:
            return False
        if self.summoning_sickness and "charge" not in self.mechanics:
            return False
        max_attacks = 2 if "windfury" in self.mechanics else 1
        return self.attack_count < max_attacks and self.effective_attack > 0


@dataclass
class Player:
    """游戏玩家"""
    user_id: int
    username: str
    player_number: int  # 1 or 2

    # 基础属性
    health: int = 30
    max_health: int = 30
    armor: int = 0
    mana: int = 1
    max_mana: int = 1
    overload: int = 0
    next_turn_overload: int = 0

    # 卡牌
    deck: List[Card] = field(default_factory=list)
    hand: List[Card] = field(default_factory=list)
    battlefield: List[Card] = field(default_factory=list)
    secrets: List[Card] = field(default_factory=list)
    graveyard: List[Card] = field(default_factory=list)
    removed: List[Card] = field(default_factory=list)

    # 英雄和武器
    hero: Optional[Card] = None
    weapon: Optional[Card] = None
    hero_power: Optional[Card] = None

    # 状态
    is_connected: bool = True
    has_conceded: bool = False
    spells_played_this_turn: int = 0
    minions_played_this_turn: int = 0

    def __post_init__(self):
        # 创建默认英雄（这里应该从数据库获取）
        if not self.hero:
            self.hero = Card(
                id=0,
                instance_id=f"hero_{self.user_id}",
                name="Hero",
                card_type=CardType.HERO_POWER,
                rarity=CardRarity.COMMON,
                card_class=CardClass.NEUTRAL,
                cost=0,
                attack=0,
                defense=30
            )

    @property
    def effective_health(self) -> int:
        return self.health + self.armor

    @property
    def is_alive(self) -> bool:
        return self.health > 0

    @property
    def available_mana(self) -> int:
        return max(0, self.max_mana - self.overload)

    @property
    def hand_size(self) -> int:
        return len(self.hand)

    @property
    def battlefield_size(self) -> int:
        return len(self.battlefield)

    @property
    def deck_size(self) -> int:
        return len(self.deck)

    def take_damage(self, damage: int) -> int:
        """承受伤害"""
        actual_damage = damage

        # 先扣除护甲
        if self.armor > 0:
            armor_damage = min(self.armor, actual_damage)
            self.armor -= armor_damage
            actual_damage -= armor_damage

        # 扣除生命值
        if actual_damage > 0:
            self.health -= actual_damage
            if self.health < 0:
                self.health = 0

        return damage

    def heal(self, amount: int) -> int:
        """治疗"""
        max_heal = self.max_health - self.health
        actual_heal = min(amount, max_heal)
        self.health += actual_heal
        return actual_heal

    def gain_armor(self, amount: int) -> int:
        """获得护甲"""
        self.armor += amount
        return amount

    def can_play_card(self, card: Card) -> bool:
        """检查是否可以出牌"""
        if card not in self.hand:
            return False
        if card.effective_cost > self.available_mana:
            return False
        if card.is_minion and self.battlefield_size >= 7:
            return False
        if card.is_weapon and self.weapon is not None:
            return False
        return True

    def play_card(self, card: Card) -> bool:
        """出牌"""
        if not self.can_play_card(card):
            return False

        # 扣除法力值
        self.mana -= card.effective_cost

        # 从手牌移除
        self.hand.remove(card)
        card.controller = self.user_id

        # 统计
        if card.is_spell:
            self.spells_played_this_turn += 1
        elif card.is_minion:
            self.minions_played_this_turn += 1

        return True

    def draw_card(self) -> Optional[Card]:
        """抽牌"""
        if not self.deck:
            # 疲劳伤害
            fatigue_damage = len(self.graveyard) + 1
            self.take_damage(fatigue_damage)
            return None

        card = self.deck.pop()
        if len(self.hand) < 10:
            self.hand.append(card)
        else:
            # 手牌已满，牌被摧毁
            self.graveyard.append(card)

        return card

    def shuffle_deck(self):
        """洗牌"""
        import random
        random.shuffle(self.deck)

    def end_turn(self):
        """结束回合"""
        # 清除临时状态
        self.mana = self.max_mana
        self.overload = self.next_turn_overload
        self.next_turn_overload = 0
        self.spells_played_this_turn = 0
        self.minions_played_this_turn = 0

        # 清除随从的召唤疲劳
        for minion in self.battlefield:
            minion.summoning_sickness = False
            minion.attack_count = 0
            minion.is_frozen = False

    def start_turn(self):
        """开始回合"""
        # 增加法力水晶
        if self.max_mana < 10:
            self.max_mana += 1
        self.mana = self.max_mana - self.overload

        # 抽一张牌
        self.draw_card()


@dataclass
class GameState:
    """游戏状态"""
    game_id: str
    player1: Player
    player2: Player
    current_player_number: int = 1
    turn_number: int = 1
    phase: GamePhase = GamePhase.MAIN
    turn_phase: TurnPhase = TurnPhase.DRAW

    # 游戏记录
    action_history: List[Dict[str, Any]] = field(default_factory=list)
    turn_history: List[Dict[str, Any]] = field(default_factory=list)

    # 游戏配置
    turn_time_limit: int = 90
    format_type: str = "standard"
    game_mode: str = "ranked"

    # 时间戳
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    current_turn_started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self):
        if not self.game_id:
            self.game_id = str(uuid.uuid4())

    @property
    def current_player(self) -> Player:
        return self.player1 if self.current_player_number == 1 else self.player2

    @property
    def opponent(self) -> Player:
        return self.player2 if self.current_player_number == 1 else self.player1

    def get_player(self, user_id: int) -> Optional[Player]:
        """根据用户ID获取玩家"""
        if self.player1.user_id == user_id:
            return self.player1
        elif self.player2.user_id == user_id:
            return self.player2
        return None

    def switch_turn(self):
        """切换回合"""
        # 结束当前玩家回合
        self.current_player.end_turn()

        # 记录回合历史
        self.turn_history.append({
            "turn_number": self.turn_number,
            "player": self.current_player_number,
            "ended_at": datetime.now(timezone.utc).isoformat(),
            "player_state": self._get_player_state(self.current_player)
        })

        # 切换玩家
        self.current_player_number = 2 if self.current_player_number == 1 else 1
        self.turn_number += 1
        self.current_turn_started_at = datetime.now(timezone.utc)

        # 开始新回合
        self.current_player.start_turn()
        self.turn_phase = TurnPhase.MAIN

        # 记录动作
        self._add_action("turn_switched", {
            "new_player": self.current_player_number,
            "turn_number": self.turn_number
        })

    def _get_player_state(self, player: Player) -> Dict[str, Any]:
        """获取玩家状态快照"""
        return {
            "health": player.health,
            "armor": player.armor,
            "mana": player.mana,
            "max_mana": player.max_mana,
            "hand_size": player.hand_size,
            "battlefield_size": player.battlefield_size,
            "deck_size": player.deck_size
        }

    def _add_action(self, action_type: str, data: Dict[str, Any] = None):
        """添加动作记录"""
        action = {
            "type": action_type,
            "player": self.current_player_number,
            "turn": self.turn_number,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": data or {}
        }
        self.action_history.append(action)

    def is_game_over(self) -> bool:
        """检查游戏是否结束"""
        return not self.player1.is_alive or not self.player2.is_alive or self.player1.has_conceded or self.player2.has_conceded

    def get_winner(self) -> Optional[Player]:
        """获取胜利者"""
        if not self.is_game_over():
            return None

        if self.player1.has_conceded or not self.player1.is_alive:
            return self.player2
        elif self.player2.has_conceded or not self.player2.is_alive:
            return self.player1

        return None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式（用于序列化）"""
        return {
            "game_id": self.game_id,
            "player1": {
                "user_id": self.player1.user_id,
                "username": self.player1.username,
                "health": self.player1.health,
                "armor": self.player1.armor,
                "mana": self.player1.mana,
                "max_mana": self.player1.max_mana,
                "hand_size": self.player1.hand_size,
                "battlefield_size": self.player1.battlefield_size,
                "deck_size": self.player1.deck_size
            },
            "player2": {
                "user_id": self.player2.user_id,
                "username": self.player2.username,
                "health": self.player2.health,
                "armor": self.player2.armor,
                "mana": self.player2.mana,
                "max_mana": self.player2.max_mana,
                "hand_size": self.player2.hand_size,
                "battlefield_size": self.player2.battlefield_size,
                "deck_size": self.player2.deck_size
            },
            "current_player": self.current_player_number,
            "turn_number": self.turn_number,
            "phase": self.phase.value,
            "turn_phase": self.turn_phase.value,
            "is_game_over": self.is_game_over(),
            "winner": self.get_winner().user_id if self.get_winner() else None
        }