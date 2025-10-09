"""
交互式游戏渲染器

整合所有UI组件，提供完整的交互式游戏体验。
"""

import pygame
import sys
from typing import Optional, List, Tuple
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.game.engine import GameEngine
from app.game.cards import Card
from app.game.state import GameState, Player

from .ui.card_component import InteractiveCard
from .ui.hand_area import HandArea
from .ui.battlefield import BattlefieldZone
from .ui.game_hud import GameHUD
from .ui.target_selector import TargetSelector


class InteractiveRenderer:
    """
    交互式游戏渲染器

    整合所有UI组件，提供完整的交互式游戏体验
    """

    def __init__(self, width: int = 1200, height: int = 800):
        """
        初始化交互式渲染器

        Args:
            width: 窗口宽度
            height: 窗口高度
        """
        self.width = width
        self.height = height

        # Pygame初始化
        self.screen = None
        self.clock = None
        self.running = False

        # 游戏状态
        self.game: Optional[GameState] = None
        self.engine = GameEngine()

        # UI组件
        self.hud = GameHUD((0, 0), (width, 70))
        self.player_hand = HandArea((50, height - 200), (width - 100, 150))
        self.player_battlefield = BattlefieldZone((50, 300), (width - 100, 180))
        self.opponent_battlefield = BattlefieldZone((50, 120), (width - 100, 180))

        # 目标选择器
        self.target_selector = TargetSelector(self.game) if self.game else None

        # 交互状态
        self.selected_card: Optional[InteractiveCard] = None
        self.dragging_card: Optional[InteractiveCard] = None
        self.current_turn_player = None

        # 同步状态数据
        self.current_mana_display = "1/1"
        self.player1_health_display = "30/30"
        self.player2_health_display = "30/30"
        self.turn_display = "玩家1的回合 - 回合 1"

        # 字体（延迟加载）
        self.font = None
        self.fonts_loaded = False

    def _load_fonts(self):
        """加载字体（延迟加载）"""
        if self.fonts_loaded:
            return

        try:
            if not pygame.get_init():
                pygame.init()
            self.font = pygame.font.Font(None, 24)
            self.fonts_loaded = True
        except:
            # 如果加载失败，使用默认字体
            try:
                if not pygame.get_init():
                    pygame.init()
                self.font = pygame.font.Font(pygame.font.get_default_font(), 24)
                self.fonts_loaded = True
            except:
                # 如果连默认字体都加载失败，使用空对象
                self.font = None
                self.fonts_loaded = True

    def create_window(self, title: str = "卡牌对战竞技场 - 交互式") -> bool:
        """
        创建游戏窗口

        Args:
            title: 窗口标题

        Returns:
            bool: 是否成功创建窗口
        """
        try:
            pygame.init()
            self.screen = pygame.display.set_mode((self.width, self.height))
            pygame.display.set_caption(title)
            self.clock = pygame.time.Clock()
            self.running = True
            return True
        except Exception as e:
            print(f"创建窗口失败: {e}")
            return False

    def initialize_game(self, player1_name: str = "玩家", player2_name: str = "AI电脑") -> bool:
        """
        初始化游戏

        Args:
            player1_name: 玩家1名称
            player2_name: 玩家2名称

        Returns:
            bool: 是否成功初始化游戏
        """
        try:
            self.game = self.engine.create_game(player1_name, player2_name)
            self.current_turn_player = self.game.current_player

            # 更新目标选择器的游戏状态
            self.target_selector = TargetSelector(self.game)

            # 初始化UI组件
            self._initialize_ui_components()

            # 同步初始状态
            self.sync_all_game_state()

            return True
        except Exception as e:
            print(f"初始化游戏失败: {e}")
            return False

    def _initialize_ui_components(self):
        """初始化UI组件"""
        if not self.game:
            return

        # 清空现有组件
        self.player_hand.clear_cards()
        self.player_battlefield.clear_minions()
        self.opponent_battlefield.clear_minions()

        # 初始化玩家手牌
        for card in self.game.current_player.hand:
            self.player_hand.add_card(
                card=card,
                on_click=self._on_card_click,
                on_drag_end=self._on_card_drag_end
            )

        # 初始化战场上的随从
        for card in self.game.current_player.battlefield:
            self.player_battlefield.add_minion(card)

        for card in self.game.opponent.battlefield:
            self.opponent_battlefield.add_minion(card)

    def sync_all_game_state(self):
        """同步所有游戏状态"""
        if not self.game:
            return

        # 同步HUD
        self.hud.update_all(self.game)

        # 同步手牌
        self.sync_hand_cards(self.game.current_player)

        # 同步战场
        self.sync_battlefield()

        # 同步显示数据
        self._sync_display_data()

    def sync_hand_cards(self, player: Player):
        """
        同步手牌显示

        Args:
            player: 玩家对象
        """
        if not player:
            return

        # 清空现有手牌组件
        self.player_hand.clear_cards()

        # 重新创建手牌组件
        for card in player.hand:
            self.player_hand.add_card(
                card=card,
                on_click=self._on_card_click,
                on_drag_end=self._on_card_drag_end
            )

    def sync_battlefield(self):
        """同步战场显示"""
        if not self.game:
            return

        # 清空现有战场
        self.player_battlefield.clear_minions()
        self.opponent_battlefield.clear_minions()

        # 重新添加随从
        for card in self.game.current_player.battlefield:
            self.player_battlefield.add_minion(card)

        for card in self.game.opponent.battlefield:
            self.opponent_battlefield.add_minion(card)

    def _sync_display_data(self):
        """同步显示数据"""
        if not self.game:
            return

        # 同步法力值显示
        self.current_mana_display = f"{self.game.current_player.current_mana}/{self.game.current_player.max_mana}"

        # 同步生命值显示
        self.player1_health_display = f"{self.game.player1.hero.health}/30"
        self.player2_health_display = f"{self.game.player2.hero.health}/30"

        # 同步回合显示
        self.turn_display = f"{self.game.current_player.name}的回合 - 回合 {self.game.turn_number}"

    def update_mana_display(self, player: Player):
        """
        更新法力值显示

        Args:
            player: 玩家对象
        """
        if player == self.game.player1:
            self.hud.update_mana_display(player, True)
        else:
            self.hud.update_mana_display(player, False)
        self.current_mana_display = f"{player.current_mana}/{player.max_mana}"

    def update_health_display(self, game: GameState):
        """
        更新生命值显示

        Args:
            game: 游戏状态
        """
        self.hud.update_health_display(game)
        self.player1_health_display = f"{game.player1.hero.health}/30"
        self.player2_health_display = f"{game.player2.hero.health}/30"

    def update_turn_indicator(self, game: GameState):
        """
        更新回合指示器

        Args:
            game: 游戏状态
        """
        self.hud.update_turn_indicator(game)
        self.turn_display = f"{game.current_player.name}的回合 - 回合 {game.turn_number}"
        self.current_turn_player = game.current_player

    def _on_card_click(self, card: Card):
        """
        处理卡牌点击事件

        Args:
            card: 被点击的卡牌
        """
        if not self.game:
            return

        # 查找对应的卡牌组件
        card_component = None
        for component in self.player_hand.card_components:
            if component.card == card:
                card_component = component
                break

        if card_component:
            # 如果有选中的卡牌，取消选中
            if self.selected_card and self.selected_card != card_component:
                self.selected_card.deselect()

            # 选中/取消选中当前卡牌
            if card_component.is_selected:
                card_component.deselect()
                self.selected_card = None
            else:
                card_component.select()
                self.selected_card = card_component

                # 检查是否可以打出这张卡牌
                if card.cost <= self.game.current_player.current_mana:
                    print(f"选中卡牌: {card.name} (费用: {card.cost})")
                else:
                    print(f"法力值不足，无法打出 {card.name}")

    def _on_card_drag_end(self, card: Card, position: Tuple[int, int]):
        """
        处理卡牌拖拽结束事件

        Args:
            card: 被拖拽的卡牌
            position: 拖拽结束位置
        """
        if not self.game:
            return

        # 检查是否拖拽到战场区域
        if self.player_battlefield.is_valid_drop_position(position):
            # 尝试打出卡牌
            result = self.engine.play_card(card)
            if result.success:
                print(f"成功打出卡牌: {card.name}")
                # 更新UI
                self.sync_all_game_state()
            else:
                print(f"无法打出卡牌: {result.message}")
        else:
            print(f"无效的放置位置: {position}")

        # 重置拖拽状态
        self.dragging_card = None

    def handle_events(self) -> bool:
        """
        处理事件

        Returns:
            bool: 是否继续运行
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左键点击
                    self._handle_mouse_down(event.pos)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # 左键释放
                    self._handle_mouse_up(event.pos)

            elif event.type == pygame.MOUSEMOTION:
                self._handle_mouse_motion(event.pos)

            elif event.type == pygame.KEYDOWN:
                self._handle_key_down(event.key)

        return True

    def _handle_mouse_down(self, position: Tuple[int, int]):
        """
        处理鼠标按下事件

        Args:
            position: 鼠标位置
        """
        # 检查手牌区域
        clicked_card = self.player_hand.handle_click(position)
        if not clicked_card:
            # 尝试开始拖拽
            self.dragging_card = self.player_hand.start_drag(position)

    def _handle_mouse_up(self, position: Tuple[int, int]):
        """
        处理鼠标释放事件

        Args:
            position: 鼠标位置
        """
        if self.dragging_card:
            self.dragging_card.end_drag(position)
            self.dragging_card = None

    def _handle_mouse_motion(self, position: Tuple[int, int]):
        """
        处理鼠标移动事件

        Args:
            position: 鼠标位置
        """
        # 更新手牌悬停状态
        self.player_hand.handle_mouse_motion(position)

        # 更新拖拽卡牌位置
        if self.dragging_card:
            self.dragging_card.move_drag(position)

    def _handle_key_down(self, key):
        """
        处理键盘按下事件

        Args:
            key: 按键
        """
        if key == pygame.K_SPACE:
            # 空格键结束回合
            self._end_turn()
        elif key == pygame.K_ESCAPE:
            # ESC键取消选择
            if self.selected_card:
                self.selected_card.deselect()
                self.selected_card = None

    def _end_turn(self):
        """结束当前回合"""
        if not self.game:
            return

        # 取消所有选中状态
        if self.selected_card:
            self.selected_card.deselect()
            self.selected_card = None

        # 结束回合（这里需要实现实际的结束回合逻辑）
        print(f"结束 {self.game.current_player.name} 的回合")

        # 简化处理：切换玩家
        self.game.current_player, self.game.opponent = self.game.opponent, self.game.current_player
        self.game.turn_number += 1

        # 恢复法力值
        self.game.current_player.current_mana = min(self.game.current_player.max_mana + 1, 10)
        self.game.current_player.max_mana = self.game.current_player.current_mana

        # 抽一张牌
        self.game.current_player.draw_card()

        # 同步UI
        self.sync_all_game_state()

    def render(self):
        """渲染游戏画面"""
        if not self.screen:
            return

        # 确保字体已加载
        self._load_fonts()

        # 清屏
        self.screen.fill((30, 30, 50))

        # 渲染各个组件
        self.hud.render(self.screen)
        self.opponent_battlefield.render(self.screen)
        self.player_battlefield.render(self.screen)
        self.player_hand.render(self.screen)

        # 渲染拖拽中的卡牌（在最上层）
        if self.dragging_card:
            self.dragging_card.render(self.screen)

        # 渲染目标选择高亮
        if self.target_selector and self.target_selector.is_selecting:
            all_target_components = []
            # 收集所有可能的target组件
            all_target_components.extend(self.player_hand.card_components)
            # 这里可以添加更多target组件
            self.target_selector.render_highlights(self.screen, all_target_components)

        # 显示调试信息
        self._render_debug_info()

        # 更新显示
        pygame.display.flip()

    def _render_debug_info(self):
        """渲染调试信息"""
        if not self.font:
            return

        try:
            debug_texts = [
                f"FPS: {int(self.clock.get_fps()) if self.clock else 0}",
                f"当前玩家: {self.current_turn_player.name if self.current_turn_player else 'None'}",
                f"手牌数量: {len(self.player_hand.card_components)}",
                f"战场随从: {len(self.player_battlefield.minions)}",
            ]

            y_offset = 100
            for text in debug_texts:
                surface = self.font.render(text, True, (255, 255, 255))
                self.screen.blit(surface, (10, y_offset))
                y_offset += 25
        except:
            pass

    def run(self) -> int:
        """
        运行游戏主循环

        Returns:
            int: 退出代码
        """
        if not self.create_window():
            return 1

        if not self.initialize_game():
            return 1

        while self.running:
            # 处理事件
            self.running = self.handle_events()

            # 渲染
            self.render()

            # 控制帧率
            if self.clock:
                self.clock.tick(60)

        # 清理
        pygame.quit()
        return 0

    def get_info(self) -> dict:
        """
        获取渲染器信息

        Returns:
            dict: 渲染器信息
        """
        return {
            'width': self.width,
            'height': self.height,
            'running': self.running,
            'has_game': self.game is not None,
            'selected_card': self.selected_card.card if self.selected_card else None,
            'dragging_card': self.dragging_card.card if self.dragging_card else None,
            'current_player': self.current_turn_player.name if self.current_turn_player else None,
            'hand_count': len(self.player_hand.card_components),
            'player_battlefield_count': len(self.player_battlefield.minions),
            'opponent_battlefield_count': len(self.opponent_battlefield.minions)
        }