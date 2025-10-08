"""
游戏引擎核心测试
采用TDD方法，先定义测试用例，然后实现功能
"""

import pytest
from typing import List, Optional
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.game.engine import GameEngine, GameState, Player, Card, CardType
from app.game.cards import create_basic_card_set


class TestGameState:
    """游戏状态测试"""

    def test_initial_game_state(self):
        """测试初始游戏状态"""
        # 创建两个玩家
        player1 = Player(1, "Player1")
        player2 = Player(2, "Player2")

        # 创建游戏状态
        game = GameState(player1, player2)

        # 验证初始状态
        assert game.current_player == 1
        assert game.turn_number == 1
        assert not game.game_over
        assert game.winner is None

        # 验证玩家初始状态
        assert player1.health == 30
        assert player1.max_mana == 1
        assert player1.current_mana == 1
        assert len(player1.hand) == 3  # 起始手牌
        assert len(player1.deck) == 27  # 30张牌 - 3张手牌
        assert len(player1.battlefield) == 0

    def test_mana_system(self):
        """测试法力值系统"""
        player1 = Player(1, "Player1")
        player2 = Player(2, "Player2")
        game = GameState(player1, player2)

        # 第一回合
        assert player1.current_mana == 1
        assert player1.max_mana == 1

        # 消耗法力值
        player1.current_mana -= 1
        assert player1.current_mana == 0

        # 进入下一回合
        game.start_new_turn()
        assert player1.current_mana == 2
        assert player1.max_mana == 2

    def test_hand_card_limit(self):
        """测试手牌上限"""
        player1 = Player(1, "Player1")
        player2 = Player(2, "Player2")

        # 添加8张手牌（超过上限）
        for i in range(8):
            player1.hand.append(Card(i, f"card_{i}", 1, 1, 1, CardType.MINION))

        assert len(player1.hand) == 8

        # 回合结束应该丢弃多余的牌
        player1.enforce_hand_limit()
        assert len(player1.hand) == 7  # 手牌上限为7

    def test_deck_empty_draw(self):
        """测试牌库空了抽牌的伤害"""
        player1 = Player(1, "Player1")
        player2 = Player(2, "Player2")
        game = GameState(player1, player2)

        # 清空牌库
        player1.deck.clear()

        # 抽牌应该受到疲劳伤害
        original_health = player1.health
        player1.draw_card()
        assert player1.health == original_health - 1  # 疲劳伤害

        # 再次抽牌，疲劳伤害增加
        player1.draw_card()
        assert player1.health == original_health - 3  # 1 + 2 疲劳伤害


