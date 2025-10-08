from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, Index, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.postgres import Base


class Deck(Base):
    """卡组模型"""
    __tablename__ = "decks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    # 卡组信息
    card_class = Column(String(30), nullable=False, index=True)  # 卡组职业
    format_type = Column(String(20), default="standard", nullable=False)  # standard, wild, classic
    is_public = Column(Boolean, default=False, nullable=False)
    is_favorite = Column(Boolean, default=False, nullable=False)

    # 统计数据
    games_played = Column(Integer, default=0, nullable=False)
    games_won = Column(Integer, default=0, nullable=False)
    games_lost = Column(Integer, default=0, nullable=False)
    win_rate = Column(Integer, default=0, nullable=False)  # 胜率百分比

    # 版本控制
    version = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_used_at = Column(DateTime(timezone=True), nullable=True)

    # 关系
    user = relationship("User", back_populates="decks")
    deck_cards = relationship("DeckCard", back_populates="deck", cascade="all, delete-orphan")

    # 索引
    __table_args__ = (
        Index('idx_decks_user_class', 'user_id', 'card_class'),
        Index('idx_decks_format_public', 'format_type', 'is_public'),
        Index('idx_decks_win_rate', 'win_rate'),
        Index('idx_decks_games_played', 'games_played'),
        Index('idx_decks_created_at', 'created_at'),
        Index('idx_decks_last_used', 'last_used_at'),
    )

    @property
    def card_count(self) -> int:
        """获取卡组中卡牌数量"""
        return sum(card.quantity for card in self.deck_cards)

    @property
    def is_valid(self) -> bool:
        """检查卡组是否有效（30张卡）"""
        return self.card_count == 30

    @property
    def dust_cost(self) -> int:
        """计算卡组奥术尘成本"""
        total_cost = 0
        for deck_card in self.deck_cards:
            if deck_card.card.rarity == "common":
                total_cost += 40 * deck_card.quantity
            elif deck_card.card.rarity == "rare":
                total_cost += 100 * deck_card.quantity
            elif deck_card.card.rarity == "epic":
                total_cost += 400 * deck_card.quantity
            elif deck_card.card.rarity == "legendary":
                total_cost += 1600 * deck_card.quantity
        return total_cost

    def update_stats(self) -> None:
        """更新卡组统计数据"""
        if self.games_played > 0:
            self.win_rate = int((self.games_won / self.games_played) * 100)

    def __repr__(self):
        return f"<Deck(id={self.id}, name='{self.name}', user_id={self.user_id}, cards={self.card_count})>"


class DeckCard(Base):
    """卡组中的卡牌模型"""
    __tablename__ = "deck_cards"

    id = Column(Integer, primary_key=True, index=True)
    deck_id = Column(Integer, ForeignKey("decks.id"), nullable=False, index=True)
    card_id = Column(Integer, ForeignKey("cards.id"), nullable=False, index=True)
    quantity = Column(Integer, default=1, nullable=False)  # 1张或2张
    position = Column(Integer, nullable=False)  # 在卡组中的位置

    # 关系
    deck = relationship("Deck", back_populates="deck_cards")
    card = relationship("Card", back_populates="deck_cards")

    # 索引
    __table_args__ = (
        Index('idx_deck_cards_deck_card', 'deck_id', 'card_id'),
        Index('idx_deck_cards_deck_position', 'deck_id', 'position'),
        Index('idx_deck_cards_quantity', 'quantity'),
    )

    def __repr__(self):
        return f"<DeckCard(deck_id={self.deck_id}, card_id={self.card_id}, quantity={self.quantity})>"


class DeckTemplate(Base):
    """卡组模板模型（推荐卡组）"""
    __tablename__ = "deck_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=False)
    author = Column(String(100), nullable=False)

    # 卡组信息
    card_class = Column(String(30), nullable=False, index=True)
    format_type = Column(String(20), default="standard", nullable=False)
    difficulty = Column(String(20), default="intermediate", nullable=False)  # beginner, intermediate, advanced
    playstyle = Column(String(50), nullable=True)  # aggro, control, combo, midrange

    # 统计数据
    usage_count = Column(Integer, default=0, nullable=False)
    rating = Column(Integer, default=0, nullable=False)  # 1-5星评分
    rating_count = Column(Integer, default=0, nullable=False)

    # 费用分布（法力曲线）
    mana_curve = Column(String(100), nullable=True)  # JSON字符串存储费用分布

    # 状态
    is_featured = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # 关系
    template_cards = relationship("DeckTemplateCard", back_populates="template", cascade="all, delete-orphan")

    # 索引
    __table_args__ = (
        Index('idx_deck_templates_class_difficulty', 'card_class', 'difficulty'),
        Index('idx_deck_templates_playstyle', 'playstyle'),
        Index('idx_deck_templates_rating', 'rating'),
        Index('idx_deck_templates_featured', 'is_featured', 'rating'),
        Index('idx_deck_templates_usage', 'usage_count'),
    )

    @property
    def average_rating(self) -> float:
        """计算平均评分"""
        if self.rating_count == 0:
            return 0.0
        return round(self.rating / self.rating_count, 2)

    def __repr__(self):
        return f"<DeckTemplate(id={self.id}, name='{self.name}', class='{self.card_class}', rating={self.average_rating})>"


class DeckTemplateCard(Base):
    """卡组模板中的卡牌模型"""
    __tablename__ = "deck_template_cards"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("deck_templates.id"), nullable=False, index=True)
    card_id = Column(Integer, ForeignKey("cards.id"), nullable=False, index=True)
    quantity = Column(Integer, default=1, nullable=False)
    is_optional = Column(Boolean, default=False, nullable=False)  # 是否为可选替换卡牌

    # 关系
    template = relationship("DeckTemplate", back_populates="template_cards")
    card = relationship("Card")

    # 索引
    __table_args__ = (
        Index('idx_deck_template_cards_template_card', 'template_id', 'card_id'),
    )

    def __repr__(self):
        return f"<DeckTemplateCard(template_id={self.template_id}, card_id={self.card_id}, quantity={self.quantity})>"