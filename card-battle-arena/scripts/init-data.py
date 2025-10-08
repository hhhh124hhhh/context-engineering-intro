#!/usr/bin/env python3
"""
卡牌对战竞技场 - 数据初始化脚本
作者: Card Battle Arena Team
版本: 1.0.0
"""

import os
import sys
import json
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "backend"))

try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.database.connection import get_database_url
    from app.models.user import User
    from app.models.card import Card
    from app.models.deck import Deck
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保已安装所有依赖并且虚拟环境已激活")
    sys.exit(1)

def create_sample_cards():
    """创建示例卡牌数据"""
    return [
        # 法师卡牌
        {
            "id": "fireball_001",
            "name": "火球术",
            "description": "造成4点伤害",
            "cost": 4,
            "class_name": "mage",
            "rarity": "common",
            "type": "spell",
            "attack": 0,
            "health": 0,
            "image_url": "/images/cards/fireball.png"
        },
        {
            "id": "frostbolt_002",
            "name": "寒冰箭",
            "description": "造成3点伤害并冻结目标",
            "cost": 2,
            "class_name": "mage",
            "rarity": "common",
            "type": "spell",
            "attack": 0,
            "health": 0,
            "image_url": "/images/cards/frostbolt.png"
        },
        {
            "id": "water_elemental_003",
            "name": "水元素",
            "description": "战吼：冻结一个敌人",
            "cost": 4,
            "class_name": "mage",
            "rarity": "common",
            "type": "minion",
            "attack": 3,
            "health": 5,
            "image_url": "/images/cards/water_elemental.png"
        },

        # 战士卡牌
        {
            "id": "fiery_war_axe_004",
            "name": "炽炎战斧",
            "description": "武器，攻击力3，耐久度2",
            "cost": 3,
            "class_name": "warrior",
            "rarity": "common",
            "type": "weapon",
            "attack": 3,
            "health": 2,
            "image_url": "/images/cards/fiery_war_axe.png"
        },
        {
            "id": "armorsmith_005",
            "name": "铁匠",
            "description": "战吼：获得2点护甲",
            "cost": 2,
            "class_name": "warrior",
            "rarity": "common",
            "type": "minion",
            "attack": 1,
            "health": 4,
            "image_url": "/images/cards/armorsmith.png"
        },

        # 猎人卡牌
        {
            "id": "kill_command_006",
            "name": "杀戮命令",
            "description": "造成3点伤害，如果有野兽在场则造成5点伤害",
            "cost": 3,
            "class_name": "hunter",
            "rarity": "common",
            "type": "spell",
            "attack": 0,
            "health": 0,
            "image_url": "/images/cards/kill_command.png"
        },
        {
            "id": "chillwind_yeti_007",
            "name": "风雪巨人",
            "description": "白板随从",
            "cost": 4,
            "class_name": "neutral",
            "rarity": "common",
            "type": "minion",
            "attack": 4,
            "health": 5,
            "image_url": "/images/cards/chillwind_yeti.png"
        },

        # 中立卡牌
        {
            "id": "boulderfist_ogre_008",
            "name": "石拳食人魔",
            "description": "白板随从",
            "cost": 6,
            "class_name": "neutral",
            "rarity": "common",
            "type": "minion",
            "attack": 6,
            "health": 7,
            "image_url": "/images/cards/boulderfist_ogre.png"
        },
        {
            "id": "wolfrider_009",
            "name": "狼骑士",
            "description": "冲锋",
            "cost": 3,
            "class_name": "neutral",
            "rarity": "common",
            "type": "minion",
            "attack": 3,
            "health": 1,
            "image_url": "/images/cards/wolfrider.png"
        },
        {
            "id": "ironfur_grizzly_010",
            "name": "铁鬃灰熊",
            "description": "嘲讽",
            "cost": 3,
            "class_name": "neutral",
            "rarity": "common",
            "type": "minion",
            "attack": 3,
            "health": 3,
            "image_url": "/images/cards/ironfur_grizzly.png"
        }
    ]

def create_sample_users():
    """创建示例用户数据"""
    return [
        {
            "username": "player1",
            "email": "player1@example.com",
            "password": "password123",
            "rating": 1000
        },
        {
            "username": "player2",
            "email": "player2@example.com",
            "password": "password123",
            "rating": 1050
        },
        {
            "username": "player3",
            "email": "player3@example.com",
            "password": "password123",
            "rating": 950
        }
    ]

