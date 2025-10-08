"""
基础卡牌数据种子文件
包含一些示例卡牌数据用于测试
"""

import asyncio
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database.postgres import AsyncSessionLocal
from app.models.card import Card


# 基础卡牌数据
BASIC_CARDS = [
    # 战士卡牌
    {
        "name": "炽炎战斧",
        "description": "装备一个3点攻击力，1点耐久度的武器。",
        "cost": 2,
        "attack": 3,
        "durability": 1,
        "card_type": "weapon",
        "rarity": "common",
        "card_class": "warrior",
        "card_set": "basic",
        "mechanics": [],
        "image_url": "/assets/cards/warrior/raging_blow.png",
        "is_collectible": True,
        "crafting_cost": 40
    },
    {
        "name": "盾牌猛击",
        "description": "获得护甲值等于你英雄护甲值的伤害。",
        "cost": 1,
        "card_type": "spell",
        "rarity": "common",
        "card_class": "warrior",
        "card_set": "basic",
        "mechanics": [],
        "image_url": "/assets/cards/warrior/shield_slam.png",
        "is_collectible": True,
        "crafting_cost": 40
    },
    {
        "name": "暴乱狂战士",
        "description": "嘲讽。每当你受到伤害时，获得+1攻击力。",
        "cost": 3,
        "attack": 2,
        "defense": 4,
        "card_type": "minion",
        "rarity": "rare",
        "card_class": "warrior",
        "card_set": "basic",
        "mechanics": ["taunt"],
        "image_url": "/assets/cards/warrior/berserker_rage.png",
        "is_collectible": True,
        "crafting_cost": 100
    },

    # 法师卡牌
    {
        "name": "火球术",
        "description": "造成6点伤害。",
        "cost": 4,
        "card_type": "spell",
        "rarity": "common",
        "card_class": "mage",
        "card_set": "basic",
        "mechanics": [],
        "image_url": "/assets/cards/mage/fireball.png",
        "is_collectible": True,
        "crafting_cost": 40
    },
    {
        "name": "寒冰箭",
        "description": "造成3点伤害并冻结一个角色。",
        "cost": 2,
        "card_type": "spell",
        "rarity": "common",
        "card_class": "mage",
        "card_set": "basic",
        "mechanics": ["freeze"],
        "image_url": "/assets/cards/mage/frostbolt.png",
        "is_collectible": True,
        "crafting_cost": 40
    },
    {
        "name": "水元素",
        "description": "冻结任何受到该随从伤害的角色。",
        "cost": 4,
        "attack": 3,
        "defense": 6,
        "card_type": "minion",
        "rarity": "common",
        "card_class": "mage",
        "card_set": "basic",
        "mechanics": ["freeze"],
        "image_url": "/assets/cards/mage/water_elemental.png",
        "is_collectible": True,
        "crafting_cost": 40
    },

    # 猎人卡牌
    {
        "name": "奥术射击",
        "description": "造成2点伤害。",
        "cost": 1,
        "card_type": "spell",
        "rarity": "common",
        "card_class": "hunter",
        "card_set": "basic",
        "mechanics": [],
        "image_url": "/assets/cards/hunter/arcane_shot.png",
        "is_collectible": True,
        "crafting_cost": 40
    },
    {
        "name": "饥饿的秃鹫",
        "description": "每当一个野兽死亡，抽一张牌。",
        "cost": 2,
        "attack": 2,
        "defense": 1,
        "card_type": "minion",
        "rarity": "rare",
        "card_class": "hunter",
        "card_set": "basic",
        "mechanics": [],
        "image_url": "/assets/cards/hunter/starving_buzzard.png",
        "is_collectible": True,
        "crafting_cost": 100
    },

    # 牧师卡牌
    {
        "name": "治疗术",
        "description": "恢复5点生命值。",
        "cost": 1,
        "card_type": "spell",
        "rarity": "common",
        "card_class": "priest",
        "card_set": "basic",
        "mechanics": [],
        "image_url": "/assets/cards/priest/lesser_heal.png",
        "is_collectible": True,
        "crafting_cost": 40
    },
    {
        "name": "精神控制",
        "description": "获得一个敌方随从的控制权。",
        "cost": 10,
        "card_type": "spell",
        "rarity": "epic",
        "card_class": "priest",
        "card_set": "basic",
        "mechanics": [],
        "image_url": "/assets/cards/priest/mind_control.png",
        "is_collectible": True,
        "crafting_cost": 400
    },

    # 潜行者卡牌
    {
        "name": "背刺",
        "description": "对未受伤的角色造成2点伤害。",
        "cost": 1,
        "card_type": "spell",
        "rarity": "common",
        "card_class": "rogue",
        "card_set": "basic",
        "mechanics": [],
        "image_url": "/assets/cards/rogue/backstab.png",
        "is_collectible": True,
        "crafting_cost": 40
    },
    {
        "name": "刺杀",
        "description": "消灭一个敌方随从。",
        "cost": 5,
        "card_type": "spell",
        "rarity": "common",
        "card_class": "rogue",
        "card_set": "basic",
        "mechanics": [],
        "image_url": "/assets/cards/rogue/assassinate.png",
        "is_collectible": True,
        "crafting_cost": 40
    },

    # 术士卡牌
    {
        "name": "生命分流",
        "description": "抽2张牌，并受到2点伤害。",
        "cost": 2,
        "card_type": "spell",
        "rarity": "common",
        "card_class": "warlock",
        "card_set": "basic",
        "mechanics": [],
        "image_url": "/assets/cards/warlock/life_tap.png",
        "is_collectible": True,
        "crafting_cost": 40
    },
    {
        "name": "地狱火",
        "description": "无法攻击。在你的回合结束时，对所有其他角色造成1点伤害。",
        "cost": 6,
        "attack": 6,
        "defense": 6,
        "card_type": "minion",
        "rarity": "epic",
        "card_class": "warlock",
        "card_set": "basic",
        "mechanics": [],
        "image_url": "/assets/cards/warlock/infernal.png",
        "is_collectible": True,
        "crafting_cost": 400
    },

    # 萨满祭司卡牌
    {
        "name": "闪电箭",
        "description": "造成3点伤害，过载（1）。",
        "cost": 1,
        "card_type": "spell",
        "rarity": "common",
        "card_class": "shaman",
        "card_set": "basic",
        "mechanics": ["overload"],
        "image_url": "/assets/cards/shaman/lightning_bolt.png",
        "is_collectible": True,
        "crafting_cost": 40
    },
    {
        "name": "风怒",
        "description": "使一个友方角色获得风怒。",
        "cost": 2,
        "card_type": "spell",
        "rarity": "common",
        "card_class": "shaman",
        "card_set": "basic",
        "mechanics": ["windfury"],
        "image_url": "/assets/cards/shaman/windfury.png",
        "is_collectible": True,
        "crafting_cost": 40
    },

    # 圣骑士卡牌
    {
        "name": "王者祝福",
        "description": "使一个随从获得+4/+4。",
        "cost": 4,
        "card_type": "spell",
        "rarity": "common",
        "card_class": "paladin",
        "card_set": "basic",
        "mechanics": [],
        "image_url": "/assets/cards/paladin/blessing_of_kings.png",
        "is_collectible": True,
        "crafting_cost": 40
    },
    {
        "name": "真银圣剑",
        "description": "装备一个4点攻击力，2点耐久度的武器。每当你的英雄攻击时，恢复2点生命值。",
        "cost": 4,
        "attack": 4,
        "durability": 2,
        "card_type": "weapon",
        "rarity": "epic",
        "card_class": "paladin",
        "card_set": "basic",
        "mechanics": ["lifesteal"],
        "image_url": "/assets/cards/paladin/truesilver_champion.png",
        "is_collectible": True,
        "crafting_cost": 400
    },

    # 德鲁伊卡牌
    {
        "name": "野性成长",
        "description": "获得一个空的法力水晶。过载（1）。",
        "cost": 2,
        "card_type": "spell",
        "rarity": "common",
        "card_class": "druid",
        "card_set": "basic",
        "mechanics": ["overload"],
        "image_url": "/assets/cards/druid/wild_growth.png",
        "is_collectible": True,
        "crafting_cost": 40
    },
    {
        "name": "横扫",
        "description": "对2个敌人造成1点伤害，并抽一张牌。",
        "cost": 2,
        "card_type": "spell",
        "rarity": "common",
        "card_class": "druid",
        "card_set": "basic",
        "mechanics": [],
        "image_url": "/assets/cards/druid/swipe.png",
        "is_collectible": True,
        "crafting_cost": 40
    }
]


async def seed_cards():
    """插入基础卡牌数据"""
    async with AsyncSessionLocal() as session:
        try:
            # 检查是否已有卡牌数据
            existing_count = await session.execute(text("SELECT COUNT(*) FROM cards"))
            count = existing_count.scalar()

            if count > 0:
                print(f"数据库中已有 {count} 张卡牌，跳过种子数据插入")
                return

            # 插入卡牌数据
            for card_data in BASIC_CARDS:
                card = Card(**card_data)
                session.add(card)

            await session.commit()
            print(f"成功插入 {len(BASIC_CARDS)} 张基础卡牌")

        except Exception as e:
            print(f"插入卡牌数据时出错: {e}")
            await session.rollback()


if __name__ == "__main__":
    asyncio.run(seed_cards())