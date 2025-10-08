import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from app.core.game.engine import GameEngine, GameState, Player
from app.core.game.card import Card, CardType
from app.models.user import User


@pytest.fixture
def mock_users():
    """模拟用户数据"""
    user1 = Mock(spec=User)
    user1.id = 1
    user1.username = "player1"
    user1.rating = 1500

    user2 = Mock(spec=User)
    user2.id = 2
    user2.username = "player2"
    user2.rating = 1400

    return user1, user2


@pytest.fixture
def sample_cards():
    """示例卡牌数据"""
    fireball = Card(
        id=1,
        name="火球术",
        cost=4,
        card_type=CardType.SPELL,
        damage=6
    )

    minion = Card(
        id=2,
        name="石元素",
        cost=3,
        card_type=CardType.MINION,
        attack=3,
        defense=5
    )

    return fireball, minion


@pytest.fixture
def game_engine(mock_users):
    """创建游戏引擎实例"""
    engine = GameEngine()
    user1, user2 = mock_users
    game_id = engine.create_game(user1.id, user2.id)
    return engine, game_id, user1, user2


class TestGameEngine:
    """游戏引擎测试"""

    def test_create_game(self, mock_users):
        """测试创建游戏"""
        engine = GameEngine()
        user1, user2 = mock_users

        game_id = engine.create_game(user1.id, user2.id)

        assert game_id is not None
        assert game_id in engine.games

        game_state = engine.games[game_id]
        assert game_state.player1_id == user1.id
        assert game_state.player2_id == user2.id
        assert game_state.current_player_number == 1
        assert not game_state.is_game_over

    def test_get_game_state(self, game_engine):
        """测试获取游戏状态"""
        engine, game_id, user1, user2 = game_engine

        state = engine.get_game_state(game_id)
        assert state is not None
        assert state.player1_id == user1.id
        assert state.player2_id == user2.id

    def test_get_nonexistent_game_state(self, game_engine):
        """测试获取不存在的游戏状态"""
        engine, _, _, _ = game_engine

        state = engine.get_game_state("nonexistent")
        assert state is None

    @pytest.mark.asyncio
    async def test_play_card(self, game_engine, sample_cards):
        """测试出牌"""
        engine, game_id, user1, user2 = game_engine
        fireball, minion = sample_cards

        # 模拟玩家手牌
        game_state = engine.games[game_id]
        current_player = game_state.current_player
        current_player.hand = [fireball, minion]
        current_player.mana = 4

        # 出牌
        success = await engine.play_card(
            game_id, user1.id, fireball.id, target_player_id=user2.id
        )

        assert success
        assert fireball not in current_player.hand
        assert fireball in current_player.graveyard

    @pytest.mark.asyncio
    async def test_play_card_without_mana(self, game_engine, sample_cards):
        """测试无法出牌（法力不足）"""
        engine, game_id, user1, user2 = game_engine
        fireball, minion = sample_cards

        game_state = engine.games[game_id]
        current_player = game_state.current_player
        current_player.hand = [fireball]
        current_player.mana = 2  # 火球术需要4点法力

        success = await engine.play_card(
            game_id, user1.id, fireball.id, target_player_id=user2.id
        )

        assert not success
        assert fireball in current_player.hand

    @pytest.mark.asyncio
    async def test_attack_minion(self, game_engine, sample_cards):
        """测试随从攻击"""
        engine, game_id, user1, user2 = game_engine
        fireball, minion = sample_cards

        # 设置战场上的随从
        game_state = engine.games[game_id]
        player1 = game_state.player1
        player2 = game_state.player2

        attacking_minion = Mock()
        attacking_minion.id = 1
        attacking_minion.attack = 3
        attacking_minion.defense = 5
        attacking_minion.can_attack = True

        defending_minion = Mock()
        defending_minion.id = 2
        defending_minion.attack = 2
        defending_minion.defense = 4

        player1.battlefield = [attacking_minion]
        player2.battlefield = [defending_minion]

        success = await engine.attack_minion(
            game_id, user1.id, attacking_minion.id, defending_minion.id
        )

        assert success
        # 验证伤害计算
        assert attacking_minion.defense == 3  # 5 - 2
        assert defending_minion.defense == 1  # 4 - 3

    @pytest.mark.asyncio
    async def test_attack_hero(self, game_engine, sample_cards):
        """测试攻击英雄"""
        engine, game_id, user1, user2 = game_engine
        fireball, minion = sample_cards

        game_state = engine.games[game_id]
        player1 = game_state.player1
        player2 = game_state.player2

        attacking_minion = Mock()
        attacking_minion.id = 1
        attacking_minion.attack = 4
        attacking_minion.can_attack = True

        player1.battlefield = [attacking_minion]
        player2.health = 30

        success = await engine.attack_hero(
            game_id, user1.id, attacking_minion.id
        )

        assert success
        assert player2.health == 26  # 30 - 4

    @pytest.mark.asyncio
    async def test_end_turn(self, game_engine):
        """测试结束回合"""
        engine, game_id, user1, user2 = game_engine

        initial_player = engine.games[game_id].current_player_number
        initial_mana = engine.games[game_id].current_player.max_mana

        success = await engine.end_turn(game_id, user1.id)

        assert success
        assert engine.games[game_id].current_player_number != initial_player
        assert engine.games[game_id].current_player.max_mana == min(initial_mana + 1, 10)

    def test_concede_game(self, game_engine):
        """测试认输"""
        engine, game_id, user1, user2 = game_engine

        success = engine.concede(game_id, user1.id)

        assert success
        assert engine.games[game_id].is_game_over
        assert engine.games[game_id].winner == user2.id

    def test_get_valid_actions(self, game_engine, sample_cards):
        """测试获取有效操作"""
        engine, game_id, user1, user2 = game_engine
        fireball, minion = sample_cards

        game_state = engine.games[game_id]
        current_player = game_state.current_player
        current_player.hand = [fireball, minion]
        current_player.mana = 4

        actions = engine.get_valid_actions(game_id, user1.id)

        assert len(actions) > 0
        # 应该包含出牌操作
        play_actions = [a for a in actions if a['type'] == 'play_card']
        assert len(play_actions) > 0

    def test_undo_action(self, game_engine):
        """测试撤销操作"""
        engine, game_id, user1, user2 = game_engine

        # 添加一些操作历史
        game_state = engine.games[game_id]
        game_state.action_history = [
            {'type': 'play_card', 'card_id': 1},
            {'type': 'attack', 'attacker_id': 1, 'target_id': 2}
        ]

        success = engine.undo_action(game_id, user1.id)

        assert success
        assert len(game_state.action_history) == 1

    def test_game_over_conditions(self, game_engine):
        """测试游戏结束条件"""
        engine, game_id, user1, user2 = game_engine

        game_state = engine.games[game_id]
        player2 = game_state.player2
        player2.health = 0

        engine.check_game_over(game_id)

        assert game_state.is_game_over
        assert game_state.winner == user1.id

    def test_mana_management(self, game_engine):
        """测试法力值管理"""
        engine, game_id, user1, user2 = game_engine

        game_state = engine.games[game_id]
        current_player = game_state.current_player

        # 测试法力值重置
        current_player.mana = 2
        current_player.max_mana = 5
        engine.reset_mana(game_id, current_player.user_id)

        assert current_player.mana == current_player.max_mana

    def test_card_draw(self, game_engine):
        """测试抽牌"""
        engine, game_id, user1, user2 = game_engine

        game_state = engine.games[game_id]
        current_player = game_state.current_player
        initial_hand_size = len(current_player.hand)

        success = engine.draw_card(game_id, current_player.user_id)

        assert success
        assert len(current_player.hand) == initial_hand_size + 1

    def test_deck_exhaustion(self, game_engine):
        """测试牌库耗尽"""
        engine, game_id, user1, user2 = game_engine

        game_state = engine.games[game_id]
        current_player = game_state.current_player
        current_player.deck = []  # 空牌库
        initial_health = current_player.health

        # 抽牌应该受到疲劳伤害
        engine.draw_card(game_id, current_player.user_id)

        assert current_player.health == initial_health - 1

    @pytest.mark.asyncio
    async def test_card_effects(self, game_engine, sample_cards):
        """测试卡牌效果"""
        engine, game_id, user1, user2 = game_engine
        fireball, minion = sample_cards

        # 为火球术添加效果处理
        with patch.object(engine, '_handle_spell_effect') as mock_effect:
            mock_effect.return_value = True

            game_state = engine.games[game_id]
            current_player = game_state.current_player
            current_player.hand = [fireball]
            current_player.mana = 4

            success = await engine.play_card(
                game_id, user1.id, fireball.id, target_player_id=user2.id
            )

            assert success
            mock_effect.assert_called_once()


