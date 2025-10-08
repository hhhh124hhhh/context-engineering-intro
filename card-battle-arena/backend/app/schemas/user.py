from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserBase(BaseModel):
    """用户基础模式"""
    email: str = Field(..., pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    username: str = Field(..., min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9_-]+$')
    display_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    country: Optional[str] = Field(None, max_length=2, pattern=r'^[A-Z]{2}$')


class UserCreate(UserBase):
    """用户创建模式"""
    password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str

    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('两次输入的密码不一致')
        return v

    @validator('password')
    def validate_password_strength(cls, v):
        from app.core.security import validate_password_strength
        result = validate_password_strength(v)
        if not result['is_valid']:
            raise ValueError('密码强度不足: ' + '; '.join(result['errors']))
        return v


class UserUpdate(BaseModel):
    """用户更新模式"""
    display_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    country: Optional[str] = Field(None, max_length=2)
    avatar_url: Optional[str] = Field(None, max_length=500)


class UserChangePassword(BaseModel):
    """用户修改密码模式"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str

    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('两次输入的新密码不一致')
        return v

    @validator('new_password')
    def validate_new_password_strength(cls, v):
        from app.core.security import validate_password_strength
        result = validate_password_strength(v)
        if not result['is_valid']:
            raise ValueError('新密码强度不足: ' + '; '.join(result['errors']))
        return v


class UserLogin(BaseModel):
    """用户登录模式"""
    username_or_email: str = Field(..., min_length=3)
    password: str
    remember_me: bool = False


class UserResponse(UserBase):
    """用户响应模式"""
    id: int
    elo_rating: float
    level: int
    experience: int
    coins: int
    display_name: Optional[str]
    avatar_url: Optional[str]
    bio: Optional[str]
    country: Optional[str]
    is_active: bool
    is_verified: bool
    is_online: bool
    games_played: int
    games_won: int
    games_lost: int
    win_streak: int
    best_win_streak: int
    created_at: datetime
    last_login_at: Optional[datetime]

    class Config:
        from_attributes = True


class UserProfile(BaseModel):
    """用户档案模式"""
    user: UserResponse
    win_rate: float
    recent_games: List[dict] = []
    achievements: List[dict] = []
    favorite_decks: List[dict] = []

    class Config:
        from_attributes = True


class Token(BaseModel):
    """令牌模式"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenRefresh(BaseModel):
    """令牌刷新模式"""
    refresh_token: str


class UserStats(BaseModel):
    """用户统计模式"""
    games_played: int
    games_won: int
    games_lost: int
    win_rate: float
    current_win_streak: int
    best_win_streak: int
    favorite_class: Optional[str]
    average_game_duration: Optional[float]
    total_play_time: int  # 总游戏时间（分钟）


class UserAchievement(BaseModel):
    """用户成就模式"""
    id: int
    achievement_id: str
    unlocked_at: datetime
    progress: int

    class Config:
        from_attributes = True


class UserSession(BaseModel):
    """用户会话模式"""
    id: int
    session_token: str
    expires_at: datetime
    created_at: datetime
    last_used_at: datetime
    ip_address: Optional[str]
    user_agent: Optional[str]

    class Config:
        from_attributes = True


class PasswordResetRequest(BaseModel):
    """密码重置请求模式"""
    email: EmailStr


class PasswordReset(BaseModel):
    """密码重置模式"""
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str

    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('两次输入的密码不一致')
        return v

    @validator('new_password')
    def validate_password_strength(cls, v):
        from app.core.security import validate_password_strength
        result = validate_password_strength(v)
        if not result['is_valid']:
            raise ValueError('密码强度不足: ' + '; '.join(result['errors']))
        return v


class EmailVerificationRequest(BaseModel):
    """邮箱验证请求模式"""
    email: EmailStr


class EmailVerification(BaseModel):
    """邮箱验证模式"""
    token: str


class FriendshipBase(BaseModel):
    """好友关系基础模式"""
    receiver_id: int


class FriendshipCreate(FriendshipBase):
    """创建好友关系模式"""
    message: Optional[str] = Field(None, max_length=200)


class FriendshipResponse(BaseModel):
    """好友关系响应模式"""
    id: int
    sender_id: int
    receiver_id: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserSearch(BaseModel):
    """用户搜索模式"""
    query: str = Field(..., min_length=2, max_length=50)
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class UserSearchResponse(BaseModel):
    """用户搜索响应模式"""
    users: List[UserResponse]
    total: int
    limit: int
    offset: int


class GameHistoryFilter(BaseModel):
    """游戏历史过滤器"""
    game_mode: Optional[str] = None
    format_type: Optional[str] = None
    result: Optional[str] = None  # win, loss
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class UserPreferences(BaseModel):
    """用户偏好设置模式"""
    language: str = Field(default="zh-CN", pattern=r'^[a-z]{2}-[A-Z]{2}$')
    theme: str = Field(default="dark", pattern=r'^(light|dark|auto)$')
    sound_enabled: bool = True
    music_enabled: bool = True
    animations_enabled: bool = True
    auto_squelch: bool = False
    show_friend_requests: bool = True
    show_chat_messages: bool = True
    email_notifications: bool = True
    push_notifications: bool = True


class UserActivity(BaseModel):
    """用户活动模式"""
    activity_type: str
    description: str
    timestamp: datetime
    metadata: Optional[dict] = None


class UserRanking(BaseModel):
    """用户排名模式"""
    user: UserResponse
    rank: int
    points: int
    tier: str
    division: int


class LeaderboardFilter(BaseModel):
    """排行榜过滤器"""
    game_mode: str = Field(default="ranked")
    time_period: str = Field(default="current_season", pattern=r'^(current_season|last_season|all_time)$')
    region: Optional[str] = None
    class_filter: Optional[str] = None
    limit: int = Field(default=100, ge=1, le=500)


class BanInfo(BaseModel):
    """封禁信息模式"""
    is_banned: bool
    ban_reason: Optional[str]
    ban_until: Optional[datetime]
    remaining_time: Optional[int]  # 剩余封禁时间（秒）


class UserReport(BaseModel):
    """用户举报模式"""
    reported_user_id: int
    reason: str = Field(..., pattern=r'^(cheating|harassment|inappropriate_name|other)$')
    description: str = Field(..., min_length=10, max_length=500)
    evidence_urls: Optional[List[str]] = []