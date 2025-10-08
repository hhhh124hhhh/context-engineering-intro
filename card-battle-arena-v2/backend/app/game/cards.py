"""
卡牌定义和基础卡组
"""

from typing import List
from dataclasses import dataclass
from enum import Enum


class CardType(Enum):
    """卡牌类型"""
    MINION = "minion"
    SPELL = "spell"
    WEAPON = "weapon"


@dataclass
class Card:
    """游戏卡牌"""
    id: int
    name: str
    cost: int
    attack: int
    health: int
    card_type: CardType

    # 基础特殊属性
    charge: bool = False          # 冲锋
    taunt: bool = False           # 嘲讽
    divine_shield: bool = False   # 圣盾
    windfury: bool = False        # 风怒
    stealth: bool = False         # 潜行
    can_attack: bool = False     # 本回合是否可以攻击

    # 基础效果
    battlecry_damage: int = 0     # 战吼伤害
    deathrattle_draw: int = 0     # 亡语抽牌数
    needs_target: bool = False    # 是否需要目标
    damage: int = 0              # 法术伤害值

    # 新增策略性关键词
    spell_damage: int = 0       # 法术伤害加成（对法术牌）
    lifelink: bool = False        # 吸血
    poison: bool = False        # 中毒（回合结束时造成伤害）
    reborn: bool = False        # 复生（死亡时返回手牌）
    echo: bool = False          # 回响（重复本回合效果）
    rush: bool = False          # 突袭（对英雄额外伤害）

    # Buff/Debuff效果
    buff_attack: int = 0        # 攻击力buff
    buff_health: int = 0        # 生命值buff
    taunt_buff: bool = False     # 获得嘲讽
    divine_shield_buff: bool = False  # 获得圣盾

    # 资源效果
    card_draw: int = 0          # 抽牌效果
    heal_amount: int = 0        # 治疗效果
    mana_gain: int = 0         # 法力值增益

    # 进阶效果
    combo_effect: bool = False    # 连击效果
    secret_card: bool = False     # 秘密牌
    quest_progress: int = 0      # 任务进度
    aura_effect: bool = False     # 光环效果


@dataclass
class Weapon:
    """武器"""
    attack: int
    durability: int
    name: str


@dataclass
class Hero:
    """英雄"""
    player_id: int
    name: str
    health: int
    armor: int = 0