class TestGameState:
    """游戏状态测试"""

    def test_game_state_initialization(self, mock_users):
        """测试游戏状态初始化"""
        user1, user2 = mock_users
        game_state = GameState(user1.id, user2.id)

        assert game_state.player1_id == user1.id
        assert game_state.player2_id == user2.id
        assert game_state.turn_number == 1
        assert game_state.current_player_number == 1
        assert not game_state.is_game_over

    def test_player_switching(self, mock_users):
        """测试玩家切换"""
        user1, user2 = mock_users
        game_state = GameState(user1.id, user2.id)

        initial_player = game_state.current_player_number
        game_state.switch_player()

        assert game_state.current_player_number != initial_player

    def test_action_history(self, mock_users):
        """测试操作历史"""
        user1, user2 = mock_users
        game_state = GameState(user1.id, user2.id)

        action = {'type': 'play_card', 'card_id': 1}
        game_state.add_action(action)

        assert len(game_state.action_history) == 1
        assert game_state.action_history[0] == action

    def test_game_state_serialization(self, mock_users):
        """测试游戏状态序列化"""
        user1, user2 = mock_users
        game_state = GameState(user1.id, user2.id)

        serialized = game_state.to_dict()
        assert 'player1_id' in serialized
        assert 'player2_id' in serialized
        assert 'turn_number' in serialized

    def test_winner_determination(self, mock_users):
        """测试胜负判定"""
        user1, user2 = mock_users
        game_state = GameState(user1.id, user2.id)

        game_state.set_winner(user1.id)
        assert game_state.winner == user1.id
        assert game_state.is_game_over


if __name__ == '__main__':
    pytest.main([__file__])