from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import json

from app.database.postgres import get_db
from app.models.card import Card
from app.models.user import User
from app.api.dependencies import get_current_user
from app.schemas.card import CardResponse, CardListResponse

router = APIRouter(tags=["cards"])

@router.get("/", response_model=List[CardListResponse])
async def get_cards(
    skip: int = 0,
    limit: int = 100,
    card_class: Optional[str] = None,
    card_type: Optional[str] = None,
    rarity: Optional[str] = None,
    is_collectible: Optional[bool] = True,
    db: Session = Depends(get_db)
):
    """获取卡牌列表"""
    query = db.query(Card)
    
    if card_class:
        query = query.filter(Card.card_class == card_class)
    
    if card_type:
        query = query.filter(Card.card_type == card_type)
    
    if rarity:
        query = query.filter(Card.rarity == rarity)
    
    if is_collectible is not None:
        query = query.filter(Card.is_collectible == is_collectible)
    
    cards = query.offset(skip).limit(limit).all()
    
    return [
        CardListResponse(
            id=card.id,
            name=card.name,
            description=card.description,
            cost=card.cost,
            attack=card.attack,
            defense=card.defense,
            card_type=card.card_type,
            rarity=card.rarity,
            card_class=card.card_class,
            is_collectible=card.is_collectible
        )
        for card in cards
    ]

@router.get("/{card_id}", response_model=CardResponse)
async def get_card(
    card_id: int,
    db: Session = Depends(get_db)
):
    """获取特定卡牌详情"""
    card = db.query(Card).filter(Card.id == card_id).first()
    
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found"
        )
    
    return CardResponse.from_orm(card)

@router.get("/search/", response_model=List[CardListResponse])
async def search_cards(
    query: str,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """搜索卡牌"""
    cards = db.query(Card).filter(
        Card.name.contains(query) | Card.description.contains(query)
    ).offset(skip).limit(limit).all()
    
    return [
        CardListResponse(
            id=card.id,
            name=card.name,
            description=card.description,
            cost=card.cost,
            attack=card.attack,
            defense=card.defense,
            card_type=card.card_type,
            rarity=card.rarity,
            card_class=card.card_class,
            is_collectible=card.is_collectible
        )
        for card in cards
    ]