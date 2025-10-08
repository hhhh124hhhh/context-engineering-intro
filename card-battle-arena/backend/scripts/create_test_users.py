#!/usr/bin/env python3
"""
测试账号创建脚本

用于创建不同类型的测试账号，方便开发和测试使用。
"""

import asyncio
import sys
import os
import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Optional

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 导入所有需要的模块
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.database.postgres import AsyncSessionLocal, engine
from app.models.user import User
from app.core.security import get_password_hash


class TestUserCreator:
    """测试用户创建器"""

    def __init__(self, password: str = "TestPass123!"):
        # bcrypt限制密码最大72字节
        if len(password.encode('utf-8')) > 72:
            # 截取前72字节并确保是有效的UTF-8字符串
            password_bytes = password.encode('utf-8')[:72]
            try:
                password = password_bytes.decode('utf-8')
            except UnicodeDecodeError:
                # 如果截断导致UTF-8解码错误，使用安全的默认密码
                password = "TestPass123!"
        self.password = password
        # 延迟hash，只在需要时才计算
        self._hashed_password = None

    @property
    def hashed_password(self):
        """延迟计算密码hash"""
        if self._hashed_password is None:
            self._hashed_password = get_password_hash(self.password)
        return self._hashed_password

    # 定义测试用户类型
    test_users = [
        {
            "username": "admin",
            "email": "admin@cardbattle.arena",
            "display_name": "管理员",
            "elo_rating": 2500.0,
            "level": 50,
            "experience": 50000,
            "coins": 10000,
            "games_played": 1000,
            "games_won": 750,
            "games_lost": 250,
            "win_streak": 15,
            "best_win_streak": 25,
            "is_verified": True,
            "bio": "系统管理员账号，用于测试管理功能"
        },
        {
            "username": "testuser",
            "email": "testuser@cardbattle.arena",
            "display_name": "测试用户",
            "elo_rating": 1000.0,
            "level": 10,
            "experience": 5000,
            "coins": 2000,
            "games_played": 100,
            "games_won": 50,
            "games_lost": 50,
            "win_streak": 3,
            "best_win_streak": 8,
            "is_verified": True,
            "bio": "普通测试用户，用于基础功能测试"
        },
        {
            "username": "newbie",
            "email": "newbie@cardbattle.arena",
            "display_name": "新手玩家",
            "elo_rating": 800.0,
            "level": 3,
            "experience": 500,
            "coins": 500,
            "games_played": 10,
            "games_won": 3,
            "games_lost": 7,
            "win_streak": 1,
            "best_win_streak": 2,
            "is_verified": False,
            "bio": "新手玩家，用于测试新手功能"
        },
        {
            "username": "master",
            "email": "master@cardbattle.arena",
            "display_name": "大师玩家",
            "elo_rating": 2800.0,
            "level": 80,
            "experience": 80000,
            "coins": 15000,
            "games_played": 2000,
            "games_won": 1600,
            "games_lost": 400,
            "win_streak": 20,
            "best_win_streak": 35,
            "is_verified": True,
            "bio": "大师级玩家，用于测试高段位功能"
        },
        {
            "username": "grandmaster",
            "email": "grandmaster@cardbattle.arena",
            "display_name": "宗师玩家",
            "elo_rating": 3000.0,
            "level": 100,
            "experience": 100000,
            "coins": 20000,
            "games_played": 3000,
            "games_won": 2400,
            "games_lost": 600,
            "win_streak": 30,
            "best_win_streak": 50,
            "is_verified": True,
            "bio": "宗师级玩家，顶级玩家测试"
        },
        {
            "username": "banned",
            "email": "banned@cardbattle.arena",
            "display_name": "被封禁用户",
            "elo_rating": 1200.0,
            "level": 15,
            "experience": 7500,
            "coins": 1000,
            "games_played": 150,
            "games_won": 75,
            "games_lost": 75,
            "win_streak": 0,
            "best_win_streak": 5,
            "is_verified": False,
            "is_banned": True,
            "ban_reason": "测试封禁功能",
            "ban_until": datetime.now(timezone.utc) + timedelta(days=7),
            "bio": "被封禁的测试账号，用于测试封禁功能"
        },
        {
            "username": "inactive",
            "email": "inactive@cardbattle.arena",
            "display_name": "不活跃用户",
            "elo_rating": 900.0,
            "level": 5,
            "experience": 1500,
            "coins": 800,
            "games_played": 20,
            "games_won": 8,
            "games_lost": 12,
            "win_streak": 0,
            "best_win_streak": 3,
            "is_verified": True,
            "last_login_at": datetime.now(timezone.utc) - timedelta(days=90),
            "bio": "长期未登录的测试账号"
        }
    ]

    async def create_test_users(self, usernames: Optional[List[str]] = None, reset: bool = False):
        """
        创建测试用户

        Args:
            usernames: 要创建的用户名列表，None表示创建所有
            reset: 是否先删除已存在的测试用户
        """
        if reset:
            await self.delete_test_users()

        # 过滤要创建的用户
        users_to_create = self.test_users
        if usernames:
            users_to_create = [u for u in self.test_users if u["username"] in usernames]

        async with AsyncSessionLocal() as session:
            created_count = 0

            for user_data in users_to_create:
                # 检查用户是否已存在
                existing_user = await session.execute(
                    select(User).where(User.username == user_data["username"])
                )
                if existing_user.scalar_one_or_none():
                    print(f"⚠️  用户 '{user_data['username']}' 已存在，跳过创建")
                    continue

                # 创建新用户
                user = User(
                    username=user_data["username"],
                    email=user_data["email"],
                    hashed_password=self.hashed_password,
                    display_name=user_data.get("display_name"),
                    elo_rating=user_data["elo_rating"],
                    level=user_data["level"],
                    experience=user_data["experience"],
                    coins=user_data["coins"],
                    games_played=user_data["games_played"],
                    games_won=user_data["games_won"],
                    games_lost=user_data["games_lost"],
                    win_streak=user_data["win_streak"],
                    best_win_streak=user_data["best_win_streak"],
                    is_active=user_data.get("is_active", True),
                    is_verified=user_data.get("is_verified", False),
                    is_banned=user_data.get("is_banned", False),
                    ban_reason=user_data.get("ban_reason"),
                    ban_until=user_data.get("ban_until"),
                    bio=user_data.get("bio"),
                    last_login_at=user_data.get("last_login_at"),
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc)
                )

                session.add(user)
                created_count += 1
                print(f"✅ 创建用户: {user_data['username']} (ELO: {user_data['elo_rating']})")

            await session.commit()
            print(f"\n🎉 成功创建 {created_count} 个测试用户")
            await self.print_user_summary()

    async def delete_test_users(self, usernames: Optional[List[str]] = None):
        """
        删除测试用户

        Args:
            usernames: 要删除的用户名列表，None表示删除所有测试用户
        """
        test_usernames = [u["username"] for u in self.test_users]
        if usernames:
            test_usernames = [u for u in test_usernames if u in usernames]

        async with AsyncSessionLocal() as session:
            deleted_count = 0

            for username in test_usernames:
                # 删除用户
                result = await session.execute(
                    delete(User).where(User.username == username)
                )
                deleted_count += result.rowcount
                print(f"🗑️  删除用户: {username}")

            await session.commit()
            print(f"\n✅ 成功删除 {deleted_count} 个测试用户")

    async def print_user_summary(self):
        """打印测试用户摘要信息"""
        print("\n" + "="*60)
        print("📋 测试账号信息汇总")
        print("="*60)
        print(f"{'用户名':<12} {'密码':<15} {'ELO':<6} {'等级':<4} {'角色':<8}")
        print("-"*60)

        for user in self.test_users:
            role = "管理员" if user["username"] == "admin" else \
                   "被封禁" if user.get("is_banned") else \
                   "不活跃" if user.get("last_login_at") and \
                   (datetime.now(timezone.utc) - user["last_login_at"]).days > 30 else \
                   "普通用户"

            print(f"{user['username']:<12} {self.password:<15} "
                  f"{int(user['elo_rating']):<6} {user['level']:<4} {role:<8}")

        print("="*60)
        print(f"🔑 统一密码: {self.password}")
        print("⚠️  请勿在生产环境使用这些测试账号！")
        print("="*60)

    async def list_test_users(self):
        """列出所有测试用户"""
        async with AsyncSessionLocal() as session:
            test_usernames = [u["username"] for u in self.test_users]

            for username in test_usernames:
                result = await session.execute(
                    select(User).where(User.username == username)
                )
                user = result.scalar_one_or_none()

                if user:
                    status = "✅ 存在"
                    if user.is_banned:
                        status = "🚫 已封禁"
                    elif not user.is_active:
                        status = "⭕ 未激活"
                else:
                    status = "❌ 不存在"

                print(f"{username:<12} {status}")


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="创建测试用户账号")
    parser.add_argument("--users", "-u",
                       help="要创建的用户名，用逗号分隔 (例: admin,testuser)")
    parser.add_argument("--password", "-p", default="TestPass123!",
                       help="测试用户密码 (默认: TestPass123!)")
    parser.add_argument("--reset", "-r", action="store_true",
                       help="先删除已存在的测试用户")
    parser.add_argument("--delete-only", "-d", action="store_true",
                       help="只删除测试用户，不创建新的")
    parser.add_argument("--list", "-l", action="store_true",
                       help="列出测试用户状态")

    args = parser.parse_args()

    # 检查环境
    if os.getenv("ENVIRONMENT") == "production":
        print("❌ 错误: 不能在生产环境创建测试用户!")
        sys.exit(1)

    creator = TestUserCreator(args.password)

    try:
        if args.list:
            await creator.list_test_users()
        elif args.delete_only:
            usernames = args.users.split(",") if args.users else None
            await creator.delete_test_users(usernames)
        else:
            usernames = args.users.split(",") if args.users else None
            await creator.create_test_users(usernames, args.reset)

    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())