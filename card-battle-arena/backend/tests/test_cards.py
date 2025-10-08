"""
卡牌系统和卡组管理测试
"""

import pytest
from unittest.mock import Mock, patch
from app.models.card import Card
from app.models.deck import Deck
from app.core.game.cards import CardEngine
from app.core.game.rules import GameRules


class TestCardModel:
    """卡牌数据模型测试"""

    def test_card_creation(self):
        """测试卡牌创建"""
        card = Card(
            id="fireball_001",
            name="火球术",
            description="造成4点伤害",
            cost=4,
            class_name="mage",
            rarity="common",
            type="spell",
            attack=0,
            health=0
        )

        assert card.id == "fireball_001"
        assert card.name == "火球术"
        assert card.cost == 4
        assert card.class_name == "mage"
        assert card.rarity == "common"
        assert card.type == "spell"
        assert card.attack == 0
        assert card.health == 0

    def test_minion_card_creation(self):
        """测试随从卡牌创建"""
        minion = Card(
            id="water_elemental_001",
            name="水元素",
            description="战吼：冻结一个敌人",
            cost=4,
            class_name="mage",
            rarity="common",
            type="minion",
            attack=3,
            health=5
        )

        assert minion.type == "minion"
        assert minion.attack == 3
        assert minion.health == 5

    def test_weapon_card_creation(self):
        """测试武器卡牌创建"""
        weapon = Card(
            id="fiery_war_axe_001",
            name="炽炎战斧",
            description="武器，攻击力3，耐久度2",
            cost=3,
            class_name="warrior",
            rarity="common",
            type="weapon",
            attack=3,
            health=2  # 武器的health字段表示耐久度
        )

        assert weapon.type == "weapon"
        assert weapon.attack == 3
        assert weapon.health == 2

    def test_card_validation(self):
        """测试卡牌数据验证"""
        # 测试无效的法力值
        with pytest.raises(ValueError):
            Card(
                id="invalid_card",
                name="无效卡牌",
                cost=-1,  # 负数法力值
                class_name="mage",
                rarity="common",
                type="spell"
            )

        # 测试无效的攻击力
        with pytest.raises(ValueError):
            Card(
                id="invalid_minion",
                name="无效随从",
                cost=4,
                class_name="mage",
                rarity="common",
                type="minion",
                attack=-1,  # 负数攻击力
                health=5
            )

    def test_card_can_play_by_class(self):
        """测试职业限制检查"""
        mage_card = Card(
            id="mage_spell",
            name="法师法术",
            cost=2,
            class_name="mage",
            rarity="common",
            type="spell"
        )

        neutral_card = Card(
            id="neutral_minion",
            name="中立随从",
            cost=2,
            class_name="neutral",
            rarity="common",
            type="minion",
            attack=1,
            health=1
        )

        # 法师可以使用法师卡牌
        assert mage_card.can_play_by_class("mage")
        # 战士不能使用法师卡牌
        assert not mage_card.can_play_by_class("warrior")
        # 任何职业都可以使用中立卡牌
        assert neutral_card.can_play_by_class("mage")
        assert neutral_card.can_play_by_class("warrior")


