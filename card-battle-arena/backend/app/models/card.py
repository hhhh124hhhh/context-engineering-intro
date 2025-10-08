from sqlalchemy import Column, Integer, String, Text, Numeric, Boolean, JSON, Index
from sqlalchemy.orm import relationship
from app.database.postgres import Base


class Card(Base):
    """卡牌模型"""
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=False)
    flavor_text = Column(Text, nullable=True)  # 卡牌背景故事文本

    # 基本属性
    cost = Column(Integer, nullable=False)  # 法力消耗
    attack = Column(Integer, nullable=True)  # 攻击力（随从和武器）
    defense = Column(Integer, nullable=True)  # 防御力/生命值（随从）
    durability = Column(Integer, nullable=True)  # 耐久度（武器）

    # 卡牌分类
    card_type = Column(String(20), nullable=False, index=True)  # minion, spell, weapon, hero_power
    rarity = Column(String(20), nullable=False, index=True)  # common, rare, epic, legendary
    card_class = Column(String(30), nullable=False, index=True)  # warrior, mage, priest, etc.
    card_set = Column(String(50), nullable=False, index=True)  # basic, classic, expert, etc.

    # 效果和机制
    mechanics = Column(JSON, nullable=True)  # 卡牌机制列表，如 ["taunt", "divine_shield", "windfury"]
    effect_text = Column(Text, nullable=True)  # 卡牌效果描述
    play_requirements = Column(JSON, nullable=True)  # 出牌条件
    deathrattle_effect = Column(JSON, nullable=True)  # 亡语效果
    battlecry_effect = Column(JSON, nullable=True)  # 战吼效果
    ongoing_effect = Column(JSON, nullable=True)  # 持续效果

    # 视觉资源
    image_url = Column(String(500), nullable=True)
    golden_image_url = Column(String(500), nullable=True)
    sound_url = Column(String(500), nullable=True)

    # 平衡和限制
    is_collectible = Column(Boolean, default=True, nullable=False)
    is_standard_legal = Column(Boolean, default=True, nullable=False)
    is_wild_legal = Column(Boolean, default=True, nullable=False)
    crafting_cost = Column(Integer, nullable=False)  # 制作成本

    # 统计数据
    play_count = Column(Integer, default=0, nullable=False)
    win_rate = Column(Numeric(5, 4), default=0.0, nullable=False)
    usage_rate = Column(Numeric(5, 4), default=0.0, nullable=False)

    # 元数据
    artist = Column(String(100), nullable=True)
    how_to_get = Column(String(200), nullable=True)
    lore = Column(Text, nullable=True)

    # 关系
    deck_cards = relationship("DeckCard", back_populates="card")
    game_cards = relationship("GameCard", back_populates="card")

    # 索引
    __table_args__ = (
        Index('idx_cards_cost', 'cost'),
        Index('idx_cards_attack', 'attack'),
        Index('idx_cards_defense', 'defense'),
        Index('idx_cards_type_rarity', 'card_type', 'rarity'),
        Index('idx_cards_class_set', 'card_class', 'card_set'),
        Index('idx_cards_collectible', 'is_collectible'),
        Index('idx_cards_standard_legal', 'is_standard_legal'),
        Index('idx_cards_win_rate', 'win_rate'),
        Index('idx_cards_usage_rate', 'usage_rate'),
    )

    @property
    def is_mana_efficient(self) -> bool:
        """判断卡牌法力效率"""
        if self.card_type == "minion":
            # 简单的效率计算：攻击力+生命值 >= 法力消耗*2
            return (self.attack or 0) + (self.defense or 0) >= self.cost * 2
        return False

    @property
    def crafting_cost_by_rarity(self) -> int:
        """根据稀有度获取制作成本"""
        costs = {
            "common": 40,
            "rare": 100,
            "epic": 400,
            "legendary": 1600
        }
        return costs.get(self.rarity, 0)

    def __repr__(self):
        return f"<Card(id={self.id}, name='{self.name}', type='{self.card_type}', cost={self.cost})>"


class CardSet(Base):
    """卡牌包模型"""
    __tablename__ = "card_sets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)

    # 发布信息
    release_date = Column(String(20), nullable=True)
    is_standard_legal = Column(Boolean, default=True, nullable=False)
    rotation_date = Column(String(20), nullable=True)

    # 卡牌包信息
    pack_cost = Column(Integer, nullable=False)  # 卡牌包金币价格
    pack_cost_real = Column(Numeric(10, 2), nullable=True)  # 真实货币价格
    card_count_common = Column(Integer, default=3, nullable=False)
    card_count_rare = Column(Integer, default=1, nullable=False)
    epic_chance = Column(Numeric(5, 4), default=0.1, nullable=False)  # 史诗概率
    legendary_chance = Column(Numeric(5, 4), default=0.05, nullable=False)  # 传说概率

    # 视觉资源
    logo_url = Column(String(500), nullable=True)
    banner_url = Column(String(500), nullable=True)

    def __repr__(self):
        return f"<CardSet(id={self.id}, name='{self.name}', code='{self.code}')>"


class UserCardCollection(Base):
    """用户卡牌收藏模型"""
    __tablename__ = "user_card_collections"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    card_id = Column(Integer, nullable=False, index=True)
    normal_count = Column(Integer, default=0, nullable=False)
    golden_count = Column(Integer, default=0, nullable=False)
    crafted_normal = Column(Integer, default=0, nullable=False)
    crafted_golden = Column(Integer, default=0, nullable=False)
    disenchanted_normal = Column(Integer, default=0, nullable=False)
    disenchanted_golden = Column(Integer, default=0, nullable=False)
    first_obtained_at = Column(String(30), nullable=True)  # 游戏内时间
    last_used_at = Column(String(30), nullable=True)

    # 关系
    user = relationship("User")
    card = relationship("Card")

    # 索引
    __table_args__ = (
        Index('idx_user_card_collections_user_card', 'user_id', 'card_id'),
        Index('idx_user_card_collections_counts', 'normal_count', 'golden_count'),
    )

    @property
    def total_count(self) -> int:
        """获取卡牌总数"""
        return self.normal_count + self.golden_count

    @property
    def can_craft_more(self) -> bool:
        """是否可以继续制作（最多2张）"""
        return self.normal_count < 2 or self.golden_count < 1

    def __repr__(self):
        return f"<UserCardCollection(user_id={self.user_id}, card_id={self.card_id}, total={self.total_count})>"