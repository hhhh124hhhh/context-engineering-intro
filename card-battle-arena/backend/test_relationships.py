#!/usr/bin/env python3
"""
测试SQLAlchemy模型关系定义是否正确
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import InvalidRequestError
from app.database.postgres import Base
from app.models.user import User, Friendship, UserAchievement, UserSession
from app.models.game import Game, GamePlayer, GameCard, GameSpectator, ChatMessage
from app.models.card import Card, UserCardCollection
from app.models.deck import Deck, DeckCard, DeckTemplate, DeckTemplateCard
from app.core.config import settings


def test_model_relationships():
    """测试所有模型关系定义"""
    print("🧪 测试SQLAlchemy模型关系定义...")

    # 创建内存数据库用于测试
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)

    # 创建会话
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        print("\n✅ 数据库表创建成功")

        # 检查所有表是否创建成功
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        print(f"\n📊 创建的表列表 ({len(tables)} 个):")
        for table in sorted(tables):
            print(f"  - {table}")

        # 检查Friendship表的外键
        print("\n🔍 检查Friendship表外键...")
        friendship_fks = inspector.get_foreign_keys('friendships')
        print(f"  Friendship外键数量: {len(friendship_fks)}")

        for fk in friendship_fks:
            print(f"  - {fk['name']}: {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")

        # 检查User表的关系
        print("\n🔍 检查User模型关系...")
        user_mapper = Base.registry.mappers[0]  # User model

        # 检查关系是否正确映射
        relationships = user_mapper.relationships
        print(f"  User关系数量: {len(relationships)}")

        for rel_name, rel in relationships.items():
            print(f"  - {rel_name}: {rel.mapper.class_.__name__}")

        # 测试Friendship关系的双向映射
        print("\n🔍 测试Friendship双向关系...")
        friendship_mapper = None
        for mapper in Base.registry.mappers:
            if mapper.class_ == Friendship:
                friendship_mapper = mapper
                break

        if friendship_mapper:
            friendship_relationships = friendship_mapper.relationships
            print(f"  Friendship关系数量: {len(friendship_relationships)}")

            for rel_name, rel in friendship_relationships.items():
                print(f"  - {rel_name}: {rel.mapper.class_.__name__}")

        print("\n✅ 所有模型关系定义验证完成!")
        return True

    except Exception as e:
        print(f"\n❌ 模型关系测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        session.close()


def test_specific_friendship_relationship():
    """特别测试Friendship关系"""
    print("\n🎯 专门测试Friendship关系...")

    try:
        # 创建内存数据库
        engine = create_engine("sqlite:///:memory:", echo=False)
        Base.metadata.create_all(engine)

        # 创建会话
        Session = sessionmaker(bind=engine)
        session = Session()

        # 创建测试用户
        user1 = User(username="test_user1", email="test1@example.com", hashed_password="hash1")
        user2 = User(username="test_user2", email="test2@example.com", hashed_password="hash2")

        session.add(user1)
        session.add(user2)
        session.commit()

        # 测试创建好友关系
        friendship = Friendship(sender_id=user1.id, receiver_id=user2.id, status="pending")
        session.add(friendship)
        session.commit()

        # 测试关系访问
        print(f"  User1的发送好友关系: {len(user1.sent_friendships)}")
        print(f"  User2的接收好友关系: {len(user2.received_friendships)}")
        print(f"  Friendship的发送者: {friendship.sender.username}")
        print(f"  Friendship的接收者: {friendship.receiver.username}")

        print("\n✅ Friendship关系测试通过!")
        return True

    except Exception as e:
        print(f"\n❌ Friendship关系测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        session.close()


if __name__ == "__main__":
    print("🚀 开始SQLAlchemy模型关系测试...")

    success1 = test_model_relationships()
    success2 = test_specific_friendship_relationship()

    if success1 and success2:
        print("\n🎉 所有测试通过！SQLAlchemy关系定义修复成功！")
        sys.exit(0)
    else:
        print("\n💥 测试失败！仍有关系定义问题需要修复。")
        sys.exit(1)