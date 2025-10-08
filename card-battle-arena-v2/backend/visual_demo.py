#!/usr/bin/env python3
"""
卡牌对战竞技场 - Pygame可视化演示
验证游戏玩法的可视化版本
"""

import sys
import time
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

# 提前导入pygame以避免循环导入问题
try:
    import pygame
except ImportError:
    print("错误：未安装Pygame，请运行 'pip install pygame' 安装")
    sys.exit(1)

from app.game.engine import GameEngine
from app.game.cards import Card, CardType
from app.visualization.pygame_renderer import PygameRenderer


def ai_turn(engine, game, renderer):
    """AI回合 - 在Pygame中执行AI操作"""
    current = game.current_player

    print(f"\n🤖 {current.name}的回合开始！")

    # 显示AI思考状态
    renderer.render_ai_thinking(True)

    # 模拟AI思考时间
    import time
    time.sleep(1.5)

    # AI出牌阶段
    cards_played = 0
    max_plays = 3

    while cards_played < max_plays and current.current_mana > 0:
        playable_cards = [card for card in current.hand if card.cost <= current.current_mana]

        if not playable_cards:
            break

        # AI选择策略：优先高攻击力随从
        if any(card.card_type == CardType.MINION for card in playable_cards):
            minion_cards = [card for card in playable_cards if card.card_type == CardType.MINION]
            minion_cards.sort(key=lambda x: x.attack, reverse=True)
            card = minion_cards[0]
        else:
            playable_cards.sort(key=lambda x: x.cost)
            card = playable_cards[0]

        print(f"🤖 {current.name}选择打出 {card.name} (费用:{card.cost})")

        # 显示AI选择
        renderer.highlight_card(card, True)
        time.sleep(1)

        result = engine.play_card(card)
        if result.success:
            print(f"✅ {current.name}成功打出了 {card.name}！")
            cards_played += 1
            time.sleep(1)
        else:
            print(f"❌ {current.name}打出失败: {result.error}")
            break

    # AI攻击阶段
    attackable_minions = [m for m in current.battlefield if m.can_attack]
    if attackable_minions:
        print(f"🤖 {current.name}考虑攻击...")
        time.sleep(1)

        for attacker in attackable_minions[:2]:  # 最多攻击2次
            targets = [game.opponent.hero] + game.opponent.battlefield

            for target in targets:
                print(f"⚔️ {current.name}的 {attacker.name} 攻击 {target.name if hasattr(target, 'name') else '英雄'}")
                time.sleep(1)

                result = engine.attack_with_minion(attacker, target)
                if result.success:
                    print(f"✅ 攻击成功！")
                    break
                else:
                    print(f"❌ 攻击失败: {result.error}")

    # 结束AI回合
    print(f"🔄 {current.name}结束回合")
    time.sleep(1)
    engine.end_turn()

    # 隐藏AI思考状态
    renderer.render_ai_thinking(False)


def main():
    """主函数"""
    # 创建游戏引擎和渲染器
    engine = GameEngine()
    renderer = PygameRenderer(1200, 800)

    # 创建游戏
    game = engine.create_game("玩家", "AI电脑")

    # 创建窗口
    screen = renderer.create_window("卡牌对战竞技场 - Pygame AI对战")

    # 游戏主循环
    running = True
    frame_count = 0
    ai_mode = True  # 默认开启AI对战模式
    player_turn_active = True

    print("Pygame AI对战已启动！")
    print("操作说明：")
    print("  鼠标左键 - 选择/拖拽卡牌，点击已选中卡牌出牌")
    print("  鼠标右键 - 取消选择")
    print("  方向键左右 - 选择手牌")
    print("  空格键 - 选中当前卡牌")
    print("  回车键 - 出牌")
    print("  C键 - 确认出牌")
    print("  ESC - 退出游戏")
    print("  N - 结束当前回合")
    print("  A - 切换AI模式 (开/关)")
    print("  D - 抽一张牌")
    print("  拖拽窗口边缘 - 调整窗口大小")
    print(f"  AI模式: {'开启' if ai_mode else '关闭'}")

    # 开始游戏
    engine.start_turn()

    while running and not game.game_over:
        # 处理事件
        running = renderer.handle_events(game, engine)

        # AI模式处理
        if ai_mode and game.current_player.name == "AI电脑":
            ai_turn(engine, game, renderer)
            engine.start_turn()

        # 渲染游戏状态
        renderer.render_game_state(game)

        # 更新显示
        renderer.update_display()

        frame_count += 1
    
    # 显示游戏结果
    if game.game_over:
        winner_name = "玩家" if game.winner == 1 else "电脑"
        print(f"游戏结束！{winner_name} 获胜！")
    
    # 退出Pygame
    pygame.quit()
    print("游戏已退出")


if __name__ == "__main__":
    print("Pygame已安装，启动可视化演示...")
    main()