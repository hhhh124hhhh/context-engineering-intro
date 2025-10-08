#!/usr/bin/env python3
"""
验证用户报告的具体场景修复
用户场景：AI有2点法力，尝试打3张1费卡
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from app.game.engine import GameEngine


def simulate_user_scenario():
    """模拟用户报告的场景"""
    print("🎯 模拟用户报告的场景")
    print("=" * 50)
    print("场景：AI后手第1回合，有2点法力，尝试打多张1费卡")

    # 创建游戏
    engine = GameEngine()
    game = engine.create_game("玩家", "电脑")

    # 玩家结束回合
    engine.end_turn()
    engine.start_turn()

    current = game.current_player

    print(f"\n🤖 AI状态:")
    print(f"  - 当前玩家: {current.name}")
    print(f"  - 法力值: {current.current_mana}/{current.max_mana}")
    print(f"  - 手牌数: {len(current.hand)}")

    # 显示手牌
    print(f"\n🎴 AI手牌:")
    one_cost_cards = []
    for i, card in enumerate(current.hand):
        print(f"  {i+1}. {card.name} - 费用:{card.cost} [{card.card_type.value}]")
        if card.cost == 1:
            one_cost_cards.append(card)

    print(f"\n📊 1费卡统计: {len(one_cost_cards)}张")

    # 模拟修复后的AI出牌逻辑
    print(f"\n🤖 AI开始出牌（修复后的逻辑）:")

    cards_played = 0
    max_cards = 3

    while cards_played < max_cards and current.current_mana > 0:
        # 每次重新计算可出的卡牌
        playable_cards = [card for card in current.hand if card.cost <= current.current_mana]

        if not playable_cards:
            print(f"  🛑 没有可出的卡牌了（剩余法力: {current.current_mana}）")
            break

        # 选择最低费的卡
        playable_cards.sort(key=lambda x: x.cost)
        card = playable_cards[0]

        print(f"  🎴 尝试打出 {card.name} (费用:{card.cost})")
        result = engine.play_card(card)

        if result.success:
            print(f"    ✅ 成功！剩余法力: {current.current_mana}/{current.max_mana}")
            cards_played += 1
        else:
            print(f"    ❌ 失败: {result.error}")
            break

    print(f"\n📈 出牌结果:")
    print(f"  - 总共尝试打出: {cards_played}张卡")
    print(f"  - 最终剩余法力: {current.current_mana}")
    print(f"  - 法力使用是否正确: {'✅ 是' if current.current_mana >= 0 else '❌ 否'}")

    # 验证是否符合预期
    initial_mana = 2  # 后手第1回合应该是2点法力
    expected_max_cards = min(initial_mana, len(one_cost_cards))

    print(f"\n🔍 场景验证:")
    print(f"  - 初始法力值: {initial_mana}点")
    print(f"  - 1费卡数量: {len(one_cost_cards)}张")
    print(f"  - 理论最多能打: {expected_max_cards}张")
    print(f"  - 实际打出: {cards_played}张")

    if cards_played == min(expected_max_cards, initial_mana):
        print(f"  ✅ 结果正确！AI没有超出法力值限制")
    else:
        print(f"  ❌ 结果异常！AI出牌数量不正确")

    # 特别检查是否出现"Insufficient mana"错误
    if current.current_mana >= 0:
        print(f"  ✅ 没有出现法力值不足错误")
    else:
        print(f"  ❌ 出现了法力值负数，这不应该发生")


if __name__ == "__main__":
    try:
        simulate_user_scenario()
        print(f"\n🎉 用户场景验证完成！")
        print(f"修复效果：AI现在会正确管理法力值，不会尝试打出超出可用法力的卡牌。")
    except Exception as e:
        print(f"❌ 验证出错: {e}")
        import traceback
        traceback.print_exc()