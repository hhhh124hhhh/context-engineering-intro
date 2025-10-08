from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import Optional
import structlog
from datetime import datetime, timedelta

from app.models.user import User, UserSession, UserAchievement
from app.models.deck import Deck

from app.database.postgres import get_db
from app.models.user import User, UserSession
from app.schemas.user import (
    UserCreate, UserLogin, UserResponse, Token, TokenRefresh,
    PasswordResetRequest, PasswordReset, EmailVerificationRequest, EmailVerification,
    UserUpdate, UserChangePassword, UserProfile, UserStats
)
from app.api.dependencies import get_current_user, get_current_verified_user, get_client_ip
from app.core.security import (
    get_password_hash, verify_password, create_access_token, create_refresh_token,
    verify_token, generate_password_reset_token, verify_password_reset_token,
    generate_verification_token, verify_email_verification_token,
    generate_session_token
)
from app.core.config import settings
from app.database.redis import get_game_cache_service

logger = structlog.get_logger()

router = APIRouter()
security = HTTPBearer()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """用户注册"""
    try:
        # 检查用户名是否已存在
        existing_user = await db.execute(
            select(User).where(User.username == user_data.username)
        )
        if existing_user.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )

        # 检查邮箱是否已存在
        existing_email = await db.execute(
            select(User).where(User.email == user_data.email)
        )
        if existing_email.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被注册"
            )

        # 创建新用户
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            display_name=user_data.display_name or user_data.username,
            bio=user_data.bio,
            country=user_data.country
        )

        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)

        # 发送邮箱验证邮件
        if settings.ENABLE_PASSWORD_RESET:
            verification_token = generate_verification_token(user_data.email)
            background_tasks.add_task(
                send_verification_email,
                user_data.email,
                verification_token,
                get_client_ip(request)
            )

        logger.info("User registered successfully", user_id=db_user.id, username=db_user.username)
        return db_user

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Registration failed", error=str(e))
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="注册失败，请稍后重试"
        )


