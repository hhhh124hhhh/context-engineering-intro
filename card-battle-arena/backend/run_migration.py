#!/usr/bin/env python3
"""
数据库迁移执行脚本
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def run_migration():
    """执行数据库迁移"""
    try:
        print("🔄 开始执行数据库迁移...")

        # 导入必要的模块
        from sqlalchemy import text
        from app.database.postgres import engine

        # 检查数据库连接
        print("📡 检查数据库连接...")
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            print("✅ 数据库连接正常")

        # 创建所有表
        print("🏗️ 创建数据库表...")
        from app.database.postgres import Base
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        print("✅ 数据库表创建成功")

        # 验证关键表是否存在
        print("🔍 验证表结构...")
        async with engine.begin() as conn:
            # 检查users表
            result = await conn.execute(text("SELECT COUNT(*) FROM users"))
            users_count = result.scalar()
            print(f"   - users表: ✅ (当前记录数: {users_count})")

            # 检查user_sessions表
            try:
                result = await conn.execute(text("SELECT COUNT(*) FROM user_sessions"))
                sessions_count = result.scalar()
                print(f"   - user_sessions表: ✅ (当前记录数: {sessions_count})")
            except Exception as e:
                print(f"   - user_sessions表: ❌ ({e})")
                return False

            # 检查friendships表
            try:
                result = await conn.execute(text("SELECT COUNT(*) FROM friendships"))
                friendships_count = result.scalar()
                print(f"   - friendships表: ✅ (当前记录数: {friendships_count})")
            except Exception as e:
                print(f"   - friendships表: ❌ ({e})")

        print("\n🎉 数据库迁移完成！")
        return True

    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主函数"""
    print("=" * 60)
    print("🗄️ 卡牌对战竞技场 - 数据库迁移")
    print("=" * 60)

    success = await run_migration()

    if success:
        print("\n📋 下一步操作:")
        print("1. 运行测试账号创建脚本:")
        print("   python scripts/create_test_users_fixed.py")
        print("2. 测试登录功能")
        print("3. 启动前端服务")

        print("\n🎮 现在可以开始使用登录功能了！")
    else:
        print("\n❌ 迁移失败，请检查:")
        print("1. PostgreSQL服务是否运行")
        print("2. 数据库连接配置是否正确")
        print("3. 数据库权限是否足够")

    print("=" * 60)
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))