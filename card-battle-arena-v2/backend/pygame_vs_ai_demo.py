#!/usr/bin/env python3
"""
卡牌对战竞技场 V2 - 增强版Pygame AI对战演示
支持完整的玩家vs AI对战，包含AI操作动画和视觉反馈
"""

import sys
import time
import pygame
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from app.game.engine import GameEngine
from app.game.cards import Card, CardType
from app.visualization.pygame_renderer import PygameRenderer


class EnhancedPygameRenderer(PygameRenderer):
    """增强版Pygame渲染器，支持AI对战"""

    def __init__(self, width=1200, height=800):
        super().__init__(width, height)
        self.ai_thinking = False
        self.ai_action_message = ""
        self.ai_message_timer = 0
        self.highlighted_cards = []

    def render_ai_thinking(self, is_thinking: bool = False):
        """渲染AI思考状态"""
        self.ai_thinking = is_thinking

    def set_ai_action_message(self, message: str):
        """设置AI操作消息"""
        self.ai_action_message = message
        self.ai_message_timer = pygame.time.get_ticks() + 2000  # 显示2秒

    def highlight_card(self, card, highlight: bool = True):
        """高亮显示卡牌"""
        if highlight and card not in self.highlighted_cards:
            self.highlighted_cards.append(card)
        elif not highlight and card in self.highlighted_cards:
            self.highlighted_cards.remove(card)

    def render_game_state(self, game):
        """重写游戏状态渲染，添加AI支持"""
        if not self.screen:
            return

        # 清屏
        self.screen.fill(self.LIGHT_GRAY)

        # 绘制标题背景
        title_bg = pygame.Rect(0, 0, self.width, 70)
        pygame.draw.rect(self.screen, self.DARK_GREEN, title_bg)

        # 绘制标题
        if self.large_font and self.screen:
            current = game.current_player
            opponent = game.opponent

            # 显示当前回合和AI状态
            if current.name == "AI电脑":
                title_text = f"🤖 {current.name}的回合 - 回合 {game.turn_number}"
                if self.ai_thinking:
                    title_text += " [思考中]"
            else:
                title_text = f"👤 {current.name}的回合 - 回合 {game.turn_number}"

            try:
                title_surface = self.large_font.render(title_text, True, self.WHITE)
                title_rect = title_surface.get_rect(center=(self.width // 2, 35))
                self.screen.blit(title_surface, title_rect)
            except:
                title_text = f"Turn {game.turn_number} - {current.name}"
                title_surface = self.large_font.render(title_text, True, self.WHITE)
                title_rect = title_surface.get_rect(center=(self.width // 2, 35))
                self.screen.blit(title_surface, title_rect)

        # 绘制玩家信息区域
        pygame.draw.rect(self.screen, self.LIGHT_BLUE, (0, 70, self.width // 2, 120))
        pygame.draw.rect(self.screen, self.LIGHT_BLUE, (self.width // 2, 70, self.width // 2, 120))

        # 绘制玩家信息
        current = game.current_player
        opponent = game.opponent

        # 当前玩家信息（左侧）
        if self.medium_font and self.screen:
            try:
                player_name = self.medium_font.render(f"{current.name}", True, self.BLACK)
            except:
                player_name = self.medium_font.render("Player", True, self.BLACK)
            self.screen.blit(player_name, (50, self.player_info_y))

        if self.font and self.screen:
            try:
                player_health = self.font.render(f"生命值: {current.hero.health}/30 HP", True, self.RED)
            except:
                player_health = self.font.render(f"HP: {current.hero.health}/30", True, self.RED)
            self.screen.blit(player_health, (50, self.player_info_y + 40))

        # 对手玩家信息（右侧）
        if self.medium_font and self.screen:
            try:
                opponent_name = self.medium_font.render(f"{opponent.name}", True, self.BLACK)
            except:
                opponent_name = self.medium_font.render("Opponent", True, self.BLACK)
            self.screen.blit(opponent_name, (self.width - 200, self.opponent_info_y))

        if self.font and self.screen:
            try:
                opponent_health = self.font.render(f"生命值: {opponent.hero.health}/30 HP", True, self.RED)
            except:
                opponent_health = self.font.render(f"HP: {opponent.hero.health}/30", True, self.RED)
            self.screen.blit(opponent_health, (self.width - 200, self.opponent_info_y + 40))

        # 法力值显示
        mana_text = f"法力值: {current.current_mana}/{current.max_mana}"
        mana_bar_width = min(250, self.width // 3)
        mana_bar_height = 25
        mana_bar_x = 50
        mana_bar_y = self.mana_bar_y

        # 法力值背景条
        pygame.draw.rect(self.screen, self.DARK_GRAY,
                        (mana_bar_x, mana_bar_y, mana_bar_width, mana_bar_height))

        # 当前法力值条
        current_mana_width = int((current.current_mana / current.max_mana) * mana_bar_width)
        pygame.draw.rect(self.screen, self.BLUE,
                        (mana_bar_x, mana_bar_y, current_mana_width, mana_bar_height))

        # 法力值文字
        if self.font and self.screen:
            try:
                mana_text_render = self.font.render(mana_text, True, self.BLACK)
            except:
                mana_text_render = self.font.render(mana_text, True, self.BLACK)
            self.screen.blit(mana_text_render, (mana_bar_x, mana_bar_y - 35))

        # 手牌显示区域背景
        hand_area_bg = pygame.Rect(0, self.hand_area_y - 50, self.width, 220)
        pygame.draw.rect(self.screen, self.GRAY, hand_area_bg, 3)

        # 手牌显示
        self._render_hand(current.hand, (50, self.hand_area_y))

        # 战场显示区域背景
        player_battlefield_bg = pygame.Rect(0, self.player_battlefield_y - 50, self.width, 180)
        opponent_battlefield_bg = pygame.Rect(0, self.opponent_battlefield_y - 50, self.width, 180)
        pygame.draw.rect(self.screen, self.LIGHT_BLUE, player_battlefield_bg, 2)
        pygame.draw.rect(self.screen, self.LIGHT_BLUE, opponent_battlefield_bg, 2)

        # 战场显示（当前玩家）
        self._render_battlefield(current.battlefield, (50, self.player_battlefield_y), "你的战场")

        # 战场显示（对手）
        self._render_battlefield(opponent.battlefield, (50, self.opponent_battlefield_y), "对手战场")

        # 显示AI操作消息
        if self.ai_action_message and pygame.time.get_ticks() < self.ai_message_timer:
            if self.small_font and self.screen:
                try:
                    message_surface = self.small_font.render(self.ai_action_message, True, self.ORANGE)
                    message_rect = message_surface.get_rect(center=(self.width // 2, self.height // 2))

                    # 绘制消息背景
                    bg_rect = message_rect.inflate(20, 10)
                    pygame.draw.rect(self.screen, self.BLACK, bg_rect)
                    pygame.draw.rect(self.screen, self.ORANGE, bg_rect, 2)

                    self.screen.blit(message_surface, message_rect)
                except:
                    pass

        # 操作提示区域
        instructions_bg = pygame.Rect(0, self.height - 60, self.width, 60)
        pygame.draw.rect(self.screen, self.DARK_GRAY, instructions_bg)

        # 操作提示
        if self.small_font and self.screen:
            try:
                instructions = "鼠标: 左键选择/出牌, 右键取消 | 键盘: ←→选择, 空格选中, 回车出牌 | 按键: N-结束回合, ESC-退出"
                instructions_text = self.small_font.render(instructions, True, self.WHITE)
            except:
                instructions = "Mouse: Left-Select/Play, Right-Cancel | Keys: ←→Select, Space-Select, Enter-Play | Keys: N-End Turn, ESC-Exit"
                instructions_text = self.small_font.render(instructions, True, self.WHITE)
            instructions_rect = instructions_text.get_rect(center=(self.width // 2, self.height - 30))
            self.screen.blit(instructions_text, instructions_rect)

        # 更新显示
        pygame.display.flip()

    def _render_hand(self, hand, position):
        """重写手牌渲染，支持高亮"""
        x, y = position
        if self.font and self.screen:
            try:
                hand_title = self.font.render("手牌:", True, self.BLACK)
            except:
                hand_title = self.font.render("Hand:", True, self.BLACK)
            self.screen.blit(hand_title, (x, y - 40))

        # 计算手牌位置以防止重叠
        max_displayed_cards = min(len(hand), self.max_cards_per_row)
        displayed_hand = hand[:max_displayed_cards]

        for i, card in enumerate(displayed_hand):
            card_x = x + i * self.card_spacing

            # 检查是否需要高亮
            is_highlighted = card in self.highlighted_cards

            # 如果是选中的卡牌，稍微抬高一些
            card_y = y - 25 if (self.selected_card and i == self.selected_card_index) else y
            card_y = y - 25 if is_highlighted else card_y

            is_keyboard_selected = (i == self.keyboard_selected_index)
            is_selected = (i == self.selected_card_index) or is_highlighted

            self.render_card(card, (card_x, card_y), is_selected, is_keyboard_selected)

    def show_ai_action_result(self, action: str, card_name: str = None, success: bool = True):
        """显示AI操作结果"""
        if success:
            self.set_ai_action_message(f"✅ AI {action}: {card_name}")
        else:
            self.set_ai_action_message(f"❌ AI {action} 失败: {card_name}")


def ai_turn_enhanced(engine, game, renderer):
    """增强版AI回合 - 带动画和视觉反馈"""
    current = game.current_player
    print(f"\n🤖 {current.name}的回合开始！")

    # 显示AI思考状态
    renderer.render_ai_thinking(True)
    renderer.render_game_state(game)
    renderer.update_display()

    # 模拟AI思考时间
    time.sleep(1.5)

    # AI出牌阶段
    cards_played = 0
    max_plays = 3

    while cards_played < max_plays and current.current_mana > 0:
        playable_cards = [card for card in current.hand if card.cost <= current.current_mana]

        if not playable_cards:
            renderer.set_ai_action_message("💭 AI没有可出的卡牌了")
            break

        # AI选择策略：优先高攻击力随从
        if any(card.card_type == CardType.MINION for card in playable_cards):
            minion_cards = [card for card in playable_cards if card.card_type == CardType.MINION]
            minion_cards.sort(key=lambda x: x.attack, reverse=True)
            card = minion_cards[0]
        else:
            playable_cards.sort(key=lambda x: x.cost)
            card = playable_cards[0]

        # 高亮AI选择的卡牌
        renderer.highlight_card(card, True)
        renderer.set_ai_action_message(f"🤖 AI选择打出 {card.name} (费用:{card.cost})")
        renderer.render_game_state(game)
        renderer.update_display()
        time.sleep(1)

        # 执行出牌
        result = engine.play_card(card)
        if result.success:
            renderer.show_ai_action_result("出牌", card.name, True)
            cards_played += 1
            time.sleep(1)
        else:
            renderer.show_ai_action_result("出牌", card.name, False)
            break

        # 取消高亮
        renderer.highlight_card(card, False)

    # AI攻击阶段
    attackable_minions = [m for m in current.battlefield if m.can_attack]
    if attackable_minions:
        renderer.set_ai_action_message("⚔️ AI考虑攻击...")
        renderer.render_game_state(game)
        renderer.update_display()
        time.sleep(1)

        for attacker in attackable_minions[:2]:  # 最多攻击2次
            targets = [game.opponent.hero] + game.opponent.battlefield

            for target in targets:
                renderer.set_ai_action_message(f"⚔️ {attacker.name} 攻击 {target.name if hasattr(target, 'name') else '英雄'}")
                renderer.render_game_state(game)
                renderer.update_display()
                time.sleep(1)

                result = engine.attack_with_minion(attacker, target)
                if result.success:
                    renderer.show_ai_action_result("攻击", f"{attacker.name} vs {target.name}", True)
                    break
                else:
                    renderer.show_ai_action_result("攻击", f"{attacker.name} vs {target.name}", False)

    # 结束AI回合
    renderer.set_ai_action_message(f"🔄 {current.name}结束回合")
    renderer.render_game_state(game)
    renderer.update_display()
    time.sleep(1)
    engine.end_turn()

    # 隐藏AI思考状态
    renderer.render_ai_thinking(False)


def main():
    """主函数"""
    print("🎮 卡牌对战竞技场 V2 - 增强版Pygame AI对战")
    print("=" * 70)
    print("🎯 玩家 vs AI电脑 - 完整对战演示")
    print("✨ 包含AI思考动画和视觉反馈")
    print("🤖 AI会自动出牌、攻击、使用策略")
    print("=" * 70)

    # 创建游戏引擎和增强版渲染器
    engine = GameEngine()
    renderer = EnhancedPygameRenderer(1200, 800)

    # 创建游戏
    game = engine.create_game("玩家", "AI电脑")

    # 创建窗口
    screen = renderer.create_window("卡牌对战竞技场 - 增强版AI对战")

    # 游戏主循环
    running = True
    turn_count = 0
    max_turns = 10

    print("✅ 游戏创建成功！")
    print("🎮 现在将开始自动演示玩家vs AI对战...")
    print("💡 关闭窗口退出游戏")
    time.sleep(2)

    # 开始游戏
    engine.start_turn()

    while running and not game.game_over and turn_count < max_turns:
        turn_count += 1

        # AI模式处理
        if game.current_player.name == "AI电脑":
            ai_turn_enhanced(engine, game, renderer)
            engine.start_turn()

        # 检查游戏是否结束
        engine.check_win_condition()

        if game.game_over:
            break

        # 处理事件（允许用户交互）
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    break
                elif event.key == pygame.K_n and game.current_player.name == "玩家":  # 玩家结束回合
                    print(f"🔄 {game.current_player.name} 结束回合")
                    engine.end_turn()
                    engine.start_turn()

        # 渲染游戏状态
        renderer.render_game_state(game)

        # 更新显示
        renderer.update_display()

        # 短暂延迟控制游戏速度
        pygame.time.wait(100)

    # 显示游戏结果
    print("\n" + "=" * 70)
    if game.game_over:
        winner_name = "玩家" if game.winner == 1 else "AI电脑"
        print(f"🏆 游戏结束！{winner_name} 获胜！")

        print(f"\n📊 最终统计:")
        print(f"  - 总回合数: {game.turn_number}")
        print(f"  - 玩家血量: {game.player1.hero.health}/30")
        print(f"  - AI血量: {game.player2.hero.health}/30")
        print(f"  - 玩家战场: {len(game.player1.battlefield)}张随从")
        print(f"  - AI战场: {len(game.player2.battlefield)}张随从")
    else:
        print("⏰ 演示时间结束，游戏仍在进行中...")

    print("\n🎉 增强版AI对战演示完成！")
    print("💡 特性：AI思考动画、操作提示、视觉反馈")
    print("🎮 下一版本将支持更多游戏模式和AI难度")

    # 退出Pygame
    pygame.quit()
    print("游戏已退出")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 游戏被中断")
    except Exception as e:
        print(f"❌ 游戏出错: {e}")
        import traceback
        traceback.print_exc()
        pygame.quit()