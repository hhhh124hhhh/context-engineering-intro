"""
Redis服务单元测试
"""

import pytest
import json
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import asyncio

from app.database.redis import RedisService, GameCacheService, init_redis, close_redis


class TestRedisService:
    """Redis服务测试类"""

    @pytest.fixture
    def mock_redis_client(self):
        """模拟Redis客户端"""
        mock_client = Mock()
        mock_client.ping.return_value = True
        return mock_client

    @pytest.fixture
    def redis_service(self, mock_redis_client):
        """创建Redis服务实例"""
        return RedisService(mock_redis_client)

    def test_set_success(self, redis_service):
        """测试成功设置键值对"""
        # 测试字符串值
        redis_service.redis.set.return_value = True
        result = redis_service.set("test_key", "test_value")
        assert result is True
        redis_service.redis.set.assert_called_once_with("test_key", "test_value", ex=None)

        # 测试字典值
        test_dict = {"key": "value"}
        redis_service.redis.set.return_value = True
        result = redis_service.set("test_dict", test_dict, expire=60)
        assert result is True
        expected_value = json.dumps(test_dict)
        redis_service.redis.set.assert_called_once_with("test_dict", expected_value, ex=60)

    def test_set_failure(self, redis_service):
        """测试设置键值对失败"""
        redis_service.redis.set.side_effect = Exception("Connection error")
        result = redis_service.set("test_key", "test_value")
        assert result is False

    def test_get_success(self, redis_service):
        """测试成功获取值"""
        # 测试字符串值
        redis_service.redis.get.return_value = "test_value"
        result = redis_service.get("test_key")
        assert result == "test_value"
        redis_service.redis.get.assert_called_once_with("test_key")

        # 测试JSON值
        test_dict = {"key": "value"}
        redis_service.redis.get.return_value = json.dumps(test_dict)
        result = redis_service.get("test_key", as_json=True)
        assert result == test_dict

    def test_get_none(self, redis_service):
        """测试获取不存在的键"""
        redis_service.redis.get.return_value = None
        result = redis_service.get("non_existent_key")
        assert result is None

    def test_get_json_decode_error(self, redis_service):
        """测试JSON解码错误"""
        redis_service.redis.get.return_value = "invalid_json"
        result = redis_service.get("test_key", as_json=True)
        assert result == "invalid_json"

    def test_get_failure(self, redis_service):
        """测试获取值失败"""
        redis_service.redis.get.side_effect = Exception("Connection error")
        result = redis_service.get("test_key")
        assert result is None

    def test_delete_success(self, redis_service):
        """测试成功删除键"""
        redis_service.redis.delete.return_value = 1
        result = redis_service.delete("test_key")
        assert result == 1
        redis_service.redis.delete.assert_called_once_with("test_key")

    def test_delete_multiple_keys(self, redis_service):
        """测试删除多个键"""
        redis_service.redis.delete.return_value = 2
        result = redis_service.delete("key1", "key2")
        assert result == 2
        redis_service.redis.delete.assert_called_once_with("key1", "key2")

    def test_delete_failure(self, redis_service):
        """测试删除键失败"""
        redis_service.redis.delete.side_effect = Exception("Connection error")
        result = redis_service.delete("test_key")
        assert result == 0

    def test_exists_true(self, redis_service):
        """测试键存在检查 - 存在"""
        redis_service.redis.exists.return_value = 1
        result = redis_service.exists("test_key")
        assert result is True
        redis_service.redis.exists.assert_called_once_with("test_key")

    def test_exists_false(self, redis_service):
        """测试键存在检查 - 不存在"""
        redis_service.redis.exists.return_value = 0
        result = redis_service.exists("test_key")
        assert result is False

    def test_exists_failure(self, redis_service):
        """测试键存在检查失败"""
        redis_service.redis.exists.side_effect = Exception("Connection error")
        result = redis_service.exists("test_key")
        assert result is False

    def test_expire_success(self, redis_service):
        """测试设置过期时间成功"""
        redis_service.redis.expire.return_value = True
        result = redis_service.expire("test_key", 300)
        assert result is True
        redis_service.redis.expire.assert_called_once_with("test_key", 300)

    def test_expire_failure(self, redis_service):
        """测试设置过期时间失败"""
        redis_service.redis.expire.side_effect = Exception("Connection error")
        result = redis_service.expire("test_key", 300)
        assert result is False

    def test_ttl_success(self, redis_service):
        """测试获取TTL成功"""
        redis_service.redis.ttl.return_value = 300
        result = redis_service.ttl("test_key")
        assert result == 300
        redis_service.redis.ttl.assert_called_once_with("test_key")

    def test_ttl_no_key(self, redis_service):
        """测试获取不存在键的TTL"""
        redis_service.redis.ttl.return_value = -1
        result = redis_service.ttl("non_existent_key")
        assert result == -1

    def test_ttl_failure(self, redis_service):
        """测试获取TTL失败"""
        redis_service.redis.ttl.side_effect = Exception("Connection error")
        result = redis_service.ttl("test_key")
        assert result == -1

    def test_hash_operations(self, redis_service):
        """测试哈希操作"""
        # 测试hset
        redis_service.redis.hset.return_value = 2
        result = redis_service.hset("test_hash", {"field1": "value1", "field2": "value2"})
        assert result == 2
        redis_service.redis.hset.assert_called_once_with("test_hash", mapping={"field1": "value1", "field2": "value2"})

        # 测试hget
        redis_service.redis.hget.return_value = "value1"
        result = redis_service.hget("test_hash", "field1")
        assert result == "value1"
        redis_service.redis.hget.assert_called_once_with("test_hash", "field1")

        # 测试hgetall
        redis_service.redis.hgetall.return_value = {"field1": "value1", "field2": "value2"}
        result = redis_service.hgetall("test_hash")
        assert result == {"field1": "value1", "field2": "value2"}
        redis_service.redis.hgetall.assert_called_once_with("test_hash")

    def test_list_operations(self, redis_service):
        """测试列表操作"""
        # 测试lpush
        redis_service.redis.lpush.return_value = 2
        result = redis_service.lpush("test_list", "item1", "item2")
        assert result == 2
        redis_service.redis.lpush.assert_called_once_with("test_list", "item1", "item2")

        # 测试rpop
        redis_service.redis.rpop.return_value = "item1"
        result = redis_service.rpop("test_list")
        assert result == "item1"
        redis_service.redis.rpop.assert_called_once_with("test_list")

        # 测试lrange
        redis_service.redis.lrange.return_value = ["item1", "item2"]
        result = redis_service.lrange("test_list", 0, -1)
        assert result == ["item1", "item2"]
        redis_service.redis.lrange.assert_called_once_with("test_list", 0, -1)

    def test_increment_decrement(self, redis_service):
        """测试递增递减操作"""
        # 测试incr
        redis_service.redis.incr.return_value = 1
        result = redis_service.incr("counter")
        assert result == 1
        redis_service.redis.incr.assert_called_once_with("counter")

        # 测试decr
        redis_service.redis.decr.return_value = 0
        result = redis_service.decr("counter")
        assert result == 0
        redis_service.redis.decr.assert_called_once_with("counter")


