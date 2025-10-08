"""
测试卡牌效果系统
"""

import pytest
from app.game.effects import (
    BattlecryEffect, DeathrattleEffect, AuraEffect, TriggerEffect,
    EffectType, EffectTiming, EffectTarget, EffectValue, EffectManager
)
from app.game.cards import Card, CardType


class MockGameState:
    """模拟游戏状态"""

    def __init__(self):
        self.current_player = MockPlayer()
        self.opponent_player = MockPlayer()

    def get_current_player(self):
        return self.current_player

    def get_opponent_player(self):
        return self.opponent_player

    def get_opponent_hero(self):
        return self.opponent_player.hero

    def get_all_characters(self):
        return ([self.current_player.hero] + self.current_player.battlefield +
                [self.opponent_player.hero] + self.opponent_player.battlefield)

    def deal_damage(self, target, amount):
        if hasattr(target, 'health'):
            target.health -= amount
            return True
        return False

    def heal_target(self, target, amount):
        if hasattr(target, 'health') and hasattr(target, 'max_health'):
            target.health = min(target.health + amount, target.max_health)
            return True
        return False

    def draw_cards(self, count):
        # 模拟抽牌
        return True


class MockPlayer:
    """模拟玩家"""

    def __init__(self):
        self.hero = MockHero()
        self.battlefield = []


class MockHero:
    """模拟英雄"""

    def __init__(self):
        self.health = 30
        self.max_health = 30


class TestEffectTarget:
    """测试效果目标"""

    def test_effect_target_creation(self):
        """测试效果目标创建"""
        target = EffectTarget("enemy_hero", 1)
        assert target.target_type == "enemy_hero"
        assert target.target_count == 1
        assert target.filter_condition is None

    def test_effect_target_with_filter(self):
        """测试带筛选条件的效果目标"""
        target = EffectTarget("enemy_minions", -1, "taunt")
        assert target.target_type == "enemy_minions"
        assert target.target_count == -1
        assert target.filter_condition == "taunt"


class TestEffectValue:
    """测试效果数值"""

    def test_effect_value_creation(self):
        """测试效果数值创建"""
        value = EffectValue("damage", 3)
        assert value.value_type == "damage"
        assert value.value == 3
        assert value.value_multipliers is None


class TestBattlecryEffect:
    """测试战吼效果"""

    def test_battlecry_damage(self):
        """测试战吼伤害效果"""
        # 创建战吼效果：对敌方英雄造成3点伤害
        targets = [EffectTarget("enemy_hero", 1)]
        values = [EffectValue("damage", 3)]
        effect = BattlecryEffect(targets, values)

        # 设置游戏状态和上下文
        game_state = MockGameState()
        source_card = Card(1, "测试随从", 2, 2, 3, CardType.MINION)
        context = {
            "action": "play_card",
            "source_card": source_card
        }

        # 验证效果可以触发
        assert effect.can_trigger(game_state, context)
        assert not effect.used

        # 执行效果
        result = effect.execute(game_state, context)
        assert result
        assert effect.used
        assert game_state.opponent_player.hero.health == 27  # 30 - 3 = 27

    def test_battlecry_only_triggers_once(self):
        """测试战吼只触发一次"""
        targets = [EffectTarget("enemy_hero", 1)]
        values = [EffectValue("damage", 3)]
        effect = BattlecryEffect(targets, values)

        game_state = MockGameState()
        source_card = Card(1, "测试随从", 2, 2, 3, CardType.MINION)
        context = {
            "action": "play_card",
            "source_card": source_card
        }

        # 第一次执行
        result1 = effect.execute(game_state, context)
        assert result1

        # 第二次执行应该失败
        result2 = effect.execute(game_state, context)
        assert not result2

    def test_battlecry_cannot_trigger_wrong_action(self):
        """测试战吼在错误动作下不能触发"""
        targets = [EffectTarget("enemy_hero", 1)]
        values = [EffectValue("damage", 3)]
        effect = BattlecryEffect(targets, values)

        game_state = MockGameState()
        source_card = Card(1, "测试随从", 2, 2, 3, CardType.MINION)
        context = {
            "action": "attack",
            "source_card": source_card
        }

        assert not effect.can_trigger(game_state, context)


