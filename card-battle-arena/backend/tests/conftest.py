import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.main import app
from app.core.database import get_db
from app.core.config import settings
from app.models.base import Base

# Test database URL
TEST_DATABASE_URL = "sqlite:///./test.db"

# Create test engine
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    # Create all tables
    Base.metadata.create_all(bind=test_engine)

    # Create session
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def override_get_db(db_session):
    """Override the get_db dependency."""
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    return _override_get_db


@pytest.fixture(scope="function")
def client(override_get_db):
    """Create a test client with database override."""
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def async_client(override_get_db):
    """Create an async test client with database override."""
    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture
def mock_user():
    """Create a mock user object."""
    user = Mock()
    user.id = 1
    user.username = "testuser"
    user.email = "test@example.com"
    user.password_hash = "$2b$12$hashed_password"
    user.rating = 1500
    user.is_active = True
    user.is_verified = True
    user.is_admin = False
    user.created_at = "2024-01-01T00:00:00Z"
    user.updated_at = "2024-01-01T00:00:00Z"
    return user


@pytest.fixture
def mock_deck():
    """Create a mock deck object."""
    deck = Mock()
    deck.id = 1
    deck.name = "Test Deck"
    deck.description = "A test deck"
    deck.card_class = "mage"
    deck.format_type = "standard"
    deck.is_public = False
    deck.is_favorite = False
    deck.games_played = 0
    deck.games_won = 0
    deck.games_lost = 0
    deck.win_rate = 0.0
    deck.version = 1
    deck.created_at = "2024-01-01T00:00:00Z"
    deck.updated_at = "2024-01-01T00:00:00Z"
    deck.last_used_at = None
    deck.cards = []
    return deck


@pytest.fixture
def mock_card():
    """Create a mock card object."""
    card = Mock()
    card.id = 1
    card.name = "Fireball"
    card.description = "Deal 6 damage"
    card.cost = 4
    card.attack = None
    card.defense = None
    card.durability = None
    card.card_type = "spell"
    card.rarity = "common"
    card.card_class = "mage"
    card.card_set = "basic"
    card.mechanics = []
    card.effect_text = None
    card.play_requirements = {}
    card.deathrattle_effect = None
    card.battlecry_effect = None
    card.ongoing_effect = None
    card.image_url = "http://example.com/fireball.png"
    card.golden_image_url = "http://example.com/fireball_golden.png"
    card.sound_url = "http://example.com/fireball.wav"
    card.is_collectible = True
    card.is_standard_legal = True
    card.is_wild_legal = True
    card.crafting_cost = 40
    card.play_count = 0
    card.win_rate = 0.0
    card.usage_rate = 0.0
    card.artist = "Test Artist"
    card.how_to_get = "Basic card"
    card.lore = "A simple fireball spell."
    return mock_card


