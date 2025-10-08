import asyncio
import time
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import logging
import structlog

from app.database.redis import redis_client
from app.models.user import User

logger = structlog.get_logger()

class GameMode(str, Enum):
    RANKED = "ranked"
    CASUAL = "casual"
    PRACTICE = "practice"
    TOURNAMENT = "tournament"
    FRIENDLY = "friendly"

class MatchStatus(str, Enum):
    WAITING = "waiting"
    MATCHING = "matching"
    MATCHED = "matched"
    GAME_STARTED = "game_started"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

@dataclass
class MatchRequest:
    """匹配请求"""
    user_id: int
    username: str
    mode: GameMode
    deck_id: int
    deck_name: str
    rating: int
    preferences: Dict = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    status: MatchStatus = MatchStatus.WAITING
    match_id: Optional[str] = None

@dataclass
class Match:
    """匹配结果"""
    match_id: str
    player1_id: int
    player2_id: int
    player1_username: str
    player2_username: str
    mode: GameMode
    deck1_id: int
    deck2_id: int
    created_at: float = field(default_factory=time.time)
    status: MatchStatus = MatchStatus.MATCHED

class MatchmakingQueue:
    """匹配队列管理"""

    def __init__(self):
        self.queues: Dict[GameMode, Dict[str, MatchRequest]] = {
            mode: {} for mode in GameMode
        }
        self.waiting_times: Dict[int, float] = {}
        self.max_wait_time = 300  # 5分钟最大等待时间
        self.expansion_thresholds = [30, 60, 120, 240]  # 等待时间扩展阈值（秒）

    def add_request(self, request: MatchRequest) -> str:
        """添加匹配请求"""
        queue_id = f"{request.user_id}:{request.created_at}"
        self.queues[request.mode][queue_id] = request
        self.waiting_times[request.user_id] = request.created_at
        logger.info("Added match request",
                   user_id=request.user_id,
                   mode=request.mode,
                   queue_id=queue_id)
        return queue_id

    def remove_request(self, user_id: int, mode: GameMode) -> Optional[MatchRequest]:
        """移除匹配请求"""
        for queue_id, request in list(self.queues[mode].items()):
            if request.user_id == user_id:
                request.status = MatchStatus.CANCELLED
                del self.queues[mode][queue_id]
                self.waiting_times.pop(user_id, None)
                logger.info("Removed match request",
                           user_id=user_id,
                           mode=mode,
                           queue_id=queue_id)
                return request
        return None

    def get_request(self, user_id: int, mode: GameMode) -> Optional[MatchRequest]:
        """获取用户的匹配请求"""
        for request in self.queues[mode].values():
            if request.user_id == user_id:
                return request
        return None

    def get_expired_requests(self) -> List[MatchRequest]:
        """获取过期的匹配请求"""
        expired = []
        current_time = time.time()

        for mode, queue in self.queues.items():
            for queue_id, request in list(queue.items()):
                wait_time = current_time - request.created_at
                if wait_time > self.max_wait_time:
                    request.status = MatchStatus.EXPIRED
                    del queue[queue_id]
                    self.waiting_times.pop(request.user_id, None)
                    expired.append(request)

        return expired

class ELOMatcher:
    """ELO积分匹配器"""

    def __init__(self):
        self.base_rating_diff = 100  # 基础ELO差距
        self.max_rating_diff = 500   # 最大ELO差距

    def calculate_rating_range(self, rating: int, wait_time: float) -> Tuple[int, int]:
        """根据等待时间计算匹配的ELO范围"""
        # 基础范围
        base_diff = self.base_rating_diff

        # 根据等待时间扩展范围
        expansion_factor = 1
        for threshold in [30, 60, 120, 240]:
            if wait_time > threshold:
                expansion_factor *= 1.5

        max_diff = min(self.base_rating_diff * expansion_factor, self.max_rating_diff)

        return max(0, rating - max_diff), rating + max_diff

    def is_matchable(self, req1: MatchRequest, req2: MatchRequest) -> bool:
        """检查两个请求是否可以匹配"""
        if req1.user_id == req2.user_id:
            return False

        # 检查模式兼容性
        if req1.mode != req2.mode:
            return False

        # 检查ELO差距
        wait_time1 = time.time() - req1.created_at
        wait_time2 = time.time() - req2.created_at
        avg_wait_time = (wait_time1 + wait_time2) / 2

        range1 = self.calculate_rating_range(req1.rating, avg_wait_time)
        range2 = self.calculate_rating_range(req2.rating, avg_wait_time)

        # 检查是否有重叠范围
        return not (range1[1] < range2[0] or range2[1] < range1[0])