class TestDeckModel:
    """卡组数据模型测试"""

    @pytest.fixture
    def sample_cards(self):
        """创建示例卡牌"""
        return [
            Card(id="card_001", name="卡牌1", cost=1, class_name="mage", rarity="common", type="spell"),
            Card(id="card_002", name="卡牌2", cost=2, class_name="mage", rarity="common", type="minion", attack=2, health=2),
            Card(id="card_003", name="卡牌3", cost=3, class_name="mage", rarity="rare", type="minion", attack=3, health=3),
        ]

    def test_deck_creation(self, sample_cards):
        """测试卡组创建"""
        deck = Deck(
            name="测试卡组",
            class_name="mage",
            user_id=1
        )

        assert deck.name == "测试卡组"
        assert deck.class_name == "mage"
        assert deck.user_id == 1
        assert len(deck.cards) == 0

    def test_add_card_to_deck(self, sample_cards):
        """测试添加卡牌到卡组"""
        deck = Deck(name="测试卡组", class_name="mage", user_id=1)

        # 添加卡牌
        deck.add_card(sample_cards[0])
        assert len(deck.cards) == 1
        assert deck.cards[0].id == "card_001"

        # 添加相同卡牌
        deck.add_card(sample_cards[0])
        assert len(deck.cards) == 2

    def test_deck_validation(self, sample_cards):
        """测试卡组验证"""
        deck = Deck(name="测试卡组", class_name="mage", user_id=1)

        # 添加30张卡牌
        for i in range(10):
            for card in sample_cards:
                deck.add_card(card)

        # 卡组应该有效
        assert deck.is_valid()

        # 清空卡组
        deck.cards.clear()
        assert not deck.is_valid()  # 空卡组无效

    def test_deck_card_count_limit(self, sample_cards):
        """测试卡组卡牌数量限制"""
        deck = Deck(name="测试卡组", class_name="mage", user_id=1)

        # 尝试添加超过2张相同卡牌
        for _ in range(3):
            deck.add_card(sample_cards[0])

        # 应该只有2张卡牌
        card_count = sum(1 for card in deck.cards if card.id == "card_001")
        assert card_count == 2

    def test_deck_mana_curve(self, sample_cards):
        """测试卡组法力曲线分析"""
        deck = Deck(name="测试卡组", class_name="mage", user_id=1)

        # 添加不同法力值的卡牌
        for i in range(10):
            for card in sample_cards:
                deck.add_card(card)

        # 分析法力曲线
        mana_curve = deck.get_mana_curve()
        assert mana_curve[1] == 10  # 10张1费卡牌
        assert mana_curve[2] == 10  # 10张2费卡牌
        assert mana_curve[3] == 10  # 10张3费卡牌


class TestCardEngine:
    """卡牌引擎测试"""

    @pytest.fixture
    def card_engine(self):
        """创建卡牌引擎实例"""
        return CardEngine()

    @pytest.fixture
    def sample_minion_card(self):
        """创建示例随从卡牌"""
        return Card(
            id="test_minion",
            name="测试随从",
            description="测试随从",
            cost=4,
            class_name="neutral",
            rarity="common",
            type="minion",
            attack=4,
            health=5
        )

    @pytest.fixture
    def sample_spell_card(self):
        """创建示例法术卡牌"""
        return Card(
            id="test_spell",
            name="测试法术",
            description="造成3点伤害",
            cost=3,
            class_name="mage",
            rarity="common",
            type="spell"
        )

    def test_play_minion_card(self, card_engine, sample_minion_card):
        """测试打出随从卡牌"""
        game_state = Mock()
        player = Mock()
        target = None

        # 打出随从卡牌
        result = card_engine.play_card(
            sample_minion_card, game_state, player, target
        )

        assert result is True
        # 验证随从被放置到战场上
        assert len(player.battlefield) > 0

    def test_play_spell_card_with_target(self, card_engine, sample_spell_card):
        """测试带目标的法术卡牌"""
        game_state = Mock()
        player = Mock()
        target = Mock()
        target.health = 10

        # 打出法术卡牌
        result = card_engine.play_card(
            sample_spell_card, game_state, player, target
        )

        assert result is True
        # 验证目标受到伤害
        assert target.health < 10

    def test_insufficient_mana(self, card_engine, sample_minion_card):
        """测试法力值不足"""
        game_state = Mock()
        player = Mock()
        player.mana = 2  # 只有2点法力值
        target = None

        # 尝试打出4费卡牌
        result = card_engine.play_card(
            sample_minion_card, game_state, player, target
        )

        assert result is False

    def test_card_battlecry_effect(self, card_engine):
        """测试卡牌战吼效果"""
        # 创建带战吼效果的卡牌
        battlecry_card = Card(
            id="battlecry_minion",
            name="战吼随从",
            description="战吼：造成2点伤害",
            cost=5,
            class_name="mage",
            rarity="rare",
            type="minion",
            attack=4,
            health=4
        )

        game_state = Mock()
        player = Mock()
        target = Mock()
        target.health = 10

        # 打出带战吼效果的卡牌
        result = card_engine.play_card(
            battlecry_card, game_state, player, target
        )

        assert result is True
        # 验证战吼效果触发
        assert target.health < 10