class TestGameCacheService:
    """游戏缓存服务测试类"""

    @pytest.fixture
    def mock_redis_service(self):
        """模拟Redis服务"""
        return Mock(spec=RedisService)

    @pytest.fixture
    def game_cache_service(self, mock_redis_service):
        """创建游戏缓存服务实例"""
        return GameCacheService(mock_redis_service)

    def test_cache_card_data_success(self, game_cache_service, mock_redis_service):
        """测试缓存卡牌数据成功"""
        mock_redis_service.set.return_value = True
        card_data = {"id": 1, "name": "Test Card", "attack": 5}

        result = game_cache_service.cache_card_data("1", card_data)
        assert result is True
        mock_redis_service.set.assert_called_once()

    def test_cache_card_data_failure(self, game_cache_service, mock_redis_service):
        """测试缓存卡牌数据失败"""
        mock_redis_service.set.return_value = False
        card_data = {"id": 1, "name": "Test Card", "attack": 5}

        result = game_cache_service.cache_card_data("1", card_data)
        assert result is False

    def test_get_cached_card(self, game_cache_service, mock_redis_service):
        """测试获取缓存的卡牌数据"""
        expected_data = {"id": 1, "name": "Test Card", "attack": 5}
        mock_redis_service.get.return_value = expected_data

        result = game_cache_service.get_cached_card("1")
        assert result == expected_data
        mock_redis_service.get.assert_called_once_with("card:1", as_json=True)

    def test_cache_user_session(self, game_cache_service, mock_redis_service):
        """测试缓存用户会话"""
        mock_redis_service.set.return_value = True
        session_data = {"session_id": "123", "ip_address": "127.0.0.1"}

        result = game_cache_service.cache_user_session("user1", session_data)
        assert result is True
        mock_redis_service.set.assert_called_once()

    def test_get_user_session(self, game_cache_service, mock_redis_service):
        """测试获取用户会话"""
        expected_data = {"session_id": "123", "ip_address": "127.0.0.1"}
        mock_redis_service.get.return_value = expected_data

        result = game_cache_service.get_user_session("user1")
        assert result == expected_data
        mock_redis_service.get.assert_called_once_with("session:user1", as_json=True)

    def test_cache_game_state(self, game_cache_service, mock_redis_service):
        """测试缓存游戏状态"""
        mock_redis_service.set.return_value = True
        game_state = {"turn": 1, "player1": {"health": 20}}

        result = game_cache_service.cache_game_state("game1", game_state)
        assert result is True
        mock_redis_service.set.assert_called_once_with("game_state:game1", game_state, expire=3600)

    def test_get_cached_game_state(self, game_cache_service, mock_redis_service):
        """测试获取缓存的游戏状态"""
        expected_state = {"turn": 1, "player1": {"health": 20}}
        mock_redis_service.get.return_value = expected_state

        result = game_cache_service.get_cached_game_state("game1")
        assert result == expected_state
        mock_redis_service.get.assert_called_once_with("game_state:game1", as_json=True)


