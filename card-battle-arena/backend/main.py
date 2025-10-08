from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import uvicorn
import structlog

from app.core.config import settings
from app.database.postgres import init_db
from app.database.redis import init_redis
from app.api.routes import auth
from app.routes import decks, matchmaking, cards
from app.core.websocket.manager import websocket_manager, disconnect_all
from app.core.matchmaking.matcher import matchmaking_engine

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Card Battle Arena API")

    # Initialize database connections
    await init_db()
    await init_redis()

    # Start matchmaking engine
    await matchmaking_engine.start()

    logger.info("Application startup complete")

    yield

    # Shutdown
    logger.info("Shutting down Card Battle Arena API")

    # Close WebSocket connections
    await disconnect_all()

    # Stop matchmaking engine
    await matchmaking_engine.stop()

    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Card Battle Arena API",
    description="Web端多人联机卡牌对战游戏后端API",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware for production
if not settings.DEBUG:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS
    )


# Include API routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
# app.include_router(game.router, prefix="/api/game", tags=["game"])
app.include_router(decks.router, prefix="/api/decks", tags=["decks"])
app.include_router(cards.router, prefix="/api/cards", tags=["cards"])
# app.include_router(social.router, prefix="/api/social", tags=["social"])
app.include_router(matchmaking.router, prefix="/api/matchmaking", tags=["matchmaking"])

# WebSocket endpoint
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    """Main WebSocket endpoint for real-time game communication"""
    await websocket_manager.connect(websocket, user_id)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Card Battle Arena API",
        "version": "1.0.0",
        "description": "Web端多人联机卡牌对战游戏后端API",
        "docs_url": "/docs" if settings.DEBUG else None,
        "health_check": "/health"
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )