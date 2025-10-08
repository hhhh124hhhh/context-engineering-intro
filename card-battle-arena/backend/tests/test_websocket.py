"""
WebSocket连接和通信测试
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock
from app.core.websocket.manager import WebSocketManager
from app.core.websocket.handlers import WebSocketHandler


class TestWebSocketManager:
    """WebSocket连接管理器测试"""

    @pytest.fixture
    def websocket_manager(self):
        """创建WebSocket管理器实例"""
        return WebSocketManager()

    @pytest.fixture
    def mock_websocket(self):
        """创建模拟WebSocket连接"""
        mock_ws = Mock()
        mock_ws.send = AsyncMock()
        mock_ws.receive = AsyncMock()
        mock_ws.client_id = "test_client_001"
        mock_ws.user_id = 1
        return mock_ws

    @pytest.mark.asyncio
    async def test_connect_client(self, websocket_manager, mock_websocket):
        """测试客户端连接"""
        # 连接客户端
        await websocket_manager.connect(mock_websocket)

        # 验证客户端已连接
        assert mock_websocket.client_id in websocket_manager.connections
        assert websocket_manager.connections[mock_websocket.client_id] == mock_websocket

    @pytest.mark.asyncio
    async def test_disconnect_client(self, websocket_manager, mock_websocket):
        """测试客户端断开连接"""
        # 先连接客户端
        await websocket_manager.connect(mock_websocket)

        # 断开连接
        await websocket_manager.disconnect(mock_websocket.client_id)

        # 验证客户端已断开
        assert mock_websocket.client_id not in websocket_manager.connections

    @pytest.mark.asyncio
    async def test_send_personal_message(self, websocket_manager, mock_websocket):
        """测试发送个人消息"""
        # 连接客户端
        await websocket_manager.connect(mock_websocket)

        # 发送消息
        message = {"type": "test", "data": "Hello, World!"}
        await websocket_manager.send_personal_message(message, mock_websocket.client_id)

        # 验证消息已发送
        mock_websocket.send.assert_called_once_with(json.dumps(message))

    @pytest.mark.asyncio
    async def test_broadcast_message(self, websocket_manager):
        """测试广播消息"""
        # 创建多个模拟客户端
        clients = []
        for i in range(3):
            mock_ws = Mock()
            mock_ws.send = AsyncMock()
            mock_ws.client_id = f"test_client_{i:03d}"
            mock_ws.user_id = i + 1
            clients.append(mock_ws)
            await websocket_manager.connect(mock_ws)

        # 广播消息
        message = {"type": "broadcast", "data": "Hello, everyone!"}
        await websocket_manager.broadcast(message)

        # 验证所有客户端都收到了消息
        for mock_ws in clients:
            mock_ws.send.assert_called_once_with(json.dumps(message))

    @pytest.mark.asyncio
    async def test_get_connected_clients(self, websocket_manager, mock_websocket):
        """测试获取已连接客户端列表"""
        # 连接客户端
        await websocket_manager.connect(mock_websocket)

        # 获取客户端列表
        clients = await websocket_manager.get_connected_clients()

        # 验证客户端列表包含该客户端
        assert mock_websocket.client_id in clients

    @pytest.mark.asyncio
    async def test_send_to_user(self, websocket_manager):
        """测试向特定用户发送消息"""
        # 创建多个客户端，其中两个属于同一用户
        mock_ws1 = Mock()
        mock_ws1.send = AsyncMock()
        mock_ws1.client_id = "test_client_001"
        mock_ws1.user_id = 1

        mock_ws2 = Mock()
        mock_ws2.send = AsyncMock()
        mock_ws2.client_id = "test_client_002"
        mock_ws2.user_id = 1

        mock_ws3 = Mock()
        mock_ws3.send = AsyncMock()
        mock_ws3.client_id = "test_client_003"
        mock_ws3.user_id = 2

        # 连接客户端
        await websocket_manager.connect(mock_ws1)
        await websocket_manager.connect(mock_ws2)
        await websocket_manager.connect(mock_ws3)

        # 向用户1发送消息
        message = {"type": "user_message", "data": "Hello, User 1!"}
        await websocket_manager.send_to_user(message, user_id=1)

        # 验证用户1的所有客户端都收到了消息
        mock_ws1.send.assert_called_once_with(json.dumps(message))
        mock_ws2.send.assert_called_once_with(json.dumps(message))
        # 用户3的客户端不应该收到消息
        mock_ws3.send.assert_not_called()


class TestWebSocketHandler:
    """WebSocket消息处理器测试"""

    @pytest.fixture
    def websocket_handler(self):
        """创建WebSocket处理器实例"""
        return WebSocketHandler()

    @pytest.fixture
    def mock_manager(self):
        """创建模拟WebSocket管理器"""
        manager = Mock()
        manager.send_personal_message = AsyncMock()
        manager.broadcast = AsyncMock()
        manager.disconnect = AsyncMock()
        return manager

    @pytest.mark.asyncio
    async def test_handle_ping_message(self, websocket_handler, mock_manager):
        """测试处理ping消息"""
        mock_websocket = Mock()
        mock_websocket.client_id = "test_client_001"

        message = {"type": "ping", "timestamp": 1234567890}

        # 处理ping消息
        await websocket_handler.handle_message(
            message, mock_websocket, mock_manager
        )

        # 验证发送了pong响应
        mock_manager.send_personal_message.assert_called_once()
        call_args = mock_manager.send_personal_message.call_args[0]
        response = call_args[0]
        assert response["type"] == "pong"
        assert response["timestamp"] == message["timestamp"]

    @pytest.mark.asyncio
    async def test_handle_game_action_message(self, websocket_handler, mock_manager):
        """测试处理游戏动作消息"""
        mock_websocket = Mock()
        mock_websocket.client_id = "test_client_001"
        mock_websocket.user_id = 1

        message = {
            "type": "game_action",
            "game_id": "test_game_001",
            "action": "play_card",
            "data": {
                "card_id": "fireball_001",
                "target": "opponent_hero"
            }
        }

        # 处理游戏动作消息
        await websocket_handler.handle_message(
            message, mock_websocket, mock_manager
        )

        # 验证广播了游戏状态更新
        mock_manager.broadcast.assert_called_once()
        call_args = mock_manager.broadcast.call_args[0]
        broadcast_message = call_args[0]
        assert broadcast_message["type"] == "game_update"
        assert "game_id" in broadcast_message
        assert "action" in broadcast_message

    @pytest.mark.asyncio
    async def test_handle_invalid_message(self, websocket_handler, mock_manager):
        """测试处理无效消息"""
        mock_websocket = Mock()
        mock_websocket.client_id = "test_client_001"

        # 测试缺少type字段的消息
        invalid_message = {"data": "some data"}

        # 处理无效消息应该抛出异常
        with pytest.raises(ValueError):
            await websocket_handler.handle_message(
                invalid_message, mock_websocket, mock_manager
            )

    @pytest.mark.asyncio
    async def test_handle_unknown_message_type(self, websocket_handler, mock_manager):
        """测试处理未知类型的消息"""
        mock_websocket = Mock()
        mock_websocket.client_id = "test_client_001"

        message = {"type": "unknown_type", "data": "some data"}

        # 处理未知类型消息应该记录警告但不抛出异常
        await websocket_handler.handle_message(
            message, mock_websocket, mock_manager
        )

        # 验证没有发送任何响应
        mock_manager.send_personal_message.assert_not_called()
        mock_manager.broadcast.assert_not_called()

    @pytest.mark.asyncio
    async def test_handle_chat_message(self, websocket_handler, mock_manager):
        """测试处理聊天消息"""
        mock_websocket = Mock()
        mock_websocket.client_id = "test_client_001"
        mock_websocket.user_id = 1

        message = {
            "type": "chat",
            "game_id": "test_game_001",
            "data": {
                "message": "Hello, opponent!"
            }
        }

        # 处理聊天消息
        await websocket_handler.handle_message(
            message, mock_websocket, mock_manager
        )

        # 验证广播了聊天消息
        mock_manager.broadcast.assert_called_once()
        call_args = mock_manager.broadcast.call_args[0]
        broadcast_message = call_args[0]
        assert broadcast_message["type"] == "chat"
        assert broadcast_message["game_id"] == "test_game_001"
        assert "user_id" in broadcast_message
        assert "message" in broadcast_message

    @pytest.mark.asyncio
    async def test_handle_connection_close(self, websocket_handler, mock_manager):
        """测试处理连接关闭"""
        mock_websocket = Mock()
        mock_websocket.client_id = "test_client_001"

        # 处理连接关闭
        await websocket_handler.handle_connection_close(mock_websocket, mock_manager)

        # 验证从管理器中断开连接
        mock_manager.disconnect.assert_called_once_with(mock_websocket.client_id)


@pytest.mark.asyncio
async def test_websocket_integration():
    """WebSocket集成测试"""
    # 这里可以添加端到端的WebSocket测试
    # 例如使用测试WebSocket服务器和客户端
    pass


if __name__ == "__main__":
    pytest.main([__file__])