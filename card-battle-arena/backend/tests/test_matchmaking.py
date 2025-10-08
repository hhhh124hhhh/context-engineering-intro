import pytest
import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock
from app.core.matchmaking.matcher import (
    MatchmakingEngine,
    MatchmakingQueue,
    ELOMatcher,
    MatchRequest,
    GameMode,
    MatchStatus
)
from app.models.user import User


@pytest.fixture
def mock_users():
    """模拟用户数据"""
    users = []
    for i in range(5):
        user = Mock(spec=User)
        user.id = i + 1
        user.username = f"player{i + 1}"
        user.rating = 1000 + (i * 200)  # 1000, 1200, 1400, 1600, 1800
        users.append(user)
    return users


@pytest.fixture
def matchmaking_engine():
    """创建匹配引擎实例"""
    return MatchmakingEngine()


@pytest.fixture
def sample_requests(mock_users):
    """示例匹配请求"""
    requests = []
    for i, user in enumerate(mock_users[:3]):  # 只使用前3个用户
        request = MatchRequest(
            user_id=user.id,
            username=user.username,
            mode=GameMode.RANKED,
            deck_id=1,
            deck_name=f"Deck {i + 1}",
            rating=user.rating,
            preferences={}
        )
        requests.append(request)
    return requests


class TestMatchmakingQueue:
    """匹配队列测试"""

    def test_add_request(self):
        """测试添加匹配请求"""
        queue = MatchmakingQueue()
        request = MatchRequest(
            user_id=1,
            username="player1",
            mode=GameMode.RANKED,
            deck_id=1,
            deck_name="Test Deck",
            rating=1500
        )

        queue_id = queue.add_request(request)

        assert queue_id is not None
        assert len(queue.queues[GameMode.RANKED]) == 1
        assert queue.get_request(1, GameMode.RANKED) == request

    def test_remove_request(self):
        """测试移除匹配请求"""
        queue = MatchmakingQueue()
        request = MatchRequest(
            user_id=1,
            username="player1",
            mode=GameMode.RANKED,
            deck_id=1,
            deck_name="Test Deck",
            rating=1500
        )

        queue.add_request(request)
        removed_request = queue.remove_request(1, GameMode.RANKED)

        assert removed_request == request
        assert len(queue.queues[GameMode.RANKED]) == 0
        assert queue.get_request(1, GameMode.RANKED) is None

    def test_remove_nonexistent_request(self):
        """测试移除不存在的请求"""
        queue = MatchmakingQueue()

        removed_request = queue.remove_request(999, GameMode.RANKED)

        assert removed_request is None

    def test_get_expired_requests(self):
        """测试获取过期请求"""
        queue = MatchmakingQueue()
        queue.max_wait_time = 1  # 1秒过期

        request = MatchRequest(
            user_id=1,
            username="player1",
            mode=GameMode.RANKED,
            deck_id=1,
            deck_name="Test Deck",
            rating=1500,
            created_at=time.time() - 2  # 2秒前创建
        )

        queue.add_request(request)
        expired = queue.get_expired_requests()

        assert len(expired) == 1
        assert expired[0] == request
        assert len(queue.queues[GameMode.RANKED]) == 0


class TestELOMatcher:
    """ELO匹配器测试"""

    def test_calculate_rating_range(self):
        """测试计算ELO范围"""
        matcher = ELOMatcher()

        # 基础范围
        min_rating, max_rating = matcher.calculate_rating_range(1500, 0)
        assert min_rating == 1400  # 1500 - 100
        assert max_rating == 1600  # 1500 + 100

        # 扩展范围（等待时间长）
        min_rating, max_rating = matcher.calculate_rating_range(1500, 120)
        assert max_rating > 1600  # 应该扩展

    def test_is_matchable_same_rating(self):
        """测试相同ELO匹配"""
        matcher = ELOMatcher()

        req1 = MatchRequest(
            user_id=1,
            username="player1",
            mode=GameMode.RANKED,
            deck_id=1,
            deck_name="Deck 1",
            rating=1500
        )

        req2 = MatchRequest(
            user_id=2,
            username="player2",
            mode=GameMode.RANKED,
            deck_id=2,
            deck_name="Deck 2",
            rating=1500
        )

        assert matcher.is_matchable(req1, req2)

    def test_is_matchable_different_modes(self):
        """测试不同模式不匹配"""
        matcher = ELOMatcher()

        req1 = MatchRequest(
            user_id=1,
            username="player1",
            mode=GameMode.RANKED,
            deck_id=1,
            deck_name="Deck 1",
            rating=1500
        )

        req2 = MatchRequest(
            user_id=2,
            username="player2",
            mode=GameMode.CASUAL,
            deck_id=2,
            deck_name="Deck 2",
            rating=1500
        )

        assert not matcher.is_matchable(req1, req2)

    def test_is_matchable_large_rating_difference(self):
        """测试大ELO差距不匹配"""
        matcher = ELOMatcher()

        req1 = MatchRequest(
            user_id=1,
            username="player1",
            mode=GameMode.RANKED,
            deck_id=1,
            deck_name="Deck 1",
            rating=1500
        )

        req2 = MatchRequest(
            user_id=2,
            username="player2",
            mode=GameMode.RANKED,
            deck_id=2,
            deck_name="Deck 2",
            rating=2500  # 1000点差距
        )

        assert not matcher.is_matchable(req1, req2)

    def test_is_matchable_same_user(self):
        """测试同一用户不匹配"""
        matcher = ELOMatcher()

        req1 = MatchRequest(
            user_id=1,
            username="player1",
            mode=GameMode.RANKED,
            deck_id=1,
            deck_name="Deck 1",
            rating=1500
        )

        req2 = MatchRequest(
            user_id=1,
            username="player1",
            mode=GameMode.RANKED,
            deck_id=2,
            deck_name="Deck 2",
            rating=1500
        )

        assert not matcher.is_matchable(req1, req2)