class TestRedisConnection:
    """Redis连接测试类"""

    @patch('app.database.redis.redis.Redis.from_url')
    @patch('app.database.redis.settings')
    async def test_init_redis_success(self, mock_settings, mock_redis_from_url):
        """测试成功初始化Redis连接"""
        mock_settings.REDIS_URL = "redis://localhost:6379"
        mock_settings.REDIS_DB = 0
        mock_client = Mock()
        mock_client.ping.return_value = True
        mock_redis_from_url.return_value = mock_client

        # 重置全局变量
        import app.database.redis
        app.database.redis.redis_client = None

        await init_redis()

        assert app.database.redis.redis_client is not None
        mock_client.ping.assert_called_once()

    @patch('app.database.redis.redis.Redis.from_url')
    @patch('app.database.redis.settings')
    async def test_init_redis_failure(self, mock_settings, mock_redis_from_url):
        """测试初始化Redis连接失败"""
        mock_settings.REDIS_URL = "redis://localhost:6379"
        mock_settings.REDIS_DB = 0
        mock_redis_from_url.side_effect = Exception("Connection failed")

        # 重置全局变量
        import app.database.redis
        app.database.redis.redis_client = None

        with pytest.raises(Exception):
            await init_redis()

    async def test_close_redis(self):
        """测试关闭Redis连接"""
        mock_client = Mock()

        # 设置全局变量
        import app.database.redis
        app.database.redis.redis_client = mock_client

        await close_redis()

        mock_client.close.assert_called_once()

    def test_check_redis_health_success(self):
        """测试Redis健康检查成功"""
        mock_client = Mock()
        mock_client.ping.return_value = True

        # 设置全局变量
        import app.database.redis
        app.database.redis.redis_client = mock_client

        result = app.database.redis.check_redis_health()
        assert result is True

    def test_check_redis_health_failure(self):
        """测试Redis健康检查失败"""
        # 设置全局变量为None
        import app.database.redis
        app.database.redis.redis_client = None

        result = app.database.redis.check_redis_health()
        assert result is False

    def test_check_redis_health_exception(self):
        """测试Redis健康检查异常"""
        mock_client = Mock()
        mock_client.ping.side_effect = Exception("Ping failed")

        # 设置全局变量
        import app.database.redis
        app.database.redis.redis_client = mock_client

        result = app.database.redis.check_redis_health()
        assert result is False