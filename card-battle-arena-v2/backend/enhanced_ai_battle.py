#!/usr/bin/env python3
"""
增强版AI对战演示
包含完整的游戏流程、视觉效果和交互功能
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
from app.visualization.design.tokens import DesignTokens
from app.visualization.components.card_renderer import CardRenderer
from app.visualization.components.layout_engine import LayoutEngine


class EnhancedAIBattle:
    """增强版AI对战类"""

    def __init__(self, width=1200, height=800):
        """初始化增强版AI对战"""
        # 首先初始化pygame
        pygame.init()

        self.width = width
        self.height = height
        self.screen = None
        self.clock = None

        # 设计系统和组件
        self.tokens = DesignTokens()
        self.layout_engine = LayoutEngine(width, height)
        self.card_renderer = CardRenderer()

        # 游戏状态
        self.engine = None
        self.game = None
        self.running = True
        self.turn_count = 0
        self.max_turns = 15

        # AI状态
        self.ai_thinking = False
        self.ai_action_message = ""
        self.ai_message_timer = 0

        # 动画效果
        self.animations = []

        # 字体
        self.fonts = {}
        self._init_fonts()

    def _init_fonts(self):
        """初始化字体"""
        try:
            # 尝试加载中文字体
            font_names = ["simhei.ttf", "simsun.ttc", "msyh.ttc"]

            # Windows系统字体路径
            import os
            if os.name == "nt":
                font_paths = [
                    "C:/Windows/Fonts/simhei.ttf",
                    "C:/Windows/Fonts/simsun.ttc",
                    "C:/Windows/Fonts/msyh.ttc"
                ]
                font_names.extend(font_paths)

            font_loaded = False
            for font_name in font_names:
                try:
                    font = pygame.font.Font(font_name, 24)
                    if font:
                        self.fonts['default'] = font
                        font_loaded = True
                        break
                except:
                    continue

            # 如果无法加载中文字体，使用系统默认字体
            if not font_loaded:
                self.fonts['default'] = pygame.font.SysFont("simhei", 24)
                if not self.fonts['default']:
                    self.fonts['default'] = pygame.font.Font(None, 24)

        except Exception as e:
            print(f"字体初始化失败: {e}")
            self.fonts['default'] = pygame.font.Font(None, 24)

        # 创建不同大小的字体
        base_font = self.fonts['default']
        self.fonts.update({
            'title': pygame.font.Font(None, 48),
            'heading': pygame.font.Font(None, 32),
            'body': pygame.font.Font(None, 24),
            'small': pygame.font.Font(None, 18),
        })

    def create_window(self):
        """创建游戏窗口"""
        try:
            self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
            pygame.display.set_caption("卡牌对战竞技场 - 增强版AI对战")
            self.clock = pygame.time.Clock()
            return True
        except Exception as e:
            print(f"创建窗口失败: {e}")
            return False

    def start_game(self):
        """开始游戏"""
        # 创建游戏引擎
        self.engine = GameEngine()
        self.game = self.engine.create_game("玩家", "AI电脑")
        self.engine.start_turn()

        print("🎮 增强版AI对战开始！")
        print("=" * 50)

    def ai_turn_enhanced(self):
        """增强版AI回合，带视觉效果"""
        current = self.game.current_player

        # 显示AI思考状态
        self.ai_thinking = True
        self.ai_action_message = "🤔 AI思考中..."
        self.ai_message_timer = pygame.time.get_ticks() + 1500

        # 渲染思考状态
        self.render_game_state()
        pygame.display.flip()

        # 模拟思考时间
        time.sleep(1.5)

        # AI出牌阶段
        cards_played = 0
        max_plays = 3

        while cards_played < max_plays and current.current_mana > 0:
            playable_cards = [card for card in current.hand if card.cost <= current.current_mana]

            if not playable_cards:
                self.ai_action_message = "💭 AI没有可出的卡牌了"
                self.ai_message_timer = pygame.time.get_ticks() + 2000
                break

            # AI选择策略
            if any(card.card_type == CardType.MINION for card in playable_cards):
                minion_cards = [card for card in playable_cards if card.card_type == CardType.MINION]
                minion_cards.sort(key=lambda x: x.attack, reverse=True)
                card = minion_cards[0]
            else:
                playable_cards.sort(key=lambda x: x.cost)
                card = playable_cards[0]

            # 显示AI选择
            self.ai_action_message = f"🎴 AI选择 {card.name} (费用:{card.cost})"
            self.ai_message_timer = pygame.time.get_ticks() + 2000

            self.render_game_state()
            pygame.display.flip()
            time.sleep(1)

            # 执行出牌
            result = self.engine.play_card(card)
            if result.success:
                self.ai_action_message = f"✅ AI成功打出 {card.name}"
                self.ai_message_timer = pygame.time.get_ticks() + 1500
                cards_played += 1
                time.sleep(1)
            else:
                self.ai_action_message = f"❌ AI出牌失败"
                self.ai_message_timer = pygame.time.get_ticks() + 2000
                break

        # AI攻击阶段
        attackable_minions = [m for m in current.battlefield if m.can_attack]
        if attackable_minions:
            self.ai_action_message = "⚔️ AI考虑攻击..."
            self.ai_message_timer = pygame.time.get_ticks() + 2000

            self.render_game_state()
            pygame.display.flip()
            time.sleep(1)

            for attacker in attackable_minions[:2]:  # 最多攻击2次
                targets = [self.game.opponent.hero] + self.game.opponent.battlefield

                for target in targets:
                    target_name = target.name if hasattr(target, 'name') else '英雄'
                    self.ai_action_message = f"⚔️ {attacker.name} 攻击 {target_name}"
                    self.ai_message_timer = pygame.time.get_ticks() + 2000

                    self.render_game_state()
                    pygame.display.flip()
                    time.sleep(1)

                    result = self.engine.attack_with_minion(attacker, target)
                    if result.success:
                        self.ai_action_message = f"✅ 攻击成功！"
                        self.ai_message_timer = pygame.time.get_ticks() + 1000
                        break
                    else:
                        self.ai_action_message = f"❌ 攻击失败"
                        self.ai_message_timer = pygame.time.get_ticks() + 2000

        # 结束AI回合
        self.ai_action_message = f"🔄 {current.name}结束回合"
        self.ai_message_timer = pygame.time.get_ticks() + 1500

        self.render_game_state()
        pygame.display.flip()
        time.sleep(1)

        self.engine.end_turn()
        self.ai_thinking = False

    def render_game_state(self):
        """渲染游戏状态"""
        if not self.screen:
            return

        # 清屏
        self.screen.fill(self.tokens.COLORS['surface']['board'])

        # 计算布局
        layout = self.layout_engine.calculate_layout()
        regions = layout['regions']

        # 渲染各个区域
        self._render_title(regions['title'])
        self._render_player_info(regions['player_info'], self.game.player1, "玩家")
        self._render_player_info(regions['opponent_info'], self.game.player2, "AI电脑")
        self._render_battlefield(regions['player_battlefield'], self.game.player1.battlefield, "玩家战场")
        self._render_battlefield(regions['opponent_battlefield'], self.game.player2.battlefield, "AI战场")
        self._render_hand(regions['hand'], self.game.current_player.hand)
        self._render_ai_message()
        self._render_instructions(regions['instructions'])

    def _render_title(self, title_rect):
        """渲染标题"""
        # 绘制标题背景
        pygame.draw.rect(self.screen, self.tokens.COLORS['primary']['main'], title_rect)

        # 绘制标题文字
        font = self.fonts.get('title')
        if font:
            current = self.game.current_player
            ai_status = " [AI思考中]" if self.ai_thinking and current.name == "AI电脑" else ""

            try:
                title_text = font.render(f"卡牌对战竞技场 - 回合 {self.turn_count}{ai_status}", True, (255, 255, 255))
            except:
                title_text = font.render(f"Card Battle Arena - Turn {self.turn_count}{ai_status}", True, (255, 255, 255))

            title_rect_center = title_text.get_rect(center=title_rect.center)
            self.screen.blit(title_text, title_rect_center)

    def _render_player_info(self, info_rect, player, title):
        """渲染玩家信息"""
        # 绘制信息背景
        bg_color = self.tokens.COLORS['primary']['light'] if player.name == self.game.current_player.name else self.tokens.COLORS['surface']['ui']
        pygame.draw.rect(self.screen, bg_color, info_rect)
        pygame.draw.rect(self.screen, self.tokens.COLORS['ui']['border'], info_rect, 2)

        # 绘制玩家信息
        font = self.fonts.get('heading')
        if font:
            try:
                name_text = font.render(f"{player.name}", True, self.tokens.COLORS['ui']['text'])
            except:
                name_text = font.render("Player", True, self.tokens.COLORS['ui']['text'])
            self.screen.blit(name_text, (info_rect.x + 20, info_rect.y + 10))

        # 绘制生命值
        font = self.fonts.get('body')
        if font:
            health_text = font.render(f"❤️ 生命值: {player.hero.health}/30", True, (255, 100, 100))
            self.screen.blit(health_text, (info_rect.x + 20, info_rect.y + 60))

            # 绘制法力值
            mana_text = font.render(f"💰 法力值: {player.current_mana}/{player.max_mana}", True, (100, 100, 255))
            self.screen.blit(mana_text, (info_rect.x + 20, info_rect.y + 90))

    def _render_battlefield(self, battlefield_rect, battlefield, title):
        """渲染战场"""
        # 绘制战场背景
        pygame.draw.rect(self.screen, self.tokens.COLORS['surface']['ui'], battlefield_rect, 2)

        # 绘制标题
        font = self.fonts.get('body')
        if font:
            try:
                title_text = font.render(f"{title} ({len(battlefield)}张)", True, self.tokens.COLORS['ui']['text'])
            except:
                title_text = font.render(f"Battlefield ({len(battlefield)})", True, self.tokens.COLORS['ui']['text'])
            self.screen.blit(title_text, (battlefield_rect.x + 20, battlefield_rect.y - 30))

        # 计算卡牌位置
        card_positions = self.layout_engine.calculate_card_positions(len(battlefield), battlefield_rect)

        # 渲染卡牌
        for i, (card, pos) in enumerate(zip(battlefield, card_positions)):
            self.card_renderer.render_card(card, pos, self.screen)

    def _render_hand(self, hand_rect, hand):
        """渲染手牌"""
        # 绘制手牌背景
        pygame.draw.rect(self.screen, self.tokens.COLORS['surface']['ui'], hand_rect, 2)

        # 绘制标题
        font = self.fonts.get('body')
        if font:
            current_player = self.game.current_player
            try:
                title_text = font.render(f"{current_player.name}的手牌 ({len(hand)}张):", True, self.tokens.COLORS['ui']['text'])
            except:
                title_text = font.render(f"{current_player.name}'s Hand ({len(hand)}):", True, self.tokens.COLORS['ui']['text'])
            self.screen.blit(title_text, (hand_rect.x + 20, hand_rect.y - 30))

        # 计算卡牌位置
        card_positions = self.layout_engine.calculate_card_positions(len(hand), hand_rect)

        # 渲染卡牌
        for i, (card, pos) in enumerate(zip(hand, card_positions)):
            # 只渲染当前玩家的手牌
            if card in self.game.current_player.hand:
                self.card_renderer.render_card(card, pos, self.screen)

    def _render_ai_message(self):
        """渲染AI操作消息"""
        if self.ai_action_message and pygame.time.get_ticks() < self.ai_message_timer:
            font = self.fonts.get('heading')
            if font:
                try:
                    message_surface = font.render(self.ai_action_message, True, (255, 200, 0))
                except:
                    message_surface = font.render("AI Action...", True, (255, 200, 0))

                message_rect = message_surface.get_rect(center=(self.width // 2, self.height // 2))

                # 绘制消息背景
                bg_rect = message_rect.inflate(40, 20)
                pygame.draw.rect(self.screen, (0, 0, 0), bg_rect)
                pygame.draw.rect(self.screen, (255, 200, 0), bg_rect, 3)

                self.screen.blit(message_surface, message_rect)

    def _render_instructions(self, instructions_rect):
        """渲染操作提示"""
        # 绘制提示背景
        pygame.draw.rect(self.screen, self.tokens.COLORS['ui']['background'], instructions_rect)

        # 绘制提示文字
        font = self.fonts.get('small')
        if font:
            try:
                instructions = "ESC - 退出 | 空格 - 快速结束回合 | 观看AI自动对战演示"
                instructions_text = font.render(instructions, True, self.tokens.COLORS['ui']['text'])
            except:
                instructions = "ESC - Exit | Space - Skip Turn | Watch AI vs AI Demo"
                instructions_text = font.render(instructions, True, self.tokens.COLORS['ui']['text'])

            instructions_rect_center = instructions_text.get_rect(center=instructions_rect.center)
            self.screen.blit(instructions_text, instructions_rect_center)

    def handle_events(self):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_SPACE:  # 空格键快速结束回合
                    if self.game.current_player.name == "玩家":
                        self.engine.end_turn()
                        self.engine.start_turn()
                        self.turn_count += 1
            elif event.type == pygame.VIDEORESIZE:
                self.width = event.w
                self.height = event.h
                self.layout_engine.update_window_size(event.w, event.h)
                self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

        return True

    def run(self):
        """运行游戏主循环"""
        if not self.create_window():
            return False

        self.start_game()

        while self.running and not self.game.game_over and self.turn_count < self.max_turns:
            # 处理事件
            self.running = self.handle_events()

            # AI回合处理
            if self.game.current_player.name == "AI电脑":
                self.ai_turn_enhanced()
                self.engine.start_turn()
                self.turn_count += 1
            else:
                # 玩家回合（自动结束，用于演示）
                time.sleep(1)  # 让玩家看到自己的回合
                self.engine.end_turn()
                self.engine.start_turn()
                self.turn_count += 1

            # 检查游戏是否结束
            self.engine.check_win_condition()

            # 渲染游戏状态
            self.render_game_state()

            # 更新显示
            pygame.display.flip()
            self.clock.tick(30)  # 30 FPS

        # 显示游戏结果
        self._show_game_result()

        return True

    def _show_game_result(self):
        """显示游戏结果"""
        if self.game.game_over:
            winner_name = "玩家" if self.game.winner == 1 else "AI电脑"
            print(f"\n🏆 游戏结束！{winner_name} 获胜！")

            # 在屏幕上显示结果
            self.screen.fill(self.tokens.COLORS['surface']['board'])

            font = self.fonts.get('title')
            if font:
                try:
                    result_text = font.render(f"🏆 {winner_name} 获胜！", True, (255, 215, 0))
                except:
                    result_text = font.render(f"Winner: {winner_name}!", True, (255, 215, 0))

                result_rect = result_text.get_rect(center=(self.width // 2, self.height // 2 - 50))
                self.screen.blit(result_text, result_rect)

            # 显示统计信息
            font = self.fonts.get('body')
            if font:
                stats = [
                    f"总回合数: {self.turn_count}",
                    f"玩家生命值: {self.game.player1.hero.health}/30",
                    f"AI生命值: {self.game.player2.hero.health}/30",
                    f"玩家战场: {len(self.game.player1.battlefield)}张随从",
                    f"AI战场: {len(self.game.player2.battlefield)}张随从"
                ]

                for i, stat in enumerate(stats):
                    try:
                        stat_text = font.render(stat, True, (255, 255, 255))
                    except:
                        stat_text = font.render(stat, True, (255, 255, 255))

                    stat_rect = stat_text.get_rect(center=(self.width // 2, self.height // 2 + 50 + i * 40))
                    self.screen.blit(stat_text, stat_rect)

            pygame.display.flip()

            # 等待几秒或用户按键
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                        waiting = False
                    elif event.type == pygame.KEYDOWN:
                        waiting = False

                pygame.time.wait(100)
        else:
            print(f"\n⏰ 演示结束（{self.turn_count}回合）")

        print(f"\n📊 最终统计:")
        print(f"  总回合数: {self.turn_count}")
        print(f"  玩家生命值: {self.game.player1.hero.health}/30")
        print(f"  AI生命值: {self.game.player2.hero.health}/30")
        print(f"  玩家战场: {len(self.game.player1.battlefield)}张随从")
        print(f"  AI战场: {len(self.game.player2.battlefield)}张随从")

        # 退出Pygame
        pygame.quit()
        print("🎉 增强版AI对战演示完成！")


def main():
    """主函数"""
    print("🎮 卡牌对战竞技场 V2 - 增强版AI对战演示")
    print("=" * 60)
    print("✨ 包含完整的视觉效果和AI对战流程")
    print("🤖 AI会自动进行策略思考和操作")
    print("🎨 现代化的UI设计和视觉反馈")
    print("=" * 60)

    try:
        battle = EnhancedAIBattle()
        success = battle.run()

        if success:
            print("✅ 演示成功完成")
        else:
            print("❌ 演示启动失败")

    except KeyboardInterrupt:
        print("\n👋 演示被中断")
        pygame.quit()
    except Exception as e:
        print(f"❌ 演示出错: {e}")
        import traceback
        traceback.print_exc()
        pygame.quit()


if __name__ == "__main__":
    main()