def create_sample_decks():
    """创建示例卡组数据"""
    return [
        {
            "name": "基础法师卡组",
            "class_name": "mage",
            "cards": [
                {"card_id": "fireball_001", "count": 2},
                {"card_id": "frostbolt_002", "count": 2},
                {"card_id": "water_elemental_003", "count": 2},
                {"card_id": "chillwind_yeti_007", "count": 2},
                {"card_id": "boulderfist_ogre_008", "count": 1},
                {"card_id": "wolfrider_009", "count": 2},
                {"card_id": "ironfur_grizzly_010", "count": 1}
            ]
        },
        {
            "name": "基础战士卡组",
            "class_name": "warrior",
            "cards": [
                {"card_id": "fiery_war_axe_004", "count": 2},
                {"card_id": "armorsmith_005", "count": 2},
                {"card_id": "chillwind_yeti_007", "count": 2},
                {"card_id": "boulderfist_ogre_008", "count": 2},
                {"card_id": "wolfrider_009", "count": 2},
                {"card_id": "ironfur_grizzly_010", "count": 2}
            ]
        }
    ]

def init_database():
    """初始化数据库数据"""
    print("🚀 开始初始化数据库数据...")

    try:
        # 创建数据库连接
        engine = create_engine(get_database_url())
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()

        # 创建示例卡牌
        print("📦 创建示例卡牌...")
        cards_data = create_sample_cards()
        for card_data in cards_data:
            # 检查卡牌是否已存在
            existing_card = db.query(Card).filter(Card.id == card_data["id"]).first()
            if not existing_card:
                card = Card(**card_data)
                db.add(card)
                print(f"  ✅ 创建卡牌: {card_data['name']}")
            else:
                print(f"  ⚠️  卡牌已存在: {card_data['name']}")

        # 创建示例用户
        print("👥 创建示例用户...")
        users_data = create_sample_users()
        created_users = []

        for user_data in users_data:
            # 检查用户是否已存在
            existing_user = db.query(User).filter(User.username == user_data["username"]).first()
            if not existing_user:
                # 注意：实际应用中应该对密码进行加密
                user = User(
                    username=user_data["username"],
                    email=user_data["email"],
                    password_hash=user_data["password"],  # 简化处理，实际应该使用bcrypt
                    rating=user_data["rating"]
                )
                db.add(user)
                created_users.append(user)
                print(f"  ✅ 创建用户: {user_data['username']}")
            else:
                print(f"  ⚠️  用户已存在: {user_data['username']}")
                created_users.append(existing_user)

        # 创建示例卡组
        print("🎴 创建示例卡组...")
        decks_data = create_sample_decks()

        for i, deck_data in enumerate(decks_data):
            if i < len(created_users):  # 确保有足够的用户分配卡组
                user = created_users[i]

                # 检查用户是否已有同名卡组
                existing_deck = db.query(Deck).filter(
                    Deck.user_id == user.id,
                    Deck.name == deck_data["name"]
                ).first()

                if not existing_deck:
                    deck = Deck(
                        name=deck_data["name"],
                        class_name=deck_data["class_name"],
                        user_id=user.id
                    )
                    db.add(deck)
                    db.flush()  # 获取deck.id

                    # 添加卡牌到卡组
                    for card_entry in deck_data["cards"]:
                        card = db.query(Card).filter(Card.id == card_entry["card_id"]).first()
                        if card:
                            # 这里需要创建关联表记录，简化处理
                            pass

                    print(f"  ✅ 为用户 {user.username} 创建卡组: {deck_data['name']}")
                else:
                    print(f"  ⚠️  卡组已存在: {deck_data['name']}")

        # 提交所有更改
        db.commit()
        print("✅ 数据库初始化完成！")

    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def create_sample_config():
    """创建示例配置文件"""
    print("⚙️  创建示例配置文件...")

    # 创建游戏配置
    game_config = {
        "max_hand_size": 10,
        "max_deck_size": 30,
        "min_deck_size": 30,
        "starting_health": 30,
        "starting_mana": 1,
        "max_mana": 10,
        "turn_time_limit": 90,
        "game_duration_limit": 3600
    }

    config_dir = project_root / "config"
    config_dir.mkdir(exist_ok=True)

    config_file = config_dir / "game_config.json"
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(game_config, f, indent=2, ensure_ascii=False)

    print(f"  ✅ 创建游戏配置: {config_file}")

def main():
    """主函数"""
    print("🎮 卡牌对战竞技场 - 数据初始化")
    print("=" * 40)
    print()

    try:
        # 初始化数据库数据
        init_database()

        # 创建配置文件
        create_sample_config()

        print()
        print("🎉 初始化完成！")
        print()
        print("📋 创建的内容:")
        print("  - 10张示例卡牌")
        print("  - 3个示例用户")
        print("  - 2个示例卡组")
        print("  - 游戏配置文件")
        print()
        print("🚀 现在可以启动开发服务器了:")
        print("  cd backend && uvicorn main:app --reload")
        print("  cd frontend && npm run dev")

    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()