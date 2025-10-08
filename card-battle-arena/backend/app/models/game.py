from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, Index, DateTime, JSON, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.postgres import Base


class Game(Base):
    """游戏记录模型"""
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    game_code = Column(String(20), unique=True, nullable=False, index=True)  # 游戏唯一代码

    # 游戏配置
    game_mode = Column(String(20), default="ranked", nullable=False)  # ranked, casual, friendly, tournament
    format_type = Column(String(20), default="standard", nullable=False)  # standard, wild, classic

    # 游戏状态
    status = Column(String(20), default="waiting", nullable=False, index=True)  # waiting, active, finished, abandoned
    current_turn = Column(Integer, default=1, nullable=False)
    current_player_id = Column(Integer, nullable=True, index=True)
    turn_time_limit = Column(Integer, default=90, nullable=False)  # 回合时间限制（秒）

    # 游戏结果
    winner_id = Column(Integer, nullable=True, index=True)
    loser_id = Column(Integer, nullable=True, index=True)
    result_reason = Column(String(50), nullable=True)  # victory, defeat, disconnect, timeout
    turns_played = Column(Integer, default=0, nullable=False)
    game_duration = Column(Integer, nullable=True)  # 游戏时长（秒）

    # ELO变化
    elo_change_winner = Column(Integer, nullable=True)
    elo_change_loser = Column(Integer, nullable=True)

    # 游戏数据（JSON格式存储详细的游戏过程）
    game_log = Column(JSON, nullable=True)  # 游戏日志
    initial_states = Column(JSON, nullable=True)  # 初始状态
    final_states = Column(JSON, nullable=True)  # 最终状态

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)

    # 关系
    players = relationship("GamePlayer", back_populates="game", cascade="all, delete-orphan")
    game_cards = relationship("GameCard", back_populates="game", cascade="all, delete-orphan")
    spectators = relationship("GameSpectator", back_populates="game", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="game", cascade="all, delete-orphan")

    # 索引
    __table_args__ = (
        Index('idx_games_mode_status', 'game_mode', 'status'),
        Index('idx_games_current_player', 'current_player_id'),
        Index('idx_games_winner_loser', 'winner_id', 'loser_id'),
        Index('idx_games_created_at', 'created_at'),
        Index('idx_games_finished_at', 'finished_at'),
        Index('idx_games_duration', 'game_duration'),
        Index('idx_games_code', 'game_code'),
    )

    @property
    def is_active(self) -> bool:
        """检查游戏是否进行中"""
        return self.status == "active"

    @property
    def player_count(self) -> int:
        """获取玩家数量"""
        return len(self.players)

    @property
    def spectator_count(self) -> int:
        """获取观战者数量"""
        return len(self.spectators)

    def get_player_by_id(self, user_id: int):
        """根据用户ID获取游戏玩家"""
        for player in self.players:
            if player.user_id == user_id:
                return player
        return None

    def __repr__(self):
        return f"<Game(id={self.id}, code='{self.game_code}', status='{self.status}')>"


class GamePlayer(Base):
    """游戏玩家模型"""
    __tablename__ = "game_players"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    player_number = Column(Integer, nullable=False)  # 1 或 2

    # 玩家状态
    is_connected = Column(Boolean, default=True, nullable=False)
    is_spectator = Column(Boolean, default=False, nullable=False)
    has_conceded = Column(Boolean, default=False, nullable=False)
    last_action_at = Column(DateTime(timezone=True), nullable=True)

    # 游戏数据（JSON格式）
    deck = Column(JSON, nullable=True)  # 卡组信息
    hand = Column(JSON, nullable=True)  # 手牌
    battlefield = Column(JSON, nullable=True)  # 战场上的随从
    secrets = Column(JSON, nullable=True)  # 奥秘
    hero = Column(JSON, nullable=True)  # 英雄信息
    hero_power = Column(JSON, nullable=True)  # 英雄技能

    # 游戏状态
    health = Column(Integer, default=30, nullable=False)
    max_health = Column(Integer, default=30, nullable=False)
    armor = Column(Integer, default=0, nullable=False)
    mana = Column(Integer, default=1, nullable=False)
    max_mana = Column(Integer, default=1, nullable=False)
    overload = Column(Integer, default=0, nullable=False)  # 过载
    crystals_next_turn = Column(Integer, default=0, nullable=False)  # 下回合法力水晶

    # 统计数据
    cards_played = Column(Integer, default=0, nullable=False)
    damage_dealt = Column(Integer, default=0, nullable=False)
    damage_taken = Column(Integer, default=0, nullable=False)
    minions_summoned = Column(Integer, default=0, nullable=False)
    spells_cast = Column(Integer, default=0, nullable=False)
    turns_taken = Column(Integer, default=0, nullable=False)

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # 关系
    game = relationship("Game", back_populates="players")
    user = relationship("User", back_populates="game_players")

    # 索引
    __table_args__ = (
        Index('idx_game_players_game_user', 'game_id', 'user_id'),
        Index('idx_game_players_number', 'player_number'),
        Index('idx_game_players_connected', 'is_connected'),
        Index('idx_game_players_conceded', 'has_conceded'),
        Index('idx_game_players_health', 'health'),
        Index('idx_game_players_mana', 'mana'),
    )

    @property
    def effective_health(self) -> int:
        """有效生命值（生命值+护甲）"""
        return self.health + self.armor

    @property
    def is_alive(self) -> bool:
        """检查玩家是否存活"""
        return self.health > 0

    @property
    def available_mana(self) -> int:
        """可用法力值"""
        return max(0, self.max_mana - self.overload)

    def __repr__(self):
        return f"<GamePlayer(id={self.id}, game_id={self.game_id}, user_id={self.user_id}, health={self.health})>"


