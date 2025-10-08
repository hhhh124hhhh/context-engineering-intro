"""
增强版Pygame渲染器
整合新的组件化架构
"""

import pygame
from typing import Tuple, Optional, List
from app.game.cards import Card
from app.visualization.design.tokens import DesignTokens
from app.visualization.components.card_renderer import CardRenderer
from app.visualization.components.layout_engine import LayoutEngine
from app.visualization.components.ui_components import HealthBar, ManaCrystal
from app.visualization.components.animation_engine import AnimationEngine, MoveAnimation


class EnhancedRenderer:
    """增强版游戏渲染器"""

    def __init__(self, width: int = 1200, height: int = 800):
        """
        初始化增强版渲染器

        Args:
            width: 窗口宽度
            height: 窗口高度
        """
        self.width = width
        self.height = height
        self.screen = None
        self.clock = None
        self.tokens = DesignTokens()

        # 初始化组件
        self.layout_engine = LayoutEngine(width, height)
        self.card_renderer = CardRenderer()
        self.animation_engine = AnimationEngine()

        # 字体系统
        self.fonts = {}
        self._init_fonts()

        # 选中的卡牌
        self.selected_card = None
        self.selected_card_index = -1
        self.keyboard_selected_index = 0

        # 交互状态
        self.dragging = False
        self.drag_offset = (0, 0)

    def create_window(self, title: str = "卡牌对战竞技场 - 增强版") -> Optional[pygame.Surface]:
        """
        创建游戏窗口

        Args:
            title: 窗口标题

        Returns:
            游戏surface
        """
        try:
            pygame.init()
            self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
            pygame.display.set_caption(title)
            self.clock = pygame.time.Clock()

            # 启动动画引擎
            self.animation_engine.start()

            return self.screen
        except Exception as e:
            print(f"创建窗口失败: {e}")
            return None

    def _init_fonts(self):
        """初始化字体系统"""
        try:
            # 尝试加载中文字体
            font_names = [
                "simhei.ttf",  # 黑体
                "simsun.ttc",  # 宋体
                "msyh.ttc",    # 微软雅黑
            ]

            # Windows系统字体路径
            import os
            if os.name == "nt":
                font_paths = [
                    "C:/Windows/Fonts/simhei.ttf",
                    "C:/Windows/Fonts/simsun.ttc",
                    "C:/Windows/Fonts/msyh.ttc",
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
        sizes = self.layout_engine.calculate_font_sizes()

        # 使用设计token的字体大小作为后备
        token_sizes = self.tokens.TYPOGRAPHY

        self.fonts.update({
            'heading': pygame.font.Font(None, sizes.get('heading', token_sizes['heading'])),
            'body': pygame.font.Font(None, sizes.get('body', token_sizes['body'])),
            'small': pygame.font.Font(None, sizes.get('caption', token_sizes['caption'])),
            'button': pygame.font.Font(None, sizes.get('button', token_sizes['button'])),
        })

    def handle_events(self):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.VIDEORESIZE:
                self._handle_resize(event.w, event.h)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_mouse_down(event.pos, event.button)
            elif event.type == pygame.MOUSEBUTTONUP:
                self._handle_mouse_up(event.pos, event.button)
            elif event.type == pygame.MOUSEMOTION:
                self._handle_mouse_motion(event.pos)
            elif event.type == pygame.KEYDOWN:
                self._handle_key_down(event.key)

        return True

    def _handle_resize(self, width: int, height: int):
        """处理窗口大小调整"""
        self.width = width
        self.height = height
        self.layout_engine.update_window_size(width, height)
        self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)

    def _handle_mouse_down(self, pos: Tuple[int, int], button: int):
        """处理鼠标按下事件"""
        if button == 1:  # 左键
            self._handle_left_click(pos)
        elif button == 3:  # 右键
            self._handle_right_click(pos)

    def _handle_left_click(self, pos: Tuple[int, int]):
        """处理左键点击"""
        # 这里可以添加点击处理逻辑
        pass

    def _handle_right_click(self, pos: Tuple[int, int]):
        """处理右键点击"""
        # 取消选择
        self.selected_card = None
        self.selected_card_index = -1
        self.keyboard_selected_index = 0

    def _handle_mouse_up(self, pos: Tuple[int, int], button: int):
        """处理鼠标释放事件"""
        if button == 1:
            self.dragging = False

    def _handle_mouse_motion(self, pos: Tuple[int, int]):
        """处理鼠标移动事件"""
        if self.dragging and self.selected_card:
            # 处理拖拽
            pass

    def _handle_key_down(self, key: int):
        """处理键盘按下事件"""
        if key == pygame.K_ESCAPE:
            # 取消选择
            self.selected_card = None
            self.selected_card_index = -1
            self.keyboard_selected_index = 0

    def render_game_state(self, game_state):
        """
        渲染游戏状态

        Args:
            game_state: 游戏状态对象
        """
        if not self.screen:
            return

        # 更新布局
        layout = self.layout_engine.calculate_layout()
        regions = layout['regions']

        # 清屏
        self.screen.fill(self.tokens.COLORS['surface']['board'])

        # 渲染各个区域
        self._render_title(regions['title'], game_state)
        self._render_player_info(regions['player_info'], game_state.current_player, "当前玩家")
        self._render_player_info(regions['opponent_info'], game_state.opponent, "对手")
        self._render_battlefield(regions['player_battlefield'], game_state.current_player.battlefield, "你的战场")
        self._render_battlefield(regions['opponent_battlefield'], game_state.opponent.battlefield, "对手战场")
        self._render_hand(regions['hand'], game_state.current_player.hand)
        self._render_instructions(regions['instructions'])

        # 更新动画
        self.animation_engine.update()

        # 更新显示
        pygame.display.flip()

    def _render_title(self, title_rect, game_state):
        """渲染标题"""
        # 绘制标题背景
        pygame.draw.rect(self.screen, self.tokens.COLORS['primary']['main'], title_rect)

        # 绘制标题文字
        font = self.fonts.get('heading')
        if font:
            try:
                title_text = font.render(f"卡牌对战竞技场 - 回合 {game_state.turn_number}", True, (255, 255, 255))
            except:
                title_text = font.render(f"Card Battle Arena - Turn {game_state.turn_number}", True, (255, 255, 255))

            title_rect_center = title_text.get_rect(center=title_rect.center)
            self.screen.blit(title_text, title_rect_center)

    def _render_player_info(self, info_rect, player, title: str):
        """渲染玩家信息"""
        # 绘制信息背景
        pygame.draw.rect(self.screen, self.tokens.COLORS['surface']['ui'], info_rect)
        pygame.draw.rect(self.screen, self.tokens.COLORS['ui']['border'], info_rect, 2)

        # 绘制玩家名称
        font = self.fonts.get('body')
        if font:
            try:
                name_text = font.render(f"{player.name}", True, self.tokens.COLORS['ui']['text'])
            except:
                name_text = font.render("Player", True, self.tokens.COLORS['ui']['text'])
            self.screen.blit(name_text, (info_rect.x + 10, info_rect.y + 10))

            # 绘制生命值
            health_text = font.render(f"生命值: {player.hero.health}", True, (255, 0, 0))
            self.screen.blit(health_text, (info_rect.x + 10, info_rect.y + 40))

    def _render_battlefield(self, battlefield_rect, battlefield, title: str):
        """渲染战场"""
        # 绘制战场背景
        pygame.draw.rect(self.screen, self.tokens.COLORS['surface']['ui'], battlefield_rect, 2)

        # 绘制标题
        font = self.fonts.get('body')
        if font:
            try:
                title_text = font.render(title, True, self.tokens.COLORS['ui']['text'])
            except:
                title_text = font.render("Battlefield", True, self.tokens.COLORS['ui']['text'])
            self.screen.blit(title_text, (battlefield_rect.x + 10, battlefield_rect.y - 25))

        # 计算卡牌位置
        card_positions = self.layout_engine.calculate_card_positions(
            len(battlefield), battlefield_rect
        )

        # 渲染卡牌
        for i, (card, pos) in enumerate(zip(battlefield, card_positions)):
            self.card_renderer.render_card(card, pos, self.screen)

    def _render_hand(self, hand_rect, hand: List[Card]):
        """渲染手牌"""
        # 绘制手牌背景
        pygame.draw.rect(self.screen, self.tokens.COLORS['surface']['ui'], hand_rect, 2)

        # 绘制标题
        font = self.fonts.get('body')
        if font:
            try:
                title_text = font.render("手牌:", True, self.tokens.COLORS['ui']['text'])
            except:
                title_text = font.render("Hand:", True, self.tokens.COLORS['ui']['text'])
            self.screen.blit(title_text, (hand_rect.x + 10, hand_rect.y - 25))

        # 计算卡牌位置
        card_positions = self.layout_engine.calculate_card_positions(len(hand), hand_rect)

        # 渲染卡牌
        for i, (card, pos) in enumerate(zip(hand, card_positions)):
            # 如果是选中的卡牌，稍微抬高
            if i == self.selected_card_index:
                pos = (pos[0], pos[1] - 20)

            is_selected = (i == self.selected_card_index)
            self.card_renderer.render_card(card, pos, self.screen, selected=is_selected)

    def _render_instructions(self, instructions_rect):
        """渲染操作提示"""
        # 绘制提示背景
        pygame.draw.rect(self.screen, self.tokens.COLORS['ui']['background'], instructions_rect)

        # 绘制提示文字
        font = self.fonts.get('small')
        if font:
            try:
                instructions = "鼠标: 左键选择/出牌, 右键取消 | 键盘: ←→选择, 空格选中, 回车出牌 | 按键: ESC-退出"
                instructions_text = font.render(instructions, True, self.tokens.COLORS['ui']['text'])
            except:
                instructions = "Mouse: Left-Select/Play, Right-Cancel | Keys: ←→Select, Space-Select, Enter-Play | ESC-Exit"
                instructions_text = font.render(instructions, True, self.tokens.COLORS['ui']['text'])

            instructions_rect_center = instructions_text.get_rect(center=instructions_rect.center)
            self.screen.blit(instructions_text, instructions_rect_center)

    def update_display(self):
        """更新显示"""
        if self.clock:
            self.clock.tick(60)

    def cleanup(self):
        """清理资源"""
        self.animation_engine.stop()
        if pygame.get_init():
            pygame.quit()

    def add_card_animation(self, card: Card, start_pos: Tuple[int, int],
                          end_pos: Tuple[int, int]) -> str:
        """
        添加卡牌动画

        Args:
            card: 卡牌对象
            start_pos: 起始位置
            end_pos: 结束位置

        Returns:
            动画ID
        """
        return self.animation_engine.add_card_animation(
            'move',
            start_pos=start_pos,
            end_pos=end_pos,
            duration=self.tokens.ANIMATION['card_play']
        )

    def is_animating(self) -> bool:
        """是否有动画正在运行"""
        return self.animation_engine.is_animating()