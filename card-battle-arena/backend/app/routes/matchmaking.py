from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import asyncio
import json

from app.database.postgres import get_db
from app.models.user import User
from app.models.deck import Deck
from app.api.dependencies import get_current_user
from app.core.matchmaking.matcher import (
    matchmaking_engine,
    MatchRequest,
    GameMode,
    MatchStatus
)
from app.schemas.matchmaking import (
    MatchRequestCreate,
    MatchRequestResponse,
    MatchResponse,
    QueueStatusResponse,
    UserMatchStatusResponse
)

router = APIRouter(prefix="/api/matchmaking", tags=["matchmaking"])

@router.post("/request", response_model=MatchRequestResponse)
async def create_match_request(
    request_data: MatchRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建匹配请求"""

    # 验证卡组存在且属于用户
    deck = db.query(Deck).filter(
        Deck.id == request_data.deck_id,
        Deck.user_id == current_user.id
    ).first()

    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deck not found or doesn't belong to user"
        )

    # 检查用户是否已经在队列中
    user_status = matchmaking_engine.get_user_status(current_user.id)
    if user_status["in_queue"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already in matchmaking queue"
        )

    # 创建匹配请求
    match_request = MatchRequest(
        user_id=current_user.id,
        username=current_user.username,
        mode=request_data.mode,
        deck_id=request_data.deck_id,
        deck_name=deck.name,
        rating=current_user.rating,
        preferences=request_data.preferences or {}
    )

    # 添加到匹配队列
    queue_id = await matchmaking_engine.add_match_request(match_request)

    return MatchRequestResponse(
        queue_id=queue_id,
        user_id=current_user.id,
        username=current_user.username,
        mode=request_data.mode,
        deck_id=request_data.deck_id,
        deck_name=deck.name,
        rating=current_user.rating,
        preferences=request_data.preferences or {},
        status=MatchStatus.WAITING,
        created_at=match_request.created_at
    )

@router.delete("/request")
async def cancel_match_request(
    mode: GameMode,
    current_user: User = Depends(get_current_user)
):
    """取消匹配请求"""

    success = await matchmaking_engine.remove_match_request(current_user.id, mode)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active match request found"
        )

    return {"message": "Match request cancelled successfully"}

@router.get("/status", response_model=UserMatchStatusResponse)
async def get_match_status(
    current_user: User = Depends(get_current_user)
):
    """获取用户匹配状态"""

    status = matchmaking_engine.get_user_status(current_user.id)

    return UserMatchStatusResponse(**status)

@router.get("/queue/{mode}", response_model=QueueStatusResponse)
async def get_queue_status(
    mode: GameMode,
    current_user: User = Depends(get_current_user)
):
    """获取队列状态"""

    status = matchmaking_engine.get_queue_status(mode)

    return QueueStatusResponse(**status)

@router.get("/queues/status")
async def get_all_queue_status(
    current_user: User = Depends(get_current_user)
):
    """获取所有队列状态"""

    all_status = {}
    for mode in GameMode:
        all_status[mode.value] = matchmaking_engine.get_queue_status(mode)

    return all_status

@router.get("/match/{match_id}", response_model=MatchResponse)
async def get_match_info(
    match_id: str,
    current_user: User = Depends(get_current_user)
):
    """获取匹配信息"""

    # 检查用户是否参与该匹配
    match = None
    for m in matchmaking_engine.active_matches.values():
        if m.match_id == match_id:
            if m.player1_id == current_user.id or m.player2_id == current_user.id:
                match = m
            break

    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found or access denied"
        )

    return MatchResponse.from_match(match)

@router.post("/match/{match_id}/ready")
async def mark_match_ready(
    match_id: str,
    current_user: User = Depends(get_current_user)
):
    """标记玩家准备就绪"""

    match = None
    for m in matchmaking_engine.active_matches.values():
        if m.match_id == match_id:
            if m.player1_id == current_user.id or m.player2_id == current_user.id:
                match = m
            break

    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )

    # 这里应该记录玩家准备状态
    # 当两个玩家都准备就绪时，开始游戏

    return {"message": "Player marked as ready"}

# WebSocket连接用于实时匹配通知
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_personal_message(self, message: dict, user_id: int):
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(json.dumps(message))
            except:
                # 连接已断开，移除
                self.active_connections.pop(user_id, None)

manager = ConnectionManager()

@router.websocket("/ws/{user_id}")
async def matchmaking_websocket(
    websocket: WebSocket,
    user_id: int,
    db: Session = Depends(get_db)
):
    """匹配WebSocket连接"""

    await manager.connect(websocket, user_id)

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            # 处理不同类型的消息
            if message["type"] == "ping":
                await manager.send_personal_message({"type": "pong"}, user_id)

            elif message["type"] == "get_status":
                status = matchmaking_engine.get_user_status(user_id)
                await manager.send_personal_message({
                    "type": "status_update",
                    "data": status
                }, user_id)

            elif message["type"] == "cancel_match":
                mode = GameMode(message["mode"])
                success = await matchmaking_engine.remove_match_request(user_id, mode)
                await manager.send_personal_message({
                    "type": "match_cancelled",
                    "success": success
                }, user_id)

    except WebSocketDisconnect:
        manager.disconnect(user_id)
        # 用户断开连接时取消匹配
        for mode in GameMode:
            await matchmaking_engine.remove_match_request(user_id, mode)

# 管理员API
@router.get("/admin/stats")
async def get_matchmaking_stats(
    current_user: User = Depends(get_current_user)
):
    """获取匹配统计信息（管理员）"""

    # 这里应该检查管理员权限
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    stats = {}
    for mode in GameMode:
        queue_status = matchmaking_engine.get_queue_status(mode)
        stats[mode.value] = queue_status

    stats["total_active_matches"] = len(matchmaking_engine.active_matches)

    return stats

@router.post("/admin/engine/start")
async def start_matchmaking_engine(
    current_user: User = Depends(get_current_user)
):
    """启动匹配引擎（管理员）"""

    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    await matchmaking_engine.start()
    return {"message": "Matchmaking engine started"}

@router.post("/admin/engine/stop")
async def stop_matchmaking_engine(
    current_user: User = Depends(get_current_user)
):
    """停止匹配引擎（管理员）"""

    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    await matchmaking_engine.stop()
    return {"message": "Matchmaking engine stopped"}

@router.get("/history")
async def get_match_history(
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取匹配历史"""

    # 这里应该从数据库查询历史记录
    # 暂时返回空列表
    return {
        "matches": [],
        "total": 0,
        "limit": limit,
        "offset": offset
    }