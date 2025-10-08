from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class CardType(str, Enum):
    MINION = "minion"
    SPELL = "spell"
    WEAPON = "weapon"
    HERO_POWER = "hero_power"

class CardRarity(str, Enum):
    COMMON = "common"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"

class CardClass(str, Enum):
    WARRIOR = "warrior"
    MAGE = "mage"
    HUNTER = "hunter"
    ROGUE = "rogue"
    PRIEST = "priest"
    WARLOCK = "warlock"
    SHAMAN = "shaman"
    PALADIN = "paladin"
    DRUID = "druid"
    NEUTRAL = "neutral"

# 基础卡牌信息
class CardInfo(BaseModel):
    id: int
    name: str
    description: str
    cost: int
    attack: Optional[int] = None
    defense: Optional[int] = None
    durability: Optional[int] = None
    card_type: CardType
    rarity: CardRarity
    card_class: CardClass
    mechanics: Optional[List[str]] = []
    image_url: Optional[str] = None

    class Config:
        from_attributes = True

# 卡组中的卡牌
class DeckCardCreate(BaseModel):
    cardId: int = Field(..., description="卡牌ID")
    quantity: int = Field(..., ge=1, le=2, description="卡牌数量")

# 创建卡组请求
class DeckCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="卡组名称")
    description: Optional[str] = Field(None, max_length=200, description="卡组描述")
    card_class: CardClass = Field(..., description="卡组职业")
    cards: List[DeckCardCreate] = Field(..., min_items=1, max_items=30, description="卡牌列表")
    is_public: bool = Field(False, description="是否公开")
    is_favorite: bool = Field(False, description="是否收藏")

    class Config:
        schema_extra = {
            "example": {
                "name": "快攻法师",
                "description": "以低费法术为主的快攻卡组",
                "card_class": "mage",
                "cards": [
                    {"cardId": 1, "quantity": 2},
                    {"cardId": 2, "quantity": 1}
                ],
                "is_public": False,
                "is_favorite": False
            }
        }

# 更新卡组请求
class DeckUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=200)
    cards: Optional[List[DeckCardCreate]] = None
    is_public: Optional[bool] = None
    is_favorite: Optional[bool] = None

# 卡组中的卡牌响应
class DeckCardResponse(BaseModel):
    cardId: int
    quantity: int
    position: int
    card: CardInfo

    class Config:
        from_attributes = True

# 卡组列表响应
class DeckListResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    card_class: CardClass
    is_public: bool
    is_favorite: bool
    games_played: int
    games_won: int
    games_lost: int
    win_rate: float
    version: int
    created_at: datetime
    updated_at: datetime
    last_used_at: Optional[datetime]
    cards_count: int

    class Config:
        from_attributes = True

# 完整卡组响应
class DeckResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    card_class: CardClass
    is_public: bool
    is_favorite: bool
    games_played: int
    games_won: int
    games_lost: int
    win_rate: float
    version: int
    created_at: datetime
    updated_at: datetime
    last_used_at: Optional[datetime]
    cards: List[DeckCardResponse]

    class Config:
        from_attributes = True

# 卡组统计信息
class DeckStats(BaseModel):
    total_cards: int = Field(..., description="总卡牌数")
    average_cost: float = Field(..., description="平均费用")
    cost_distribution: Dict[int, int] = Field(..., description="费用分布")
    type_distribution: Dict[str, int] = Field(..., description="类型分布")
    rarity_distribution: Dict[str, int] = Field(..., description="稀有度分布")

# 卡组使用统计
class DeckUsageStats(BaseModel):
    total_games: int
    win_rate: float
    average_game_length: float  # 平均游戏时长（分钟）
    best_matchup: Optional[str]  # 最佳对阵职业
    worst_matchup: Optional[str]  # 最差对阵职业
    recent_performance: List[Dict[str, Any]]  # 最近表现

# 卡组分享信息
class DeckShare(BaseModel):
    deck_id: int
    share_code: str
    share_url: str
    expires_at: Optional[datetime]
    is_public: bool

# 卡组导入数据
class DeckImportData(BaseModel):
    name: str
    description: Optional[str]
    card_class: CardClass
    cards: List[DeckCardCreate]
    source: str  # 导入来源（deckstring, text, json等）
    original_data: Dict[str, Any]  # 原始导入数据

# 卡组验证结果
class DeckValidation(BaseModel):
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    card_count: int
    unique_cards: int
    format_legality: str  # standard, wild, none

# 卡组推荐
class DeckRecommendation(BaseModel):
    deck_id: int
    name: str
    description: str
    win_rate: float
    games_played: int
    difficulty: str  # easy, medium, hard
    playstyle: str  # aggro, control, combo, midrange
    recommended_cards: List[Dict[str, Any]]  # 推荐替换卡牌

# 卡组分析
class DeckAnalysis(BaseModel):
    mana_curve: Dict[int, int]  # 法力曲线
    synergy_score: float  # 配合度评分
    consistency_score: float  # 稳定性评分
    power_level: float  # 强度评分
    matchups: Dict[str, float]  # 各职业胜率
    improvement_suggestions: List[str]  # 改进建议