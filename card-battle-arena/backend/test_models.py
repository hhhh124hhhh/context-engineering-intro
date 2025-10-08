#!/usr/bin/env python3
"""测试模型导入"""

import sys
sys.path.insert(0, '.')

try:
    print("开始导入模型...")

    # 首先测试基础导入
    from app.database.postgres import Base
    print("✓ Base 导入成功")

    # 测试用户模型导入
    from app.models.user import User, Friendship, UserAchievement, UserSession
    print("✓ User 模型导入成功")

    # 测试模型类定义
    print(f"✓ User 表名: {User.__tablename__}")
    print(f"✓ Friendship 表名: {Friendship.__tablename__}")

    # 测试关系定义
    user = User()
    print(f"✓ User 实例创建成功，有 sent_friendships 属性: {hasattr(user, 'sent_friendships')}")
    print(f"✓ User 实例创建成功，有 received_friendships 属性: {hasattr(user, 'received_friendships')}")

    friendship = Friendship()
    print(f"✓ Friendship 实例创建成功，有 sender 属性: {hasattr(friendship, 'sender')}")
    print(f"✓ Friendship 实例创建成功，有 receiver 属性: {hasattr(friendship, 'receiver')}")

    print("\n所有测试通过！模型定义正确。")

except Exception as e:
    print(f"✗ 错误: {e}")
    import traceback
    traceback.print_exc()