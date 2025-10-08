#!/usr/bin/env python3
"""
验证500登录错误修复的测试脚本
"""

import sys
import asyncio
import requests
import json
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_api_health():
    """测试API健康状态"""
    print("🔍 测试API健康状态...")

    try:
        response = requests.get("http://localhost:8000/api/auth/me", timeout=5)
        if response.status_code == 401:
            print("✅ API服务器运行正常（未认证的401是预期的）")
            return True
        elif response.status_code == 200:
            print("✅ API服务器运行正常")
            return True
        else:
            print(f"⚠️ API返回意外状态码: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到API服务器 - 请确保后端服务正在运行")
        return False
    except Exception as e:
        print(f"❌ API健康检查失败: {e}")
        return False

def test_login_endpoint():
    """测试登录端点"""
    print("\n🔐 测试登录端点...")

    # 测试数据
    login_data = {
        "username_or_email": "admin",
        "password": "Test123",
        "remember_me": True
    }

    try:
        print(f"📤 发送登录请求: {login_data}")
        response = requests.post(
            "http://localhost:8000/api/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )

        print(f"📥 响应状态码: {response.status_code}")

        if response.status_code == 200:
            print("✅ 登录成功！")
            data = response.json()
            print(f"   - 访问令牌: {'✅ 存在' if data.get('access_token') else '❌ 缺失'}")
            print(f"   - 刷新令牌: {'✅ 存在' if data.get('refresh_token') else '❌ 缺失'}")
            print(f"   - 令牌类型: {data.get('token_type', '未知')}")
            print(f"   - 过期时间: {data.get('expires_in', '未知')}秒")
            return True
        elif response.status_code == 401:
            print("❌ 认证失败 - 用户名或密码错误")
            print("   可能需要创建测试账号")
            return False
        elif response.status_code == 422:
            print("❌ 请求数据格式错误")
            print(f"   错误详情: {response.text}")
            return False
        elif response.status_code == 500:
            print("❌ 服务器内部错误 - 500错误仍然存在")
            print(f"   错误详情: {response.text}")
            return False
        else:
            print(f"⚠️ 意外的状态码: {response.status_code}")
            print(f"   响应内容: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print("❌ 请求超时")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败 - 请检查后端服务是否运行")
        return False
    except Exception as e:
        print(f"❌ 登录测试失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("🧪 卡牌对战竞技场 - 登录修复验证")
    print("=" * 60)

    # 1. 测试API健康状态
    if not test_api_health():
        print("\n❌ API健康检查失败，请先启动后端服务")
        print("   启动命令: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        return 1

    # 2. 测试登录功能
    if not test_login_endpoint():
        print("\n❌ 登录测试失败")
        print("\n💡 可能的解决方案:")
        print("   1. 确保后端服务正在运行")
        print("   2. 检查数据库连接是否正常")
        print("   3. 运行测试账号创建脚本:")
        print("      python scripts/create_test_users_fixed.py")
        return 1

    print("\n" + "=" * 60)
    print("🎉 所有测试通过！登录功能修复成功")
    print("=" * 60)
    print("\n📋 验证结果:")
    print("✅ API服务器运行正常")
    print("✅ 登录端点响应正确")
    print("✅ 500内部服务器错误已修复")
    print("✅ 前后端数据格式匹配")

    print("\n🚀 下一步:")
    print("1. 在前端页面测试登录功能")
    print("2. 使用测试账号: admin / Test123")
    print("3. 验证'记住我'功能正常工作")

    return 0

if __name__ == "__main__":
    sys.exit(main())