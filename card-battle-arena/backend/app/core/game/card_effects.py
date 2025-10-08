from typing import Dict, List, Any, Optional, Callable
from abc import ABC, abstractmethod
import structlog
from enum import Enum

from app.core.game.state import Card, Player, GameState

logger = structlog.get_logger()


class EffectType(Enum):
    """效果类型"""
    DAMAGE = "damage"
    HEAL = "heal"
    BUFF = "buff"
    DEBUFF = "debuff"
    SUMMON = "summon"
    DESTROY = "destroy"
    DRAW = "draw"
    MANA = "mana"
    ARMOR = "armor"
    SILENCE = "silence"
    FREEZE = "freeze"
    TAUNT = "taunt"
    CHARGE = "charge"
    WINDFURY = "windfury"
    STEALTH = "stealth"
    DIVINE_SHIELD = "divine_shield"
    POISONOUS = "poisonous"
    LIFESTEAL = "lifesteal"


class CardEffect(ABC):
    """卡牌效果基类"""

    def __init__(self, effect_type: EffectType, value: int = 0):
        self.effect_type = effect_type
        self.value = value

    @abstractmethod
    async def apply(self, card: Card, game_state: GameState, player: Player, target_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """应用效果"""
        pass


class DamageEffect(CardEffect):
    """伤害效果"""

    async def apply(self, card: Card, game_state: GameState, player: Player, target_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        target_type = target_data.get("type") if target_data else None
        target_id = target_data.get("id") if target_data else None

        damage = self.value

        if target_type == "minion" and target_id:
            # 攻击随从
            opponent = game_state.opponent
            target = self._find_minion_by_id(opponent, target_id)
            if target:
                # 处理神圣护盾
                if "divine_shield" in target.mechanics:
                    target.mechanics.remove("divine_shield")
                    return {"success": True, "divine_shield_blocked": True}

                # 造成伤害
                target.current_defense -= damage

                # 检查死亡
                if target.effective_defense <= 0:
                    opponent.battlefield.remove(target)
                    target.location = "graveyard"
                    opponent.graveyard.append(target)

                return {
                    "success": True,
                    "damage": damage,
                    "target": target.instance_id,
                    "target_survived": target.effective_defense > 0
                }

        elif target_type == "hero":
            # 攻击英雄
            opponent = game_state.opponent
            actual_damage = opponent.take_damage(damage)

            return {
                "success": True,
                "damage": actual_damage,
                "target_health": opponent.health,
                "target_armor": opponent.armor
            }

        return {"success": False, "error": "Invalid target"}

    def _find_minion_by_id(self, player: Player, instance_id: str) -> Optional[Card]:
        """根据实例ID查找随从"""
        for minion in player.battlefield:
            if minion.instance_id == instance_id:
                return minion
        return None


class HealEffect(CardEffect):
    """治疗效果"""

    async def apply(self, card: Card, game_state: GameState, player: Player, target_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        target_type = target_data.get("type") if target_data else "hero"
        target_id = target_data.get("id") if target_data else None

        heal_amount = self.value

        if target_type == "minion" and target_id:
            # 治疗随从
            target = self._find_minion_by_id(player, target_id)
            if target:
                actual_heal = min(heal_amount, target.defense - target.effective_defense)
                target.current_defense += actual_heal

                return {
                    "success": True,
                    "heal": actual_heal,
                    "target": target.instance_id,
                    "new_defense": target.effective_defense
                }

        elif target_type == "hero":
            # 治疗英雄
            actual_heal = player.heal(heal_amount)

            return {
                "success": True,
                "heal": actual_heal,
                "new_health": player.health
            }

        return {"success": False, "error": "Invalid target"}

    def _find_minion_by_id(self, player: Player, instance_id: str) -> Optional[Card]:
        """根据实例ID查找随从"""
        for minion in player.battlefield:
            if minion.instance_id == instance_id:
                return minion
        return None


class BuffEffect(CardEffect):
    """增益效果"""

    async def apply(self, card: Card, game_state: GameState, player: Player, target_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        target_type = target_data.get("type") if target_data else "minion"
        target_id = target_data.get("id") if target_data else None

        if target_type == "minion" and target_id:
            target = self._find_minion_by_id(player, target_id)
            if target:
                # 应用增益（这里简化为增加攻击力和生命值）
                attack_buff = self.value
                defense_buff = self.value

                target.current_attack = (target.current_attack or 0) + attack_buff
                target.current_defense = (target.current_defense or 0) + defense_buff

                return {
                    "success": True,
                    "attack_buff": attack_buff,
                    "defense_buff": defense_buff,
                    "target": target.instance_id,
                    "new_attack": target.effective_attack,
                    "new_defense": target.effective_defense
                }

        return {"success": False, "error": "Invalid target"}

    def _find_minion_by_id(self, player: Player, instance_id: str) -> Optional[Card]:
        """根据实例ID查找随从"""
        for minion in player.battlefield:
            if minion.instance_id == instance_id:
                return minion
        return None


class SummonEffect(CardEffect):
    """召唤效果"""

    async def apply(self, card: Card, game_state: GameState, player: Player, target_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        # 这里应该指定要召唤的随从，简化处理
        # 假设效果中包含要召唤的随从信息
        summon_data = target_data.get("summon_data") if target_data else None

        if not summon_data:
            return {"success": False, "error": "No summon data provided"}

        # 创建要召唤的随从（这里简化处理）
        from app.core.game.state import Card, CardType, CardRarity, CardClass
        summoned_minion = Card(
            id=summon_data.get("id", 0),
            instance_id=f"summoned_{card.instance_id}_{summon_data.get('id', 0)}",
            name=summon_data.get("name", "Summoned Minion"),
            card_type=CardType.MINION,
            rarity=CardRarity.COMMON,
            card_class=CardClass.NEUTRAL,
            cost=0,
            attack=summon_data.get("attack", 1),
            defense=summon_data.get("defense", 1),
            mechanics=summon_data.get("mechanics", [])
        )

        # 检查战场空间
        if len(player.battlefield) >= 7:
            return {"success": False, "error": "Battlefield is full"}

        # 召唤随从
        player.battlefield.append(summoned_minion)
        summoned_minion.location = "battlefield"
        summoned_minion.controller = player.user_id

        return {
            "success": True,
            "summoned": summoned_minion.instance_id,
            "name": summoned_minion.name,
            "attack": summoned_minion.effective_attack,
            "defense": summoned_minion.effective_defense
        }


class DrawEffect(CardEffect):
    """抽牌效果"""

    async def apply(self, card: Card, game_state: GameState, player: Player, target_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        drawn_cards = []

        for _ in range(self.value):
            drawn_card = player.draw_card()
            if drawn_card:
                drawn_cards.append({
                    "instance_id": drawn_card.instance_id,
                    "name": drawn_card.name,
                    "cost": drawn_card.effective_cost
                })

        return {
            "success": True,
            "cards_drawn": len(drawn_cards),
            "cards": drawn_cards
        }


class ManaEffect(CardEffect):
    """法力效果"""

    async def apply(self, card: Card, game_state: GameState, player: Player, target_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        # 增加法力水晶（临时或永久）
        is_temporary = target_data.get("temporary", True) if target_data else True

        if is_temporary:
            player.mana += self.value
        else:
            player.max_mana = min(10, player.max_mana + self.value)
            player.mana += self.value

        return {
            "success": True,
            "mana_gained": self.value,
            "temporary": is_temporary,
            "current_mana": player.mana,
            "max_mana": player.max_mana
        }


class ArmorEffect(CardEffect):
    """护甲效果"""

    async def apply(self, card: Card, game_state: GameState, player: Player, target_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        armor_gained = player.gain_armor(self.value)

        return {
            "success": True,
            "armor_gained": armor_gained,
            "total_armor": player.armor
        }


class CardEffectProcessor:
    """卡牌效果处理器"""

    def __init__(self):
        # 效果类型到处理器类的映射
        self.effect_handlers: Dict[EffectType, type] = {
            EffectType.DAMAGE: DamageEffect,
            EffectType.HEAL: HealEffect,
            EffectType.BUFF: BuffEffect,
            EffectType.SUMMON: SummonEffect,
            EffectType.DRAW: DrawEffect,
            EffectType.MANA: ManaEffect,
            EffectType.ARMOR: ArmorEffect,
        }

        # 卡牌效果映射（这里应该从数据库或配置文件加载）
        self.card_effects = self._load_card_effects()

    def _load_card_effects(self) -> Dict[int, List[CardEffect]]:
        """加载卡牌效果映射"""
        # 这里是一个简化的示例，实际应该从数据库加载
        effects = {
            # 火球术
            1: [DamageEffect(EffectType.DAMAGE, 6)],
            # 治疗术
            2: [HealEffect(EffectType.HEAL, 5)],
            # 火球术（更多伤害）
            3: [DamageEffect(EffectType.DAMAGE, 6)],
            # 奇迹硬币
            4: [ManaEffect(EffectType.MANA, 1, False)],
            # 野性成长
            5: [ManaEffect(EffectType.MANA, 1, False)],
            # 抽牌相关的法术
            6: [DrawEffect(EffectType.DRAW, 2)],
            # 盾牌猛击
            7: [DamageEffect(EffectType.DAMAGE, 1)],  # 实际应该根据护甲值
            # 铁炉火
            8: [DamageEffect(EffectType.DAMAGE, 2)],
            # 刺骨
            9: [DamageEffect(EffectType.DAMAGE, 5)],
            # 横扫
            10: [DamageEffect(EffectType.DAMAGE, 1)],
        }
        return effects

    async def process_battlecry(
        self,
        card: Card,
        game_state: GameState,
        player: Player,
        target_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """处理战吼效果"""
        effects = self.card_effects.get(card.id, [])

        results = []
        for effect in effects:
            try:
                result = await effect.apply(card, game_state, player, target_data)
                results.append(result)
            except Exception as e:
                logger.error("Error processing battlecry effect", card_id=card.id, error=str(e))
                results.append({"success": False, "error": str(e)})

        return {
            "success": True,
            "effects": results,
            "card": card.instance_id
        }

    async def process_deathrattle(
        self,
        card: Card,
        game_state: GameState,
        player: Player,
        target_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """处理亡语效果"""
        # 类似于战吼，但是是随从死亡时触发
        effects = self.card_effects.get(card.id, [])

        results = []
        for effect in effects:
            if isinstance(effect, SummonEffect):  # 通常亡语是召唤其他随从
                try:
                    result = await effect.apply(card, game_state, player, target_data)
                    results.append(result)
                except Exception as e:
                    logger.error("Error processing deathrattle effect", card_id=card.id, error=str(e))
                    results.append({"success": False, "error": str(e)})

        return {
            "success": True,
            "effects": results,
            "card": card.instance_id
        }

    async def process_spell(
        self,
        card: Card,
        game_state: GameState,
        player: Player,
        target_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """处理法术效果"""
        effects = self.card_effects.get(card.id, [])

        results = []
        for effect in effects:
            try:
                result = await effect.apply(card, game_state, player, target_data)
                results.append(result)
            except Exception as e:
                logger.error("Error processing spell effect", card_id=card.id, error=str(e))
                results.append({"success": False, "error": str(e)})

        return {
            "success": True,
            "effects": results,
            "card": card.instance_id
        }

    async def process_hero_power(
        self,
        hero_power: Card,
        game_state: GameState,
        player: Player,
        target_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """处理英雄技能效果"""
        # 这里可以根据职业实现不同的英雄技能
        effects = []

        # 根据职业选择效果
        if hero_power.card_class.value == "warrior":
            effects.append(ArmorEffect(EffectType.ARMOR, 2))
        elif hero_power.card_class.value == "mage":
            effects.append(DamageEffect(EffectType.DAMAGE, 1))
        elif hero_power.card_class.value == "priest":
            effects.append(HealEffect(EffectType.HEAL, 2))
        elif hero_power.card_class.value == "hunter":
            # 猎人技能通常是随从攻击
            pass
        elif hero_power.card_class.value == "druid":
            effects.append(ArmorEffect(EffectType.ARMOR, 1))
            effects.append(DrawEffect(EffectType.DRAW, 1))
        elif hero_power.card_class.value == "warlock":
            effects.append(DrawEffect(EffectType.DRAW, 1))
            effects.append(DamageEffect(EffectType.DAMAGE, 2))  # 抽牌并受伤

        results = []
        for effect in effects:
            try:
                result = await effect.apply(hero_power, game_state, player, target_data)
                results.append(result)
            except Exception as e:
                logger.error("Error processing hero power effect", error=str(e))
                results.append({"success": False, "error": str(e)})

        return {
            "success": True,
            "effects": results,
            "hero_power": hero_power.instance_id
        }

    def get_card_effects(self, card_id: int) -> List[CardEffect]:
        """获取卡牌效果列表"""
        return self.card_effects.get(card_id, [])

    def add_card_effect(self, card_id: int, effect: CardEffect):
        """添加卡牌效果"""
        if card_id not in self.card_effects:
            self.card_effects[card_id] = []
        self.card_effects[card_id].append(effect)