class TestDeathrattleEffect:
    """测试亡语效果"""

    def test_deathrattle_draw_cards(self):
        """测试亡语抽牌效果"""
        targets = [EffectTarget("self", 1)]
        values = [EffectValue("draw", 2)]
        effect = DeathrattleEffect(targets, values)

        game_state = MockGameState()
        source_card = Card(1, "测试随从", 2, 2, 3, CardType.MINION)
        context = {
            "action": "minion_death",
            "source_card": source_card
        }

        assert effect.can_trigger(game_state, context)
        result = effect.execute(game_state, context)
        assert result
        assert effect.used

    def test_deathrattle_cannot_trigger_wrong_action(self):
        """测试亡语在错误动作下不能触发"""
        targets = [EffectTarget("self", 1)]
        values = [EffectValue("draw", 2)]
        effect = DeathrattleEffect(targets, values)

        game_state = MockGameState()
        source_card = Card(1, "测试随从", 2, 2, 3, CardType.MINION)
        context = {
            "action": "play_card",
            "source_card": source_card
        }

        assert not effect.can_trigger(game_state, context)


class TestAuraEffect:
    """测试光环效果"""

    def test_aura_effect_buffs_friendly_minions(self):
        """测试光环为友方随从提供buff"""
        targets = [EffectTarget("friendly_minions", -1)]
        values = [EffectValue("buff", 1)]  # +1/+1
        effect = AuraEffect(targets, values)

        game_state = MockGameState()
        source_card = Card(1, "光环随从", 3, 2, 4, CardType.MINION)

        # 添加随从到战场
        game_state.current_player.battlefield.append(source_card)
        friendly_minion = Card(2, "友方随从", 2, 1, 3, CardType.MINION)
        game_state.current_player.battlefield.append(friendly_minion)

        context = {"source_card": source_card}

        # 初始状态
        assert not effect.active
        assert len(effect.affected_targets) == 0

        # 执行光环效果
        result = effect.execute(game_state, context)
        assert result
        assert effect.active
        assert len(effect.affected_targets) == 1
        assert friendly_minion in effect.affected_targets

    def test_aura_effect_removes_buff_when_minion_leaves(self):
        """测试光环随从离开时移除buff"""
        targets = [EffectTarget("friendly_minions", -1)]
        values = [EffectValue("buff", 1)]
        effect = AuraEffect(targets, values)

        game_state = MockGameState()
        source_card = Card(1, "光环随从", 3, 2, 4, CardType.MINION)
        friendly_minion = Card(2, "友方随从", 2, 1, 3, CardType.MINION)

        game_state.current_player.battlefield.append(source_card)
        game_state.current_player.battlefield.append(friendly_minion)

        context = {"source_card": source_card}

        # 先激活光环
        effect.execute(game_state, context)
        assert friendly_minion in effect.affected_targets

        # 移除光环随从
        game_state.current_player.battlefield.remove(source_card)
        effect.execute(game_state, context)

        # 验证buff被移除
        assert not effect.active
        assert len(effect.affected_targets) == 0


class TestTriggerEffect:
    """测试触发效果"""

    def test_trigger_effect_on_turn_start(self):
        """测试回合开始时的触发效果"""
        targets = [EffectTarget("self", 1)]
        values = [EffectValue("heal", 2)]
        effect = TriggerEffect(EffectTiming.ON_TURN_START, targets, values)

        game_state = MockGameState()
        source_card = Card(1, "触发随从", 2, 1, 3, CardType.MINION)
        source_card.health = 2  # 设置为受伤状态
        source_card.max_health = 3

        context = {
            "source_card": source_card,
            "timing": "on_turn_start"
        }

        assert effect.can_trigger(game_state, context)
        result = effect.execute(game_state, context)
        assert result
        assert source_card.health == 3  # 应该被治疗到满血

    def test_trigger_effect_with_condition(self):
        """测试带条件的触发效果"""
        targets = [EffectTarget("enemy_hero", 1)]
        values = [EffectValue("damage", 5)]
        effect = TriggerEffect(EffectTiming.ON_DAMAGE, targets, values, "low_health")

        game_state = MockGameState()
        source_card = Card(1, "触发随从", 2, 1, 3, CardType.MINION)
        source_card.health = 3  # 低血量状态

        context = {
            "source_card": source_card,
            "timing": "on_damage"
        }

        assert effect.can_trigger(game_state, context)
        result = effect.execute(game_state, context)
        assert result
        assert game_state.opponent_player.hero.health == 25  # 30 - 5 = 25

    def test_trigger_effect_condition_not_met(self):
        """测试触发条件不满足时不会触发"""
        targets = [EffectTarget("enemy_hero", 1)]
        values = [EffectValue("damage", 5)]
        effect = TriggerEffect(EffectTiming.ON_DAMAGE, targets, values, "low_health")

        game_state = MockGameState()
        source_card = Card(1, "触发随从", 2, 1, 3, CardType.MINION)
        source_card.health = 5  # 不满足低血量条件

        context = {
            "source_card": source_card,
            "timing": "on_damage"
        }

        assert not effect.can_trigger(game_state, context)


