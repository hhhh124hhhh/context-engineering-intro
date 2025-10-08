"""Database models for Card Battle Arena"""

from app.models.user import User, Friendship, UserAchievement, UserSession
from app.models.card import Card, CardSet, UserCardCollection
from app.models.deck import Deck, DeckCard, DeckTemplate, DeckTemplateCard
from app.models.game import Game, GamePlayer, GameCard, GameSpectator, ChatMessage

# Export all models for Alembic autodiscovery
__all__ = [
    # User models
    "User",
    "Friendship",
    "UserAchievement",
    "UserSession",

    # Card models
    "Card",
    "CardSet",
    "UserCardCollection",

    # Deck models
    "Deck",
    "DeckCard",
    "DeckTemplate",
    "DeckTemplateCard",

    # Game models
    "Game",
    "GamePlayer",
    "GameCard",
    "GameSpectator",
    "ChatMessage",
]