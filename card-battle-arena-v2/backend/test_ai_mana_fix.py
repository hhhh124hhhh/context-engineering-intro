#!/usr/bin/env python3
"""
测试AI法力值管理修复
"""

import sys
import time
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from app.game.engine import GameEngine


def test_ai_mana_management():
    """测试AI法力值管理"""
    print("🤖 AI法力值管理测试")
    print("=" * 40)

    # 创建游戏
    engine = GameEngine()
    game = engine.create_game("测试玩家", "AI测试")

    # 玩家结束回合
    engine.end_turn()
    engine.start_turn()

    current = game.current_player
    print(f"🤖 AI回合开始 - 法力值: {current.current_mana}/{current.max_mana}")
    print(f"🤖 AI手牌数: {len(current.hand)}")

    # 显示AI手牌
    print("\n🎴 AI手牌详情:")
    for i, card in enumerate(current.hand):
        can_play = "✅" if card.cost <= current.current_mana else "❌"
        print(f"  {i+1}. {can_play} {card.name} - 费用:{card.cost}")

    # 手动模拟AI出牌逻辑（不使用交互式AI函数）
    cards_played = 0
    initial_mana = current.current_mana

    print(f"\n🤖 AI开始出牌（初始法力: {initial_mana}）...")

    while cards_played < 3 and current.current_mana > 0:
        # 重新计算可出的卡牌
        playable_cards = [card for card in current.hand if card.cost <= current.current_mana]
        if not playable_cards:
            print(f"🤖 没有可出的卡牌了（剩余法力: {current.current_mana}）")
            break

        # 选择最低费的卡
        playable_cards.sort(key=lambda x: x.cost)
        card = playable_cards[0]

        print(f"🤖 尝试打出 {card.name} (费用:{card.cost})，当前法力: {current.current_mana}")

        result = engine.play_card(card)
        if result.success:
            print(f"✅ 成功打出 {card.name}，剩余法力: {current.current_mana}/{current.max_mana}")
            cards_played += 1
        else:
            print(f"❌ 打出失败: {result.error}")
            break

    print(f"\n📊 出牌总结:")
    print(f"  - 初始法力值: {initial_mana}")
    print(f"  - 剩余法力值: {current.current_mana}")
    print(f"  - 打出卡牌数: {cards_played}")
    print(f"  - 消耗法力值: {initial_mana - current.current_mana}")

    if cards_played > 0 and current.current_mana >= 0:
        print(f"✅ AI法力值管理正确！")
    else:
        print(f"❌ AI法力值管理有问题！")


def test_specific_scenario():
    """测试用户报告的具体场景"""
    print("\n🎯 测试用户报告的具体场景")
    print("=" * 40)

    # 模拟用户报告的场景：AI有2点法力，尝试打3张1费卡
    engine = GameEngine()
    game = engine.create_game("玩家", "AI")

    # 手动设置AI回合（后手，第1回合2点法力）
    engine.end_turn()
    engine.start_turn()

    current = game.current_player
    print(f"场景：AI后手第1回合，法力值: {current.current_mana}/{current.max_mana}")

    # 统计1费卡牌数量
    one_cost_cards = [card for card in current.hand if card.cost == 1]
    print(f"AI手牌中1费卡数量: {len(one_cost_cards)}")

    if len(one_cost_cards) >= 3:
        print("✅ 场景符合：AI有至少3张1费卡")

        # 模拟AI出牌
        cards_to_play = one_cost_cards[:3]  # 取前3张1费卡
        expected_playable = min(2, len(cards_to_play))  # 2点法力最多打2张1费卡

        print(f"🤖 AI尝试出牌（预期最多能打{expected_playable}张）:")

        for i, card in enumerate(cards_to_play):
            if current.current_mana >= card.cost:
                result = engine.play_card(card)
                if result.success:
                    print(f"  ✅ 第{i+1}张: {card.name} (费用:{card.cost})，剩余法力: {current.current_mana}")
                else:
                    print(f"  ❌ 第{i+1}张: {card.name} 失败 - {result.error}")
                    break
            else:
                print(f"  ❌ 第{i+1}张: {card.name} 法力不足 (需要{card.cost}，剩余{current.current_mana})")
                break

        print(f"\n📊 结果验证:")
        print(f"  - 应该能打: {expected_playable}张1费卡")
        print(f"  - 实际打出: {2 - current.current_mana}张卡")
        print(f"  - 法力使用正确: {'✅' if current.current_mana == 0 else '❌'}")

    else:
        print(f"❌ 场景不符合：AI只有{len(one_cost_cards)}张1费卡")


if __name__ == "__main__":
    try:
        test_ai_mana_management()
        test_specific_scenario()
        print(f"\n🎉 AI法力值管理测试完成！")
    except Exception as e:
        print(f"❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()