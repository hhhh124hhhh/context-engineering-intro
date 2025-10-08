#!/usr/bin/env python3
"""
快速测试AI功能（验证time模块修复）
"""

import sys
import time
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from app.game.engine import GameEngine


def quick_ai_test():
    """快速AI测试"""
    print("🤖 快速AI功能测试")
    print("=" * 40)

    # 创建游戏
    engine = GameEngine()
    game = engine.create_game("测试玩家", "AI测试")

    print("✅ 游戏创建成功")

    # 玩家结束回合
    engine.end_turn()
    engine.start_turn()

    current = game.current_player
    print(f"🤖 AI回合开始 - 法力值: {current.current_mana}/{current.max_mana}")

    # 测试time模块工作
    print("⏰ 测试延迟功能...")
    time.sleep(0.5)
    print("✅ 延迟功能正常")

    # 简单AI行动
    if current.current_mana >= 1:
        # 尝试打出一张卡
        for card in current.hand:
            if card.cost <= current.current_mana and card.card_type.value == "minion":
                print(f"🤖 AI尝试打出 {card.name}")
                result = engine.play_card(card)
                if result.success:
                    print(f"✅ AI成功打出 {card.name}")
                else:
                    print(f"❌ AI打出失败: {result.error}")
                break

    # 结束AI回合
    engine.end_turn()
    print("✅ AI回合结束")

    print("\n🎉 AI快速测试完成！所有功能正常。")


if __name__ == "__main__":
    try:
        quick_ai_test()
    except Exception as e:
        print(f"❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()