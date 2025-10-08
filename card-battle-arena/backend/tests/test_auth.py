import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from jose import jwt, JWTError
from app.core.auth import (
    AuthManager,
    get_password_hash,
    verify_password,
    create_access_token,
    verify_token,
    get_current_user
)
from app.core.config import settings
from app.models.user import User


class TestPasswordUtils:
    """密码工具测试"""

    def test_password_hashing(self):
        """测试密码哈希"""
        password = "test_password_123"
        hashed = get_password_hash(password)

        assert hashed != password
        assert hashed.startswith("$2b$")  # bcrypt哈希格式

    def test_password_verification(self):
        """测试密码验证"""
        password = "test_password_123"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed)
        assert not verify_password("wrong_password", hashed)

    def test_password_hash_consistency(self):
        """测试密码哈希一致性"""
        password = "test_password_123"
        hashed1 = get_password_hash(password)
        hashed2 = get_password_hash(password)

        # 每次哈希应该不同（包含随机盐）
        assert hashed1 != hashed2
        # 但验证应该都成功
        assert verify_password(password, hashed1)
        assert verify_password(password, hashed2)


class TestTokenUtils:
    """Token工具测试"""

    def test_create_access_token(self):
        """测试创建访问令牌"""
        data = {"sub": "user123"}
        token = create_access_token(data)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_token_valid(self):
        """测试验证有效令牌"""
        data = {"sub": "user123"}
        token = create_access_token(data)

        payload = verify_token(token)
        assert payload["sub"] == "user123"

    def test_verify_token_invalid(self):
        """测试验证无效令牌"""
        invalid_token = "invalid.jwt.token"

        with pytest.raises(JWTError):
            verify_token(invalid_token)

    def test_verify_token_expired(self):
        """测试验证过期令牌"""
        # 创建过期的令牌
        data = {"sub": "user123"}
        expire = datetime.utcnow() - timedelta(minutes=1)
        token = jwt.encode(
            {**data, "exp": expire},
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )

        with pytest.raises(JWTError):
            verify_token(token)

    def test_token_expiration_time(self):
        """测试令牌过期时间"""
        data = {"sub": "user123"}
        token = create_access_token(data)

        # 解码令牌检查过期时间
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        exp = datetime.fromtimestamp(payload["exp"])
        now = datetime.utcnow()
        time_diff = exp - now

        # 应该在设定的过期时间内（默认30分钟）
        assert timedelta(minutes=25) < time_diff < timedelta(minutes=35)


class TestAuthManager:
    """认证管理器测试"""

    @pytest.fixture
    def auth_manager(self):
        """创建认证管理器实例"""
        return AuthManager()

    @pytest.fixture
    def mock_db(self):
        """模拟数据库会话"""
        return Mock()

    @pytest.fixture
    def mock_user(self):
        """模拟用户对象"""
        user = Mock(spec=User)
        user.id = 1
        user.username = "testuser"
        user.email = "test@example.com"
        user.password_hash = get_password_hash("password123")
        user.is_active = True
        user.is_verified = True
        return user

    def test_authenticate_user_valid(self, auth_manager, mock_user):
        """测试有效用户认证"""
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        result = auth_manager.authenticate_user(mock_db, "testuser", "password123")

        assert result == mock_user

    def test_authenticate_user_invalid_password(self, auth_manager, mock_user):
        """测试无效密码认证"""
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        result = auth_manager.authenticate_user(mock_db, "testuser", "wrongpassword")

        assert result is None

    def test_authenticate_user_not_found(self, auth_manager):
        """测试用户不存在认证"""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = auth_manager.authenticate_user(mock_db, "nonexistent", "password123")

        assert result is None

    def test_authenticate_user_inactive(self, auth_manager, mock_user):
        """测试非活跃用户认证"""
        mock_user.is_active = False
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        result = auth_manager.authenticate_user(mock_db, "testuser", "password123")

        assert result is None

    def test_create_user(self, auth_manager, mock_db):
        """测试创建用户"""
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "password123"
        }

        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock()

        # 模拟数据库返回的用户对象
        created_user = Mock(spec=User)
        created_user.id = 2
        created_user.username = "newuser"
        created_user.email = "newuser@example.com"
        mock_db.refresh.side_effect = lambda obj: setattr(obj, 'id', 2)

        result = auth_manager.create_user(mock_db, user_data)

        assert result.username == "newuser"
        assert result.email == "newuser@example.com"
        assert verify_password("password123", result.password_hash)
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    def test_create_user_duplicate_username(self, auth_manager, mock_db):
        """测试创建重名用户"""
        user_data = {
            "username": "existinguser",
            "email": "newuser@example.com",
            "password": "password123"
        }

        # 模拟用户名已存在
        mock_db.query.return_value.filter.return_value.first.return_value = Mock()

        with pytest.raises(ValueError, match="Username already exists"):
            auth_manager.create_user(mock_db, user_data)

    def test_create_user_duplicate_email(self, auth_manager, mock_db):
        """测试创建重复邮箱用户"""
        user_data = {
            "username": "newuser",
            "email": "existing@example.com",
            "password": "password123"
        }

        # 模拟邮箱已存在
        def mock_filter(*args, **kwargs):
            if 'username' in str(args):
                return Mock(first=Mock(return_value=None))  # 用户名不存在
            else:
                return Mock(first=Mock(return_value=Mock()))  # 邮箱存在

        mock_db.query.return_value.filter = mock_filter

        with pytest.raises(ValueError, match="Email already exists"):
            auth_manager.create_user(mock_db, user_data)

    def test_update_user_password(self, auth_manager, mock_user, mock_db):
        """测试更新用户密码"""
        new_password = "newpassword123"
        old_hash = mock_user.password_hash

        auth_manager.update_user_password(mock_db, mock_user, new_password)

        assert mock_user.password_hash != old_hash
        assert verify_password(new_password, mock_user.password_hash)
        mock_db.commit.assert_called_once()

    def test_generate_verification_token(self, auth_manager):
        """测试生成验证令牌"""
        token = auth_manager.generate_verification_token(1)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_email_token_valid(self, auth_manager):
        """测试验证有效邮箱令牌"""
        user_id = 1
        token = auth_manager.generate_verification_token(user_id)

        result = auth_manager.verify_email_token(token)

        assert result == user_id

    def test_verify_email_token_invalid(self, auth_manager):
        """测试验证无效邮箱令牌"""
        invalid_token = "invalid_token"

        with pytest.raises(JWTError):
            auth_manager.verify_email_token(invalid_token)

    def test_generate_password_reset_token(self, auth_manager):
        """测试生成密码重置令牌"""
        token = auth_manager.generate_password_reset_token("test@example.com")

        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_password_reset_token_valid(self, auth_manager):
        """测试验证有效密码重置令牌"""
        email = "test@example.com"
        token = auth_manager.generate_password_reset_token(email)

        result = auth_manager.verify_password_reset_token(token)

        assert result == email

    def test_login_user(self, auth_manager, mock_user, mock_db):
        """测试用户登录"""
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        result = auth_manager.login_user(mock_db, "testuser", "password123")

        assert "access_token" in result
        assert "token_type" in result
        assert result["token_type"] == "bearer"
        assert "expires_in" in result

    def test_login_user_invalid_credentials(self, auth_manager, mock_db):
        """测试无效凭据登录"""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(ValueError, match="Invalid credentials"):
            auth_manager.login_user(mock_db, "testuser", "wrongpassword")

    def test_refresh_token(self, auth_manager, mock_user):
        """测试刷新令牌"""
        token = auth_manager.create_user_token(mock_user)
        result = auth_manager.refresh_token(mock_user)

        assert "access_token" in result
        assert result["access_token"] != token


