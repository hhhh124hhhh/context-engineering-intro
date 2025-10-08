from typing import Dict, Any, Optional
import json
import structlog
from datetime import datetime, timezone
from fastapi import WebSocket

from app.core.websocket.manager import websocket_manager, game_room_manager
from app.models.user import User
from app.models.game import Game, GamePlayer
from app.api.dependencies import get_current_user_optional, get_current_user
from app.database.postgres import AsyncSessionLocal
from app.core.config import settings

logger = structlog.get_logger()


class WebSocketEventHandler:
    """WebSocket事件处理器"""

    def __init__(self):
        self.handlers = {
            "ping": self.handle_ping,
            "join_game": self.handle_join_game,
            "leave_game": self.handle_leave_game,
            "game_action": self.handle_game_action,
            "chat_message": self.handle_chat_message,
            "spectate_game": self.handle_spectate_game,
            "ready_check": self.handle_ready_check,
            "get_room_state": self.handle_get_room_state,
        }

    async def handle_message(self, websocket: WebSocket, user_id: int, message: str):
        """处理WebSocket消息"""
        try:
            data = json.loads(message)
            event_type = data.get("type")
            payload = data.get("payload", {})

            if event_type in self.handlers:
                handler = self.handlers[event_type]
                await handler(websocket, user_id, payload)
            else:
                await self.send_error(websocket, user_id, f"未知事件类型: {event_type}")

        except json.JSONDecodeError:
            await self.send_error(websocket, user_id, "无效的JSON格式")
        except Exception as e:
            logger.error("WebSocket message handling error", user_id=user_id, error=str(e))
            await self.send_error(websocket, user_id, "消息处理失败")

    async def send_error(self, websocket: WebSocket, user_id: int, error_message: str):
        """发送错误消息"""
        error_response = {
            "type": "error",
            "error": error_message,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        try:
            await websocket.send_text(json.dumps(error_response, ensure_ascii=False))
        except Exception as e:
            logger.error("Failed to send error message", user_id=user_id, error=str(e))

    async def send_success(self, websocket: WebSocket, user_id: int, message: str, data: Dict[str, Any] = None):
        """发送成功消息"""
        success_response = {
            "type": "success",
            "message": message,
            "data": data or {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        try:
            await websocket.send_text(json.dumps(success_response, ensure_ascii=False))
        except Exception as e:
            logger.error("Failed to send success message", user_id=user_id, error=str(e))

    async def handle_ping(self, websocket: WebSocket, user_id: int, payload: Dict[str, Any]):
        """处理心跳消息"""
        pong_response = {
            "type": "pong",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "server_time": datetime.now(timezone.utc).timestamp()
        }
        await websocket.send_text(json.dumps(pong_response))

    async def handle_join_game(self, websocket: WebSocket, user_id: int, payload: Dict[str, Any]):
        """处理加入游戏"""
        try:
            game_id = payload.get("game_id")
            if not game_id:
                await self.send_error(websocket, user_id, "缺少游戏ID")
                return

            # 验证游戏存在且用户有权限
            async with AsyncSessionLocal() as db:
                game = await db.get(Game, game_id)
                if not game:
                    await self.send_error(websocket, user_id, "游戏不存在")
                    return

                # 检查用户是否为游戏参与者
                game_player = None
                for player in game.players:
                    if player.user_id == user_id:
                        game_player = player
                        break

                if not game_player:
                    await self.send_error(websocket, user_id, "你不是该游戏的参与者")
                    return

                # 加入房间
                player_data = {
                    "username": game_player.user.username,
                    "player_number": game_player.player_number,
                    "health": game_player.health,
                    "mana": game_player.mana,
                    "max_mana": game_player.max_mana
                }

                await game_room_manager.add_player(game_id, user_id, player_data)
                await self.send_success(websocket, user_id, "成功加入游戏", {"game_id": game_id})

                logger.info("User joined game via WebSocket", user_id=user_id, game_id=game_id)

        except Exception as e:
            logger.error("Join game error", user_id=user_id, error=str(e))
            await self.send_error(websocket, user_id, "加入游戏失败")

    async def handle_leave_game(self, websocket: WebSocket, user_id: int, payload: Dict[str, Any]):
        """处理离开游戏"""
        try:
            game_id = payload.get("game_id")
            if not game_id:
                await self.send_error(websocket, user_id, "缺少游戏ID")
                return

            await game_room_manager.remove_player(game_id, user_id)
            await self.send_success(websocket, user_id, "成功离开游戏")

            logger.info("User left game via WebSocket", user_id=user_id, game_id=game_id)

        except Exception as e:
            logger.error("Leave game error", user_id=user_id, error=str(e))
            await self.send_error(websocket, user_id, "离开游戏失败")

    async def handle_game_action(self, websocket: WebSocket, user_id: int, payload: Dict[str, Any]):
        """处理游戏动作"""
        try:
            game_id = payload.get("game_id")
            action_type = payload.get("action_type")
            action_data = payload.get("action_data", {})

            if not game_id or not action_type:
                await self.send_error(websocket, user_id, "缺少必要参数")
                return

            # 这里应该调用游戏引擎来验证和执行动作
            # 暂时只记录日志
            event_data = {
                "user_id": user_id,
                "action_type": action_type,
                "action_data": action_data,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

            await game_room_manager.send_game_event(game_id, {
                "type": "player_action",
                "player_id": user_id,
                "action": event_data
            })

            await self.send_success(websocket, user_id, "游戏动作已处理", {
                "action_type": action_type
            })

            logger.info("Game action processed", user_id=user_id, game_id=game_id, action_type=action_type)

        except Exception as e:
            logger.error("Game action error", user_id=user_id, error=str(e))
            await self.send_error(websocket, user_id, "游戏动作处理失败")

    async def handle_chat_message(self, websocket: WebSocket, user_id: int, payload: Dict[str, Any]):
        """处理聊天消息"""
        try:
            game_id = payload.get("game_id")
            message_content = payload.get("message", "").strip()
            message_type = payload.get("message_type", "game")  # game, private

            if not game_id or not message_content:
                await self.send_error(websocket, user_id, "消息内容不能为空")
                return

            if len(message_content) > 500:
                await self.send_error(websocket, user_id, "消息长度不能超过500字符")
                return

            # 获取用户信息
            async with AsyncSessionLocal() as db:
                user = await db.get(User, user_id)
                if not user:
                    await self.send_error(websocket, user_id, "用户不存在")
                    return

            # 构建聊天消息
            chat_message = {
                "id": f"msg_{datetime.now().timestamp()}_{user_id}",
                "sender_id": user_id,
                "sender_name": user.display_name or user.username,
                "content": message_content,
                "message_type": message_type,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

            # 广播消息
            if message_type == "game":
                await game_room_manager.send_game_event(game_id, {
                    "type": "chat_message",
                    "message": chat_message
                })
            else:
                # 私聊消息需要特殊处理
                target_user_id = payload.get("target_user_id")
                if target_user_id:
                    await websocket_manager.send_personal_message(target_user_id, {
                        "type": "private_chat_message",
                        "message": chat_message
                    })
                    await self.send_success(websocket, user_id, "私聊消息已发送")

            await self.send_success(websocket, user_id, "消息已发送")

            logger.info("Chat message processed", user_id=user_id, game_id=game_id, message_type=message_type)

        except Exception as e:
            logger.error("Chat message error", user_id=user_id, error=str(e))
            await self.send_error(websocket, user_id, "消息发送失败")

    async def handle_spectate_game(self, websocket: WebSocket, user_id: int, payload: Dict[str, Any]):
        """处理观战请求"""
        try:
            game_id = payload.get("game_id")
            if not game_id:
                await self.send_error(websocket, user_id, "缺少游戏ID")
                return

            # 验证游戏存在且允许观战
            async with AsyncSessionLocal() as db:
                game = await db.get(Game, game_id)
                if not game:
                    await self.send_error(websocket, user_id, "游戏不存在")
                    return

                if not settings.ENABLE_SPECTATOR_MODE:
                    await self.send_error(websocket, user_id, "观战功能未启用")
                    return

                # 检查游戏是否允许观战
                if game.status not in ["active", "waiting"]:
                    await self.send_error(websocket, user_id, "该游戏不允许观战")
                    return

                # 获取用户信息
                user = await db.get(User, user_id)
                if not user:
                    await self.send_error(websocket, user_id, "用户不存在")
                    return

                # 加入观战
                spectator_data = {
                    "username": user.display_name or user.username,
                    "joined_at": datetime.now(timezone.utc)
                }

                await game_room_manager.add_spectator(game_id, user_id, spectator_data)
                await self.send_success(websocket, user_id, "成功开始观战", {"game_id": game_id})

                logger.info("User started spectating game", user_id=user_id, game_id=game_id)

        except Exception as e:
            logger.error("Spectate game error", user_id=user_id, error=str(e))
            await self.send_error(websocket, user_id, "观战失败")

    async def handle_ready_check(self, websocket: WebSocket, user_id: int, payload: Dict[str, Any]):
        """处理准备检查"""
        try:
            game_id = payload.get("game_id")
            is_ready = payload.get("is_ready", False)

            if not game_id:
                await self.send_error(websocket, user_id, "缺少游戏ID")
                return

            # 更新房间中的玩家准备状态
            room_state = game_room_manager.get_room_state(game_id)
            if room_state:
                for player in room_state["players"]:
                    if player["user_id"] == user_id:
                        player["is_ready"] = is_ready
                        break

                # 广播准备状态更新
                await game_room_manager.send_game_event(game_id, {
                    "type": "player_ready_update",
                    "user_id": user_id,
                    "is_ready": is_ready
                })

                # 检查是否所有玩家都准备好了
                all_ready = all(player["is_ready"] for player in room_state["players"])
                if all_ready and len(room_state["players"]) >= 2:
                    await game_room_manager.send_game_event(game_id, {
                        "type": "all_players_ready",
                        "game_starting": True
                    })

            await self.send_success(websocket, user_id, "准备状态已更新")

            logger.info("Ready check processed", user_id=user_id, game_id=game_id, is_ready=is_ready)

        except Exception as e:
            logger.error("Ready check error", user_id=user_id, error=str(e))
            await self.send_error(websocket, user_id, "准备状态更新失败")

    async def handle_get_room_state(self, websocket: WebSocket, user_id: int, payload: Dict[str, Any]):
        """处理获取房间状态请求"""
        try:
            game_id = payload.get("game_id")
            if not game_id:
                await self.send_error(websocket, user_id, "缺少游戏ID")
                return

            room_state = game_room_manager.get_room_state(game_id)
            if room_state:
                await self.send_success(websocket, user_id, "房间状态获取成功", {
                    "room_state": room_state
                })
            else:
                await self.send_error(websocket, user_id, "房间不存在")

        except Exception as e:
            logger.error("Get room state error", user_id=user_id, error=str(e))
            await self.send_error(websocket, user_id, "获取房间状态失败")


# 全局事件处理器实例
event_handler = WebSocketEventHandler()


async def handle_websocket_connection(websocket: WebSocket, user_id: int):
    """处理WebSocket连接"""
    try:
        # 连接已建立，等待消息
        while True:
            message = await websocket.receive_text()
            await event_handler.handle_message(websocket, user_id, message)

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected", user_id=user_id)
        await websocket_manager.disconnect(user_id, "客户端主动断开")
    except Exception as e:
        logger.error("WebSocket connection error", user_id=user_id, error=str(e))
        await websocket_manager.disconnect(user_id, "连接错误")