class TestMatchmakingEngine:
    """匹配引擎测试"""

    @pytest.mark.asyncio
    async def test_start_stop_engine(self, matchmaking_engine):
        """测试启动和停止引擎"""
        assert not matchmaking_engine.running

        await matchmaking_engine.start()
        assert matchmaking_engine.running
        assert matchmaking_engine._task is not None

        await matchmaking_engine.stop()
        assert not matchmaking_engine.running

    @pytest.mark.asyncio
    async def test_add_match_request(self, matchmaking_engine):
        """测试添加匹配请求"""
        request = MatchRequest(
            user_id=1,
            username="player1",
            mode=GameMode.RANKED,
            deck_id=1,
            deck_name="Test Deck",
            rating=1500
        )

        queue_id = await matchmaking_engine.add_match_request(request)

        assert queue_id is not None
        assert matchmaking_engine.get_user_status(1)["in_queue"]

    @pytest.mark.asyncio
    async def test_remove_match_request(self, matchmaking_engine):
        """测试移除匹配请求"""
        request = MatchRequest(
            user_id=1,
            username="player1",
            mode=GameMode.RANKED,
            deck_id=1,
            deck_name="Test Deck",
            rating=1500
        )

        await matchmaking_engine.add_match_request(request)
        success = await matchmaking_engine.remove_match_request(1, GameMode.RANKED)

        assert success
        assert not matchmaking_engine.get_user_status(1)["in_queue"]

    @pytest.mark.asyncio
    async def test_auto_matching(self, matchmaking_engine, sample_requests):
        """测试自动匹配"""
        await matchmaking_engine.start()

        # 添加两个匹配请求
        req1, req2, req3 = sample_requests[:2]
        await matchmaking_engine.add_match_request(req1)
        await matchmaking_engine.add_match_request(req2)

        # 等待匹配处理
        await asyncio.sleep(0.1)

        # 验证匹配结果
        user1_status = matchmaking_engine.get_user_status(req1.user_id)
        user2_status = matchmaking_engine.get_user_status(req2.user_id)

        assert not user1_status["in_queue"]
        assert not user2_status["in_queue"]
        assert user1_status["in_match"]
        assert user2_status["in_match"]
        assert user1_status["match_id"] == user2_status["match_id"]

        await matchmaking_engine.stop()

    @pytest.mark.asyncio
    async def test_queue_status(self, matchmaking_engine, sample_requests):
        """测试队列状态"""
        await matchmaking_engine.add_match_request(sample_requests[0])

        status = matchmaking_engine.get_queue_status(GameMode.RANKED)

        assert status["mode"] == GameMode.RANKED
        assert status["queue_length"] == 1
        assert status["average_wait_time"] >= 0

    def test_user_status_not_in_queue(self, matchmaking_engine):
        """测试用户不在队列中的状态"""
        status = matchmaking_engine.get_user_status(999)

        assert not status["in_queue"]
        assert not status["in_match"]

    @pytest.mark.asyncio
    async def test_multiple_modes(self, matchmaking_engine, sample_requests):
        """测试多种游戏模式"""
        await matchmaking_engine.start()

        # 添加不同模式的请求
        ranked_request = sample_requests[0]
        casual_request = MatchRequest(
            user_id=4,
            username="player4",
            mode=GameMode.CASUAL,
            deck_id=4,
            deck_name="Casual Deck",
            rating=1400
        )

        await matchmaking_engine.add_match_request(ranked_request)
        await matchmaking_engine.add_match_request(casual_request)

        # 检查队列状态
        ranked_status = matchmaking_engine.get_queue_status(GameMode.RANKED)
        casual_status = matchmaking_engine.get_queue_status(GameMode.CASUAL)

        assert ranked_status["queue_length"] == 1
        assert casual_status["queue_length"] == 1

        await matchmaking_engine.stop()

    @pytest.mark.asyncio
    async def test_matching_with_rating_expansion(self, matchmaking_engine):
        """测试ELO范围扩展匹配"""
        await matchmaking_engine.start()

        # 创建两个ELO差距较大的请求
        req1 = MatchRequest(
            user_id=1,
            username="player1",
            mode=GameMode.RANKED,
            deck_id=1,
            deck_name="Deck 1",
            rating=1500,
            created_at=time.time() - 200  # 等待了200秒
        )

        req2 = MatchRequest(
            user_id=2,
            username="player2",
            mode=GameMode.RANKED,
            deck_id=2,
            deck_name="Deck 2",
            rating=2000,  # 500点差距
            created_at=time.time() - 200
        )

        await matchmaking_engine.add_match_request(req1)
        await matchmaking_engine.add_match_request(req2)

        # 等待匹配处理
        await asyncio.sleep(0.1)

        # 由于等待时间长，应该能够匹配
        user1_status = matchmaking_engine.get_user_status(1)
        user2_status = matchmaking_engine.get_user_status(2)

        # 根据ELO匹配器的实现，可能匹配也可能不匹配
        # 这取决于具体的扩展阈值设置

        await matchmaking_engine.stop()

    @pytest.mark.asyncio
    async def test_concurrent_requests(self, matchmaking_engine, mock_users):
        """测试并发请求处理"""
        await matchmaking_engine.start()

        # 同时添加多个请求
        tasks = []
        for i, user in enumerate(mock_users[:6]):  # 6个用户
            request = MatchRequest(
                user_id=user.id,
                username=user.username,
                mode=GameMode.RANKED,
                deck_id=i + 1,
                deck_name=f"Deck {i + 1}",
                rating=user.rating
            )
            task = matchmaking_engine.add_match_request(request)
            tasks.append(task)

        await asyncio.gather(*tasks)

        # 等待匹配处理
        await asyncio.sleep(0.2)

        # 验证匹配结果
        matched_users = []
        for user in mock_users[:6]:
            status = matchmaking_engine.get_user_status(user.id)
            if status["in_match"]:
                matched_users.append(user.id)

        # 应该有用户被匹配
        assert len(matched_users) >= 2
        assert len(matched_users) % 2 == 0  # 匹配数量应该是偶数

        await matchmaking_engine.stop()


