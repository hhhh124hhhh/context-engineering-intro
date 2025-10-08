import redis
import json
from typing import Any, Optional, Union
import structlog
from app.core.config import settings

# Redis client instance
redis_client = None

logger = structlog.get_logger()


async def init_redis() -> None:
    """Initialize Redis connection"""
    global redis_client

    try:
        logger.info("Initializing Redis connection", redis_url=settings.REDIS_URL)
        redis_client = redis.Redis.from_url(
            settings.REDIS_URL,
            db=settings.REDIS_DB,
            max_connections=20,
            retry_on_timeout=True,
            socket_keepalive=True,
            decode_responses=True
        )

        # Test connection
        redis_client.ping()
        logger.info("Redis connection established successfully")

    except Exception as e:
        logger.error("Failed to initialize Redis connection", error=str(e))
        raise


async def close_redis() -> None:
    """Close Redis connection"""
    global redis_client

    if redis_client:
        redis_client.close()


async def get_redis():
    """Get Redis client"""
    if redis_client is None:
        raise RuntimeError("Redis not initialized")
    return redis_client


class RedisService:
    """Redis service wrapper with common operations"""

    def __init__(self, redis_client):
        self.redis = redis_client

    def set(
        self,
        key: str,
        value: Union[str, dict, list],
        expire: Optional[int] = None
    ) -> bool:
        """Set a key-value pair in Redis"""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)

            result = self.redis.set(key, value, ex=expire)
            return result
        except Exception as e:
            logger.error("Redis set operation failed", key=key, error=str(e))
            return False

    def get(self, key: str, as_json: bool = False):
        """Get a value from Redis"""
        try:
            value = self.redis.get(key)

            if value is None:
                return None

            if as_json:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    logger.warning("Failed to decode JSON from Redis", key=key)
                    return value

            return value
        except Exception as e:
            logger.error("Redis get operation failed", key=key, error=str(e))
            return None

    def delete(self, *keys: str) -> int:
        """Delete keys from Redis"""
        try:
            result = self.redis.delete(*keys)
            return result
        except Exception as e:
            logger.error("Redis delete operation failed", keys=keys, error=str(e))
            return 0

    def exists(self, key: str) -> bool:
        """Check if key exists in Redis"""
        try:
            result = self.redis.exists(key) > 0
            return result
        except Exception as e:
            logger.error("Redis exists operation failed", key=key, error=str(e))
            return False

    def expire(self, key: str, seconds: int) -> bool:
        """Set expiration for a key"""
        try:
            result = self.redis.expire(key, seconds)
            return result
        except Exception as e:
            logger.error("Redis expire operation failed", key=key, seconds=seconds, error=str(e))
            return False

    def ttl(self, key: str) -> int:
        """Get time to live for a key"""
        try:
            result = self.redis.ttl(key)
            return result
        except Exception as e:
            logger.error("Redis TTL operation failed", key=key, error=str(e))
            return -1

    def hset(self, name: str, mapping: dict) -> int:
        """Set hash fields"""
        try:
            result = self.redis.hset(name, mapping=mapping)
            return result
        except Exception as e:
            logger.error("Redis hset operation failed", name=name, error=str(e))
            return 0

    def hget(self, name: str, key: str):
        """Get hash field"""
        try:
            result = self.redis.hget(name, key)
            return result
        except Exception as e:
            logger.error("Redis hget operation failed", name=name, key=key, error=str(e))
            return None

    def hgetall(self, name: str) -> dict:
        """Get all hash fields"""
        try:
            result = self.redis.hgetall(name)
            return result
        except Exception as e:
            logger.error("Redis hgetall operation failed", name=name, error=str(e))
            return {}

    def lpush(self, name: str, *values: str) -> int:
        """Push values to list head"""
        try:
            result = self.redis.lpush(name, *values)
            return result
        except Exception as e:
            logger.error("Redis lpush operation failed", name=name, error=str(e))
            return 0

    def rpop(self, name: str):
        """Pop value from list tail"""
        try:
            result = self.redis.rpop(name)
            return result
        except Exception as e:
            logger.error("Redis rpop operation failed", name=name, error=str(e))
            return None

    def lrange(self, name: str, start: int = 0, end: int = -1) -> list:
        """Get list range"""
        try:
            result = self.redis.lrange(name, start, end)
            return result
        except Exception as e:
            logger.error("Redis lrange operation failed", name=name, error=str(e))
            return []

    def incr(self, key: str) -> int:
        """Increment numeric value"""
        try:
            result = self.redis.incr(key)
            return result
        except Exception as e:
            logger.error("Redis incr operation failed", key=key, error=str(e))
            return 0

    def decr(self, key: str) -> int:
        """Decrement numeric value"""
        try:
            result = self.redis.decr(key)
            return result
        except Exception as e:
            logger.error("Redis decr operation failed", key=key, error=str(e))
            return 0


