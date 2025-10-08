from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Optional, Any
import json
import asyncio
import structlog
from datetime import datetime, timezone

from app.models.user import User
from app.models.game import Game, GamePlayer, GameSpectator
from app.core.config import settings

logger = structlog.get_logger()


class ConnectionManager:
    """WebSocket连接管理器"""

    def __init__(self):
        # 活跃连接：user_id -> WebSocket
        self.active_connections: Dict[int, WebSocket] = {}
        # 游戏房间：game_id -> List[user_id]
        self.game_rooms: Dict[int, List[int]] = {}
        # 用户状态：user_id -> user_info
        self.user_info: Dict[int, Dict[str, Any]] = {}
        # 连接元数据：user_id -> connection_info
        self.connection_info: Dict[int, Dict[str, Any]] = {}

    async def connect(self, websocket: WebSocket, user_id: int, user_info: Dict[str, Any] = None):
        """建立WebSocket连接"""
        try:
            await websocket.accept()

            # 如果用户已有连接，先断开旧连接
            if user_id in self.active_connections:
                await self.disconnect(user_id, "新连接已建立")

            # 建立新连接
            self.active_connections[user_id] = websocket
            self.user_info[user_id] = user_info or {}
            self.connection_info[user_id] = {
                "connected_at": datetime.now(timezone.utc),
                "last_ping": datetime.now(timezone.utc),
                "ip_address": websocket.client.host if websocket.client else "unknown"
            }

            logger.info("WebSocket connection established", user_id=user_id)
            return True

        except Exception as e:
            logger.error("Failed to establish WebSocket connection", user_id=user_id, error=str(e))
            return False

    async def disconnect(self, user_id: int, reason: str = "连接断开"):
        """断开WebSocket连接"""
        if user_id in self.active_connections:
            try:
                websocket = self.active_connections[user_id]
                await websocket.close(code=1000, reason=reason)
            except Exception as e:
                logger.warning("Error closing WebSocket connection", user_id=user_id, error=str(e))

            # 清理连接数据
            del self.active_connections[user_id]

            # 从游戏房间中移除
            for game_id, players in self.game_rooms.items():
                if user_id in players:
                    players.remove(user_id)
                    # 通知其他玩家该用户已断线
                    await self.broadcast_to_room(game_id, {
                        "type": "user_disconnected",
                        "user_id": user_id,
                        "reason": reason
                    }, exclude_users=[user_id])

            # 清理用户数据
            if user_id in self.user_info:
                del self.user_info[user_id]
            if user_id in self.connection_info:
                del self.connection_info[user_id]

            logger.info("WebSocket connection closed", user_id=user_id, reason=reason)

    async def send_personal_message(self, user_id: int, message: Dict[str, Any]):
        """发送个人消息"""
        if user_id in self.active_connections:
            try:
                websocket = self.active_connections[user_id]
                await websocket.send_text(json.dumps(message, ensure_ascii=False))
                return True
            except Exception as e:
                logger.error("Failed to send personal message", user_id=user_id, error=str(e))
                # 连接可能已断开，清理连接
                await self.disconnect(user_id, "发送消息失败")
                return False
        return False

    async def broadcast_to_room(self, game_id: int, message: Dict[str, Any], exclude_users: List[int] = None):
        """向游戏房间广播消息"""
        if game_id not in self.game_rooms:
            return

        exclude_users = exclude_users or []
        failed_users = []

        for user_id in self.game_rooms[game_id]:
            if user_id not in exclude_users:
                success = await self.send_personal_message(user_id, message)
                if not success:
                    failed_users.append(user_id)

        # 清理失败的连接
        for user_id in failed_users:
            await self.disconnect(user_id, "连接已失效")

    async def join_game_room(self, user_id: int, game_id: int):
        """加入游戏房间"""
        if game_id not in self.game_rooms:
            self.game_rooms[game_id] = []

        if user_id not in self.game_rooms[game_id]:
            self.game_rooms[game_id].append(user_id)
            logger.info("User joined game room", user_id=user_id, game_id=game_id)

    async def leave_game_room(self, user_id: int, game_id: int):
        """离开游戏房间"""
        if game_id in self.game_rooms and user_id in self.game_rooms[game_id]:
            self.game_rooms[game_id].remove(user_id)

            # 如果房间为空，清理房间
            if not self.game_rooms[game_id]:
                del self.game_rooms[game_id]

            logger.info("User left game room", user_id=user_id, game_id=game_id)

    def get_room_users(self, game_id: int) -> List[int]:
        """获取房间内用户列表"""
        return self.game_rooms.get(game_id, [])

    def get_user_rooms(self, user_id: int) -> List[int]:
        """获取用户所在的房间列表"""
        rooms = []
        for game_id, users in self.game_rooms.items():
            if user_id in users:
                rooms.append(game_id)
        return rooms

    def is_user_connected(self, user_id: int) -> bool:
        """检查用户是否在线"""
        return user_id in self.active_connections

    def get_connected_users_count(self) -> int:
        """获取在线用户数量"""
        return len(self.active_connections)

    async def ping_all_connections(self):
        """向所有连接发送心跳"""
        ping_message = {
            "type": "ping",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        failed_users = []
        for user_id, websocket in list(self.active_connections.items()):
            try:
                await websocket.send_text(json.dumps(ping_message))
                # 更新最后心跳时间
                if user_id in self.connection_info:
                    self.connection_info[user_id]["last_ping"] = datetime.now(timezone.utc)
            except Exception as e:
                logger.warning("Ping failed for user", user_id=user_id, error=str(e))
                failed_users.append(user_id)

        # 清理失败的连接
        for user_id in failed_users:
            await self.disconnect(user_id, "心跳超时")

    async def cleanup_stale_connections(self):
        """清理过期连接"""
        stale_threshold = settings.WS_CONNECTION_TIMEOUT_SECONDS
        current_time = datetime.now(timezone.utc)

        stale_users = []
        for user_id, info in self.connection_info.items():
            connection_age = (current_time - info["connected_at"]).total_seconds()
            last_ping_age = (current_time - info["last_ping"]).total_seconds()

            if connection_age > stale_threshold or last_ping_age > stale_threshold:
                stale_users.append(user_id)

        for user_id in stale_users:
            await self.disconnect(user_id, "连接超时")

    async def get_connection_stats(self) -> Dict[str, Any]:
        """获取连接统计信息"""
        return {
            "total_connections": len(self.active_connections),
            "active_rooms": len(self.game_rooms),
            "total_room_users": sum(len(users) for users in self.game_rooms.values()),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


class GameRoomManager:
    """游戏房间管理器"""

    def __init__(self, connection_manager: ConnectionManager):
        self.connection_manager = connection_manager
        self.room_states: Dict[int, Dict[str, Any]] = {}  # game_id -> room_state

    async def create_room(self, game_id: int, game_data: Dict[str, Any]):
        """创建游戏房间"""
        self.room_states[game_id] = {
            "game_id": game_id,
            "created_at": datetime.now(timezone.utc),
            "players": [],
            "spectators": [],
            "status": "waiting",
            "current_turn": None,
            "game_state": game_data
        }

        logger.info("Game room created", game_id=game_id)

    async def add_player(self, game_id: int, user_id: int, player_data: Dict[str, Any]):
        """添加玩家到房间"""
        if game_id not in self.room_states:
            await self.create_room(game_id, {})

        # 检查玩家是否已在房间中
        if not any(p["user_id"] == user_id for p in self.room_states[game_id]["players"]):
            player_info = {
                "user_id": user_id,
                "joined_at": datetime.now(timezone.utc),
                "is_ready": False,
                **player_data
            }
            self.room_states[game_id]["players"].append(player_info)

            # 加入WebSocket房间
            await self.connection_manager.join_game_room(user_id, game_id)

            # 通知房间内其他玩家
            await self.connection_manager.broadcast_to_room(game_id, {
                "type": "player_joined",
                "player": player_info
            }, exclude_users=[user_id])

            logger.info("Player added to room", game_id=game_id, user_id=user_id)

    async def add_spectator(self, game_id: int, user_id: int, spectator_data: Dict[str, Any]):
        """添加观战者到房间"""
        if game_id not in self.room_states:
            await self.create_room(game_id, {})

        # 检查观战者是否已在房间中
        if not any(s["user_id"] == user_id for s in self.room_states[game_id]["spectators"]):
            spectator_info = {
                "user_id": user_id,
                "joined_at": datetime.now(timezone.utc),
                **spectator_data
            }
            self.room_states[game_id]["spectators"].append(spectator_info)

            # 加入WebSocket房间
            await self.connection_manager.join_game_room(user_id, game_id)

            # 发送当前游戏状态给观战者
            room_state = self.room_states[game_id]
            await self.connection_manager.send_personal_message(user_id, {
                "type": "room_state",
                "state": room_state
            })

            logger.info("Spectator added to room", game_id=game_id, user_id=user_id)

    async def remove_player(self, game_id: int, user_id: int):
        """从房间移除玩家"""
        if game_id in self.room_states:
            # 从玩家列表移除
            self.room_states[game_id]["players"] = [
                p for p in self.room_states[game_id]["players"]
                if p["user_id"] != user_id
            ]

            # 离开WebSocket房间
            await self.connection_manager.leave_game_room(user_id, game_id)

            # 通知房间内其他玩家
            await self.connection_manager.broadcast_to_room(game_id, {
                "type": "player_left",
                "user_id": user_id
            })

            logger.info("Player removed from room", game_id=game_id, user_id=user_id)

    async def update_room_state(self, game_id: int, state_updates: Dict[str, Any]):
        """更新房间状态"""
        if game_id in self.room_states:
            self.room_states[game_id].update(state_updates)

            # 广播状态更新
            await self.connection_manager.broadcast_to_room(game_id, {
                "type": "room_state_update",
                "updates": state_updates
            })

    async def send_game_event(self, game_id: int, event_data: Dict[str, Any]):
        """发送游戏事件"""
        await self.connection_manager.broadcast_to_room(game_id, {
            "type": "game_event",
            "event": event_data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

    def get_room_state(self, game_id: int) -> Optional[Dict[str, Any]]:
        """获取房间状态"""
        return self.room_states.get(game_id)

    def get_room_players(self, game_id: int) -> List[Dict[str, Any]]:
        """获取房间玩家列表"""
        if game_id in self.room_states:
            return self.room_states[game_id]["players"]
        return []

    def get_room_spectators(self, game_id: int) -> List[Dict[str, Any]]:
        """获取房间观战者列表"""
        if game_id in self.room_states:
            return self.room_states[game_id]["spectators"]
        return []


# 全局实例
websocket_manager = ConnectionManager()
game_room_manager = GameRoomManager(websocket_manager)


# 定期任务
async def start_websocket_tasks():
    """启动WebSocket定期任务"""
    # 心跳任务
    async def heartbeat_task():
        while True:
            try:
                await websocket_manager.ping_all_connections()
                await asyncio.sleep(settings.WS_HEARTBEAT_INTERVAL_SECONDS)
            except Exception as e:
                logger.error("Heartbeat task error", error=str(e))
                await asyncio.sleep(5)

    # 清理任务
    async def cleanup_task():
        while True:
            try:
                await websocket_manager.cleanup_stale_connections()
                await asyncio.sleep(60)  # 每分钟清理一次
            except Exception as e:
                logger.error("Cleanup task error", error=str(e))
                await asyncio.sleep(30)

    # 启动任务
    asyncio.create_task(heartbeat_task())
    asyncio.create_task(cleanup_task())

    logger.info("WebSocket background tasks started")


async def disconnect_all():
    """断开所有连接"""
    for user_id in list(websocket_manager.active_connections.keys()):
        await websocket_manager.disconnect(user_id, "服务器关闭")
    logger.info("All WebSocket connections disconnected")