def create_basic_card_set() -> List[Card]:
    """创建基础卡组"""
    cards = []

    # 1费随从 (基础)
    cards.append(Card(1, "新手战士", 1, 1, 2, CardType.MINION, charge=True))
    cards.append(Card(2, "血色十字军", 1, 2, 1, CardType.MINION))
    cards.append(Card(3, "狼人渗透者", 1, 1, 1, CardType.MINION, stealth=True))

    # 新增1费策略性随从
    cards.append(Card(4, "鱼人招潮者", 1, 1, 2, CardType.MINION, card_draw=1))
    cards.append(Card(5, "光明祭司", 1, 0, 2, CardType.MINION, heal_amount=2))
    cards.append(Card(6, "暗影潜伏者", 1, 1, 1, CardType.MINION, stealth=True, poison=True))
    cards.append(Card(7, "狂野战士", 1, 2, 1, CardType.MINION, rush=True))
    cards.append(Card(8, "奥术学徒", 1, 1, 1, CardType.MINION, spell_damage=1))

    # 2费随从
    cards.append(Card(9, "铁炉堡火枪手", 2, 2, 2, CardType.MINION))
    cards.append(Card(10, "暴风城卫兵", 2, 1, 3, CardType.MINION, taunt=True))
    cards.append(Card(11, "迅猛龙", 2, 2, 1, CardType.MINION, charge=True))

    # 新增2费策略性随从
    cards.append(Card(12, "年轻的女祭司", 2, 1, 3, CardType.MINION, heal_amount=2, taunt=True))
    cards.append(Card(13, "暗影刺客", 2, 2, 2, CardType.MINION, stealth=True, combo_effect=True))
    cards.append(Card(14, "熔岩元素", 2, 2, 3, CardType.MINION, taunt=True))
    cards.append(Card(15, "野性之灵", 2, 3, 1, CardType.MINION, charge=True))

    # 3费随从
    cards.append(Card(16, "肯瑞托法师", 3, 2, 3, CardType.MINION))
    cards.append(Card(17, "铁炉堡传送门", 3, 2, 4, CardType.MINION))
    cards.append(Card(18, "银色侍从", 3, 3, 3, CardType.MINION, divine_shield=True))

    # 新增3费策略性随从
    cards.append(Card(19, "圣光护卫", 3, 1, 4, CardType.MINION, taunt=True, divine_shield=True))
    cards.append(Card(20, "暗影牧师", 3, 2, 3, CardType.MINION, heal_amount=2, card_draw=1))
    cards.append(Card(21, "狂战士", 3, 3, 3, CardType.MINION, windfury=True, rush=True))
    cards.append(Card(22, "自然之怒", 3, 2, 4, CardType.MINION, taunt=True))

    # 4费随从
    cards.append(Card(23, "暴怒狼人", 4, 4, 4, CardType.MINION, charge=True, windfury=True))
    cards.append(Card(24, "暴风城指挥官", 4, 3, 5, CardType.MINION, taunt=True))
    cards.append(Card(25, "血骑士", 4, 4, 5, CardType.MINION, lifelink=True))

    # 新增4费策略性随从
    cards.append(Card(26, "光明之主", 4, 4, 6, CardType.MINION, divine_shield=True))
    cards.append(Card(27, "暗影牧师", 4, 3, 5, CardType.MINION, card_draw=2))
    cards.append(Card(28, "元素萨满", 4, 2, 5, CardType.MINION, taunt=True, aura_effect=True))

    # 法术卡
    fireball = Card(101, "火球术", 4, 0, 0, CardType.SPELL)
    fireball.damage = 6
    fireball.needs_target = True
    cards.append(fireball)

    frostbolt = Card(102, "寒冰箭", 2, 0, 0, CardType.SPELL)
    frostbolt.damage = 3
    frostbolt.needs_target = True
    cards.append(frostbolt)

    # 新增策略性法术卡
    arcane_intellect = Card(103, "奥术智慧", 2, 0, 0, CardType.SPELL)
    arcane_intellect.card_draw = 2
    cards.append(arcane_intellect)

    heal = Card(104, "治疗之触", 1, 0, 0, CardType.SPELL)
    heal.heal_amount = 5
    heal.needs_target = True
    cards.append(heal)

    arcane_blast = Card(105, "奥术飞弹", 1, 0, 0, CardType.SPELL)
    arcane_blast.damage = 2
    arcane_blast.needs_target = True
    arcane_blast.spell_damage = 1  # 法术加成
    cards.append(arcane_blast)

    # 武器卡
    dagger = Card(201, "刺客之刃", 1, 1, 2, CardType.WEAPON)
    cards.append(dagger)

    sword = Card(202, "炽炎战斧", 2, 3, 2, CardType.WEAPON)
    cards.append(sword)

    # 新增策略性武器卡
    truesilver = Card(203, "真银圣剑", 3, 4, 3, CardType.WEAPON, divine_shield=True)
    cards.append(truesilver)

    doomhammer = Card(204, "毁灭之锤", 5, 8, 5, CardType.WEAPON, windfury=True)
    cards.append(doomhammer)

    return cards


def create_starter_deck() -> List[Card]:
    """创建新手卡组"""
    deck = []
    basic_cards = create_basic_card_set()

    # 每张基础卡牌放2张，组成30张卡组
    for card in basic_cards[:15]:  # 前15张卡
        deck.append(card)
        # 创建卡牌副本（不同的实例ID）
        card_copy = Card(
            card.id + 1000,  # 不同的ID
            card.name,
            card.cost,
            card.attack,
            card.health,
            card.card_type,
            card.charge,
            card.taunt,
            card.divine_shield,
            card.windfury,
            card.stealth,
            card.can_attack,
            card.battlecry_damage,
            card.deathrattle_draw,
            card.needs_target,
            card.damage
        )
        deck.append(card_copy)

    return deck[:30]  # 确保30张卡