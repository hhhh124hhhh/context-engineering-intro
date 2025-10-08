"""
认证路由单元测试
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer

from app.api.routes.auth import login, logout, refresh_token
from app.models.user import User, UserSession
from app.schemas.user import UserLogin, TokenRefresh


class TestAuthRoutes:
    """认证路由测试类"""

    @pytest.fixture
    def mock_db(self):
        """模拟数据库会话"""
        return AsyncMock()

    @pytest.fixture
    def mock_request(self):
        """模拟请求对象"""
        mock_request = Mock()
        mock_request.headers = {"user-agent": "test-agent"}
        return mock_request

    @pytest.fixture
    def test_user(self):
        """测试用户数据"""
        user = Mock(spec=User)
        user.id = 1
        user.username = "testuser"
        user.email = "test@example.com"
        user.hashed_password = "hashed_password"
        user.is_active = True
        user.is_banned_currently = False
        return user

    @pytest.fixture
    def user_credentials(self):
        """用户登录凭据"""
        return UserLogin(
            username_or_email="testuser",
            password="testpassword",
            remember_me=False
        )

    @pytest.fixture
    def refresh_token_data(self):
        """刷新令牌数据"""
        return TokenRefresh(refresh_token="test_refresh_token")

    @patch('app.api.routes.auth.verify_password')
    @patch('app.api.routes.auth.create_access_token')
    @patch('app.api.routes.auth.create_refresh_token')
    @patch('app.api.routes.auth.generate_session_token')
    @patch('app.api.routes.auth.get_client_ip')
    @patch('app.api.routes.auth.get_game_cache_service')
    async def test_login_success(
        self,
        mock_cache_service,
        mock_get_ip,
        mock_generate_session,
        mock_create_refresh,
        mock_create_access,
        mock_verify_password,
        mock_db,
        mock_request,
        test_user,
        user_credentials
    ):
        """测试登录成功"""
        # 设置模拟返回值
        mock_db.scalar_one_or_none.return_value = test_user
        mock_verify_password.return_value = True
        mock_create_access.return_value = "access_token"
        mock_create_refresh.return_value = "refresh_token"
        mock_generate_session.return_value = "session_token"
        mock_get_ip.return_value = "127.0.0.1"

        mock_cache_instance = AsyncMock()
        mock_cache_service.return_value = mock_cache_instance

        # 执行登录
        result = await login(user_credentials, mock_request, mock_db)

        # 验证结果
        assert result["access_token"] == "access_token"
        assert result["refresh_token"] == "refresh_token"
        assert result["token_type"] == "bearer"
        assert isinstance(result["expires_in"], timedelta)

        # 验证数据库操作
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called()

        # 验证缓存操作
        mock_cache_service.assert_called_once()
        mock_cache_instance.cache_user_session.assert_called_once()

    @patch('app.api.routes.auth.verify_password')
    async def test_login_invalid_credentials(
        self,
        mock_verify_password,
        mock_db,
        mock_request,
        test_user,
        user_credentials
    ):
        """测试登录失败 - 无效凭据"""
        # 设置模拟返回值
        mock_db.scalar_one_or_none.return_value = test_user
        mock_verify_password.return_value = False

        # 执行登录并验证异常
        with pytest.raises(HTTPException) as exc_info:
            await login(user_credentials, mock_request, mock_db)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "用户名/邮箱或密码错误" in str(exc_info.value.detail)

    async def test_login_user_not_found(
        self,
        mock_db,
        mock_request,
        user_credentials
    ):
        """测试登录失败 - 用户不存在"""
        # 设置模拟返回值
        mock_db.scalar_one_or_none.return_value = None

        # 执行登录并验证异常
        with pytest.raises(HTTPException) as exc_info:
            await login(user_credentials, mock_request, mock_db)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "用户名/邮箱或密码错误" in str(exc_info.value.detail)

    @patch('app.api.routes.auth.verify_password')
    async def test_login_user_inactive(
        self,
        mock_verify_password,
        mock_db,
        mock_request,
        test_user,
        user_credentials
    ):
        """测试登录失败 - 用户被禁用"""
        # 设置模拟返回值
        test_user.is_active = False
        mock_db.scalar_one_or_none.return_value = test_user
        mock_verify_password.return_value = True

        # 执行登录并验证异常
        with pytest.raises(HTTPException) as exc_info:
            await login(user_credentials, mock_request, mock_db)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "账户已被禁用" in str(exc_info.value.detail)

    @patch('app.api.routes.auth.verify_password')
    async def test_login_user_banned(
        self,
        mock_verify_password,
        mock_db,
        mock_request,
        test_user,
        user_credentials
    ):
        """测试登录失败 - 用户被封禁"""
        # 设置模拟返回值
        test_user.is_banned_currently = True
        test_user.ban_reason = "作弊行为"
        mock_db.scalar_one_or_none.return_value = test_user
        mock_verify_password.return_value = True

        # 执行登录并验证异常
        with pytest.raises(HTTPException) as exc_info:
            await login(user_credentials, mock_request, mock_db)

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "账户已被封禁" in str(exc_info.value.detail)

    @patch('app.api.routes.auth.verify_password')
    @patch('app.api.routes.auth.create_access_token')
    @patch('app.api.routes.auth.create_refresh_token')
    @patch('app.api.routes.auth.generate_session_token')
    @patch('app.api.routes.auth.get_client_ip')
    @patch('app.api.routes.auth.get_game_cache_service')
    async def test_login_database_error(
        self,
        mock_cache_service,
        mock_get_ip,
        mock_generate_session,
        mock_create_refresh,
        mock_create_access,
        mock_verify_password,
        mock_db,
        mock_request,
        test_user,
        user_credentials
    ):
        """测试登录时数据库错误"""
        # 设置模拟返回值
        mock_db.scalar_one_or_none.return_value = test_user
        mock_verify_password.return_value = True
        mock_create_access.return_value = "access_token"
        mock_create_refresh.return_value = "refresh_token"
        mock_generate_session.return_value = "session_token"
        mock_get_ip.return_value = "127.0.0.1"

        # 模拟数据库提交错误
        mock_db.commit.side_effect = Exception("Database error")

        # 执行登录并验证异常
        with pytest.raises(HTTPException) as exc_info:
            await login(user_credentials, mock_request, mock_db)

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "会话创建失败" in str(exc_info.value.detail)
        mock_db.rollback.assert_called_once()

    @patch('app.api.routes.auth.verify_password')
    @patch('app.api.routes.auth.create_access_token')
    @patch('app.api.routes.auth.create_refresh_token')
    @patch('app.api.routes.auth.generate_session_token')
    @patch('app.api.routes.auth.get_client_ip')
    @patch('app.api.routes.auth.get_game_cache_service')
    async def test_login_cache_error(
        self,
        mock_cache_service,
        mock_get_ip,
        mock_generate_session,
        mock_create_refresh,
        mock_create_access,
        mock_verify_password,
        mock_db,
        mock_request,
        test_user,
        user_credentials
    ):
        """测试登录时缓存错误（应该不影响登录）"""
        # 设置模拟返回值
        mock_db.scalar_one_or_none.return_value = test_user
        mock_verify_password.return_value = True
        mock_create_access.return_value = "access_token"
        mock_create_refresh.return_value = "refresh_token"
        mock_generate_session.return_value = "session_token"
        mock_get_ip.return_value = "127.0.0.1"

        # 模拟缓存服务错误
        mock_cache_instance = AsyncMock()
        mock_cache_instance.cache_user_session.side_effect = Exception("Cache error")
        mock_cache_service.return_value = mock_cache_instance

        # 执行登录（应该成功）
        result = await login(user_credentials, mock_request, mock_db)

        # 验证登录仍然成功
        assert result["access_token"] == "access_token"
        assert result["refresh_token"] == "refresh_token"

    @patch('app.api.routes.auth.get_game_cache_service')
    async def test_logout_success(self, mock_cache_service, mock_db, test_user):
        """测试登出成功"""
        # 设置模拟返回值
        mock_cache_instance = AsyncMock()
        mock_cache_service.return_value = mock_cache_instance

        # 执行登出
        result = await logout(test_user, mock_db)

        # 验证结果
        assert result["message"] == "登出成功"
        mock_db.execute.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_cache_service.assert_called_once()

    @patch('app.api.routes.auth.get_game_cache_service')
    async def test_logout_cache_error(self, mock_cache_service, mock_db, test_user):
        """测试登出时缓存错误（应该不影响登出）"""
        # 设置模拟返回值
        mock_cache_instance = AsyncMock()
        mock_cache_instance.redis.delete.side_effect = Exception("Cache error")
        mock_cache_service.return_value = mock_cache_instance

        # 执行登出（应该成功）
        result = await logout(test_user, mock_db)

        # 验证登出仍然成功
        assert result["message"] == "登出成功"
        mock_db.execute.assert_called_once()
        mock_db.commit.assert_called_once()

    async def test_logout_database_error(self, mock_db, test_user):
        """测试登出时数据库错误"""
        # 模拟数据库错误
        mock_db.execute.side_effect = Exception("Database error")

        # 执行登出并验证异常
        with pytest.raises(HTTPException) as exc_info:
            await logout(test_user, mock_db)

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "登出失败" in str(exc_info.value.detail)

    @patch('app.api.routes.auth.verify_token')
    @patch('app.api.routes.auth.create_access_token')
    @patch('app.api.routes.auth.create_refresh_token')
    async def test_refresh_token_success(
        self,
        mock_create_refresh,
        mock_create_access,
        mock_verify_token,
        mock_db,
        test_user,
        refresh_token_data
    ):
        """测试刷新令牌成功"""
        # 设置模拟返回值
        mock_verify_token.return_value = 1
        mock_db.get.return_value = test_user
        mock_create_access.return_value = "new_access_token"
        mock_create_refresh.return_value = "new_refresh_token"

        # 模拟会话查询
        mock_session = Mock()
        mock_session.refresh_token = refresh_token_data.refresh_token
        mock_session.expires_at = datetime.utcnow() + timedelta(hours=1)
        mock_scalar_result = Mock()
        mock_scalar_result.scalar_one_or_none.return_value = mock_session
        mock_db.execute.return_value = mock_scalar_result

        # 执行刷新令牌
        result = await refresh_token(refresh_token_data, mock_db)

        # 验证结果
        assert result["access_token"] == "new_access_token"
        assert result["refresh_token"] == "new_refresh_token"
        assert result["token_type"] == "bearer"

    @patch('app.api.routes.auth.verify_token')
    async def test_refresh_token_invalid_token(self, mock_verify_token, mock_db, refresh_token_data):
        """测试刷新令牌失败 - 无效令牌"""
        # 设置模拟返回值
        mock_verify_token.return_value = None

        # 执行刷新令牌并验证异常
        with pytest.raises(HTTPException) as exc_info:
            await refresh_token(refresh_token_data, mock_db)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "无效的刷新令牌" in str(exc_info.value.detail)

    @patch('app.api.routes.auth.verify_token')
    async def test_refresh_token_user_not_found(self, mock_verify_token, mock_db, refresh_token_data):
        """测试刷新令牌失败 - 用户不存在"""
        # 设置模拟返回值
        mock_verify_token.return_value = 1
        mock_db.get.return_value = None

        # 执行刷新令牌并验证异常
        with pytest.raises(HTTPException) as exc_info:
            await refresh_token(refresh_token_data, mock_db)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "用户不存在或已被禁用" in str(exc_info.value.detail)

    @patch('app.api.routes.auth.verify_token')
    async def test_refresh_token_session_expired(
        self,
        mock_verify_token,
        mock_db,
        test_user,
        refresh_token_data
    ):
        """测试刷新令牌失败 - 会话过期"""
        # 设置模拟返回值
        mock_verify_token.return_value = 1
        mock_db.get.return_value = test_user

        # 模拟过期会话
        mock_session = Mock()
        mock_session.expires_at = datetime.utcnow() - timedelta(hours=1)
        mock_scalar_result = Mock()
        mock_scalar_result.scalar_one_or_none.return_value = mock_session
        mock_db.execute.return_value = mock_scalar_result

        # 执行刷新令牌并验证异常
        with pytest.raises(HTTPException) as exc_info:
            await refresh_token(refresh_token_data, mock_db)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "会话已过期" in str(exc_info.value.detail)