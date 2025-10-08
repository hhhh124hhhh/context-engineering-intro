from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

from app.core.matchmaking.matcher import GameMode, MatchStatus

# 匹配请求相关模型
class MatchRequestCreate(BaseModel):
    """创建匹配请求"""
    mode: GameMode = Field(..., description="游戏模式")
    deck_id: int = Field(..., description="使用的卡组ID")
    preferences: Optional[Dict[str, Any]] = Field(None, description="匹配偏好设置")

    class Config:
        schema_extra = {
            "example": {
                "mode": "ranked",
                "deck_id": 1,
                "preferences": {
                    "max_wait_time": 300,
                    "rating_tolerance": 200
                }
            }
        }

class MatchRequestResponse(BaseModel):
    """匹配请求响应"""
    queue_id: str
    user_id: int
    username: str
    mode: GameMode
    deck_id: int
    deck_name: str
    rating: int
    preferences: Dict[str, Any]
    status: MatchStatus
    created_at: float

    class Config:
        from_attributes = True

# 匹配结果相关模型
class MatchResponse(BaseModel):
    """匹配结果响应"""
    match_id: str
    player1_id: int
    player2_id: int
    player1_username: str
    player2_username: str
    mode: GameMode
    deck1_id: int
    deck2_id: int
    created_at: float
    status: MatchStatus

    @classmethod
    def from_match(cls, match):
        """从Match对象创建响应"""
        return cls(
            match_id=match.match_id,
            player1_id=match.player1_id,
            player2_id=match.player2_id,
            player1_username=match.player1_username,
            player2_username=match.player2_username,
            mode=match.mode,
            deck1_id=match.deck1_id,
            deck2_id=match.deck2_id,
            created_at=match.created_at,
            status=match.status
        )

    class Config:
        from_attributes = True

# 队列状态相关模型
class QueueStatusResponse(BaseModel):
    """队列状态响应"""
    mode: GameMode
    queue_length: int = Field(..., description="队列中等待的玩家数量")
    average_wait_time: float = Field(..., description="平均等待时间（秒）")
    active_matches: int = Field(..., description="活跃的对局数量")

    class Config:
        from_attributes = True

# 用户匹配状态相关模型
class UserMatchStatusResponse(BaseModel):
    """用户匹配状态响应"""
    in_queue: bool = Field(False, description="是否在队列中")
    in_match: bool = Field(False, description="是否在游戏中")
    mode: Optional[GameMode] = Field(None, description="游戏模式")
    wait_time: Optional[float] = Field(None, description="等待时间（秒）")
    status: Optional[MatchStatus] = Field(None, description="匹配状态")
    deck_id: Optional[int] = Field(None, description="使用的卡组ID")
    match_id: Optional[str] = Field(None, description="匹配ID")

    class Config:
        from_attributes = True

# 匹配历史相关模型
class MatchHistoryItem(BaseModel):
    """匹配历史项"""
    match_id: str
    opponent_username: str
    mode: GameMode
    result: str  # win, loss, draw
    duration: int  # 游戏时长（秒）
    rating_change: int
    played_at: datetime

    class Config:
        from_attributes = True

class MatchHistoryResponse(BaseModel):
    """匹配历史响应"""
    matches: List[MatchHistoryItem]
    total: int
    limit: int
    offset: int

    class Config:
        from_attributes = True

# 匹配统计相关模型
class MatchmakingStatsResponse(BaseModel):
    """匹配统计响应"""
    total_matches: int
    average_wait_time: float
    matches_by_mode: Dict[str, int]
    matches_by_result: Dict[str, int]
    rating_distribution: Dict[str, int]
    peak_hours: List[int]

    class Config:
        from_attributes = True

# WebSocket消息相关模型
class WebSocketMessage(BaseModel):
    """WebSocket消息基类"""
    type: str
    timestamp: float = Field(default_factory=lambda: __import__('time').time())

class MatchFoundMessage(WebSocketMessage):
    """匹配成功消息"""
    type: str = "match_found"
    match: MatchResponse
    time_to_match: float  # 匹配耗时

class MatchCancelledMessage(WebSocketMessage):
    """匹配取消消息"""
    type: str = "match_cancelled"
    reason: str  # 取消原因

class QueueUpdateMessage(WebSocketMessage):
    """队列更新消息"""
    type: str = "queue_update"
    queue_length: int
    estimated_wait_time: float

class StatusUpdateMessage(WebSocketMessage):
    """状态更新消息"""
    type: str = "status_update"
    status: UserMatchStatusResponse

# 匹配偏好设置
class MatchPreferences(BaseModel):
    """匹配偏好设置"""
    max_wait_time: Optional[int] = Field(300, description="最大等待时间（秒）")
    rating_tolerance: Optional[int] = Field(200, description="ELO容忍度")
    prefer_same_region: Optional[bool] = Field(True, description="偏好同地区玩家")
    avoid_recent_players: Optional[bool] = Field(True, description="避免最近对战过的玩家")
    deck_type_preference: Optional[str] = Field(None, description="卡组类型偏好")

# 观战相关模型
class SpectateRequest(BaseModel):
    """观战请求"""
    match_id: str = Field(..., description="要观战的比赛ID")

class SpectateResponse(BaseModel):
    """观战响应"""
    success: bool
    match_id: Optional[str] = None
    spectator_token: Optional[str] = None
    message: Optional[str] = None

# 排行榜相关模型
class LeaderboardEntry(BaseModel):
    """排行榜条目"""
    rank: int
    user_id: int
    username: str
    rating: int
    wins: int
    losses: int
    win_rate: float
    streak: int  # 连胜/连败

class LeaderboardResponse(BaseModel):
    """排行榜响应"""
    mode: GameMode
    season: str
    entries: List[LeaderboardEntry]
    user_rank: Optional[int] = None

# 赛季相关模型
class SeasonInfo(BaseModel):
    """赛季信息"""
    season_id: str
    name: str
    start_date: datetime
    end_date: Optional[datetime]
    is_active: bool
    rewards: Dict[str, Any]

# 锦标赛相关模型
class TournamentInfo(BaseModel):
    """锦标赛信息"""
    tournament_id: str
    name: str
    mode: GameMode
    max_participants: int
    current_participants: int
    start_time: datetime
    status: str  # registration, ongoing, completed
    entry_fee: Optional[int] = None
    prize_pool: Optional[int] = None

class TournamentRegistration(BaseModel):
    """锦标赛注册"""
    tournament_id: str
    deck_id: int