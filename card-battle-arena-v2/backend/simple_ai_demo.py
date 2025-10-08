#!/usr/bin/env python3
"""
简化版AI对战演示
测试AI在Pygame界面的对战功能
"""

import sys
import time
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

try:
    import pygame
except ImportError:
    print("错误：未安装Pygame")
    sys.exit(1)

from app.game.engine import GameEngine
from app.game.cards import Card, CardType


def simple_ai_turn(engine, game):
    """简单AI回合"""
    current = game.current_player
    print(f"\n🤖 {current.name}的回合")

    # AI出牌
    cards_played = 0
    while cards_played < 2 and current.current_mana > 0:
        playable_cards = [card for card in current.hand if card.cost <= current.current_mana]

        if not playable_cards:
            break

        # 选择第一张可出的卡牌
        card = playable_cards[0]
        result = engine.play_card(card)

        if result.success:
            print(f"✅ AI打出 {card.name}")
            cards_played += 1
        else:
            break

    # AI攻击
    for attacker in current.battlefield[:2]:  # 最多攻击2次
        if attacker.can_attack:
            result = engine.attack_with_minion(attacker, game.opponent.hero)
            if result.success:
                print(f"⚔️ AI {attacker.name} 攻击英雄")

    # 结束回合
    engine.end_turn()


def main():
    """主函数"""
    print("🎮 简化版AI对战演示")
    print("=" * 40)

    # 初始化Pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("AI对战演示")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)

    # 创建游戏
    engine = GameEngine()
    game = engine.create_game("玩家", "AI电脑")
    engine.start_turn()

    print("✅ 游戏创建成功")

    # 游戏循环
    running = True
    turn_count = 0
    max_turns = 10

    while running and not game.game_over and turn_count < max_turns:
        turn_count += 1

        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # AI回合
        if game.current_player.name == "AI电脑":
            simple_ai_turn(engine, game)
            engine.start_turn()

        # 玩家回合（自动结束）
        else:
            engine.end_turn()
            engine.start_turn()

        # 检查游戏是否结束
        engine.check_win_condition()

        # 渲染界面
        screen.fill((50, 50, 50))

        # 显示游戏信息
        turn_text = font.render(f"回合 {turn_count} - {game.current_player.name}", True, (255, 255, 255))
        screen.blit(turn_text, (50, 50))

        player_health_text = font.render(f"玩家: {game.player1.hero.health}/30", True, (255, 100, 100))
        screen.blit(player_health_text, (50, 100))

        ai_health_text = font.render(f"AI: {game.player2.hero.health}/30", True, (100, 100, 255))
        screen.blit(ai_health_text, (50, 150))

        player_cards_text = font.render(f"玩家手牌: {len(game.player1.hand)}张", True, (200, 200, 200))
        screen.blit(player_cards_text, (50, 200))

        ai_cards_text = font.render(f"AI手牌: {len(game.player2.hand)}张", True, (200, 200, 200))
        screen.blit(ai_cards_text, (50, 250))

        player_battlefield_text = font.render(f"玩家战场: {len(game.player1.battlefield)}张", True, (200, 200, 200))
        screen.blit(player_battlefield_text, (50, 300))

        ai_battlefield_text = font.render(f"AI战场: {len(game.player2.battlefield)}张", True, (200, 200, 200))
        screen.blit(ai_battlefield_text, (50, 350))

        # 提示信息
        hint_text = font.render("ESC退出", True, (150, 150, 150))
        screen.blit(hint_text, (50, 500))

        pygame.display.flip()
        clock.tick(2)  # 2 FPS，让游戏慢一点

        # 短暂延迟
        time.sleep(0.5)

    # 游戏结束
    if game.game_over:
        winner = "玩家" if game.winner == 1 else "AI电脑"
        print(f"\n🏆 游戏结束！{winner} 获胜！")
    else:
        print(f"\n⏰ 演示结束（{turn_count}回合）")

    print(f"最终状态:")
    print(f"  玩家生命值: {game.player1.hero.health}/30")
    print(f"  AI生命值: {game.player2.hero.health}/30")

    # 退出
    pygame.quit()
    print("演示结束")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n演示被中断")
        pygame.quit()
    except Exception as e:
        print(f"❌ 演示出错: {e}")
        import traceback
        traceback.print_exc()
        pygame.quit()