class TestCardPlaying:
    """卡牌出牌测试"""

    def test_play_minion_card(self):
        """测试打出随从卡"""
        engine = GameEngine()
        game = engine.create_game("Player1", "Player2")

        # 创建一个1费随从
        minion_card = Card(1, "Test Minion", 1, 2, 1, CardType.MINION)
        game.current_player_hand.append(minion_card)

        # 打出随从
        result = engine.play_card(minion_card, target=None)

        assert result.success
        assert len(game.current_player.battlefield) == 1
        assert game.current_player.current_mana == 0  # 消耗了1点法力值
        assert minion_card not in game.current_player.hand

    def test_play_spell_card(self):
        """测试打出法术卡"""
        engine = GameEngine()
        game = engine.create_game("Player1", "Player2")

        # 创建一个2费法术卡（造成3点伤害）
        spell_card = Card(2, "Fireball", 2, 0, 0, CardType.SPELL)
        spell_card.damage = 3
        game.current_player_hand.append(spell_card)

        original_health = game.opponent.health

        # 打出法术卡攻击对手英雄
        result = engine.play_card(spell_card, target=game.opponent)

        assert result.success
        assert game.opponent.health == original_health - 3
        assert game.current_player.current_mana == 0  # 消耗了2点法力值
        assert spell_card not in game.current_player.hand

    def test_insufficient_mana(self):
        """测试法力值不足时无法出牌"""
        engine = GameEngine()
        game = engine.create_game("Player1", "Player2")

        # 创建一个5费卡牌，但只有1点法力值
        expensive_card = Card(5, "Expensive Card", 5, 5, 5, CardType.MINION)
        game.current_player_hand.append(expensive_card)

        # 尝试打出卡牌
        result = engine.play_card(expensive_card, target=None)

        assert not result.success
        assert "insufficient mana" in result.error.lower()
        assert len(game.current_player.battlefield) == 0
        assert expensive_card in game.current_player.hand

    def test_play_weapon_card(self):
        """测试打出武器卡"""
        engine = GameEngine()
        game = engine.create_game("Player1", "Player2")

        # 创建一个2费武器（2攻击力，2耐久度）
        weapon_card = Card(6, "Dagger", 2, 2, 0, CardType.WEAPON)
        game.current_player_hand.append(weapon_card)

        # 打出武器
        result = engine.play_card(weapon_card, target=None)

        assert result.success
        assert game.current_player.weapon is not None
        assert game.current_player.weapon.attack == 2
        assert game.current_player.weapon.durability == 2
        assert game.current_player.current_mana == 0

    def test_play_card_with_target(self):
        """测试需要目标的卡牌"""
        engine = GameEngine()
        game = engine.create_game("Player1", "Player2")

        # 在场上放一个随从作为目标
        target_minion = Card(7, "Target Minion", 1, 2, 1, CardType.MINION)
        game.opponent.battlefield.append(target_minion)

        # 创建一个需要目标的法术卡
        spell_card = Card(8, "Target Spell", 1, 0, 0, CardType.SPELL)
        spell_card.needs_target = True
        spell_card.damage = 2
        game.current_player_hand.append(spell_card)

        # 不指定目标，应该失败
        result_no_target = engine.play_card(spell_card, target=None)
        assert not result_no_target.success

        # 指定有效目标，应该成功
        result_with_target = engine.play_card(spell_card, target=target_minion)
        assert result_with_target.success
        assert target_minion.health == 0  # 2 - 2 = 0，应该死亡