@router.post("/login", response_model=Token)
async def login(
    user_credentials: UserLogin,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """用户登录"""
    try:
        # 查找用户（支持用户名或邮箱登录）
        if "@" in user_credentials.username_or_email:
            user = await db.execute(
                select(User).where(User.email == user_credentials.username_or_email)
            )
        else:
            user = await db.execute(
                select(User).where(User.username == user_credentials.username_or_email)
            )

        db_user = user.scalar_one_or_none()
        if not db_user or not verify_password(user_credentials.password, db_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名/邮箱或密码错误",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 检查用户状态
        if not db_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="账户已被禁用",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if db_user.is_banned_currently:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"账户已被封禁，原因：{db_user.ban_reason or '违反社区规范'}",
            )

        # 创建访问令牌
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        if user_credentials.remember_me:
            access_token_expires = timedelta(days=7)  # 7天

        access_token = create_access_token(
            subject=db_user.id,
            expires_delta=access_token_expires
        )
        refresh_token = create_refresh_token(subject=db_user.id)

        # 创建会话记录
        session_expires_seconds = 7 * 24 * 60 * 60 if user_credentials.remember_me else 24 * 60 * 60
        session = UserSession(
            user_id=db_user.id,
            session_token=generate_session_token(),
            refresh_token=refresh_token,
            expires_at=datetime.utcnow() + timedelta(seconds=session_expires_seconds),
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("user-agent")
        )
        db.add(session)
        try:
            await db.commit()
        except Exception as db_error:
            logger.error("Failed to commit session to database", user_id=db_user.id, error=str(db_error))
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="会话创建失败，请稍后重试"
            )

        # 缓存用户会话（非关键操作，失败不影响登录）
        try:
            cache_service = await get_game_cache_service()
            cache_service.cache_user_session(db_user.id, {
                "session_id": session.id,
                "ip_address": session.ip_address,
                "login_time": session.created_at.isoformat()
            })
        except Exception as e:
            # 缓存失败不影响登录流程，只记录日志
            logger.warning("Failed to cache user session", user_id=db_user.id, error=str(e))

        logger.info("User logged in successfully", user_id=db_user.id, ip_address=get_client_ip(request))

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": access_token_expires.total_seconds()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Login failed", error=str(e), exc_info=True)
        # 不暴露具体错误信息给客户端，防止信息泄露
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登录失败，请稍后重试"
        )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    token_data: TokenRefresh,
    db: AsyncSession = Depends(get_db)
):
    """刷新访问令牌"""
    try:
        # 验证刷新令牌
        user_id = verify_token(token_data.refresh_token, "refresh")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的刷新令牌"
            )

        # 查找用户
        user = await db.get(User, user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在或已被禁用"
            )

        # 检查会话是否存在且有效
        session = await db.execute(
            select(UserSession).where(
                UserSession.user_id == user_id,
                UserSession.refresh_token == token_data.refresh_token,
                UserSession.is_active == True
            )
        )
        db_session = session.scalar_one_or_none()

        if not db_session or db_session.expires_at < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="会话已过期，请重新登录"
            )

        # 创建新的访问令牌
        access_token = create_access_token(subject=user_id)
        new_refresh_token = create_refresh_token(subject=user_id)

        # 更新会话
        db_session.refresh_token = new_refresh_token
        db_session.last_used_at = datetime.utcnow()
        await db.commit()

        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Token refresh failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="令牌刷新失败"
        )


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """用户登出"""
    try:
        # 禁用用户的所有会话
        await db.execute(
            update(UserSession).where(
                UserSession.user_id == current_user.id,
                UserSession.is_active == True
            ).values(is_active=False)
        )
        await db.commit()

        # 清除缓存（非关键操作，失败不影响登出）
        try:
            cache_service = await get_game_cache_service()
            cache_service.redis.delete(f"session:{current_user.id}")
        except Exception as e:
            # 缓存清理失败不影响登出流程，只记录日志
            logger.warning("Failed to clear user session cache", user_id=current_user.id, error=str(e))

        logger.info("User logged out successfully", user_id=current_user.id)
        return {"message": "登出成功"}

    except Exception as e:
        logger.error("Logout failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登出失败"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """获取当前用户信息"""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新当前用户信息"""
    try:
        # 更新用户信息
        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(current_user, field, value)

        await db.commit()
        await db.refresh(current_user)

        logger.info("User profile updated", user_id=current_user.id)
        return current_user

    except Exception as e:
        logger.error("Profile update failed", error=str(e))
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新失败，请稍后重试"
        )


@router.post("/change-password")
async def change_password(
    password_data: UserChangePassword,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """修改密码"""
    try:
        # 验证当前密码
        if not verify_password(password_data.current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="当前密码错误"
            )

        # 更新密码
        current_user.hashed_password = get_password_hash(password_data.new_password)
        await db.commit()

        # 禁用所有其他会话（强制重新登录）
        await db.execute(
            update(UserSession).where(
                UserSession.user_id == current_user.id,
                UserSession.is_active == True
            ).values(is_active=False)
        )
        await db.commit()

        logger.info("Password changed successfully", user_id=current_user.id)
        return {"message": "密码修改成功，请重新登录"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Password change failed", error=str(e))
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="密码修改失败"
        )


@router.post("/request-password-reset")
async def request_password_reset(
    request_data: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """请求密码重置"""
    try:
        # 查找用户
        user = await db.execute(
            select(User).where(User.email == request_data.email)
        )
        db_user = user.scalar_one_or_none()

        if not db_user:
            # 为了安全，即使用户不存在也返回成功消息
            return {"message": "如果邮箱存在，重置链接已发送"}

        # 生成重置令牌
        reset_token = generate_password_reset_token(db_user.email)

        # 发送重置邮件
        background_tasks.add_task(
            send_password_reset_email,
            db_user.email,
            reset_token
        )

        logger.info("Password reset requested", email=request_data.email)
        return {"message": "重置链接已发送到您的邮箱"}

    except Exception as e:
        logger.error("Password reset request failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="请求失败，请稍后重试"
        )


@router.post("/reset-password")
async def reset_password(
    reset_data: PasswordReset,
    db: AsyncSession = Depends(get_db)
):
    """重置密码"""
    try:
        # 验证重置令牌
        email = verify_password_reset_token(reset_data.token)
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效或已过期的重置令牌"
            )

        # 查找用户
        user = await db.execute(
            select(User).where(User.email == email)
        )
        db_user = user.scalar_one_or_none()

        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )

        # 更新密码
        db_user.hashed_password = get_password_hash(reset_data.new_password)
        await db.commit()

        logger.info("Password reset successfully", email=email)
        return {"message": "密码重置成功"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Password reset failed", error=str(e))
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="密码重置失败"
        )


@router.post("/request-email-verification")
async def request_email_verification(
    request_data: EmailVerificationRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """请求邮箱验证"""
    try:
        # 查找用户
        user = await db.execute(
            select(User).where(User.email == request_data.email)
        )
        db_user = user.scalar_one_or_none()

        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )

        if db_user.is_verified:
            return {"message": "邮箱已验证"}

        # 生成验证令牌
        verification_token = generate_verification_token(db_user.email)

        # 发送验证邮件
        background_tasks.add_task(
            send_verification_email,
            db_user.email,
            verification_token
        )

        logger.info("Email verification requested", email=request_data.email)
        return {"message": "验证链接已发送到您的邮箱"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Email verification request failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="请求失败，请稍后重试"
        )


@router.post("/verify-email")
async def verify_email(
    verification_data: EmailVerification,
    db: AsyncSession = Depends(get_db)
):
    """验证邮箱"""
    try:
        # 验证令牌
        email = verify_email_verification_token(verification_data.token)
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效或已过期的验证令牌"
            )

        # 查找用户
        user = await db.execute(
            select(User).where(User.email == email)
        )
        db_user = user.scalar_one_or_none()

        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )

        # 更新验证状态
        db_user.is_verified = True
        await db.commit()

        logger.info("Email verified successfully", email=email)
        return {"message": "邮箱验证成功"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Email verification failed", error=str(e))
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="邮箱验证失败"
        )


@router.get("/profile", response_model=UserProfile)
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取用户完整档案"""
    try:
        # 获取用户统计
        stats = UserStats(
            games_played=current_user.games_played,
            games_won=current_user.games_won,
            games_lost=current_user.games_lost,
            win_rate=current_user.win_rate,
            current_win_streak=current_user.win_streak,
            best_win_streak=current_user.best_win_streak
        )

        # 获取成就
        achievements = await db.execute(
            select(UserAchievement).where(UserAchievement.user_id == current_user.id)
        )
        achievement_list = achievements.scalars().all()

        # 获取最近的卡组
        recent_decks = await db.execute(
            select(Deck).where(Deck.user_id == current_user.id)
            .order_by(Deck.last_used_at.desc())
            .limit(5)
        )
        deck_list = recent_decks.scalars().all()

        return UserProfile(
            user=current_user,
            win_rate=stats.win_rate,
            recent_games=[],  # 可以添加最近游戏记录
            achievements=[achievement.__dict__ for achievement in achievement_list],
            favorite_decks=[deck.__dict__ for deck in deck_list]
        )

    except Exception as e:
        logger.error("Profile fetch failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取档案失败"
        )


# 邮件发送函数（占位符，需要实际实现）
async def send_verification_email(email: str, token: str, ip_address: Optional[str] = None):
    """发送邮箱验证邮件"""
    # 这里应该实现实际的邮件发送逻辑
    logger.info("Verification email sent", email=email, token=token[:10] + "...", ip_address=ip_address)


async def send_password_reset_email(email: str, token: str):
    """发送密码重置邮件"""
    # 这里应该实现实际的邮件发送逻辑
    logger.info("Password reset email sent", email=email, token=token[:10] + "...")