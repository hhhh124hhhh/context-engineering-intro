from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Numeric, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.postgres import Base


class User(Base):
    """用户模型"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)

    # 游戏相关字段
    elo_rating = Column(Numeric(10, 2), default=1000.0, nullable=False)
    level = Column(Integer, default=1, nullable=False)
    experience = Column(Integer, default=0, nullable=False)
    coins = Column(Integer, default=1000, nullable=False)

    # 个人信息
    display_name = Column(String(100), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    country = Column(String(2), nullable=True)

    # 状态字段
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_online = Column(Boolean, default=False, nullable=False)
    is_banned = Column(Boolean, default=False, nullable=False)
    ban_reason = Column(Text, nullable=True)
    ban_until = Column(DateTime(timezone=True), nullable=True)

    # 统计数据
    games_played = Column(Integer, default=0, nullable=False)
    games_won = Column(Integer, default=0, nullable=False)
    games_lost = Column(Integer, default=0, nullable=False)
    win_streak = Column(Integer, default=0, nullable=False)
    best_win_streak = Column(Integer, default=0, nullable=False)

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    # 关系
    decks = relationship("Deck", back_populates="user", cascade="all, delete-orphan")
    game_players = relationship("GamePlayer", back_populates="user")
    sent_friendships = relationship("Friendship", foreign_keys="Friendship.sender_id", back_populates="sender")
    received_friendships = relationship("Friendship", foreign_keys="Friendship.receiver_id", back_populates="receiver")
    chat_messages = relationship("ChatMessage", back_populates="sender")

    # 索引
    __table_args__ = (
        Index('idx_users_elo_rating', 'elo_rating'),
        Index('idx_users_games_played', 'games_played'),
        Index('idx_users_win_rate', 'games_won', 'games_played'),
        Index('idx_users_created_at', 'created_at'),
        Index('idx_users_last_login', 'last_login_at'),
        Index('idx_users_online', 'is_online', 'last_login_at'),
    )

    @property
    def win_rate(self) -> float:
        """计算胜率"""
        if self.games_played == 0:
            return 0.0
        return round((self.games_won / self.games_played) * 100, 2)

    @property
    def is_banned_currently(self) -> bool:
        """检查当前是否被封禁"""
        if not self.is_banned or not self.ban_until:
            return self.is_banned
        from datetime import datetime, timezone
        return self.ban_until > datetime.now(timezone.utc)

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', elo={self.elo_rating})>"


class Friendship(Base):
    """好友关系模型"""
    __tablename__ = "friendships"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, nullable=False, index=True)
    receiver_id = Column(Integer, nullable=False, index=True)
    status = Column(String(20), default="pending", nullable=False)  # pending, accepted, blocked
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # 关系
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_friendships")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="received_friendships")

    # 索引
    __table_args__ = (
        Index('idx_friendships_sender_receiver', 'sender_id', 'receiver_id'),
        Index('idx_friendships_status', 'status'),
    )

    def __repr__(self):
        return f"<Friendship(sender_id={self.sender_id}, receiver_id={self.receiver_id}, status='{self.status}')>"


class UserAchievement(Base):
    """用户成就模型"""
    __tablename__ = "user_achievements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    achievement_id = Column(String(50), nullable=False, index=True)
    unlocked_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    progress = Column(Integer, default=0, nullable=False)

    # 关系
    user = relationship("User")

    # 索引
    __table_args__ = (
        Index('idx_user_achievements_user_achievement', 'user_id', 'achievement_id'),
        Index('idx_user_achievements_unlocked_at', 'unlocked_at'),
    )

    def __repr__(self):
        return f"<UserAchievement(user_id={self.user_id}, achievement_id='{self.achievement_id}')>"


class UserSession(Base):
    """用户会话模型"""
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    refresh_token = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_used_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # 关系
    user = relationship("User")

    # 索引
    __table_args__ = (
        Index('idx_user_sessions_user_token', 'user_id', 'session_token'),
        Index('idx_user_sessions_expires_at', 'expires_at'),
        Index('idx_user_sessions_last_used', 'last_used_at'),
    )

    def __repr__(self):
        return f"<UserSession(user_id={self.user_id}, expires_at='{self.expires_at}')>"