class TestCombat:
    """战斗系统测试"""

    def test_minion_attack_hero(self):
        """测试随从攻击英雄"""
        engine = GameEngine()
        game = engine.create_game("Player1", "Player2")

        # 在场上放一个攻击力为2的随从
        minion = Card(9, "Attacker", 1, 2, 3, CardType.MINION)
        minion.can_attack = True  # 假设随从可以攻击
        game.current_player.battlefield.append(minion)

        original_opponent_health = game.opponent.health

        # 随从攻击对手英雄
        result = engine.attack_with_minion(minion, target=game.opponent.hero)

        assert result.success
        assert game.opponent.health == original_opponent_health - 2
        assert minion.can_attack == False  # 攻击后本回合不能再次攻击

    def test_minion_attack_minion(self):
        """测试随从攻击随从"""
        engine = GameEngine()
        game = engine.create_game("Player1", "Player2")

        # 攻击方随从
        attacker = Card(10, "Attacker", 2, 3, 2, CardType.MINION)
        attacker.can_attack = True
        game.current_player.battlefield.append(attacker)

        # 防守方随从
        defender = Card(11, "Defender", 1, 2, 1, CardType.MINION)
        game.opponent.battlefield.append(defender)

        # 随从攻击随从
        result = engine.attack_with_minion(attacker, target=defender)

        assert result.success
        assert attacker.health == 1  # 3 - 2 = 1
        assert defender.health == 0  # 2 - 2 = 0，应该死亡
        assert defender not in game.opponent.battlefield

    def test_hero_attack_with_weapon(self):
        """测试英雄装备武器后攻击"""
        engine = GameEngine()
        game = engine.create_game("Player1", "Player2")

        # 给玩家装备武器
        weapon = Card(12, "Sword", 2, 3, 0, CardType.WEAPON)
        weapon.durability = 3
        game.current_player.weapon = weapon

        original_opponent_health = game.opponent.health

        # 英雄攻击
        result = engine.attack_with_hero(target=game.opponent.hero)

        assert result.success
        assert game.opponent.health == original_opponent_health - 3
        assert weapon.durability == 2  # 消耗1点耐久度

    def test_cannot_attack_without_charge(self):
        """测试没有冲锋的随从不能立即攻击"""
        engine = GameEngine()
        game = engine.create_game("Player1", "Player2")

        # 创建没有冲锋的随从
        minion = Card(13, "No Charge", 2, 3, 2, CardType.MINION)
        minion.charge = False
        game.current_player.battlefield.append(minion)

        # 尝试攻击应该失败
        result = engine.attack_with_minion(minion, target=game.opponent.hero)
        assert not result.success
        assert "cannot attack this turn" in result.error.lower()

    def test_taunt_mechanic(self):
        """测试嘲讽机制"""
        engine = GameEngine()
        game = engine.create_game("Player1", "Player2")

        # 攻击方随从
        attacker = Card(14, "Attacker", 1, 2, 2, CardType.MINION)
        attacker.can_attack = True
        game.current_player.battlefield.append(attacker)

        # 防守方的嘲讽随从和非嘲讽随从
        taunt_minion = Card(15, "Taunt Minion", 2, 1, 2, CardType.MINION)
        taunt_minion.taunt = True
        normal_minion = Card(16, "Normal Minion", 1, 5, 1, CardType.MINION)
        game.opponent.battlefield.extend([taunt_minion, normal_minion])

        # 攻击非嘲讽随从应该失败
        result_attack_normal = engine.attack_with_minion(attacker, target=normal_minion)
        assert not result_attack_normal.success
        assert "must attack taunt minion first" in result_attack_normal.error.lower()

        # 攻击嘲讽随从应该成功
        result_attack_taunt = engine.attack_with_minion(attacker, target=taunt_minion)
        assert result_attack_taunt.success


class TestGameRules:
    """游戏规则测试"""

    def test_win_condition_hero_death(self):
        """测试英雄死亡时的胜负判定"""
        engine = GameEngine()
        game = engine.create_game("Player1", "Player2")

        # 将对手英雄生命值降至0
        game.opponent.health = 0

        # 检查游戏结束状态
        engine.check_win_condition()

        assert game.game_over
        assert game.winner == game.current_player.player_id

    def test_turn_sequence(self):
        """测试回合顺序"""
        engine = GameEngine()
        game = engine.create_game("Player1", "Player2")

        # 初始回合
        assert game.current_player.player_id == 1
        assert game.turn_number == 1

        # 结束当前回合
        engine.end_turn()

        # 切换到对手回合
        assert game.current_player.player_id == 2
        assert game.turn_number == 1

        # 再次结束回合
        engine.end_turn()

        # 回到玩家1，回合数增加
        assert game.current_player.player_id == 1
        assert game.turn_number == 2

    def test_card_draw_at_turn_start(self):
        """测试回合开始时抽牌"""
        engine = GameEngine()
        game = engine.create_game("Player1", "Player2")

        # 记录当前手牌数量
        initial_hand_size = len(game.current_player.hand)

        # 结束当前回合
        engine.end_turn()

        # 再结束一个回合回到玩家1
        engine.end_turn()

        # 验证抽了一张牌
        assert len(game.current_player.hand) == initial_hand_size + 1

    def test_mana_crystal_growth(self):
        """测试法力水晶增长"""
        engine = GameEngine()
        game = engine.create_game("Player1", "Player2")

        # 第一回合
        assert game.current_player.max_mana == 1

        # 进行到第5回合
        for _ in range(4):  # 已经是第1回合，再进行4次
            engine.end_turn()
            engine.end_turn()

        assert game.current_player.max_mana == 5
        assert game.current_player.current_mana == 5

    def test_max_mana_limit(self):
        """测试法力值上限"""
        engine = GameEngine()
        game = engine.create_game("Player1", "Player2")

        # 进行到第15回合（超过最大法力值10）
        for _ in range(14):
            engine.end_turn()
            engine.end_turn()

        # 法力值应该限制在10
        assert game.current_player.max_mana == 10
        assert game.current_player.current_mana == 10