@pytest.fixture
def auth_headers(mock_user):
    """Create authentication headers for testing."""
    from jose import jwt
    from app.core.config import settings

    token_data = {"sub": str(mock_user.id)}
    token = jwt.encode(token_data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def mock_redis():
    """Create a mock Redis client."""
    redis_mock = Mock()
    redis_mock.get = AsyncMock(return_value=None)
    redis_mock.set = AsyncMock(return_value=True)
    redis_mock.delete = AsyncMock(return_value=1)
    redis_mock.exists = AsyncMock(return_value=False)
    redis_mock.expire = AsyncMock(return_value=True)
    redis_mock.hget = AsyncMock(return_value=None)
    redis_mock.hset = AsyncMock(return_value=True)
    redis_mock.hgetall = AsyncMock(return_value={})
    redis_mock.hdel = AsyncMock(return_value=1)
    return redis_mock


@pytest.fixture
def mock_websocket():
    """Create a mock WebSocket connection."""
    websocket_mock = Mock()
    websocket_mock.accept = AsyncMock()
    websocket_mock.send_text = AsyncMock()
    websocket_mock.receive_text = AsyncMock(return_value='{"type": "ping"}')
    websocket_mock.close = AsyncMock()
    return websocket_mock


@pytest.fixture
def sample_game_state():
    """Create a sample game state for testing."""
    return {
        "game_id": "test_game_1",
        "player1_id": 1,
        "player2_id": 2,
        "current_player_number": 1,
        "turn_number": 1,
        "turn_time_limit": 90,
        "is_game_over": False,
        "winner": None,
        "action_history": [],
        "player1": {
            "user_id": 1,
            "username": "player1",
            "health": 30,
            "max_health": 30,
            "armor": 0,
            "mana": 1,
            "max_mana": 1,
            "hand": [],
            "battlefield": [],
            "deck_count": 20,
            "graveyard_count": 0,
        },
        "player2": {
            "user_id": 2,
            "username": "player2",
            "health": 30,
            "max_health": 30,
            "armor": 0,
            "mana": 0,
            "max_mana": 0,
            "hand": [],
            "battlefield": [],
            "deck_count": 20,
            "graveyard_count": 0,
        }
    }


@pytest.fixture
def sample_match_request():
    """Create a sample match request for testing."""
    return {
        "user_id": 1,
        "username": "testuser",
        "mode": "ranked",
        "deck_id": 1,
        "deck_name": "Test Deck",
        "rating": 1500,
        "preferences": {
            "max_wait_time": 300,
            "rating_tolerance": 200
        }
    }


@pytest.fixture
def sample_match():
    """Create a sample match for testing."""
    return {
        "match_id": "match_1_123456789",
        "player1_id": 1,
        "player2_id": 2,
        "player1_username": "player1",
        "player2_username": "player2",
        "mode": "ranked",
        "deck1_id": 1,
        "deck2_id": 2,
        "created_at": 1234567890,
        "status": "matched"
    }


# Test configuration
@pytest.fixture(scope="session", autouse=True)
def test_config():
    """Configure test settings."""
    import os

    # Set test environment variables
    os.environ["TESTING"] = "1"
    os.environ["DATABASE_URL"] = TEST_DATABASE_URL
    os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"

    yield

    # Clean up
    os.environ.pop("TESTING", None)
    os.environ.pop("DATABASE_URL", None)
    os.environ.pop("SECRET_KEY", None)


# Mock fixtures for external services
@pytest.fixture
def mock_email_service():
    """Create a mock email service."""
    email_mock = Mock()
    email_mock.send_verification_email = AsyncMock(return_value=True)
    email_mock.send_password_reset_email = AsyncMock(return_value=True)
    email_mock.send_match_notification = AsyncMock(return_value=True)
    return email_mock


@pytest.fixture
def mock_payment_service():
    """Create a mock payment service."""
    payment_mock = Mock()
    payment_mock.create_payment_intent = AsyncMock(return_value={"id": "pi_test_123"})
    payment_mock.confirm_payment = AsyncMock(return_value={"status": "succeeded"})
    payment_mock.refund_payment = AsyncMock(return_value={"status": "succeeded"})
    return payment_mock


@pytest.fixture
def mock_analytics_service():
    """Create a mock analytics service."""
    analytics_mock = Mock()
    analytics_mock.track_event = AsyncMock(return_value=True)
    analytics_mock.track_user_action = AsyncMock(return_value=True)
    analytics_mock.track_game_metrics = AsyncMock(return_value=True)
    return analytics_mock


# Performance testing fixtures
@pytest.fixture
def performance_monitor():
    """Create a performance monitor for testing."""
    import time

    class PerformanceMonitor:
        def __init__(self):
            self.start_time = None
            self.end_time = None
            self.memory_usage = []

        def start(self):
            self.start_time = time.time()

        def stop(self):
            self.end_time = time.time()

        @property
        def duration(self):
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return None

    return PerformanceMonitor()


# Error simulation fixtures
@pytest.fixture
def simulate_network_error():
    """Create a fixture to simulate network errors."""
    def _simulate_error(message="Network error"):
        raise ConnectionError(message)
    return _simulate_error


@pytest.fixture
def simulate_database_error():
    """Create a fixture to simulate database errors."""
    def _simulate_error(message="Database error"):
        raise Exception(message)
    return _simulate_error


@pytest.fixture
def simulate_timeout_error():
    """Create a fixture to simulate timeout errors."""
    def _simulate_error(message="Timeout error"):
        raise TimeoutError(message)
    return _simulate_error