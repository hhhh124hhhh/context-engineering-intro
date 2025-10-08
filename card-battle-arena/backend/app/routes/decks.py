from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import json

from app.database.postgres import get_db
from app.models.user import User
from app.models.deck import Deck, DeckCard
from app.models.card import Card
from app.api.dependencies import get_current_user
from app.schemas.deck import (
    DeckCreate,
    DeckUpdate,
    DeckResponse,
    DeckListResponse,
    DeckStats
)

router = APIRouter(prefix="/api/decks", tags=["decks"])

@router.get("/", response_model=List[DeckListResponse])
async def get_decks(
    skip: int = 0,
    limit: int = 50,
    card_class: Optional[str] = None,
    is_public: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户的卡组列表"""
    query = db.query(Deck).filter(Deck.user_id == current_user.id)

    if card_class:
        query = query.filter(Deck.card_class == card_class)

    if is_public is not None:
        query = query.filter(Deck.is_public == is_public)

    decks = query.offset(skip).limit(limit).all()

    return [
        DeckListResponse(
            id=deck.id,
            name=deck.name,
            description=deck.description,
            card_class=deck.card_class,
            is_public=deck.is_public,
            is_favorite=deck.is_favorite,
            games_played=deck.games_played,
            games_won=deck.games_won,
            games_lost=deck.games_lost,
            win_rate=deck.win_rate,
            version=deck.version,
            created_at=deck.created_at,
            updated_at=deck.updated_at,
            last_used_at=deck.last_used_at,
            cards_count=len(deck.cards) if deck.cards else 0
        )
        for deck in decks
    ]

@router.get("/{deck_id}", response_model=DeckResponse)
async def get_deck(
    deck_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取特定卡组详情"""
    deck = db.query(Deck).filter(
        Deck.id == deck_id,
        Deck.user_id == current_user.id
    ).first()

    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deck not found"
        )

    return DeckResponse.from_orm(deck)

@router.post("/", response_model=DeckResponse)
async def create_deck(
    deck_data: DeckCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建新卡组"""

    # 验证卡牌数量限制
    total_cards = sum(card.quantity for card in deck_data.cards)
    if total_cards != 30:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Deck must contain exactly 30 cards"
        )

    # 验证卡牌存在性和数量限制
    card_counts = {}
    for deck_card in deck_data.cards:
        card = db.query(Card).filter(Card.id == deck_card.cardId).first()
        if not card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Card with id {deck_card.cardId} not found"
            )

        # 检查卡牌数量限制
        max_quantity = 1 if card.rarity == 'legendary' else 2
        current_count = card_counts.get(deck_card.cardId, 0) + deck_card.quantity
        if current_count > max_quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Card {card.name} quantity exceeds limit of {max_quantity}"
            )

        card_counts[deck_card.cardId] = current_count

    # 创建卡组
    deck = Deck(
        user_id=current_user.id,
        name=deck_data.name,
        description=deck_data.description,
        card_class=deck_data.card_class,
        is_public=deck_data.is_public,
        is_favorite=deck_data.is_favorite,
        version=1
    )

    db.add(deck)
    db.flush()  # 获取deck.id

    # 添加卡牌
    for position, card_data in enumerate(deck_data.cards):
        deck_card = DeckCard(
            deck_id=deck.id,
            card_id=card_data.cardId,
            quantity=card_data.quantity,
            position=position
        )
        db.add(deck_card)

    db.commit()
    db.refresh(deck)

    return DeckResponse.from_orm(deck)

@router.put("/{deck_id}", response_model=DeckResponse)
async def update_deck(
    deck_id: int,
    deck_data: DeckUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新卡组"""

    deck = db.query(Deck).filter(
        Deck.id == deck_id,
        Deck.user_id == current_user.id
    ).first()

    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deck not found"
        )

    # 更新基本信息
    if deck_data.name is not None:
        deck.name = deck_data.name
    if deck_data.description is not None:
        deck.description = deck_data.description
    if deck_data.is_public is not None:
        deck.is_public = deck_data.is_public
    if deck_data.is_favorite is not None:
        deck.is_favorite = deck_data.is_favorite

    # 更新卡牌
    if deck_data.cards is not None:
        # 验证卡牌数量限制
        total_cards = sum(card.quantity for card in deck_data.cards)
        if total_cards != 30:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Deck must contain exactly 30 cards"
            )

        # 删除现有卡牌
        db.query(DeckCard).filter(DeckCard.deck_id == deck.id).delete()

        # 添加新卡牌
        for position, card_data in enumerate(deck_data.cards):
            card = db.query(Card).filter(Card.id == card_data.cardId).first()
            if not card:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Card with id {card_data.cardId} not found"
                )

            deck_card = DeckCard(
                deck_id=deck.id,
                card_id=card_data.cardId,
                quantity=card_data.quantity,
                position=position
            )
            db.add(deck_card)

        # 增加版本号
        deck.version += 1

    db.commit()
    db.refresh(deck)

    return DeckResponse.from_orm(deck)

