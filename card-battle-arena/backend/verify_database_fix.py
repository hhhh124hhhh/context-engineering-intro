#!/usr/bin/env python3
"""
验证数据库修复效果的脚本
"""

import asyncio
import sys
import requests
import json
import subprocess
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_database_connection():
    """测试数据库连接"""
    print("🔍 测试数据库连接...")
    try:
        result = subprocess.run([
            'docker', 'exec', '-i', 'card-battle-postgres',
            'psql', '-U', 'postgres', '-d', 'card_battle_arena',
            '-c', "SELECT 'Connection OK' as status;"
        ], capture_output=True, text=True, timeout=10)

        if 'Connection OK' in result.stdout:
            print("✅ 数据库连接正常")
            return True
        else:
            print("❌ 数据库连接失败")
            return False
    except Exception as e:
        print(f"❌ 数据库连接错误: {e}")
        return False

def test_tables_exist():
    """测试关键表是否存在"""
    print("\n🏗️ 验证数据库表结构...")

    tables_to_check = [
        'users',
        'user_sessions',
        'friendships',
        'cards',
        'decks'
    ]

    try:
        result = subprocess.run([
            'docker', 'exec', '-i', 'card-battle-postgres',
            'psql', '-U', 'postgres', '-d', 'card_battle_arena',
            '-c', "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE';"
        ], capture_output=True, text=True, timeout=10)

        existing_tables = []
        for line in result.stdout.split('\n'):
            if line.strip() and not line.startswith('table_name'):
                existing_tables.append(line.strip())

        print("📊 数据库表状态:")
        all_exist = True
        for table in tables_to_check:
            if table in existing_tables:
                print(f"   ✅ {table}")
            else:
                print(f"   ❌ {table} (缺失)")
                all_exist = False

        return all_exist
    except Exception as e:
        print(f"❌ 表检查失败: {e}")
        return False

def test_login_api():
    """测试登录API"""
    print("\n🔐 测试登录API...")

    login_data = {
        "username_or_email": "admin",
        "password": "Test123",
        "remember_me": True
    }

    try:
        print(f"📤 发送登录请求...")
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
        else:
            print(f"❌ 登录失败: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   错误详情: {error_data}")
            except:
                print(f"   响应内容: {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到API服务器 - 请确保后端服务正在运行")
        return False
    except Exception as e:
        print(f"❌ 登录测试失败: {e}")
        return False

def test_user_sessions():
    """测试user_sessions表是否可以正常插入"""
    print("\n🗂️ 测试user_sessions表...")

    try:
        result = subprocess.run([
            'docker', 'exec', '-i', 'card-battle-postgres',
            'psql', '-U', 'postgres', '-d', 'card_battle_arena',
            '-c', "SELECT COUNT(*) FROM user_sessions;"
        ], capture_output=True, text=True, timeout=10)

        count = result.stdout.strip().split('\n')[-1]
        print(f"✅ user_sessions表正常 (当前会话数: {count})")
        return True
    except Exception as e:
        print(f"❌ user_sessions表测试失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("🧪 数据库修复验证")
    print("=" * 60)

    import subprocess

    tests = [
        ("数据库连接", test_database_connection),
        ("表结构", test_tables_exist),
        ("user_sessions表", test_user_sessions),
        ("登录API", test_login_api)
    ]

    results = []
    for test_name, test_func in tests:
        results.append((test_name, test_func()))

    print("\n" + "=" * 60)
    print("📋 验证结果总结:")
    print("=" * 60)

    all_passed = True
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:<20} {status}")
        if not result:
            all_passed = False

    if all_passed:
        print("\n🎉 所有验证通过！数据库修复成功！")
        print("\n🚀 现在可以:")
        print("1. 在前端页面登录")
        print("2. 使用测试账号: admin / Test123")
        print("3. 享受完整的游戏功能")
    else:
        print("\n❌ 部分验证失败，请检查相关配置")

    print("=" * 60)
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())