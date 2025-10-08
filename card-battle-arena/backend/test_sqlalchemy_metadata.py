#!/usr/bin/env python3
"""
测试SQLAlchemy元数据和关系定义的完整性
不连接数据库，只测试模型定义是否正确
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, '.')

def test_metadata_creation():
    """测试SQLAlchemy元数据创建"""
    print("🧪 测试SQLAlchemy元数据创建...")

    try:
        # 导入Base和所有模型
        from app.database.postgres import Base
        from app.models.user import User, Friendship, UserAchievement, UserSession
        from app.models.card import Card, UserCardCollection
        from app.models.deck import Deck, DeckCard
        from app.models.game import Game, GamePlayer, ChatMessage

        print("✅ 所有模型导入成功")

        # 创建元数据
        metadata = Base.metadata

        # 获取所有表
        tables = metadata.tables
        print(f"✅ 发现 {len(tables)} 个表:")

        for table_name in sorted(tables.keys()):
            table = tables[table_name]
            print(f"  📋 {table_name}")

            # 检查外键
            foreign_keys = list(table.foreign_keys)
            if foreign_keys:
                print(f"    🔗 外键 ({len(foreign_keys)} 个):")
                for fk in foreign_keys:
                    print(f"      - {fk.parent.name} -> {fk.column.table.name}.{fk.column.name}")

            # 检查索引
            indexes = list(table.indexes)
            if indexes:
                print(f"    📊 索引 ({len(indexes)} 个):")
                for idx in indexes:
                    print(f"      - {idx.name}: {', '.join(col.name for col in idx.columns)}")

        # 特别检查Friendship表
        if 'friendships' in tables:
            friendship_table = tables['friendships']
            print(f"\n🎯 详细检查Friendship表:")

            # 检查必需的列
            required_columns = ['id', 'sender_id', 'receiver_id', 'status', 'created_at', 'updated_at']
            for col_name in required_columns:
                if col_name in friendship_table.columns:
                    print(f"  ✅ 列 {col_name}: {friendship_table.columns[col_name].type}")
                else:
                    print(f"  ❌ 缺少列: {col_name}")
                    return False

            # 检查外键
            fk_columns = [fk.parent.name for fk in friendship_table.foreign_keys]
            expected_fks = ['sender_id', 'receiver_id']
            for fk_col in expected_fks:
                if fk_col in fk_columns:
                    print(f"  ✅ 外键 {fk_col}: 正确定义")
                else:
                    print(f"  ❌ 缺少外键: {fk_col}")
                    return False

        # 测试关系映射
        print(f"\n🔍 检查关系映射:")

        # 检查User模型的sent_friendships关系
        user_relationships = User.__mapper__.relationships
        friendship_relationships = Friendship.__mapper__.relationships

        print(f"  User关系数量: {len(user_relationships)}")
        print(f"  Friendship关系数量: {len(friendship_relationships)}")

        # 检查关键关系
        key_relationships = {
            'User': ['sent_friendships', 'received_friendships'],
            'Friendship': ['sender', 'receiver']
        }

        for model_name, rels in key_relationships.items():
            model = locals()[model_name]
            mapper = model.__mapper__
            for rel_name in rels:
                if rel_name in mapper.relationships:
                    rel = mapper.relationships[rel_name]
                    print(f"  ✅ {model_name}.{rel_name} -> {rel.mapper.class_.__name__}")
                else:
                    print(f"  ❌ 缺少关系: {model_name}.{rel_name}")
                    return False

        print(f"\n🎉 SQLAlchemy元数据测试通过!")
        print("✅ 所有模型定义正确，关系完整")
        return True

    except Exception as e:
        print(f"\n❌ SQLAlchemy元数据测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_specific_relationship_errors():
    """专门测试之前报告的关系错误"""
    print(f"\n🎯 专门测试Friendship关系错误...")

    try:
        from app.models.user import User, Friendship

        # 检查NoForeignKeysError错误
        print("  🔍 检查NoForeignKeysError问题...")

        # 创建元数据来模拟SQLAlchemy的关系检查
        from app.database.postgres import Base
        metadata = Base.metadata

        # 这里不会抛出NoForeignKeysError，因为我们已经正确定义了外键
        if 'users' in metadata.tables and 'friendships' in metadata.tables:
            print("  ✅ users和friendships表都存在")

            friendship_table = metadata.tables['friendships']
            user_table = metadata.tables['users']

            # 检查外键是否指向正确的表
            for fk in friendship_table.foreign_keys:
                if fk.column.table.name == 'users':
                    print(f"  ✅ 外键 {fk.parent.name} 正确指向users表")
                else:
                    print(f"  ❌ 外键 {fk.parent.name} 指向错误的表: {fk.column.table.name}")
                    return False

        print("  ✅ Friendship关系检查通过")
        return True

    except Exception as e:
        print(f"  ❌ Friendship关系测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("🚀 SQLAlchemy元数据和关系完整性测试")
    print("=" * 60)

    success1 = test_metadata_creation()
    success2 = test_specific_relationship_errors()

    print("\n" + "=" * 60)
    if success1 and success2:
        print("🎉 所有测试通过！")
        print("✅ SQLAlchemy关系定义修复成功！")
        print("✅ NoForeignKeysError问题已解决！")
        return 0
    else:
        print("💥 测试失败！")
        print("❌ 仍有关系定义问题需要修复")
        return 1


if __name__ == "__main__":
    sys.exit(main())