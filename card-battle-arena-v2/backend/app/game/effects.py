"""
卡牌效果系统
处理战吼、亡语、光环等各种卡牌效果
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class EffectType(Enum):
    """效果类型"""
    BATTLECRY = "battlecry"      # 战吼
    DEATHRATTLE = "deathrattle"  # 亡语
    AURA = "aura"               # 光环
    TRIGGER = "trigger"         # 触发
    ENCHANTMENT = "enchantment" # 附魔
    ONGOING = "ongoing"         # 持续


class EffectTiming(Enum):
    """效果触发时机"""
    ON_PLAY = "on_play"           # 打出时
    ON_DEATH = "on_death"         # 死亡时
    ON_ATTACK = "on_attack"       # 攻击时
    ON_DAMAGE = "on_damage"       # 受伤时
    ON_TURN_START = "on_turn_start"  # 回合开始时
    ON_TURN_END = "on_turn_end"    # 回合结束时
    ON_MINION_SUMMON = "on_minion_summon"  # 随从召唤时


@dataclass
class EffectTarget:
    """效果目标"""
    target_type: str  # "self", "enemy_hero", "friendly_minions", "enemy_minions", "all"
    target_count: int = 1  # 目标数量，-1表示全部
    filter_condition: Optional[str] = None  # 筛选条件


@dataclass
class EffectValue:
    """效果数值"""
    value_type: str  # "damage", "heal", "buff", "draw", "mana"
    value: int = 0
    value_multipliers: List[float] = None  # 乘数列表


class BaseEffect(ABC):
    """基础效果类"""

    def __init__(self, effect_type: EffectType, timing: EffectTiming,
                 targets: List[EffectTarget], values: List[EffectValue]):
        self.effect_type = effect_type
        self.timing = timing
        self.targets = targets
        self.values = values
        self.used = False  # 效果是否已使用

    @abstractmethod
    def can_trigger(self, game_state: Any, context: Any) -> bool:
        """判断效果是否可以触发"""
        pass

    @abstractmethod
    def execute(self, game_state: Any, context: Any) -> bool:
        """执行效果"""
        pass

    def get_valid_targets(self, game_state: Any, target_def: EffectTarget) -> List[Any]:
        """获取有效目标列表"""
        # 这里需要根据具体游戏状态实现目标选择逻辑
        targets = []

        if target_def.target_type == "self":
            targets = [context.get("source_card")]
        elif target_def.target_type == "enemy_hero":
            targets = [game_state.get_opponent_hero()]
        elif target_def.target_type == "friendly_minions":
            targets = game_state.get_current_player().battlefield
        elif target_def.target_type == "enemy_minions":
            targets = game_state.get_opponent_player().battlefield
        elif target_def.target_type == "all":
            targets = game_state.get_all_characters()

        # 应用筛选条件
        if target_def.filter_condition:
            targets = self._filter_targets(targets, target_def.filter_condition)

        # 限制目标数量
        if target_def.target_count > 0 and len(targets) > target_def.target_count:
            targets = targets[:target_def.target_count]

        return targets

    def _filter_targets(self, targets: List[Any], condition: str) -> List[Any]:
        """根据条件筛选目标"""
        filtered = []
        for target in targets:
            if self._matches_condition(target, condition):
                filtered.append(target)
        return filtered

    def _matches_condition(self, target: Any, condition: str) -> bool:
        """检查目标是否匹配条件"""
        # 简化实现，实际应该支持更复杂的条件解析
        if condition == "minion":
            return hasattr(target, 'card_type') and target.card_type.value == "minion"
        elif condition == "damaged":
            return hasattr(target, 'health') and hasattr(target, 'max_health') and target.health < target.max_health
        elif condition == "taunt":
            return hasattr(target, 'taunt') and target.taunt

        return False


class BattlecryEffect(BaseEffect):
    """战吼效果"""

    def __init__(self, targets: List[EffectTarget], values: List[EffectValue]):
        super().__init__(EffectType.BATTLECRY, EffectTiming.ON_PLAY, targets, values)

    def can_trigger(self, game_state: Any, context: Any) -> bool:
        """战吼在打出时触发，且只触发一次"""
        return not self.used and context.get("action") == "play_card"

    def execute(self, game_state: Any, context: Any) -> bool:
        """执行战吼效果"""
        if not self.can_trigger(game_state, context):
            return False

        source_card = context.get("source_card")
        if not source_card:
            return False

        success = True
        for target_def, value_def in zip(self.targets, self.values):
            targets = self.get_valid_targets(game_state, target_def)
            for target in targets:
                if not self._apply_effect(target, value_def, game_state):
                    success = False

        self.used = True
        return success

    def _apply_effect(self, target: Any, value_def: EffectValue, game_state: Any) -> bool:
        """应用效果到目标"""
        if value_def.value_type == "damage":
            return game_state.deal_damage(target, value_def.value)
        elif value_def.value_type == "heal":
            return game_state.heal_target(target, value_def.value)
        elif value_def.value_type == "buff":
            return self._apply_buff(target, value_def)
        elif value_def.value_type == "draw":
            return game_state.draw_cards(value_def.value)

        return False

    def _apply_buff(self, target: Any, value_def: EffectValue) -> bool:
        """应用buff效果"""
        if hasattr(target, 'buff_attack'):
            target.buff_attack += value_def.value
        if hasattr(target, 'buff_health'):
            target.buff_health += value_def.value
        return True


class DeathrattleEffect(BaseEffect):
    """亡语效果"""

    def __init__(self, targets: List[EffectTarget], values: List[EffectValue]):
        super().__init__(EffectType.DEATHRATTLE, EffectTiming.ON_DEATH, targets, values)

    def can_trigger(self, game_state: Any, context: Any) -> bool:
        """亡语在死亡时触发"""
        return not self.used and context.get("action") == "minion_death"

    def execute(self, game_state: Any, context: Any) -> bool:
        """执行亡语效果"""
        if not self.can_trigger(game_state, context):
            return False

        source_card = context.get("source_card")
        if not source_card:
            return False

        success = True
        for target_def, value_def in zip(self.targets, self.values):
            targets = self.get_valid_targets(game_state, target_def)
            for target in targets:
                if not self._apply_deathrattle_effect(target, value_def, game_state):
                    success = False

        self.used = True
        return success

    def _apply_deathrattle_effect(self, target: Any, value_def: EffectValue, game_state: Any) -> bool:
        """应用亡语效果"""
        if value_def.value_type == "draw":
            return game_state.draw_cards(value_def.value)
        elif value_def.value_type == "damage":
            return game_state.deal_damage(target, value_def.value)
        elif value_def.value_type == "summon":
            # 召唤新的随从（需要指定随从ID）
            return self._summon_minion(value_def.value, game_state)

        return False

    def _summon_minion(self, minion_id: int, game_state: Any) -> bool:
        """召唤随从"""
        # 这里需要从卡牌数据库中查找对应ID的随从并召唤
        # 简化实现
        return True


class AuraEffect(BaseEffect):
    """光环效果"""

    def __init__(self, targets: List[EffectTarget], values: List[EffectValue]):
        super().__init__(EffectType.AURA, EffectTiming.ONGOING, targets, values)
        self.active = False
        self.affected_targets = []

    def can_trigger(self, game_state: Any, context: Any) -> bool:
        """光环效果持续生效"""
        return context.get("source_card") in game_state.get_current_player().battlefield

    def execute(self, game_state: Any, context: Any) -> bool:
        """执行光环效果"""
        source_card = context.get("source_card")
        if not source_card:
            return False

        # 获取当前应该影响的目标
        current_targets = []
        for target_def in self.targets:
            current_targets.extend(self.get_valid_targets(game_state, target_def))

        # 移除不再受影响的目标的buff
        for target in self.affected_targets:
            if target not in current_targets:
                self._remove_aura_buff(target)

        # 为新受影响的目标添加buff
        for target in current_targets:
            if target not in self.affected_targets:
                self._apply_aura_buff(target)

        self.affected_targets = current_targets
        self.active = True
        return True

    def _apply_aura_buff(self, target: Any):
        """应用光环buff"""
        for value_def in self.values:
            if value_def.value_type == "buff":
                if hasattr(target, 'buff_attack'):
                    target.buff_attack += value_def.value
                if hasattr(target, 'buff_health'):
                    target.buff_health += value_def.value

    def _remove_aura_buff(self, target: Any):
        """移除光环buff"""
        for value_def in self.values:
            if value_def.value_type == "buff":
                if hasattr(target, 'buff_attack'):
                    target.buff_attack -= value_def.value
                if hasattr(target, 'buff_health'):
                    target.buff_health -= value_def.value


class TriggerEffect(BaseEffect):
    """触发效果"""

    def __init__(self, timing: EffectTiming, targets: List[EffectTarget], values: List[EffectValue],
                 condition: Optional[str] = None):
        super().__init__(EffectType.TRIGGER, timing, targets, values)
        self.condition = condition  # 触发条件

    def can_trigger(self, game_state: Any, context: Any) -> bool:
        """检查触发条件"""
        if self.timing.value != context.get("timing"):
            return False

        if self.condition and not self._check_condition(context):
            return False

        return True

    def execute(self, game_state: Any, context: Any) -> bool:
        """执行触发效果"""
        if not self.can_trigger(game_state, context):
            return False

        source_card = context.get("source_card")
        if not source_card:
            return False

        success = True
        for target_def, value_def in zip(self.targets, self.values):
            targets = self.get_valid_targets(game_state, target_def)
            for target in targets:
                if not self._apply_trigger_effect(target, value_def, game_state, context):
                    success = False

        return success

    def _check_condition(self, context: Any) -> bool:
        """检查触发条件"""
        # 简化实现，实际应该支持复杂条件解析
        if self.condition == "low_health":
            source_card = context.get("source_card")
            return hasattr(source_card, 'health') and source_card.health <= 5
        elif self.condition == "friendly_minion_died":
            return context.get("friendly_minion_death", False)

        return True

    def _apply_trigger_effect(self, target: Any, value_def: EffectValue,
                             game_state: Any, context: Any) -> bool:
        """应用触发效果"""
        if value_def.value_type == "heal":
            return game_state.heal_target(target, value_def.value)
        elif value_def.value_type == "damage":
            return game_state.deal_damage(target, value_def.value)
        elif value_def.value_type == "draw":
            return game_state.draw_cards(value_def.value)

        return False


class EffectManager:
    """效果管理器"""

    def __init__(self):
        self.active_effects = []  # 当前活跃的效果列表

    def register_effect(self, effect: BaseEffect, source_card: Any):
        """注册效果"""
        effect.source_card = source_card
        self.active_effects.append(effect)

    def trigger_effects(self, timing: EffectTiming, game_state: Any, context: Any):
        """触发指定时机的所有效果"""
        context["timing"] = timing.value

        for effect in self.active_effects:
            if effect.can_trigger(game_state, context):
                effect.execute(game_state, context)

    def remove_card_effects(self, source_card: Any):
        """移除指定卡牌的所有效果"""
        self.active_effects = [
            effect for effect in self.active_effects
            if getattr(effect, 'source_card', None) != source_card
        ]

    def get_active_auras(self) -> List[AuraEffect]:
        """获取所有活跃的光环效果"""
        return [effect for effect in self.active_effects if isinstance(effect, AuraEffect)]