@router.delete("/{deck_id}")
async def delete_deck(
    deck_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除卡组"""

    deck = db.query(Deck).filter(
        Deck.id == deck_id,
        Deck.user_id == current_user.id
    ).first()

    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deck not found"
        )

    db.delete(deck)
    db.commit()

    return {"message": "Deck deleted successfully"}

@router.post("/{deck_id}/copy", response_model=DeckResponse)
async def copy_deck(
    deck_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """复制卡组"""

    original_deck = db.query(Deck).filter(Deck.id == deck_id).first()
    if not original_deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deck not found"
        )

    # 创建新卡组
    new_deck = Deck(
        user_id=current_user.id,
        name=f"{original_deck.name} (副本)",
        description=original_deck.description,
        card_class=original_deck.card_class,
        is_public=False,
        is_favorite=False,
        version=1
    )

    db.add(new_deck)
    db.flush()

    # 复制卡牌
    original_cards = db.query(DeckCard).filter(
        DeckCard.deck_id == deck_id
    ).order_by(DeckCard.position).all()

    for card in original_cards:
        new_card = DeckCard(
            deck_id=new_deck.id,
            card_id=card.card_id,
            quantity=card.quantity,
            position=card.position
        )
        db.add(new_card)

    db.commit()
    db.refresh(new_deck)

    return DeckResponse.from_orm(new_deck)

@router.post("/{deck_id}/favorite")
async def toggle_favorite(
    deck_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """切换收藏状态"""

    deck = db.query(Deck).filter(
        Deck.id == deck_id,
        Deck.user_id == current_user.id
    ).first()

    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deck not found"
        )

    deck.is_favorite = not deck.is_favorite
    db.commit()

    return {"is_favorite": deck.is_favorite}

@router.get("/{deck_id}/stats", response_model=DeckStats)
async def get_deck_stats(
    deck_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取卡组统计信息"""

    deck = db.query(Deck).filter(
        Deck.id == deck_id,
        Deck.user_id == current_user.id
    ).first()

    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deck not found"
        )

    # 计算统计信息
    cards = deck.cards or []
    total_cards = sum(card.quantity for card in cards)
    total_cost = sum(card.quantity * card.card.cost for card in cards)
    average_cost = total_cost / total_cards if total_cards > 0 else 0

    # 费用分布
    cost_distribution = {}
    for i in range(8):  # 0-7费
        cost_distribution[i] = sum(
            card.quantity for card in cards
            if card.card.cost == i
        )

    # 类型分布
    type_distribution = {}
    for card in cards:
        card_type = card.card.card_type
        type_distribution[card_type] = type_distribution.get(card_type, 0) + card.quantity

    # 稀有度分布
    rarity_distribution = {}
    for card in cards:
        rarity = card.card.rarity
        rarity_distribution[rarity] = rarity_distribution.get(rarity, 0) + card.quantity

    return DeckStats(
        total_cards=total_cards,
        average_cost=round(average_cost, 1),
        cost_distribution=cost_distribution,
        type_distribution=type_distribution,
        rarity_distribution=rarity_distribution
    )

@router.post("/import")
async def import_deck(
    deck_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """导入卡组"""

    try:
        # 验证导入数据
        if 'cards' not in deck_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cards data is required"
            )

        # 转换为DeckCreate格式
        deck_create = DeckCreate(
            name=deck_data.get('name', '导入的卡组'),
            description=deck_data.get('description'),
            card_class=deck_data.get('card_class', 'neutral'),
            cards=deck_data['cards']
        )

        # 创建卡组
        return await create_deck(deck_create, db, current_user)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to import deck: {str(e)}"
        )

@router.get("/{deck_id}/export")
async def export_deck(
    deck_id: int,
    format: str = "json",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """导出卡组"""

    deck = db.query(Deck).filter(
        Deck.id == deck_id,
        Deck.user_id == current_user.id
    ).first()

    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deck not found"
        )

    if format == "json":
        return DeckResponse.from_orm(deck)
    elif format == "text":
        # 文本格式
        lines = [f"{deck.name}"]
        lines.append(f"职业: {deck.card_class}")
        if deck.description:
            lines.append(f"描述: {deck.description}")
        lines.append("")
        lines.append("卡牌列表:")

        for card in deck.cards or []:
            lines.append(f"{card.quantity}x {card.card.name}")

        return {"text": "\n".join(lines)}
    elif format == "deckstring":
        # 简化的卡组代码（实际应用中需要更复杂的编码）
        cards_data = [
            {"id": card.card_id, "quantity": card.quantity}
            for card in deck.cards or []
        ]

        deckstring_data = {
            "cards": cards_data,
            "format": 1,
            "heroes": [get_hero_id_by_class(deck.card_class)]
        }

        return {"deckstring": json.dumps(deckstring_data)}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported export format"
        )

def get_hero_id_by_class(card_class: str) -> int:
    """根据职业获取英雄ID"""
    hero_ids = {
        'warrior': 7,
        'mage': 8,
        'hunter': 9,
        'rogue': 10,
        'priest': 11,
        'warlock': 12,
        'shaman': 13,
        'paladin': 14,
        'druid': 15,
        'neutral': 16
    }
    return hero_ids.get(card_class, 16)