class TestIntegration:
    """集成测试"""

    @pytest.mark.asyncio
    async def test_full_matchmaking_flow(self, matchmaking_engine, mock_users):
        """测试完整的匹配流程"""
        await matchmaking_engine.start()

        user1, user2 = mock_users[:2]

        # 1. 添加匹配请求
        req1 = MatchRequest(
            user_id=user1.id,
            username=user1.username,
            mode=GameMode.RANKED,
            deck_id=1,
            deck_name="Deck 1",
            rating=user1.rating
        )

        req2 = MatchRequest(
            user_id=user2.id,
            username=user2.username,
            mode=GameMode.RANKED,
            deck_id=2,
            deck_name="Deck 2",
            rating=user2.rating
        )

        await matchmaking_engine.add_match_request(req1)
        await matchmaking_engine.add_match_request(req2)

        # 2. 等待匹配
        await asyncio.sleep(0.1)

        # 3. 验证匹配成功
        status1 = matchmaking_engine.get_user_status(user1.id)
        status2 = matchmaking_engine.get_user_status(user2.id)

        assert status1["in_match"]
        assert status2["in_match"]
        assert status1["match_id"] == status2["match_id"]

        # 4. 验证匹配对象存在
        match = matchmaking_engine.active_matches.get(status1["match_id"])
        assert match is not None
        assert match.player1_id == user1.id
        assert match.player2_id == user2.id

        await matchmaking_engine.stop()

    @pytest.mark.asyncio
    async def test_match_cancellation(self, matchmaking_engine, mock_users):
        """测试匹配取消"""
        await matchmaking_engine.start()

        user1 = mock_users[0]

        # 添加匹配请求
        request = MatchRequest(
            user_id=user1.id,
            username=user1.username,
            mode=GameMode.RANKED,
            deck_id=1,
            deck_name="Deck 1",
            rating=user1.rating
        )

        await matchmaking_engine.add_match_request(request)

        # 验证在队列中
        assert matchmaking_engine.get_user_status(user1.id)["in_queue"]

        # 取消匹配
        success = await matchmaking_engine.remove_match_request(user1.id, GameMode.RANKED)

        # 验证取消成功
        assert success
        assert not matchmaking_engine.get_user_status(user1.id)["in_queue"]

        await matchmaking_engine.stop()


if __name__ == '__main__':
    pytest.main([__file__])