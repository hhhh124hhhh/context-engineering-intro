from fastapi import Depends, HTTPException, status, WebSocket
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import structlog

from app.database.postgres import get_db
from app.models.user import User, UserSession
from app.core.security import verify_token
from app.core.config import settings

logger = structlog.get_logger()

# HTTP Bearer scheme for token authentication
security = HTTPBearer(auto_error=False)


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """获取当前用户（可选，允许匿名访问）"""
    if not credentials:
        return None

    try:
        # 验证访问令牌
        user_id = verify_token(credentials.credentials, "access")
        if user_id is None:
            return None

        # 从数据库获取用户
        user = await db.get(User, user_id)
        if user is None or not user.is_active:
            return None

        # 检查用户是否被封禁
        if user.is_banned_currently:
            return None

        return user

    except Exception as e:
        logger.warning("Optional user authentication failed", error=str(e))
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """获取当前用户（必需，已认证）"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        # 验证访问令牌
        user_id = verify_token(credentials.credentials, "access")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的认证凭据",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 从数据库获取用户
        user = await db.get(User, user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 检查用户状态
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户账户已被禁用",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if user.is_banned_currently:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"用户账户已被封禁，原因：{user.ban_reason or '违反社区规范'}",
            )

        # 更新最后登录时间
        from datetime import datetime, timezone
        user.last_login_at = datetime.now(timezone.utc)
        await db.commit()

        return user

    except HTTPException:
        raise
    except Exception as e:
        logger.error("User authentication failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="认证失败",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_verified_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """获取当前已验证邮箱的用户"""
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="请先验证邮箱地址",
        )
    return current_user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """获取当前活跃用户（在线状态）"""
    # 可以在这里添加额外的活跃状态检查
    return current_user


async def get_current_user_by_refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db)
) -> User:
    """通过刷新令牌获取用户"""
    try:
        # 验证刷新令牌
        user_id = verify_token(refresh_token, "refresh")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的刷新令牌",
            )

        # 从数据库获取用户
        user = await db.get(User, user_id)
        if user is None or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在或已被禁用",
            )

        if user.is_banned_currently:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="用户账户已被封禁",
            )

        return user

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Refresh token authentication failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="刷新令牌认证失败",
        )


class WebSocketAuth:
    """WebSocket认证管理器"""

    def __init__(self):
        self.active_connections = {}

    async def authenticate_websocket(
        self,
        websocket: WebSocket,
        token: Optional[str] = None,
        db: AsyncSession = Depends(get_db)
    ) -> Optional[User]:
        """WebSocket认证"""
        if not token:
            await websocket.close(code=1008, reason="未提供认证令牌")
            return None

        try:
            # 验证令牌
            user_id = verify_token(token, "access")
            if user_id is None:
                await websocket.close(code=1008, reason="无效的认证令牌")
                return None

            # 获取用户
            user = await db.get(User, user_id)
            if user is None or not user.is_active:
                await websocket.close(code=1008, reason="用户不存在或已被禁用")
                return None

            if user.is_banned_currently:
                await websocket.close(code=1008, reason="用户账户已被封禁")
                return None

            # 记录连接
            self.active_connections[user_id] = websocket

            # 更新用户在线状态
            user.is_online = True
            await db.commit()

            logger.info("User authenticated via WebSocket", user_id=user_id)
            return user

        except Exception as e:
            logger.error("WebSocket authentication failed", error=str(e))
            await websocket.close(code=1008, reason="认证失败")
            return None

    async def disconnect_user(self, user_id: int, db: AsyncSession):
        """断开用户连接"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]

        # 更新用户离线状态
        user = await db.get(User, user_id)
        if user:
            user.is_online = False
            await db.commit()

        logger.info("User disconnected", user_id=user_id)

    def get_user_connection(self, user_id: int) -> Optional[WebSocket]:
        """获取用户连接"""
        return self.active_connections.get(user_id)

    async def send_to_user(self, user_id: int, message: dict):
        """向特定用户发送消息"""
        websocket = self.get_user_connection(user_id)
        if websocket:
            try:
                import json
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error("Failed to send WebSocket message", user_id=user_id, error=str(e))


# 全局WebSocket认证实例
websocket_auth = WebSocketAuth()


async def get_websocket_user(
    websocket: WebSocket,
    token: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """WebSocket用户认证依赖"""
    return await websocket_auth.authenticate_websocket(websocket, token, db)


def require_permissions(required_permissions: list):
    """权限检查装饰器工厂"""
    def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        # 这里可以扩展权限系统
        # 目前简单检查用户是否为管理员
        if "admin" in required_permissions:
            # 假设管理员有特殊的用户ID或角色
            if current_user.id not in [1]:  # 示例：只有ID为1的用户是管理员
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="权限不足",
                )
        return current_user
    return permission_checker


# 常用的权限检查依赖
get_admin_user = require_permissions(["admin"])


async def rate_limit_check(
    request,
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """速率限制检查"""
    # 这里可以实现基于用户的速率限制
    # 目前跳过实际实现
    pass


def get_client_ip(request) -> str:
    """获取客户端IP地址"""
    # 检查代理头
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    # 回退到客户端IP
    return request.client.host if request.client else "unknown"