class TestCardEffects:
    """卡牌效果测试"""

    def test_battlecry_effect(self):
        """测试战吼效果"""
        engine = GameEngine()
        game = engine.create_game("Player1", "Player2")

        # 创建有战吼效果的随从（造成2点伤害）
        minion = Card(17, "Battlecry Minion", 2, 2, 2, CardType.MINION)
        minion.battlecry_damage = 2
        game.current_player_hand.append(minion)

        original_health = game.opponent.health

        # 打出随从
        result = engine.play_card(minion, target=game.opponent.hero)

        assert result.success
        assert game.opponent.health == original_health - 2  # 战吼伤害
        assert len(game.current_player.battlefield) == 1

    def test_deathrattle_effect(self):
        """测试亡语效果"""
        engine = GameEngine()
        game = engine.create_game("Player1", "Player2")

        # 创建有亡语效果的随从（死亡时抽一张牌）
        minion = Card(18, "Deathrattle Minion", 2, 1, 2, CardType.MINION)
        minion.deathrattle_draw = 1
        game.current_player.battlefield.append(minion)

        initial_hand_size = len(game.current_player.hand)
        initial_deck_size = len(game.current_player.deck)

        # 随从死亡
        minion.health = 0
        engine.remove_dead_minions()

        # 验证亡语效果
        assert len(game.current_player.hand) == initial_hand_size + 1
        assert len(game.current_player.deck) == initial_deck_size - 1
        assert minion not in game.current_player.battlefield

    def test_divine_shield(self):
        """测试圣盾效果"""
        engine = GameEngine()
        game = engine.create_game("Player1", "Player2")

        # 创建有圣盾的随从
        shielded_minion = Card(19, "Shielded Minion", 2, 3, 2, CardType.MINION)
        shielded_minion.divine_shield = True
        shielded_minion.can_attack = True
        game.current_player.battlefield.append(shielded_minion)

        # 创建攻击随从
        attacker = Card(20, "Attacker", 2, 2, 2, CardType.MINION)
        attacker.can_attack = True
        game.opponent.battlefield.append(attacker)

        # 攻击圣盾随从
        result = engine.attack_with_minion(attacker, target=shielded_minion)

        assert result.success
        assert shielded_minion.divine_shield == False  # 圣盾被破
        assert shielded_minion.health == 3  # 生命值不变
        assert attacker.health == 2  # 攻击方受到正常伤害


class TestGameStatePersistence:
    """游戏状态持久化测试"""

    def test_save_game_state(self):
        """测试保存游戏状态"""
        engine = GameEngine()
        game = engine.create_game("Player1", "Player2")

        # 进行一些游戏操作
        card1 = Card(21, "Card1", 1, 1, 1, CardType.MINION)
        card2 = Card(22, "Card2", 2, 2, 2, CardType.MINION)
        game.current_player.hand.extend([card1, card2])

        # 打出一张卡
        engine.play_card(card1, target=None)

        # 保存游戏状态
        saved_state = engine.save_game_state()

        assert saved_state is not None
        assert saved_state['game_id'] == game.game_id
        assert saved_state['current_player'] == 1
        assert len(saved_state['player1']['battlefield']) == 1

    def test_load_game_state(self):
        """测试加载游戏状态"""
        engine = GameEngine()

        # 创建预设的游戏状态
        saved_state = {
            'game_id': 'test_game',
            'current_player': 2,
            'turn_number': 5,
            'player1': {
                'health': 25,
                'current_mana': 3,
                'max_mana': 5,
                'hand': [{'id': 1, 'name': 'Card1', 'cost': 1}],
                'battlefield': [{'id': 2, 'name': 'Minion1', 'attack': 2, 'health': 3}]
            },
            'player2': {
                'health': 28,
                'current_mana': 5,
                'max_mana': 5,
                'hand': [],
                'battlefield': []
            }
        }

        # 加载游戏状态
        game = engine.load_game_state(saved_state)

        assert game.game_id == 'test_game'
        assert game.current_player.player_id == 2
        assert game.turn_number == 5
        assert game.player1.health == 25
        assert len(game.player1.battlefield) == 1
        assert game.player1.battlefield[0].attack == 2