class GameCard(Base):
    """游戏中的卡牌模型"""
    __tablename__ = "game_cards"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False, index=True)
    card_id = Column(Integer, ForeignKey("cards.id"), nullable=False, index=True)
    player_id = Column(Integer, nullable=False, index=True)
    instance_id = Column(String(50), nullable=False, index=True)  # 卡牌实例ID

    # 卡牌状态
    location = Column(String(20), nullable=False, index=True)  # deck, hand, battlefield, graveyard, secret, removed
    position = Column(Integer, nullable=True)  # 位置（手牌或战场位置）

    # 动态属性（可能被效果修改）
    current_cost = Column(Integer, nullable=True)
    current_attack = Column(Integer, nullable=True)
    current_defense = Column(Integer, nullable=True)
    is_dormant = Column(Boolean, default=False, nullable=False)  # 休眠
    is_silenced = Column(Boolean, default=False, nullable=False)  # 沉默
    is_frozen = Column(Boolean, default=False, nullable=False)  # 冰冻
    attack_count = Column(Integer, default=0, nullable=False)  # 攻击次数
    summoning_sickness = Column(Boolean, default=True, nullable=False)  # 嘲讽疲劳

    # 效果和标记
    effects = Column(JSON, nullable=True)  # 当前效果列表
    enchantments = Column(JSON, nullable=True)  # 附魔效果
    mechanics = Column(JSON, nullable=True)  # 当前机制标签

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    played_at = Column(DateTime(timezone=True), nullable=True)
    destroyed_at = Column(DateTime(timezone=True), nullable=True)

    # 关系
    game = relationship("Game", back_populates="game_cards")
    card = relationship("Card", back_populates="game_cards")

    # 索引
    __table_args__ = (
        Index('idx_game_cards_game_player', 'game_id', 'player_id'),
        Index('idx_game_cards_location', 'location'),
        Index('idx_game_cards_instance', 'instance_id'),
        Index('idx_game_cards_position', 'position'),
        Index('idx_game_cards_created', 'created_at'),
    )

    @property
    def is_minion(self) -> bool:
        """是否为随从"""
        return self.card.card_type == "minion"

    @property
    def is_spell(self) -> bool:
        """是否为法术"""
        return self.card.card_type == "spell"

    @property
    def is_weapon(self) -> bool:
        """是否为武器"""
        return self.card.card_type == "weapon"

    @property
    def effective_attack(self) -> int:
        """有效攻击力"""
        return self.current_attack or self.card.attack or 0

    @property
    def effective_defense(self) -> int:
        """有效防御力/生命值"""
        return self.current_defense or self.card.defense or 0

    @property
    def effective_cost(self) -> int:
        """有效法力消耗"""
        return self.current_cost or self.card.cost

    def can_attack(self) -> bool:
        """检查是否可以攻击"""
        if not self.is_minion or self.is_dormant or self.is_frozen:
            return False
        if self.summoning_sickness and "charge" not in (self.mechanics or []):
            return False
        if self.attack_count >= (2 if "windfury" in (self.mechanics or []) else 1):
            return False
        return self.effective_attack > 0

    def __repr__(self):
        return f"<GameCard(id={self.id}, game_id={self.game_id}, card_id={self.card_id}, location='{self.location}')>"


class GameSpectator(Base):
    """游戏观战者模型"""
    __tablename__ = "game_spectators"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    joined_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    left_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # 关系
    game = relationship("Game", back_populates="spectators")
    user = relationship("User")

    # 索引
    __table_args__ = (
        Index('idx_game_spectators_game_user', 'game_id', 'user_id'),
        Index('idx_game_spectators_active', 'is_active'),
        Index('idx_game_spectators_joined', 'joined_at'),
    )

    def __repr__(self):
        return f"<GameSpectator(id={self.id}, game_id={self.game_id}, user_id={self.user_id})>"


class ChatMessage(Base):
    """聊天消息模型"""
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=True, index=True)  # 游戏内聊天
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)  # 私聊接收者
    message_type = Column(String(20), default="game", nullable=False)  # game, private, system
    content = Column(Text, nullable=False)
    is_emote = Column(Boolean, default=False, nullable=False)

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    read_at = Column(DateTime(timezone=True), nullable=True)

    # 关系
    game = relationship("Game", back_populates="chat_messages")
    sender = relationship("User", back_populates="chat_messages")

    # 索引
    __table_args__ = (
        Index('idx_chat_messages_game', 'game_id'),
        Index('idx_chat_messages_sender_receiver', 'sender_id', 'receiver_id'),
        Index('idx_chat_messages_type', 'message_type'),
        Index('idx_chat_messages_created', 'created_at'),
        Index('idx_chat_messages_unread', 'receiver_id', 'read_at'),
    )

    def __repr__(self):
        return f"<ChatMessage(id={self.id}, sender_id={self.sender_id}, type='{self.message_type}')>"