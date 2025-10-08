from typing import Dict, List, Optional, Any, Set
import json
import asyncio
from datetime import datetime, timezone
from dataclasses import dataclass, field
from enum import Enum

import structlog

from app.core.websocket.manager import websocket_manager

logger = structlog.get_logger()


class RoomType(Enum):
    """房间类型"""
    GAME = "game"
    CHAT = "chat"
    TOURNAMENT = "tournament"
    MATCHMAKING = "matchmaking"


class RoomStatus(Enum):
    """房间状态"""
    WAITING = "waiting"
    ACTIVE = "active"
    FINISHED = "finished"
    CLOSED = "closed"


@dataclass
class RoomMember:
    """房间成员"""
    user_id: int
    username: str
    joined_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    is_online: bool = True
    last_seen: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    role: str = "member"  # member, admin, spectator
    permissions: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Room:
    """房间数据类"""
    room_id: str
    room_type: RoomType
    name: str
    description: str = ""
    max_members: int = 100
    is_private: bool = False
    password: Optional[str] = None
    status: RoomStatus = RoomStatus.WAITING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: int = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    # 房间成员和配置
    members: Dict[int, RoomMember] = field(default_factory=dict)
    banned_users: Set[int] = field(default_factory=set)
    settings: Dict[str, Any] = field(default_factory=dict)

    # 游戏相关（如果是游戏房间）
    game_id: Optional[int] = None
    game_state: Dict[str, Any] = field(default_factory=dict)

    class Config:
        arbitrary_types_allowed = True


