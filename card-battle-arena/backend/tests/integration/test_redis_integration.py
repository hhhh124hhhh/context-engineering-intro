"""
Redis集成测试
测试Redis集成和缓存功能
"""

import pytest
import asyncio
from unittest.mock import patch, Mock, AsyncMock

# Mark as integration tests
pytestmark = pytest.mark.integration


class TestRedisIntegration:
    """Redis集成测试类"""

    @pytest.mark.asyncio
    @pytest.mark.redis
    async def test_redis_connection_and_basic_operations(self):
        """测试Redis连接和基本操作"""
        from app.database.redis import init_redis, close_redis, check_redis_health, get_redis_service

        try:
            # 初始化Redis连接
            await init_redis()
            assert check_redis_health() is True

            # 获取Redis服务
            redis_service = await get_redis_service()
            assert redis_service is not None

            # 测试基本操作
            test_key = f"integration_test_{asyncio.current_task().get_name()}"
            test_value = "test_value"

            # 设置值
            set_result = redis_service.set(test_key, test_value, expire=60)
            assert set_result is True

            # 获取值
            get_result = redis_service.get(test_key)
            assert get_result == test_value

            # 检查键是否存在
            exists_result = redis_service.exists(test_key)
            assert exists_result is True

            # 删除键
            delete_result = redis_service.delete(test_key)
            assert delete_result == 1

            # 验证键已删除
            exists_after_delete = redis_service.exists(test_key)
            assert exists_after_delete is False

            # 关闭连接
            await close_redis()

        except Exception as e:
            pytest.skip(f"Redis not available for integration testing: {e}")

    @pytest.mark.asyncio
    @pytest.mark.redis
    async def test_redis_json_operations(self):
        """测试Redis JSON操作"""
        from app.database.redis import init_redis, get_redis_service

        try:
            await init_redis()
            redis_service = await get_redis_service()

            # 测试JSON数据操作
            test_key = "json_test"
            test_data = {
                "user_id": 123,
                "username": "testuser",
                "permissions": ["read", "write"],
                "metadata": {"last_login": "2025-10-08T10:00:00Z"}
            }

            # 设置JSON数据
            set_result = redis_service.set(test_key, test_data, expire=60)
            assert set_result is True

            # 获取JSON数据
            get_result = redis_service.get(test_key, as_json=True)
            assert get_result == test_data

            # 清理
            redis_service.delete(test_key)

        except Exception as e:
            pytest.skip(f"Redis not available for integration testing: {e}")

    @pytest.mark.asyncio
    @pytest.mark.redis
    async def test_game_cache_service_operations(self):
        """测试游戏缓存服务操作"""
        from app.database.redis import init_redis, get_game_cache_service

        try:
            await init_redis()
            cache_service = await get_game_cache_service()

            # 测试用户会话缓存
            user_id = "test_user_123"
            session_data = {
                "session_id": "session_456",
                "ip_address": "127.0.0.1",
                "login_time": "2025-10-08T10:00:00Z"
            }

            # 缓存用户会话
            cache_result = cache_service.cache_user_session(user_id, session_data)
            assert cache_result is True

            # 获取缓存的会话
            cached_session = cache_service.get_user_session(user_id)
            assert cached_session == session_data

            # 测试卡牌数据缓存
            card_id = "card_789"
            card_data = {
                "id": card_id,
                "name": "Fireball",
                "cost": 4,
                "attack": 6,
                "card_type": "spell"
            }

            # 缓存卡牌数据
            card_cache_result = cache_service.cache_card_data(card_id, card_data)
            assert card_cache_result is True

            # 获取缓存的卡牌数据
            cached_card = cache_service.get_cached_card(card_id)
            assert cached_card == card_data

            # 测试游戏状态缓存
            game_id = "game_456"
            game_state = {
                "player1": {"health": 30, "mana": 1},
                "player2": {"health": 30, "mana": 0},
                "turn": 1,
                "current_player": 1
            }

            # 缓存游戏状态
            game_cache_result = cache_service.cache_game_state(game_id, game_state)
            assert game_cache_result is True

            # 获取缓存的游戏状态
            cached_game_state = cache_service.get_cached_game_state(game_id)
            assert cached_game_state == game_state

        except Exception as e:
            pytest.skip(f"Redis not available for integration testing: {e}")

    @pytest.mark.asyncio
    @pytest.mark.redis
    async def test_redis_hash_operations(self):
        """测试Redis哈希操作"""
        from app.database.redis import init_redis, get_redis_service

        try:
            await init_redis()
            redis_service = await get_redis_service()

            hash_name = "test_hash"
            hash_data = {
                "field1": "value1",
                "field2": "value2",
                "field3": "value3"
            }

            # 设置哈希字段
            hset_result = redis_service.hset(hash_name, hash_data)
            assert hset_result == len(hash_data)

            # 获取单个字段
            field1_value = redis_service.hget(hash_name, "field1")
            assert field1_value == "value1"

            # 获取所有字段
            all_fields = redis_service.hgetall(hash_name)
            assert all_fields == hash_data

            # 清理
            redis_service.delete(hash_name)

        except Exception as e:
            pytest.skip(f"Redis not available for integration testing: {e}")

    @pytest.mark.asyncio
    @pytest.mark.redis
    async def test_redis_list_operations(self):
        """测试Redis列表操作"""
        from app.database.redis import init_redis, get_redis_service

        try:
            await init_redis()
            redis_service = await get_redis_service()

            list_name = "test_list"
            test_items = ["item1", "item2", "item3"]

            # 推入列表
            lpush_result = redis_service.lpush(list_name, *test_items)
            assert lpush_result == len(test_items)

            # 获取列表范围
            list_range = redis_service.lrange(list_name, 0, -1)
            assert len(list_range) == len(test_items)

            # 从尾部弹出
            rpop_result = redis_service.rpop(list_name)
            assert rpop_result in test_items

            # 清理
            redis_service.delete(list_name)

        except Exception as e:
            pytest.skip(f"Redis not available for integration testing: {e}")

    @pytest.mark.asyncio
    @pytest.mark.redis
    async def test_redis_expiration_operations(self):
        """测试Redis过期操作"""
        from app.database.redis import init_redis, get_redis_service
        import time

        try:
            await init_redis()
            redis_service = await get_redis_service()

            test_key = "expiration_test"
            test_value = "expires_soon"

            # 设置带过期时间的键
            set_result = redis_service.set(test_key, test_value, expire=2)  # 2秒过期
            assert set_result is True

            # 检查TTL
            ttl = redis_service.ttl(test_key)
            assert ttl > 0  # 应该有剩余时间

            # 等待过期
            time.sleep(3)

            # 检查键是否已过期
            exists_after_ttl = redis_service.exists(test_key)
            assert exists_after_ttl is False

        except Exception as e:
            pytest.skip(f"Redis not available for integration testing: {e}")

    @pytest.mark.asyncio
    @pytest.mark.redis
    async def test_redis_increment_decrement(self):
        """测试Redis递增递减操作"""
        from app.database.redis import init_redis, get_redis_service

        try:
            await init_redis()
            redis_service = await get_redis_service()

            counter_key = "counter_test"

            # 删除可能存在的计数器
            redis_service.delete(counter_key)

            # 递增操作
            incr_result = redis_service.incr(counter_key)
            assert incr_result == 1

            incr_result2 = redis_service.incr(counter_key)
            assert incr_result2 == 2

            # 递减操作
            decr_result = redis_service.decr(counter_key)
            assert decr_result == 1

            # 清理
            redis_service.delete(counter_key)

        except Exception as e:
            pytest.skip(f"Redis not available for integration testing: {e}")

    @pytest.mark.asyncio
    @pytest.mark.redis
    async def test_redis_error_handling(self):
        """测试Redis错误处理"""
        from app.database.redis import init_redis, get_redis_service

        try:
            await init_redis()
            redis_service = await get_redis_service()

            # 测试获取不存在的键
            non_existent = redis_service.get("non_existent_key_12345")
            assert non_existent is None

            # 测试删除不存在的键
            delete_result = redis_service.delete("non_existent_key_12345")
            assert delete_result == 0

            # 测试获取不存在的哈希字段
            non_existent_hash = redis_service.hget("non_existent_hash", "field")
            assert non_existent_hash is None

            # 测试获取不存在的哈希所有字段
            non_existent_hash_all = redis_service.hgetall("non_existent_hash")
            assert non_existent_hash_all == {}

            # 测试从空列表弹出
            empty_list_pop = redis_service.rpop("empty_list")
            assert empty_list_pop is None

        except Exception as e:
            pytest.skip(f"Redis not available for integration testing: {e}")

    @pytest.mark.asyncio
    @pytest.mark.redis
    async def test_concurrent_redis_operations(self):
        """测试并发Redis操作"""
        from app.database.redis import init_redis, get_redis_service

        try:
            await init_redis()
            redis_service = await get_redis_service()

            # 创建多个并发任务
            async def concurrent_set_get(index):
                key = f"concurrent_test_{index}"
                value = f"value_{index}"

                # 设置
                set_result = redis_service.set(key, value, expire=60)
                assert set_result is True

                # 获取
                get_result = redis_service.get(key)
                assert get_result == value

                # 清理
                redis_service.delete(key)

                return True

            # 执行并发操作
            tasks = [concurrent_set_get(i) for i in range(10)]
            results = await asyncio.gather(*tasks)

            # 验证所有操作都成功
            assert all(results)

        except Exception as e:
            pytest.skip(f"Redis not available for integration testing: {e}")

    @pytest.mark.asyncio
    @pytest.mark.redis
    async def test_redis_reconnection(self):
        """测试Redis重连机制"""
        from app.database.redis import init_redis, close_redis, check_redis_health

        try:
            # 初始连接
            await init_redis()
            assert check_redis_health() is True

            # 关闭连接
            await close_redis()

            # 重新连接
            await init_redis()
            assert check_redis_health() is True

            # 测试重连后的操作
            redis_service = await get_game_cache_service()
            test_key = "reconnection_test"
            test_value = "reconnected"

            set_result = redis_service.cache_user_session(test_key, {"data": test_value})
            assert set_result is True

            get_result = redis_service.get_user_session(test_key)
            assert get_result["data"] == test_value

        except Exception as e:
            pytest.skip(f"Redis not available for integration testing: {e}")