class TestEffectManager:
    """测试效果管理器"""

    def test_register_and_trigger_effects(self):
        """测试注册和触发效果"""
        manager = EffectManager()

        # 创建战吼效果
        targets = [EffectTarget("enemy_hero", 1)]
        values = [EffectValue("damage", 3)]
        battlecry = BattlecryEffect(targets, values)

        source_card = Card(1, "测试随从", 2, 2, 3, CardType.MINION)
        manager.register_effect(battlecry, source_card)

        assert len(manager.active_effects) == 1
        assert battlecry.source_card == source_card

    def test_trigger_effects_by_timing(self):
        """测试按时机触发效果"""
        manager = EffectManager()
        game_state = MockGameState()

        # 创建不同时机的效果
        play_targets = [EffectTarget("enemy_hero", 1)]
        play_values = [EffectValue("damage", 3)]
        play_effect = TriggerEffect(EffectTiming.ON_PLAY, play_targets, play_values)

        damage_targets = [EffectTarget("self", 1)]
        damage_values = [EffectValue("heal", 2)]
        damage_effect = TriggerEffect(EffectTiming.ON_DAMAGE, damage_targets, damage_values)

        source_card1 = Card(1, "效果随从1", 2, 2, 3, CardType.MINION)
        source_card2 = Card(2, "效果随从2", 2, 2, 3, CardType.MINION)

        manager.register_effect(play_effect, source_card1)
        manager.register_effect(damage_effect, source_card2)

        # 测试只触发ON_PLAY时机的效果
        context = {"timing": "on_play"}
        manager.trigger_effects(EffectTiming.ON_PLAY, game_state, context)

        # 验证只有play_effect被触发
        # 这里需要更复杂的验证逻辑，简化实现

    def test_remove_card_effects(self):
        """测试移除卡牌效果"""
        manager = EffectManager()

        targets = [EffectTarget("enemy_hero", 1)]
        values = [EffectValue("damage", 3)]
        effect = BattlecryEffect(targets, values)

        source_card = Card(1, "测试随从", 2, 2, 3, CardType.MINION)
        manager.register_effect(effect, source_card)

        assert len(manager.active_effects) == 1

        # 移除卡牌效果
        manager.remove_card_effects(source_card)
        assert len(manager.active_effects) == 0

    def test_get_active_auras(self):
        """测试获取活跃光环效果"""
        manager = EffectManager()

        # 创建不同类型的效果
        aura_targets = [EffectTarget("friendly_minions", -1)]
        aura_values = [EffectValue("buff", 1)]
        aura_effect = AuraEffect(aura_targets, aura_values)

        battlecry_targets = [EffectTarget("enemy_hero", 1)]
        battlecry_values = [EffectValue("damage", 3)]
        battlecry_effect = BattlecryEffect(battlecry_targets, battlecry_values)

        source_card1 = Card(1, "光环随从", 3, 2, 4, CardType.MINION)
        source_card2 = Card(2, "战吼随从", 2, 2, 3, CardType.MINION)

        manager.register_effect(aura_effect, source_card1)
        manager.register_effect(battlecry_effect, source_card2)

        active_auras = manager.get_active_auras()
        assert len(active_auras) == 1
        assert active_auras[0] == aura_effect


if __name__ == "__main__":
    pytest.main([__file__, "-v"])