from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class CardBase(BaseModel):
    """卡牌基础模型"""
    name: str
    description: str
    flavor_text: Optional[str] = None

    # 基本属性
    cost: int
    attack: Optional[int] = None
    defense: Optional[int] = None
    durability: Optional[int] = None

    # 卡牌分类
    card_type: str
    rarity: str
    card_class: str
    card_set: str

    # 效果和机制
    mechanics: Optional[List[str]] = None
    effect_text: Optional[str] = None
    play_requirements: Optional[Dict[str, Any]] = None
    deathrattle_effect: Optional[Dict[str, Any]] = None
    battlecry_effect: Optional[Dict[str, Any]] = None
    ongoing_effect: Optional[Dict[str, Any]] = None

    # 视觉资源
    image_url: Optional[str] = None
    golden_image_url: Optional[str] = None
    sound_url: Optional[str] = None

    # 平衡和限制
    is_collectible: bool
    is_standard_legal: bool
    is_wild_legal: bool
    crafting_cost: int

    # 统计数据
    play_count: int
    win_rate: float
    usage_rate: float

    # 元数据
    artist: Optional[str] = None
    how_to_get: Optional[str] = None
    lore: Optional[str] = None

    class Config:
        from_attributes = True


class CardCreate(CardBase):
    """创建卡牌模型"""
    pass


class CardUpdate(BaseModel):
    """更新卡牌模型"""
    name: Optional[str] = None
    description: Optional[str] = None
    flavor_text: Optional[str] = None

    # 基本属性
    cost: Optional[int] = None
    attack: Optional[int] = None
    defense: Optional[int] = None
    durability: Optional[int] = None

    # 卡牌分类
    card_type: Optional[str] = None
    rarity: Optional[str] = None
    card_class: Optional[str] = None
    card_set: Optional[str] = None

    # 效果和机制
    mechanics: Optional[List[str]] = None
    effect_text: Optional[str] = None
    play_requirements: Optional[Dict[str, Any]] = None
    deathrattle_effect: Optional[Dict[str, Any]] = None
    battlecry_effect: Optional[Dict[str, Any]] = None
    ongoing_effect: Optional[Dict[str, Any]] = None

    # 视觉资源
    image_url: Optional[str] = None
    golden_image_url: Optional[str] = None
    sound_url: Optional[str] = None

    # 平衡和限制
    is_collectible: Optional[bool] = None
    is_standard_legal: Optional[bool] = None
    is_wild_legal: Optional[bool] = None
    crafting_cost: Optional[int] = None

    # 统计数据
    play_count: Optional[int] = None
    win_rate: Optional[float] = None
    usage_rate: Optional[float] = None

    # 元数据
    artist: Optional[str] = None
    how_to_get: Optional[str] = None
    lore: Optional[str] = None

    class Config:
        from_attributes = True


class CardInDBBase(CardBase):
    """数据库卡牌基础模型"""
    id: int

    class Config:
        from_attributes = True


class Card(CardInDBBase):
    """卡牌完整模型"""
    pass


class CardListResponse(BaseModel):
    """卡牌列表响应模型"""
    id: int
    name: str
    description: str
    cost: int
    attack: Optional[int] = None
    defense: Optional[int] = None
    card_type: str
    rarity: str
    card_class: str
    is_collectible: bool

    class Config:
        from_attributes = True


class CardResponse(CardInDBBase):
    """卡牌详细响应模型"""
    pass


class CardSetBase(BaseModel):
    """卡牌包基础模型"""
    name: str
    code: str
    description: Optional[str] = None

    # 发布信息
    release_date: Optional[str] = None
    is_standard_legal: bool
    rotation_date: Optional[str] = None

    # 卡牌包信息
    pack_cost: int
    pack_cost_real: Optional[float] = None
    card_count_common: int
    card_count_rare: int
    epic_chance: float
    legendary_chance: float

    # 视觉资源
    logo_url: Optional[str] = None
    banner_url: Optional[str] = None

    class Config:
        from_attributes = True


class CardSetCreate(CardSetBase):
    """创建卡牌包模型"""
    pass


class CardSetUpdate(BaseModel):
    """更新卡牌包模型"""
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None

    # 发布信息
    release_date: Optional[str] = None
    is_standard_legal: Optional[bool] = None
    rotation_date: Optional[str] = None

    # 卡牌包信息
    pack_cost: Optional[int] = None
    pack_cost_real: Optional[float] = None
    card_count_common: Optional[int] = None
    card_count_rare: Optional[int] = None
    epic_chance: Optional[float] = None
    legendary_chance: Optional[float] = None

    # 视觉资源
    logo_url: Optional[str] = None
    banner_url: Optional[str] = None

    class Config:
        from_attributes = True


class CardSet(CardSetBase):
    """卡牌包完整模型"""
    id: int

    class Config:
        from_attributes = True


class UserCardCollectionBase(BaseModel):
    """用户卡牌收藏基础模型"""
    user_id: int
    card_id: int
    normal_count: int
    golden_count: int
    crafted_normal: int
    crafted_golden: int
    disenchanted_normal: int
    disenchanted_golden: int
    first_obtained_at: Optional[str] = None
    last_used_at: Optional[str] = None

    class Config:
        from_attributes = True


class UserCardCollectionCreate(UserCardCollectionBase):
    """创建用户卡牌收藏模型"""
    pass


class UserCardCollectionUpdate(BaseModel):
    """更新用户卡牌收藏模型"""
    user_id: Optional[int] = None
    card_id: Optional[int] = None
    normal_count: Optional[int] = None
    golden_count: Optional[int] = None
    crafted_normal: Optional[int] = None
    crafted_golden: Optional[int] = None
    disenchanted_normal: Optional[int] = None
    disenchanted_golden: Optional[int] = None
    first_obtained_at: Optional[str] = None
    last_used_at: Optional[str] = None

    class Config:
        from_attributes = True


class UserCardCollection(UserCardCollectionBase):
    """用户卡牌收藏完整模型"""
    id: int

    class Config:
        from_attributes = True