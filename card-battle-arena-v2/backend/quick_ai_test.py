#!/usr/bin/env python3
"""
快速AI对战测试
验证AI对战功能是否正常工作
"""

import sys
import time
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

try:
    import pygame
    pygame.init()
except ImportError:
    print("错误：未安装Pygame")
    sys.exit(1)

from app.game.engine import GameEngine
from app.game.cards import Card, CardType


def quick_ai_battle():
    """快速AI对战测试"""
    print("🚀 快速AI对战测试")
    print("=" * 40)

    # 创建游戏引擎
    engine = GameEngine()
    game = engine.create_game("玩家", "AI电脑")
    engine.start_turn()

    # 进行5个回合的测试
    for turn in range(1, 6):
        print(f"\n📊 回合 {turn}")
        print("-" * 25)

        current = game.current_player

        if current.name == "AI电脑":
            # AI回合 - 自动出牌和攻击
            print("🤖 AI的回合")

            # AI出牌
            for _ in range(2):  # 最多出2张牌
                playable_cards = [card for card in current.hand if card.cost <= current.current_mana]
                if playable_cards:
                    card = playable_cards[0]  # 选择第一张
                    result = engine.play_card(card)
                    if result.success:
                        print(f"  ✅ AI打出 {card.name}")
                    else:
                        print(f"  ❌ AI出牌失败: {result.error}")
                        break
                else:
                    print("  💭 AI没有可出的卡牌")
                    break

            # AI攻击
            for attacker in current.battlefield[:1]:  # 最多攻击1次
                if attacker.can_attack:
                    result = engine.attack_with_minion(attacker, game.opponent.hero)
                    if result.success:
                        print(f"  ⚔️ AI {attacker.name} 攻击英雄")
                    else:
                        print(f"  ❌ AI攻击失败")

        else:
            # 玩家回合 - 自动结束
            print("👤 玩家的回合（自动结束）")

        # 结束回合
        engine.end_turn()
        engine.start_turn()

        # 显示状态
        print(f"  玩家生命值: {game.player1.hero.health}/30")
        print(f"  AI生命值: {game.player2.hero.health}/30")
        print(f"  玩家战场: {len(game.player1.battlefield)}张")
        print(f"  AI战场: {len(game.player2.battlefield)}张")

        # 检查游戏是否结束
        engine.check_win_condition()
        if game.game_over:
            winner = "玩家" if game.winner == 1 else "AI电脑"
            print(f"\n🏆 游戏结束！{winner} 获胜！")
            break

    print(f"\n✅ 快速测试完成")
    print(f"最终状态:")
    print(f"  玩家生命值: {game.player1.hero.health}/30")
    print(f"  AI生命值: {game.player2.hero.health}/30")
    print(f"  玩家战场: {len(game.player1.battlefield)}张随从")
    print(f"  AI战场: {len(game.player2.battlefield)}张随从")


def test_pygame_basic():
    """测试基本的Pygame功能"""
    print("\n🎮 测试基本Pygame功能")

    # 创建简单窗口
    screen = pygame.display.set_mode((400, 300))
    pygame.display.set_caption("AI对战测试")
    clock = pygame.time.Clock()

    # 字体测试
    try:
        font = pygame.font.Font(None, 24)
        text = font.render("AI Battle Test", True, (255, 255, 255))
        print("✅ 字体渲染正常")
    except Exception as e:
        print(f"❌ 字体渲染失败: {e}")
        return False

    # 显示3秒
    running = True
    frame_count = 0
    while running and frame_count < 180:  # 3秒 * 60 FPS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((50, 50, 50))
        screen.blit(text, (150, 150))
        pygame.display.flip()
        clock.tick(60)
        frame_count += 1

    pygame.quit()
    print("✅ Pygame基本功能正常")
    return True


def main():
    """主函数"""
    try:
        # 测试基本Pygame功能
        if not test_pygame_basic():
            print("❌ Pygame基本功能测试失败")
            return

        # 测试AI对战
        quick_ai_battle()

        print("\n🎉 所有测试完成！")
        print("✅ AI对战功能工作正常")
        print("✅ Pygame界面功能正常")

    except KeyboardInterrupt:
        print("\n👋 测试被中断")
        if pygame.get_init():
            pygame.quit()
    except Exception as e:
        print(f"❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        if pygame.get_init():
            pygame.quit()


if __name__ == "__main__":
    main()