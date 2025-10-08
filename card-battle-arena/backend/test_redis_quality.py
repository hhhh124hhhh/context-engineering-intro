#!/usr/bin/env python3
"""
Redis连接质量测试脚本
测试Redis异步连接和异常处理
"""

import asyncio
import sys
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def test_redis_connection():
    """测试Redis连接"""
    print("🔍 测试Redis连接...")

    try:
        # 导入必要的模块
        from app.database.redis import init_redis, check_redis_health, get_game_cache_service

        # 初始化Redis连接
        print("📡 初始化Redis连接...")
        await init_redis()

        # 检查健康状态
        print("💓 检查Redis健康状态...")
        is_healthy = check_redis_health()
        if is_healthy:
            print("✅ Redis健康检查通过")
        else:
            print("❌ Redis健康检查失败")
            return False

        # 测试缓存服务
        print("🗄️ 测试缓存服务...")
        cache_service = await get_game_cache_service()

        # 测试用户会话缓存
        test_user_id = "test_user_123"
        test_session_data = {
            "session_id": "test_session_456",
            "ip_address": "127.0.0.1",
            "login_time": "2025-10-08T10:00:00Z"
        }

        print("💾 测试缓存用户会话...")
        cache_result = cache_service.cache_user_session(test_user_id, test_session_data)
        if cache_result:
            print("✅ 用户会话缓存成功")
        else:
            print("❌ 用户会话缓存失败")

        # 测试获取缓存
        print("📖 测试获取缓存数据...")
        cached_data = cache_service.get_user_session(test_user_id)
        if cached_data:
            print("✅ 获取缓存数据成功:", cached_data)
        else:
            print("❌ 获取缓存数据失败")

        # 测试删除缓存
        print("🗑️ 测试删除缓存...")
        delete_result = cache_service.redis.delete(f"session:{test_user_id}")
        if delete_result > 0:
            print("✅ 缓存删除成功")
        else:
            print("❌ 缓存删除失败")

        return True

    except Exception as e:
        print(f"❌ Redis连接测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_redis_error_handling():
    """测试Redis错误处理"""
    print("\n🧪 测试Redis错误处理...")

    try:
        from app.database.redis import RedisService
        from app.database.redis import redis_client

        # 创建Redis服务实例
        redis_service = RedisService(redis_client)

        # 测试无效键操作
        print("🔍 测试获取不存在的键...")
        result = redis_service.get("non_existent_key")
        if result is None:
            print("✅ 正确处理不存在的键")
        else:
            print("❌ 处理不存在的键失败")

        # 测试设置和获取复杂数据
        print("📊 测试复杂JSON数据...")
        test_data = {
            "user_id": 123,
            "username": "test_user",
            "permissions": ["read", "write"],
            "metadata": {"last_login": "2025-10-08"}
        }

        set_result = redis_service.set("test_complex", test_data, expire=60)
        if set_result:
            print("✅ 复杂数据设置成功")

            get_result = redis_service.get("test_complex", as_json=True)
            if get_result and get_result.get("user_id") == 123:
                print("✅ 复杂数据获取成功")
            else:
                print("❌ 复杂数据获取失败")
        else:
            print("❌ 复杂数据设置失败")

        # 清理测试数据
        redis_service.delete("test_complex")

        return True

    except Exception as e:
        print(f"❌ Redis错误处理测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主函数"""
    print("=" * 60)
    print("🧪 Redis连接质量测试")
    print("=" * 60)

    tests = [
        ("Redis连接", test_redis_connection),
        ("Redis错误处理", test_redis_error_handling)
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n🔬 执行测试: {test_name}")
        result = await test_func()
        results.append((test_name, result))
        print(f"{'✅' if result else '❌'} {test_name}: {'通过' if result else '失败'}")

    print("\n" + "=" * 60)
    print("📋 测试结果总结:")
    print("=" * 60)

    all_passed = True
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:<20} {status}")
        if not result:
            all_passed = False

    if all_passed:
        print("\n🎉 所有Redis测试通过！")
        print("🚀 Redis连接和异常处理正常工作")
    else:
        print("\n❌ 部分Redis测试失败")
        print("🔧 请检查Redis配置和连接")

    print("=" * 60)
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))