"""
改进的交互式游戏渲染器

基于TDD方法实现UI布局改进，解决当前布局问题。
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
from .ui_layout_config import UI_LAYOUT_CONFIG, get_region_config, get_component_config
from .window_manager import WindowManager, WindowConfig


class ImprovedInteractiveRenderer:
    """
    改进的交互式游戏渲染器

    基于TDD方法实现UI布局改进，解决手牌空间不足等问题
    """

    def __init__(self, width: int = 1200, height: int = 800,
                 window_config: Optional[WindowConfig] = None):
        """
        初始化改进的交互式渲染器

        Args:
            width: 窗口宽度
            height: 窗口高度
            window_config: 窗口配置，为None时自动创建
        """
        # 创建窗口配置
        if window_config is None:
            window_config = WindowConfig(width=width, height=height)

        # 创建窗口管理器
        self.window_manager = WindowManager(window_config)

        # 保持向后兼容的属性
        self.width = window_config.width
        self.height = window_config.height

        # Pygame相关 (由window_manager管理)
        self.screen = None
        self.clock = None
        self.running = False

        # 游戏状态
        self.game: Optional[GameState] = None
        self.engine = GameEngine()

        # 使用改进的UI布局配置
        self._setup_improved_layout()

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

        # 菜单状态
        self.menu_visible = False
        self.menu_selection = 0
        self.menu_options = [
            "打出手牌 (1)",
            "使用英雄技能 (2)",
            "随从攻击 (3)",
            "英雄攻击 (4)",
            "结束回合 (5)",
            "查看游戏状态 (6)",
            "退出游戏 (7)"
        ]

    def _setup_improved_layout(self):
        """设置改进的UI布局"""
        # 使用窗口管理器获取动态布局区域
        regions = self.window_manager.get_layout_regions()

        # 创建改进的UI组件，使用动态区域配置
        self.hud = GameHUD(regions['hud'][:2], regions['hud'][2:])

        # 改进的手牌区域 - 使用动态布局的高度 (240px)
        self.player_hand = HandArea(regions['hand_area'][:2], regions['hand_area'][2:])

        # 战场区域位置调整
        self.opponent_battlefield = BattlefieldZone(
            regions['opponent_battlefield'][:2],
            regions['opponent_battlefield'][2:]
        )
        self.player_battlefield = BattlefieldZone(
            regions['player_battlefield'][:2],
            regions['player_battlefield'][2:]
        )

        # 添加游戏控制区域
        self.game_controls = GameControlsArea(self)

        # 添加玩家信息显示区域
        self.player_info_display = PlayerInfoDisplay(self)

        # 目标选择器
        self.target_selector = TargetSelector(self.game) if self.game else None

    def _load_fonts(self):
        """加载字体（延迟加载）"""
        if self.fonts_loaded:
            return

        try:
            if not pygame.get_init():
                pygame.init()
            # 使用支持中文的字体
            from .font_manager import get_best_font
            self.font = get_best_font(24, prefer_chinese=True)
            self.fonts_loaded = True
        except Exception as e:
            print(f"字体加载失败: {e}")
            try:
                if not pygame.get_init():
                    pygame.init()
                # 降级到系统字体
                self.font = pygame.font.SysFont('simhei', 24)  # 黑体
                self.fonts_loaded = True
            except:
                try:
                    # 最后降级到默认字体
                    self.font = pygame.font.Font(pygame.font.get_default_font(), 24)
                    self.fonts_loaded = True
                except:
                    self.font = None
                    self.fonts_loaded = True

    def create_window(self, title: str = "卡牌对战竞技场 - 改进版") -> bool:
        """
        创建游戏窗口

        Args:
            title: 窗口标题

        Returns:
            bool: 是否成功创建窗口
        """
        try:
            # 更新窗口标题
            self.window_manager.window_config.title = title

            # 使用窗口管理器创建窗口
            success = self.window_manager.create_window()
            if success:
                # 获取pygame对象
                self.screen = self.window_manager.screen
                self.clock = self.window_manager.clock
                self.running = True

                # 更新内部尺寸属性
                self.width = self.window_manager.window_config.width
                self.height = self.window_manager.window_config.height

                print(f"✓ 窗口创建成功: {self.width}x{self.height}")

            return success
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
        """同步手牌显示"""
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

    def _on_card_click(self, card: Card):
        """处理卡牌点击事件"""
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
        """处理卡牌拖拽结束事件"""
        if not self.game:
            return

        # 检查是否拖拽到战场区域
        if self.player_battlefield.is_valid_drop_position(position):
            # 检查是否有足够的法力值
            if card.cost > self.game.current_player.current_mana:
                print(f"❌ 法力值不足，无法打出 {card.name}")
                return
                
            # 尝试打出卡牌
            result = self.engine.play_card(card)
            if result.success:
                print(f"✅ 成功打出卡牌: {card.name}")
                # 更新UI
                self.sync_all_game_state()
            else:
                print(f"❌ 无法打出卡牌: {result.message}")
        else:
            print(f"❌ 无效的放置位置: {position}")

        # 重置拖拽状态
        self.dragging_card = None

    def handle_events(self) -> bool:
        """处理事件"""
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
        """处理鼠标按下事件"""
        # 检查游戏控制按钮
        if self.game_controls and self.game_controls.handle_click(position):
            return

        # 检查手牌区域
        hand_clicked = self.player_hand.handle_click(position)
        if not hand_clicked:
            # 尝试开始拖拽
            self.dragging_card = self.player_hand.start_drag(position)

    def _handle_mouse_up(self, position: Tuple[int, int]):
        """处理鼠标释放事件"""
        if self.dragging_card:
            self.dragging_card.end_drag(position)
            self.dragging_card = None

    def _handle_mouse_motion(self, position: Tuple[int, int]):
        """处理鼠标移动事件"""
        # 更新手牌悬停状态
        self.player_hand.handle_mouse_motion(position)

        # 更新拖拽卡牌位置
        if self.dragging_card:
            self.dragging_card.move_drag(position)

    def _handle_key_down(self, key):
        """处理键盘按下事件"""
        if key == pygame.K_SPACE:
            # 空格键结束回合
            self._end_turn()
        elif key == pygame.K_ESCAPE:
            # ESC键取消选择或关闭菜单
            if self.menu_visible:
                self.menu_visible = False
            elif self.selected_card:
                self.selected_card.deselect()
                self.selected_card = None
        elif key == pygame.K_m:
            # M键显示/隐藏菜单
            self.menu_visible = not self.menu_visible
            self.menu_selection = 0
        elif self.menu_visible:
            # 菜单导航
            if key == pygame.K_UP:
                self.menu_selection = (self.menu_selection - 1) % len(self.menu_options)
            elif key == pygame.K_DOWN:
                self.menu_selection = (self.menu_selection + 1) % len(self.menu_options)
            elif key == pygame.K_RETURN:
                self._handle_menu_selection()
        elif key == pygame.K_1:
            # 快捷键1: 打出手牌
            self._play_selected_card()
        elif key == pygame.K_2:
            # 快捷键2: 使用英雄技能
            self._use_hero_power()
        elif key == pygame.K_3:
            # 快捷键3: 随从攻击
            self._attack_with_minion()
        elif key == pygame.K_4:
            # 快捷键4: 英雄攻击
            self._attack_with_hero()
        elif key == pygame.K_5:
            # 快捷键5: 结束回合
            self._end_turn()
        elif key == pygame.K_6:
            # 快捷键6: 查看游戏状态
            self._show_game_state()
        elif key == pygame.K_7:
            # 快捷键7: 退出游戏
            self.running = False

    def _show_menu(self):
        """显示游戏菜单"""
        self.menu_visible = True
        self.menu_selection = 0

    def _handle_menu_selection(self):
        """处理菜单选择"""
        if not self.game:
            return

        option = self.menu_selection
        self.menu_visible = False

        if option == 0:  # 打出手牌
            self._play_selected_card()
        elif option == 1:  # 使用英雄技能
            self._use_hero_power()
        elif option == 2:  # 随从攻击
            self._attack_with_minion()
        elif option == 3:  # 英雄攻击
            self._attack_with_hero()
        elif option == 4:  # 结束回合
            self._end_turn()
        elif option == 5:  # 查看游戏状态
            self._show_game_state()
        elif option == 6:  # 退出游戏
            self.running = False

    def _play_selected_card(self):
        """打出选中的卡牌"""
        if not self.game or not self.selected_card:
            return

        card = self.selected_card.card
        if card.cost > self.game.current_player.current_mana:
            print("❌ 法力值不足！")
            return

        result = self.engine.play_card(card)
        if result.success:
            print(f"✅ 成功打出 {card.name}!")
            self.selected_card = None
            self.sync_all_game_state()
        else:
            print(f"❌ 无法打出 {card.name}: {result.message}")

    def _use_hero_power(self):
        """使用英雄技能"""
        if not self.game:
            return

        result = self.engine.use_hero_power()
        if result.success:
            print("✅ 英雄技能使用成功!")
            self.sync_all_game_state()
        else:
            print(f"❌ 无法使用英雄技能: {result.message}")

    def _attack_with_minion(self):
        """随从攻击"""
        print("⚔️ 随从攻击功能需要通过UI选择攻击目标")

    def _attack_with_hero(self):
        """英雄攻击"""
        if not self.game:
            return

        result = self.engine.attack_with_hero(self.game.opponent.hero)
        if result.success:
            print("✅ 英雄攻击成功!")
            self.sync_all_game_state()
        else:
            print(f"❌ 无法进行英雄攻击: {result.message}")

    def _show_game_state(self):
        """显示游戏状态"""
        if not self.game:
            return

        print("\n" + "="*50)
        print("🎮 游戏状态")
        print("="*50)
        print(f"回合: {self.game.turn_number}")
        print(f"当前玩家: {self.game.current_player.name}")
        print(f"法力值: {self.game.current_player.current_mana}/{self.game.current_player.max_mana}")
        print(f"你的生命值: {self.game.current_player.hero.health}")
        print(f"对手生命值: {self.game.opponent.hero.health}")
        print(f"手牌数: {len(self.game.current_player.hand)}")
        print(f"你的战场随从数: {len(self.game.current_player.battlefield)}")
        print(f"对手战场随从数: {len(self.game.opponent.battlefield)}")
        print("="*50)

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

        # 使用GameState类的正确方法来切换玩家
        self.game.end_turn()
        self.game.start_new_turn()

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

        # 渲染新增的组件
        if hasattr(self, 'player_info_display'):
            self.player_info_display.render(self.screen)

        if hasattr(self, 'game_controls'):
            self.game_controls.render(self.screen)

        # 渲染拖拽中的卡牌（在最上层）
        if self.dragging_card:
            self.dragging_card.render(self.screen)

        # 渲染目标选择高亮
        if self.target_selector and self.target_selector.is_selecting:
            all_target_components = []
            all_target_components.extend(self.player_hand.card_components)
            self.target_selector.render_highlights(self.screen, all_target_components)

        # 显示调试信息
        self._render_debug_info()

        # 显示菜单
        if self.menu_visible:
            self._render_menu()

        # 更新显示
        pygame.display.flip()

    def _render_menu(self):
        """渲染游戏菜单"""
        if not self.screen:
            return

        # 确保字体已加载
        self._load_fonts()

        # 菜单背景
        menu_width = 300
        menu_height = len(self.menu_options) * 40 + 60
        menu_x = (self.width - menu_width) // 2
        menu_y = (self.height - menu_height) // 2
        menu_rect = pygame.Rect(menu_x, menu_y, menu_width, menu_height)
        
        # 绘制半透明背景
        s = pygame.Surface((menu_width, menu_height), pygame.SRCALPHA)
        s.fill((0, 0, 0, 200))
        self.screen.blit(s, (menu_x, menu_y))
        
        # 绘制边框
        pygame.draw.rect(self.screen, (255, 255, 255), menu_rect, 2)
        
        # 绘制标题 - 使用安全的中文字体渲染
        try:
            from .font_manager import render_text_safely
            title = render_text_safely("游戏副本菜单", 36, (255, 255, 255))
            title_rect = title.get_rect(centerx=menu_x + menu_width // 2, y=menu_y + 10)
            self.screen.blit(title, title_rect)
            
            # 绘制选项
            for i, option in enumerate(self.menu_options):
                color = (255, 255, 0) if i == self.menu_selection else (255, 255, 255)
                text = render_text_safely(option, 24, color)
                text_rect = text.get_rect(centerx=menu_x + menu_width // 2, y=menu_y + 50 + i * 40)
                self.screen.blit(text, text_rect)
                
            # 绘制提示
            hint = render_text_safely("↑↓ 选择, Enter 确认, Esc 返回", 20, (200, 200, 200))
            hint_rect = hint.get_rect(centerx=menu_x + menu_width // 2, y=menu_y + menu_height - 25)
            self.screen.blit(hint, hint_rect)
        except Exception as e:
            print(f"菜单渲染错误: {e}")

    def _render_debug_info(self):
        """渲染调试信息"""
        # 确保字体已加载
        self._load_fonts()
        
        if not self.screen:
            return

        try:
            from .font_manager import render_text_safely
            
            debug_texts = [
                f"改进版渲染器",
                f"手牌区域高度: {self.player_hand.size[1]}px",
                f"卡牌高度: 160px",
                f"可用操作空间: {self.player_hand.size[1] - 160}px",
                f"游戏控制: {'✅' if hasattr(self, 'game_controls') else '❌'}",
                f"当前玩家: {self.current_turn_player.name if self.current_turn_player else 'None'}",
                f"手牌数量: {len(self.player_hand.card_components)}",
            ]

            y_offset = 100
            for text in debug_texts:
                surface = render_text_safely(text, 20, (255, 255, 255))
                self.screen.blit(surface, (10, y_offset))
                y_offset += 25
        except Exception as e:
            print(f"调试信息渲染错误: {e}")

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


class GameControlsArea:
    """游戏控制区域"""

    def __init__(self, renderer):
        self.renderer = renderer
        self.config = get_component_config("end_turn_button")
        self.is_hovered = False

    def get_button_rect(self) -> pygame.Rect:
        """获取结束回合按钮的矩形区域"""
        return pygame.Rect(*self.renderer.window_manager.get_end_turn_button_rect())

    def handle_click(self, position: Tuple[int, int]) -> bool:
        """处理点击事件"""
        button_rect = self.get_button_rect()
        if button_rect.collidepoint(position):
            self.renderer._end_turn()
            return True
        return False

    def handle_mouse_motion(self, position: Tuple[int, int]) -> bool:
        """处理鼠标移动事件"""
        button_rect = self.get_button_rect()
        was_hovered = self.is_hovered
        self.is_hovered = button_rect.collidepoint(position)
        return self.is_hovered != was_hovered

    def render(self, surface: pygame.Surface):
        """渲染游戏控制区域"""
        if not surface:
            return

        button_rect = self.get_button_rect()

        # 绘制结束回合按钮
        color = self.config["hover_color"] if self.is_hovered else self.config["background_color"]
        pygame.draw.rect(surface, color, button_rect, border_radius=self.config["corner_radius"])
        pygame.draw.rect(surface, (255, 255, 255), button_rect, 2, border_radius=self.config["corner_radius"])

        # 渲染按钮文本 - 使用安全文本渲染
        try:
            from .font_manager import render_text_safely
            text_surface = render_text_safely(
                self.config["text"],
                self.config["font_size"],
                self.config["text_color"]
            )
            text_rect = text_surface.get_rect(center=button_rect.center)
            surface.blit(text_surface, text_rect)
        except Exception as e:
            print(f"按钮文本渲染警告: {e}")
            # 降级到基础字体
            try:
                font = pygame.font.Font(None, self.config["font_size"])
                text = font.render(self.config["text"], True, self.config["text_color"])
                text_rect = text.get_rect(center=button_rect.center)
                surface.blit(text, text_rect)
            except:
                pass


class PlayerInfoDisplay:
    """玩家信息显示区域"""

    def __init__(self, renderer):
        self.renderer = renderer

    def render(self, surface: pygame.Surface):
        """渲染玩家信息"""
        if not surface or not self.renderer.game:
            return

        try:
            from .font_manager import render_text_safely

            # 玩家1信息 (当前玩家) - 显示在HUD区域
            p1_text = f"玩家1: ❤️ {self.renderer.player1_health_display} 💰 {self.renderer.current_mana_display}"
            p1_surface = render_text_safely(p1_text, 18, (255, 255, 255))
            # 将玩家1信息显示在HUD区域的左侧
            p1_rect = p1_surface.get_rect(midleft=(20, 40))
            surface.blit(p1_surface, p1_rect)

            # 玩家2信息 (对手) - 显示在HUD区域
            p2_text = f"玩家2: ❤️ {self.renderer.player2_health_display}"
            p2_surface = render_text_safely(p2_text, 18, (255, 255, 255))
            # 将玩家2信息显示在HUD区域的右侧
            p2_rect = p2_surface.get_rect(midright=(self.renderer.width - 20, 40))
            surface.blit(p2_surface, p2_rect)

        except Exception as e:
            print(f"玩家信息渲染警告: {e}")
            # 降级到基础渲染
            try:
                font = pygame.font.Font(None, 18)

                # 玩家1信息
                p1_text = f"P1: HP:{self.renderer.player1_health_display} MP:{self.renderer.current_mana_display}"
                p1_surface = font.render(p1_text, True, (255, 255, 255))
                surface.blit(p1_surface, (50, 100))

                # 玩家2信息
                p2_text = f"P2: HP:{self.renderer.player2_health_display}"
                p2_surface = font.render(p2_text, True, (255, 255, 255))
                surface.blit(p2_surface, (50, 30))
            except:
                pass