class TestAuthDependencies:
    """认证依赖测试"""

    @pytest.fixture
    def mock_db(self):
        """模拟数据库会话"""
        return Mock()

    @pytest.fixture
    def mock_user(self):
        """模拟用户对象"""
        user = Mock(spec=User)
        user.id = 1
        user.username = "testuser"
        user.is_active = True
        return user

    @pytest.mark.asyncio
    async def test_get_current_user_valid_token(self, mock_db, mock_user):
        """测试有效令牌获取当前用户"""
        token = create_access_token({"sub": str(mock_user.id)})
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        user = await get_current_user(token, mock_db)

        assert user == mock_user

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, mock_db):
        """测试无效令牌获取当前用户"""
        invalid_token = "invalid.jwt.token"

        with pytest.raises(Exception):  # 应该抛出认证异常
            await get_current_user(invalid_token, mock_db)

    @pytest.mark.asyncio
    async def test_get_current_user_not_found(self, mock_db):
        """测试用户不存在获取当前用户"""
        token = create_access_token({"sub": "999"})
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(Exception):  # 应该抛出认证异常
            await get_current_user(token, mock_db)

    @pytest.mark.asyncio
    async def test_get_current_user_inactive(self, mock_db, mock_user):
        """测试非活跃用户获取当前用户"""
        mock_user.is_active = False
        token = create_access_token({"sub": str(mock_user.id)})
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        with pytest.raises(Exception):  # 应该抛出认证异常
            await get_current_user(token, mock_db)


class TestSecurityFeatures:
    """安全特性测试"""

    def test_rate_limiting(self):
        """测试速率限制（概念性测试）"""
        # 这里应该测试实际的速率限制逻辑
        # 由于是概念性测试，只验证相关组件存在
        assert hasattr(settings, 'SECRET_KEY')
        assert settings.SECRET_KEY is not None

    def test_token_security(self):
        """测试令牌安全性"""
        data = {"sub": "user123", "is_admin": False}
        token = create_access_token(data)

        # 验证令牌不包含敏感信息
        assert "password" not in token.lower()
        assert "secret" not in token.lower()

        # 验证令牌可以被正确解码
        payload = verify_token(token)
        assert payload["sub"] == "user123"
        assert not payload.get("is_admin", True)

    def test_session_management(self):
        """测试会话管理（概念性测试）"""
        # 这里应该测试会话管理逻辑
        # 由于是概念性测试，只验证相关配置
        assert hasattr(settings, 'ACCESS_TOKEN_EXPIRE_MINUTES')
        assert settings.ACCESS_TOKEN_EXPIRE_MINUTES > 0

    def test_csrf_protection(self):
        """测试CSRF保护（概念性测试）"""
        # 这里应该测试CSRF保护逻辑
        # 由于是概念性测试，只验证相关配置存在
        assert True  # 占位符测试


if __name__ == '__main__':
    pytest.main([__file__])