class RoomManager:
    """房间管理器"""

    def __init__(self):
        self.rooms: Dict[str, Room] = {}
        self.user_rooms: Dict[int, Set[str]] = {}  # user_id -> room_ids
        self.room_counters: Dict[str, int] = {"game": 0, "chat": 0, "tournament": 0, "matchmaking": 0}

    async def create_room(
        self,
        room_type: RoomType,
        name: str,
        creator_id: int,
        creator_username: str,
        description: str = "",
        max_members: int = 100,
        is_private: bool = False,
        password: Optional[str] = None,
        metadata: Dict[str, Any] = None
    ) -> str:
        """创建房间"""
        # 生成房间ID
        room_id = self._generate_room_id(room_type)

        # 创建房间
        room = Room(
            room_id=room_id,
            room_type=room_type,
            name=name,
            description=description,
            max_members=max_members,
            is_private=is_private,
            password=password,
            created_by=creator_id,
            metadata=metadata or {}
        )

        # 创建者加入房间并设为管理员
        creator_member = RoomMember(
            user_id=creator_id,
            username=creator_username,
            role="admin",
            permissions={"manage_room", "kick_members", "ban_members"}
        )
        room.members[creator_id] = creator_member

        # 更新用户的房间列表
        if creator_id not in self.user_rooms:
            self.user_rooms[creator_id] = set()
        self.user_rooms[creator_id].add(room_id)

        # 保存房间
        self.rooms[room_id] = room

        logger.info("Room created", room_id=room_id, room_type=room_type.value, creator_id=creator_id)
        return room_id

    async def join_room(
        self,
        room_id: str,
        user_id: int,
        username: str,
        password: Optional[str] = None
    ) -> bool:
        """加入房间"""
        if room_id not in self.rooms:
            logger.warning("Room not found", room_id=room_id, user_id=user_id)
            return False

        room = self.rooms[room_id]

        # 检查用户是否被禁止
        if user_id in room.banned_users:
            logger.warning("Banned user attempted to join", room_id=room_id, user_id=user_id)
            return False

        # 检查用户是否已在房间中
        if user_id in room.members:
            logger.info("User already in room", room_id=room_id, user_id=user_id)
            return True

        # 检查房间是否已满
        if len(room.members) >= room.max_members:
            logger.warning("Room is full", room_id=room_id, user_id=user_id)
            return False

        # 检查私有房间密码
        if room.is_private and room.password and room.password != password:
            logger.warning("Invalid password for private room", room_id=room_id, user_id=user_id)
            return False

        # 添加成员
        member = RoomMember(user_id=user_id, username=username)
        room.members[user_id] = member

        # 更新用户的房间列表
        if user_id not in self.user_rooms:
            self.user_rooms[user_id] = set()
        self.user_rooms[user_id].add(room_id)

        # 通知房间内其他成员
        await self._broadcast_to_room(room_id, {
            "type": "member_joined",
            "member": {
                "user_id": user_id,
                "username": username,
                "joined_at": member.joined_at.isoformat(),
                "role": member.role
            }
        }, exclude_users=[user_id])

        logger.info("User joined room", room_id=room_id, user_id=user_id)
        return True

    async def leave_room(self, room_id: str, user_id: int) -> bool:
        """离开房间"""
        if room_id not in self.rooms:
            return False

        room = self.rooms[room_id]

        if user_id not in room.members:
            return False

        member = room.members[user_id]
        del room.members[user_id]

        # 更新用户的房间列表
        if user_id in self.user_rooms:
            self.user_rooms[user_id].discard(room_id)
            if not self.user_rooms[user_id]:
                del self.user_rooms[user_id]

        # 通知房间内其他成员
        await self._broadcast_to_room(room_id, {
            "type": "member_left",
            "user_id": user_id,
            "username": member.username,
            "left_at": datetime.now(timezone.utc).isoformat()
        })

        # 如果房间为空，删除房间
        if not room.members:
            await self._delete_room(room_id)
        # 如果是管理员离开且房间还有成员，转让管理权
        elif member.role == "admin" and room.members:
            new_admin_id = next(iter(room.members))
            room.members[new_admin_id].role = "admin"
            room.members[new_admin_id].permissions.update({"manage_room", "kick_members", "ban_members"})

            await self._broadcast_to_room(room_id, {
                "type": "admin_transferred",
                "new_admin_id": new_admin_id,
                "new_admin_username": room.members[new_admin_id].username
            })

        logger.info("User left room", room_id=room_id, user_id=user_id)
        return True

    async def kick_member(self, room_id: str, admin_id: int, target_user_id: int) -> bool:
        """踢出成员"""
        if room_id not in self.rooms:
            return False

        room = self.rooms[room_id]

        # 检查操作权限
        admin_member = room.members.get(admin_id)
        if not admin_member or "kick_members" not in admin_member.permissions:
            return False

        # 不能踢出管理员
        target_member = room.members.get(target_user_id)
        if not target_member or target_member.role == "admin":
            return False

        # 踢出成员
        await self.leave_room(room_id, target_user_id)

        # 通知被踢出的用户
        await websocket_manager.send_personal_message(target_user_id, {
            "type": "kicked_from_room",
            "room_id": room_id,
            "room_name": room.name,
            "reason": "被管理员踢出"
        })

        logger.info("Member kicked", room_id=room_id, admin_id=admin_id, target_user_id=target_user_id)
        return True

    async def ban_member(self, room_id: str, admin_id: int, target_user_id: int) -> bool:
        """禁止成员"""
        if room_id not in self.rooms:
            return False

        room = self.rooms[room_id]

        # 检查操作权限
        admin_member = room.members.get(admin_id)
        if not admin_member or "ban_members" not in admin_member.permissions:
            return False

        # 不能禁止管理员
        target_member = room.members.get(target_user_id)
        if not target_member or target_member.role == "admin":
            return False

        # 添加到禁止列表
        room.banned_users.add(target_user_id)

        # 先踢出
        await self.leave_room(room_id, target_user_id)

        # 通知被禁止的用户
        await websocket_manager.send_personal_message(target_user_id, {
            "type": "banned_from_room",
            "room_id": room_id,
            "room_name": room.name,
            "reason": "被管理员禁止"
        })

        logger.info("Member banned", room_id=room_id, admin_id=admin_id, target_user_id=target_user_id)
        return True

    async def update_room_settings(self, room_id: str, user_id: int, settings: Dict[str, Any]) -> bool:
        """更新房间设置"""
        if room_id not in self.rooms:
            return False

        room = self.rooms[room_id]

        # 检查操作权限
        member = room.members.get(user_id)
        if not member or "manage_room" not in member.permissions:
            return False

        # 更新设置
        room.settings.update(settings)

        # 通知房间内所有成员
        await self._broadcast_to_room(room_id, {
            "type": "room_settings_updated",
            "settings": settings,
            "updated_by": user_id
        })

        logger.info("Room settings updated", room_id=room_id, user_id=user_id, settings=settings)
        return True

    async def send_room_message(self, room_id: str, sender_id: int, message: str, message_type: str = "chat") -> bool:
        """发送房间消息"""
        if room_id not in self.rooms:
            return False

        room = self.rooms[room_id]

        # 检查发送者权限
        sender_member = room.members.get(sender_id)
        if not sender_member:
            return False

        # 构建消息
        chat_message = {
            "id": f"msg_{datetime.now().timestamp()}_{sender_id}",
            "sender_id": sender_id,
            "sender_username": sender_member.username,
            "content": message,
            "message_type": message_type,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        # 广播消息
        await self._broadcast_to_room(room_id, {
            "type": "room_message",
            "message": chat_message
        })

        logger.info("Room message sent", room_id=room_id, sender_id=sender_id, message_type=message_type)
        return True

    async def get_room_info(self, room_id: str, user_id: int) -> Optional[Dict[str, Any]]:
        """获取房间信息"""
        if room_id not in self.rooms:
            return None

        room = self.rooms[room_id]

        # 检查用户权限
        if user_id not in room.members:
            return None

        # 构建房间信息
        members_info = []
        for member_id, member in room.members.items():
            members_info.append({
                "user_id": member_id,
                "username": member.username,
                "role": member.role,
                "is_online": member.is_online,
                "joined_at": member.joined_at.isoformat()
            })

        room_info = {
            "room_id": room_id,
            "room_type": room.room_type.value,
            "name": room.name,
            "description": room.description,
            "status": room.status.value,
            "member_count": len(room.members),
            "max_members": room.max_members,
            "created_at": room.created_at.isoformat(),
            "created_by": room.created_by,
            "members": members_info,
            "settings": room.settings,
            "metadata": room.metadata
        }

        if room.game_id:
            room_info["game_id"] = room.game_id
            room_info["game_state"] = room.game_state

        return room_info

    async def get_user_rooms(self, user_id: int) -> List[Dict[str, Any]]:
        """获取用户所在的房间列表"""
        if user_id not in self.user_rooms:
            return []

        rooms_info = []
        for room_id in self.user_rooms[user_id]:
            room_info = await self.get_room_info(room_id, user_id)
            if room_info:
                rooms_info.append(room_info)

        return rooms_info

    def _generate_room_id(self, room_type: RoomType) -> str:
        """生成房间ID"""
        counter = self.room_counters.get(room_type.value, 0)
        self.room_counters[room_type.value] = counter + 1
        return f"{room_type.value}_{counter:06d}"

    async def _broadcast_to_room(self, room_id: str, message: Dict[str, Any], exclude_users: List[int] = None):
        """向房间广播消息"""
        if room_id not in self.rooms:
            return

        room = self.rooms[room_id]
        exclude_users = exclude_users or []

        for user_id in room.members:
            if user_id not in exclude_users:
                await websocket_manager.send_personal_message(user_id, message)

    async def _delete_room(self, room_id: str):
        """删除房间"""
        if room_id in self.rooms:
            # 通知所有成员房间即将关闭
            room = self.rooms[room_id]
            await self._broadcast_to_room(room_id, {
                "type": "room_closed",
                "reason": "房间已关闭"
            })

            # 清理数据
            for user_id in room.members:
                if user_id in self.user_rooms:
                    self.user_rooms[user_id].discard(room_id)

            del self.rooms[room_id]
            logger.info("Room deleted", room_id=room_id)

    async def cleanup_inactive_rooms(self):
        """清理非活跃房间"""
        current_time = datetime.now(timezone.utc)
        inactive_rooms = []

        for room_id, room in self.rooms.items():
            # 检查房间是否长时间没有活动
            last_activity = max(
                (member.last_seen for member in room.members.values()),
                default=room.created_at
            )

            if (current_time - last_activity).total_seconds() > 3600:  # 1小时无活动
                inactive_rooms.append(room_id)

        for room_id in inactive_rooms:
            await self._delete_room(room_id)

        if inactive_rooms:
            logger.info("Cleaned up inactive rooms", count=len(inactive_rooms))


# 全局房间管理器实例
room_manager = RoomManager()


# 定期清理任务
async def start_room_cleanup_task():
    """启动房间清理任务"""
    while True:
        try:
            await room_manager.cleanup_inactive_rooms()
            await asyncio.sleep(300)  # 每5分钟清理一次
        except Exception as e:
            logger.error("Room cleanup task error", error=str(e))
            await asyncio.sleep(60)