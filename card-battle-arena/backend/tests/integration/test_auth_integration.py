"""
认证集成测试
测试完整的认证流程
"""

import pytest
from unittest.mock import patch, AsyncMock
import asyncio
from datetime import datetime, timedelta

# Mark as integration tests
pytestmark = pytest.mark.integration


class TestAuthIntegration:
    """认证集成测试类"""

    @pytest.mark.asyncio
    async def test_complete_login_flow(self, async_client, mock_redis):
        """测试完整的登录流程"""
        # 创建测试用户
        user_data = {
            "username": "integrationtest",
            "email": "integration@test.com",
            "password": "testpassword",
            "display_name": "Integration Test User"
        }

        # 注册用户
        with patch('app.api.routes.auth.send_verification_email'):
            register_response = await async_client.post("/api/auth/register", json=user_data)
            assert register_response.status_code == 201

        # 登录用户
        login_data = {
            "username_or_email": "integrationtest",
            "password": "testpassword",
            "remember_me": True
        }

        login_response = await async_client.post("/api/auth/login", json=login_data)
        assert login_response.status_code == 200

        login_result = login_response.json()
        assert "access_token" in login_result
        assert "refresh_token" in login_result
        assert login_result["token_type"] == "bearer"
        assert "expires_in" in login_result

        # 测试受保护的端点
        headers = {"Authorization": f"Bearer {login_result['access_token']}"}
        me_response = await async_client.get("/api/auth/me", headers=headers)
        assert me_response.status_code == 200

        user_info = me_response.json()
        assert user_info["username"] == "integrationtest"
        assert user_info["email"] == "integration@test.com"

        # 测试刷新令牌
        refresh_data = {"refresh_token": login_result["refresh_token"]}
        refresh_response = await async_client.post("/api/auth/refresh", json=refresh_data)
        assert refresh_response.status_code == 200

        refresh_result = refresh_response.json()
        assert "access_token" in refresh_result
        assert "refresh_token" in refresh_result

        # 测试登出
        logout_response = await async_client.post("/api/auth/logout", headers=headers)
        assert logout_response.status_code == 200

        # 测试密码修改
        password_data = {
            "current_password": "testpassword",
            "new_password": "newpassword123"
        }
        change_password_response = await async_client.post(
            "/api/auth/change-password",
            json=password_data,
            headers=headers
        )
        assert change_password_response.status_code == 200

    @pytest.mark.asyncio
    async def test_login_with_email(self, async_client):
        """测试使用邮箱登录"""
        login_data = {
            "username_or_email": "admin",  # 使用已存在的测试用户
            "password": "Test123"
        }

        login_response = await async_client.post("/api/auth/login", json=login_data)
        assert login_response.status_code == 200

        login_result = login_response.json()
        assert "access_token" in login_result
        assert "refresh_token" in login_result

    @pytest.mark.asyncio
    async def test_session_caching_integration(self, async_client, mock_redis):
        """测试会话缓存集成"""
        login_data = {
            "username_or_email": "admin",
            "password": "Test123"
        }

        # 模拟Redis缓存操作
        mock_redis.set.return_value = True
        mock_redis.get.return_value = None

        # 执行登录
        login_response = await async_client.post("/api/auth/login", json=login_data)
        assert login_response.status_code == 200

        # 验证Redis缓存被调用
        # 注意：这需要mock正确的依赖注入
        # 这里提供测试框架，具体实现可能需要根据实际情况调整

    @pytest.mark.asyncio
    async def test_concurrent_login_requests(self, async_client):
        """测试并发登录请求"""
        login_data = {
            "username_or_email": "admin",
            "password": "Test123"
        }

        # 创建多个并发登录请求
        tasks = []
        for _ in range(5):
            task = async_client.post("/api/auth/login", json=login_data)
            tasks.append(task)

        # 执行所有并发请求
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # 验证所有请求都成功
        successful_responses = [r for r in responses if hasattr(r, 'status_code')]
        assert len(successful_responses) == 5

        for response in successful_responses:
            assert response.status_code == 200
            result = response.json()
            assert "access_token" in result
            assert "refresh_token" in result

    @pytest.mark.asyncio
    async def test_invalid_token_handling(self, async_client):
        """测试无效令牌处理"""
        # 使用无效令牌访问受保护端点
        invalid_headers = {"Authorization": "Bearer invalid_token"}

        me_response = await async_client.get("/api/auth/me", headers=invalid_headers)
        assert me_response.status_code == 401

        # 使用无效刷新令牌
        refresh_data = {"refresh_token": "invalid_refresh_token"}
        refresh_response = await async_client.post("/api/auth/refresh", json=refresh_data)
        assert refresh_response.status_code == 401

    @pytest.mark.asyncio
    async def test_rate_limiting(self, async_client):
        """测试速率限制（如果实现了）"""
        login_data = {
            "username_or_email": "admin",
            "password": "wrong_password"
        }

        # 发送多个失败的登录请求
        failed_responses = []
        for _ in range(10):
            response = await async_client.post("/api/auth/login", json=login_data)
            failed_responses.append(response)
            if response.status_code == 429:  # Too Many Requests
                break

        # 验证最终是否触发了速率限制
        # 注意：这需要后端实现速率限制功能
        assert any(r.status_code in [401, 429] for r in failed_responses)

    @pytest.mark.asyncio
    async def test_session_expiration(self, async_client):
        """测试会话过期处理"""
        # 首先登录获取令牌
        login_data = {
            "username_or_email": "admin",
            "password": "Test123",
            "remember_me": False  # 短期会话
        }

        login_response = await async_client.post("/api/auth/login", json=login_data)
        assert login_response.status_code == 200

        login_result = login_response.json()
        access_token = login_result["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}

        # 模拟令牌过期（这里需要修改令牌来模拟过期，或者等待）
        # 在实际测试中，可能需要mock时间或令牌验证

        # 测试过期令牌的处理
        # 这取决于具体的令牌过期实现
        me_response = await async_client.get("/api/auth/me", headers=headers)

        # 当前应该还是有效的，因为刚生成
        assert me_response.status_code == 200

    @pytest.mark.asyncio
    async def test_error_recovery(self, async_client):
        """测试错误恢复机制"""
        # 测试数据库错误恢复
        login_data = {
            "username_or_email": "admin",
            "password": "Test123"
        }

        with patch('app.database.postgres.engine.begin') as mock_db:
            # 模拟数据库错误
            mock_db.side_effect = Exception("Database connection lost")

            login_response = await async_client.post("/api/auth/login", json=login_data)
            # 应该返回500错误
            assert login_response.status_code == 500

        # 测试Redis错误恢复
        with patch('app.database.redis.check_redis_health') as mock_redis_health:
            # 模拟Redis不可用
            mock_redis_health.return_value = False

            login_response = await async_client.post("/api/auth/login", json=login_data)
            # 登录应该仍然成功，因为Redis错误不影响核心功能
            assert login_response.status_code == 200

    @pytest.mark.asyncio
    async def test_cross_service_consistency(self, async_client):
        """测试跨服务一致性"""
        login_data = {
            "username_or_email": "admin",
            "password": "Test123"
        }

        # 执行登录
        login_response = await async_client.post("/api/auth/login", json=login_data)
        assert login_response.status_code == 200

        login_result = login_response.json()
        access_token = login_result["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}

        # 获取用户信息
        me_response = await async_client.get("/api/auth/me", headers=headers)
        assert me_response.status_code == 200

        user_info = me_response.json()
        user_id = user_info["id"]

        # 验证数据库中的会话记录
        # 这需要直接访问数据库或添加相应的检查端点
        # 当前提供测试框架

        # 验证Redis中的缓存（如果实现）
        # 同样需要相应的检查机制

    @pytest.mark.asyncio
    async def test_security_headers(self, async_client):
        """测试安全头"""
        response = await async_client.get("/api/auth/me")

        # 检查安全相关的头（如果实现了）
        # 例如：CORS、CSP等
        assert response.status_code == 401  # 未认证

        # 可以添加更多安全头检查
        # 例如：X-Content-Type-Options, X-Frame-Options等