class TestGameRules:
    """游戏规则测试"""

    @pytest.fixture
    def game_rules(self):
        """创建游戏规则实例"""
        return GameRules()

    def test_max_hand_size(self, game_rules):
        """测试最大手牌数量"""
        player = Mock()
        player.hand = [Mock() for _ in range(9)]  # 9张手牌

        # 添加第10张卡牌应该成功
        assert game_rules.can_add_card_to_hand(player)

        # 添加第11张卡牌应该失败
        player.hand.append(Mock())
        assert not game_rules.can_add_card_to_hand(player)

    def test_mana_system(self, game_rules):
        """测试法力值系统"""
        player = Mock()
        player.turn = 5
        player.max_mana = 10
        player.current_mana = 7

        # 检查是否有足够法力值
        assert game_rules.has_enough_mana(player, 5)
        assert game_rules.has_enough_mana(player, 7)
        assert not game_rules.has_enough_mana(player, 8)

    def test_attack_rules(self, game_rules):
        """测试攻击规则"""
        attacker = Mock()
        attacker.attack = 4
        attacker.can_attack = True

        defender = Mock()
        defender.health = 5
        defender.is_taunt = False

        # 检查是否可以攻击
        assert game_rules.can_attack(attacker, defender)

        # 测试嘲讽效果
        defender.is_taunt = True
        assert game_rules.can_attack(attacker, defender)

        # 测试无法攻击的随从
        attacker.can_attack = False
        assert not game_rules.can_attack(attacker, defender)

    def test_game_end_conditions(self, game_rules):
        """测试游戏结束条件"""
        game_state = Mock()

        # 测试英雄死亡
        game_state.player1.hero.health = 0
        game_state.player2.hero.health = 30

        assert game_rules.is_game_over(game_state)
        assert game_rules.get_winner(game_state) == game_state.player2

        # 测试双方英雄都死亡（平局）
        game_state.player1.hero.health = 0
        game_state.player2.hero.health = 0

        assert game_rules.is_game_over(game_state)
        assert game_rules.get_winner(game_state) is None  # 平局

        # 测试游戏未结束
        game_state.player1.hero.health = 20
        game_state.player2.hero.health = 15

        assert not game_rules.is_game_over(game_state)


class TestCardIntegration:
    """卡牌系统集成测试"""

    def test_complete_card_play_sequence(self):
        """测试完整的出牌流程"""
        # 创建游戏状态
        game_state = Mock()
        player = Mock()
        player.mana = 4
        player.max_mana = 4
        player.hand = []
        player.battlefield = []

        # 创建卡牌
        card = Card(
            id="test_card",
            name="测试卡牌",
            description="测试卡牌",
            cost=4,
            class_name="neutral",
            rarity="common",
            type="minion",
            attack=3,
            health=4
        )

        # 添加卡牌到手牌
        player.hand.append(card)

        # 检查是否可以出牌
        game_rules = GameRules()
        assert game_rules.has_enough_mana(player, card.cost)

        # 出牌
        card_engine = CardEngine()
        result = card_engine.play_card(card, game_state, player, None)

        assert result is True
        assert card not in player.hand  # 卡牌离手
        assert len(player.battlefield) > 0  # 随从上场

    def test_card_combinations(self):
        """测试卡牌组合效果"""
        # 这里可以测试多张卡牌的组合效果
        # 例如：冲锋+嘲讽、法强+法术等
        pass


if __name__ == "__main__":
    pytest.main([__file__])