class MatchmakingEngine:
    """匹配引擎主类"""

    def __init__(self):
        self.queue = MatchmakingQueue()
        self.elo_matcher = ELOMatcher()
        self.active_matches: Dict[str, Match] = {}
        self.match_counter = 0
        self.running = False
        self._task: Optional[asyncio.Task] = None

    async def start(self):
        """启动匹配引擎"""
        if self.running:
            return

        self.running = True
        self._task = asyncio.create_task(self._matching_loop())
        logger.info("Matchmaking engine started")

    async def stop(self):
        """停止匹配引擎"""
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Matchmaking engine stopped")

    async def add_match_request(self, request: MatchRequest) -> str:
        """添加匹配请求"""
        queue_id = self.queue.add_request(request)

        # 立即尝试匹配
        await self._process_matching(request.mode)

        return queue_id

    async def remove_match_request(self, user_id: int, mode: GameMode) -> bool:
        """移除匹配请求"""
        request = self.queue.remove_request(user_id, mode)
        return request is not None

    async def _matching_loop(self):
        """匹配循环"""
        while self.running:
            try:
                # 处理所有模式的匹配
                for mode in GameMode:
                    await self._process_matching(mode)

                # 清理过期请求
                expired = self.queue.get_expired_requests()
                for request in expired:
                    await self._notify_expired(request)

                # 等待下一次匹配
                await asyncio.sleep(2)  # 每2秒处理一次

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error in matching loop", error=str(e))
                await asyncio.sleep(5)

    async def _process_matching(self, mode: GameMode):
        """处理特定模式的匹配"""
        requests = list(self.queue.queues[mode].values())

        # 按等待时间排序（优先匹配等待时间长的）
        requests.sort(key=lambda r: r.created_at)

        matched_users: Set[int] = set()

        for i, req1 in enumerate(requests):
            if req1.user_id in matched_users:
                continue

            for req2 in requests[i+1:]:
                if req2.user_id in matched_users:
                    continue

                if self.elo_matcher.is_matchable(req1, req2):
                    # 创建匹配
                    match = await self._create_match(req1, req2)
                    if match:
                        matched_users.add(req1.user_id)
                        matched_users.add(req2.user_id)

                        # 从队列中移除
                        self.queue.remove_request(req1.user_id, mode)
                        self.queue.remove_request(req2.user_id, mode)

                        # 通知匹配成功
                        await self._notify_match_found(match)
                        break

    async def _create_match(self, req1: MatchRequest, req2: MatchRequest) -> Optional[Match]:
        """创建匹配"""
        try:
            self.match_counter += 1
            match_id = f"match_{self.match_counter}_{int(time.time())}"

            match = Match(
                match_id=match_id,
                player1_id=req1.user_id,
                player2_id=req2.user_id,
                player1_username=req1.username,
                player2_username=req2.username,
                mode=req1.mode,
                deck1_id=req1.deck_id,
                deck2_id=req2.deck_id
            )

            # 更新请求状态
            req1.status = MatchStatus.MATCHED
            req2.status = MatchStatus.MATCHED
            req1.match_id = match_id
            req2.match_id = match_id

            # 存储匹配
            self.active_matches[match_id] = match

            # 存储到Redis
            await self._save_match_to_redis(match)

            logger.info("Created match",
                       match_id=match_id,
                       player1=req1.username,
                       player2=req2.username,
                       mode=req1.mode)

            return match

        except Exception as e:
            logger.error("Failed to create match", error=str(e))
            return None

    async def _save_match_to_redis(self, match: Match):
        """保存匹配到Redis"""
        match_data = {
            "match_id": match.match_id,
            "player1_id": match.player1_id,
            "player2_id": match.player2_id,
            "player1_username": match.player1_username,
            "player2_username": match.player2_username,
            "mode": match.mode,
            "deck1_id": match.deck1_id,
            "deck2_id": match.deck2_id,
            "created_at": match.created_at,
            "status": match.status
        }

        await redis_client.hset(
            f"match:{match.match_id}",
            mapping=match_data
        )

        # 设置过期时间（1小时）
        await redis_client.expire(f"match:{match.match_id}", 3600)

    async def _notify_match_found(self, match: Match):
        """通知匹配成功"""
        # 这里应该通过WebSocket通知玩家
        # 暂时记录日志
        logger.info("Notifying match found",
                   match_id=match.match_id,
                   player1=match.player1_username,
                   player2=match.player2_username)

    async def _notify_expired(self, request: MatchRequest):
        """通知匹配过期"""
        logger.info("Match request expired",
                   user_id=request.user_id,
                   mode=request.mode,
                   wait_time=time.time() - request.created_at)

    def get_queue_status(self, mode: GameMode) -> Dict:
        """获取队列状态"""
        requests = list(self.queue.queues[mode].values())
        current_time = time.time()

        wait_times = [current_time - req.created_at for req in requests]
        avg_wait_time = sum(wait_times) / len(wait_times) if wait_times else 0

        return {
            "mode": mode,
            "queue_length": len(requests),
            "average_wait_time": avg_wait_time,
            "active_matches": len([m for m in self.active_matches.values() if m.mode == mode])
        }

    def get_user_status(self, user_id: int) -> Dict:
        """获取用户匹配状态"""
        for mode in GameMode:
            request = self.queue.get_request(user_id, mode)
            if request:
                wait_time = time.time() - request.created_at
                return {
                    "in_queue": True,
                    "mode": request.mode,
                    "wait_time": wait_time,
                    "status": request.status,
                    "deck_id": request.deck_id
                }

        # 检查是否在活跃匹配中
        for match in self.active_matches.values():
            if match.player1_id == user_id or match.player2_id == user_id:
                return {
                    "in_queue": False,
                    "in_match": True,
                    "match_id": match.match_id,
                    "mode": match.mode,
                    "status": match.status
                }

        return {
            "in_queue": False,
            "in_match": False
        }

# 全局匹配引擎实例
matchmaking_engine = MatchmakingEngine()