class TestAIPlayer:
    """AI玩家测试"""

    def test_ai_makes_decision(self):
        """测试AI决策"""
        engine = GameEngine()
        game = engine.create_game("Player1", "AI")

        # 给AI一些手牌
        card1 = Card(23, "AI Card1", 1, 1, 1, CardType.MINION)
        card2 = Card(24, "AI Card2", 2, 2, 2, CardType.MINION)
        game.current_player.hand.extend([card1, card2])

        # AI做出决策
        decision = engine.ai_make_decision(game.current_player)

        assert decision is not None
        assert decision.action in ['play_card', 'attack', 'end_turn']
        if decision.action == 'play_card':
            assert decision.card in game.current_player.hand

    def test_ai_difficulty_levels(self):
        """测试AI难度等级"""
        engine = GameEngine()

        # 测试简单AI
        easy_ai = engine.create_ai_player("EasyAI", difficulty="easy")
        assert easy_ai.difficulty == "easy"

        # 测试普通AI
        normal_ai = engine.create_ai_player("NormalAI", difficulty="normal")
        assert normal_ai.difficulty == "normal"

        # 测试困难AI
        hard_ai = engine.create_ai_player("HardAI", difficulty="hard")
        assert hard_ai.difficulty == "hard"


class TestHeroPower:
    """英雄技能测试"""

    def test_hero_power_usage(self):
        """测试英雄技能使用"""
        engine = GameEngine()
        game = engine.create_game("Player1", "Player2")

        current = game.current_player

        # 初始状态：没有使用过英雄技能
        assert not current.used_hero_power
        assert current.current_mana >= 2  # 需要至少2点法力值

        # 使用英雄技能
        result = engine.use_hero_power()

        # 验证结果
        assert result.success
        assert current.used_hero_power
        assert current.current_mana == current.max_mana - 2

        # 不能重复使用
        result2 = engine.use_hero_power()
        assert not result2.success
        assert "already used" in result2.error.lower()

    def test_hero_power_insufficient_mana(self):
        """测试法力值不足时无法使用英雄技能"""
        engine = GameEngine()
        game = engine.create_game("Player1", "Player2")

        current = game.current_player
        # 将法力值设为1（不够使用英雄技能）
        current.current_mana = 1

        # 尝试使用英雄技能
        result = engine.use_hero_power()

        assert not result.success
        assert "insufficient mana" in result.error.lower()
        assert not current.used_hero_power

    def test_hero_power_deals_damage(self):
        """测试英雄技能造成伤害"""
        engine = GameEngine()
        game = engine.create_game("Player1", "Player2")

        original_opponent_health = game.opponent.hero.health

        # 使用英雄技能
        result = engine.use_hero_power()

        assert result.success
        # 英雄技能应该造成1点伤害
        assert game.opponent.hero.health == original_opponent_health - 1

    def test_hero_power_resets_after_turn(self):
        """测试回合结束后英雄技能使用状态重置"""
        engine = GameEngine()
        game = engine.create_game("Player1", "Player2")

        current = game.current_player

        # 使用英雄技能
        result = engine.use_hero_power()
        assert result.success
        assert current.used_hero_power

        # 结束回合
        engine.end_turn()

        # 回到该玩家时，英雄技能状态应该重置
        engine.end_turn()  # 回到玩家1

        assert not current.used_hero_power
        # 应该可以再次使用英雄技能
        result2 = engine.use_hero_power()
        assert result2.success


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])