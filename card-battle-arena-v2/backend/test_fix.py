#!/usr/bin/env python3
"""
测试修复是否有效
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from app.game.engine import GameEngine
from app.game.cards import Card, CardType


def test_card_attributes():
    """测试卡牌属性"""
    engine = GameEngine()
    game = engine.create_game("Test", "AI")

    current = game.current_player

    print("测试手牌中的卡牌属性:")
    for i, card in enumerate(current.hand):
        print(f"{i+1}. {card.name} - 类型: {card.card_type.value}")
        print(f"   属性: attack={card.attack}, health={card.health}")

        if card.card_type == CardType.WEAPON:
            print(f"   武器卡牌耐久度存储在health字段中: {card.health}")

        # 测试是否会出错
        try:
            if hasattr(card, 'durability'):
                print(f"   有durability属性: {card.durability}")
            else:
                print(f"   无durability属性 (正常，Card类型没有这个属性)")
        except AttributeError as e:
            print(f"   ❌ 属性错误: {e}")

    print("\n✅ 测试完成")


if __name__ == "__main__":
    test_card_attributes()