# Cache service for game data
class GameCacheService:
    """Cache service for game-related data"""

    def __init__(self, redis_service: RedisService):
        self.redis = redis_service

    def cache_card_data(self, card_id: str, card_data: dict) -> bool:
        """Cache card data"""
        key = f"card:{card_id}"
        result = self.redis.set(
            key,
            card_data,
            expire=settings.CARD_CACHE_TTL_SECONDS
        )
        if result:
            logger.debug("Card data cached successfully", card_id=card_id)
        else:
            logger.warning("Failed to cache card data", card_id=card_id)
        return result

    def get_cached_card(self, card_id: str):
        """Get cached card data"""
        key = f"card:{card_id}"
        result = self.redis.get(key, as_json=True)
        if result:
            logger.debug("Card data retrieved from cache", card_id=card_id)
        return result

    def cache_user_session(self, user_id: str, session_data: dict) -> bool:
        """Cache user session data"""
        key = f"session:{user_id}"
        result = self.redis.set(
            key,
            session_data,
            expire=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        if result:
            logger.debug("User session cached successfully", user_id=user_id)
        else:
            logger.warning("Failed to cache user session", user_id=user_id)
        return result

    def get_user_session(self, user_id: str):
        """Get cached user session"""
        key = f"session:{user_id}"
        result = self.redis.get(key, as_json=True)
        if result:
            logger.debug("User session retrieved from cache", user_id=user_id)
        return result

    def cache_game_state(self, game_id: str, game_state: dict) -> bool:
        """Cache game state"""
        key = f"game_state:{game_id}"
        return self.redis.set(key, game_state, expire=3600)  # 1 hour

    def get_cached_game_state(self, game_id: str):
        """Get cached game state"""
        key = f"game_state:{game_id}"
        return self.redis.get(key, as_json=True)

    def add_to_matchmaking_queue(self, user_id: str, queue_data: dict) -> bool:
        """Add user to matchmaking queue"""
        key = f"matchmaking:{queue_data['game_mode']}"
        self.redis.lpush(key, json.dumps({user_id: queue_data}))
        return True

    def remove_from_matchmaking_queue(self, user_id: str, game_mode: str) -> bool:
        """Remove user from matchmaking queue"""
        # This is a simplified implementation
        # In production, you'd want to scan and remove specific entries
        key = f"matchmaking:{game_mode}"
        queue_data = self.redis.lrange(key, 0, -1)

        for i, entry in enumerate(queue_data):
            data = json.loads(entry)
            if user_id in data:
                # Remove from Redis list (requires more complex logic)
                # For now, just log the removal
                return True

        return False


# Health check function
def check_redis_health() -> bool:
    """Check if Redis is healthy"""
    try:
        if redis_client:
            redis_client.ping()
            return True
        logger.warning("Redis health check failed: client not initialized")
        return False
    except Exception as e:
        logger.error("Redis health check failed", error=str(e))
        return False


# Dependency to get Redis service (async version)
async def get_redis_service():
    """Dependency to get Redis service (async)"""
    redis_conn = await get_redis()
    return RedisService(redis_conn)


async def get_game_cache_service():
    """Dependency to get game cache service (async)"""
    redis_service = await get_redis_service()
    return GameCacheService(redis_service)