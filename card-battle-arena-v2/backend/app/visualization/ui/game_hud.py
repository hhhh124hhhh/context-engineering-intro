"""
游戏HUD组件

显示游戏状态信息，如回合数、法力值、生命值等。
"""

import pygame
from typing import Tuple, Optional
from app.game.state import GameState
from app.visualization.font_manager import get_best_font, render_text_safely


class GameHUD:
    """
    游戏HUD（平视显示器）

    显示游戏状态信息，如回合数、法力值、生命值等
    """

    def __init__(self, position: Tuple[int, int], size: Tuple[int, int] = (1200, 60)):
        """
        初始化游戏HUD

        Args:
            position: HUD位置 (x, y)
            size: HUD尺寸 (width, height)
        """
        self.position = position
        self.size = size

        # 游戏状态数据
        self.turn_display = "玩家1的回合 - 回合 1"
        self.player1_health_display = "30/30"
        self.player2_health_display = "30/30"
        self.player1_mana_display = "1/1"
        self.player2_mana_display = "1/1"

        # 视觉效果
        self.bg_color = (50, 50, 100)  # 深蓝色背景
        self.text_color = (255, 255, 255)  # 白色文字
        self.health_color = (255, 100, 100)  # 红色生命值
        self.mana_color = (100, 100, 255)  # 蓝色法力值

        # 字体（使用Windows优化字体管理器）
        self.title_font = None
        self.info_font = None
        self.fonts_loaded = False

        # 矩形区域
        self.rect = pygame.Rect(position, size)

    def _load_fonts(self):
        """加载字体（使用Windows优化字体管理器）"""
        if self.fonts_loaded:
            return

        try:
            if not pygame.get_init():
                pygame.init()
            # 使用Windows优化的字体管理器
            self.title_font = get_best_font(24, prefer_chinese=True)
            self.info_font = get_best_font(20, prefer_chinese=True)
            self.fonts_loaded = True
        except Exception as e:
            # 如果加载失败，使用安全渲染方法
            print(f"字体加载警告: {e}")
            self.title_font = None
            self.info_font = None
            self.fonts_loaded = True

    def update_turn_indicator(self, game: GameState):
        """
        更新回合指示器

        Args:
            game: 游戏状态
        """
        current_player = game.current_player
        self.turn_display = f"{current_player.name}的回合 - 回合 {game.turn_number}"

    def update_health_display(self, game: GameState):
        """
        更新生命值显示

        Args:
            game: 游戏状态
        """
        player1 = game.player1
        player2 = game.player2

        self.player1_health_display = f"{player1.hero.health}/30"
        self.player2_health_display = f"{player2.hero.health}/30"

    def update_mana_display(self, player, is_player1: bool = True):
        """
        更新法力值显示

        Args:
            player: 玩家对象
            is_player1: 是否为玩家1
        """
        mana_text = f"{player.current_mana}/{player.max_mana}"
        if is_player1:
            self.player1_mana_display = mana_text
        else:
            self.player2_mana_display = mana_text

    def update_all(self, game: GameState):
        """
        更新所有HUD信息

        Args:
            game: 游戏状态
        """
        self.update_turn_indicator(game)
        self.update_health_display(game)
        self.update_mana_display(game.player1, True)
        self.update_mana_display(game.player2, False)

    def render(self, surface: pygame.Surface):
        """
        渲染HUD

        Args:
            surface: 目标surface
        """
        if not surface:
            return

        # 确保字体已加载
        self._load_fonts()

        # 绘制背景
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=5)

        # 绘制边框
        pygame.draw.rect(surface, self.text_color, self.rect, 2, border_radius=5)

        # 渲染回合信息
        self._render_turn_info(surface)

        # 渲染玩家信息
        self._render_player_info(surface)

    def _render_turn_info(self, surface: pygame.Surface):
        """
        渲染回合信息

        Args:
            surface: 目标surface
        """
        try:
            # 使用安全的文本渲染方法
            turn_surface = render_text_safely(self.turn_display, 24, self.text_color)
            turn_rect = turn_surface.get_rect(centerx=self.rect.centerx, y=self.rect.y + 5)
            surface.blit(turn_surface, turn_rect)
        except Exception as e:
            # 如果安全渲染也失败，显示最简单的版本
            try:
                simple_text = f"Turn {self.turn_display.split()[-1] if self.turn_display else '1'}"
                simple_surface = render_text_safely(simple_text, 20, self.text_color)
                simple_rect = simple_surface.get_rect(centerx=self.rect.centerx, y=self.rect.y + 5)
                surface.blit(simple_surface, simple_rect)
            except:
                pass  # 如果连简化版本都失败，就跳过回合显示

    def _render_player_info(self, surface: pygame.Surface):
        """
        渲染玩家信息

        Args:
            surface: 目标surface
        """
        y_offset = 35

        try:
            # 玩家1信息（左侧）
            p1_health_text = f"❤️ {self.player1_health_display}"
            p1_health_surface = render_text_safely(p1_health_text, 20, self.health_color)
            surface.blit(p1_health_surface, (self.rect.x + 20, y_offset))

            p1_mana_text = f"💰 {self.player1_mana_display}"
            p1_mana_surface = render_text_safely(p1_mana_text, 20, self.mana_color)
            surface.blit(p1_mana_surface, (self.rect.x + 150, y_offset))

            # 玩家2信息（右侧）
            p2_health_text = f"❤️ {self.player2_health_display}"
            p2_health_surface = render_text_safely(p2_health_text, 20, self.health_color)
            p2_health_rect = p2_health_surface.get_rect(right=self.rect.right - 150, y=y_offset)
            surface.blit(p2_health_surface, p2_health_rect)

            p2_mana_text = f"💰 {self.player2_mana_display}"
            p2_mana_surface = render_text_safely(p2_mana_text, 20, self.mana_color)
            p2_mana_rect = p2_mana_surface.get_rect(right=self.rect.right - 20, y=y_offset)
            surface.blit(p2_mana_surface, p2_mana_rect)

        except Exception as e:
            # 如果渲染失败，显示简化版本
            try:
                # 简单的数字显示
                simple_text = f"P1: {self.player1_health_display} | P2: {self.player2_health_display}"
                simple_surface = render_text_safely(simple_text, 18, self.text_color)
                simple_rect = simple_surface.get_rect(centerx=self.rect.centerx, y=y_offset)
                surface.blit(simple_surface, simple_rect)
            except:
                pass

    def set_turn_display(self, turn_text: str):
        """
        设置回合显示文本

        Args:
            turn_text: 回合文本
        """
        self.turn_display = turn_text

    def set_health_display(self, player1_health: str, player2_health: str):
        """
        设置生命值显示

        Args:
            player1_health: 玩家1生命值文本
            player2_health: 玩家2生命值文本
        """
        self.player1_health_display = player1_health
        self.player2_health_display = player2_health

    def set_mana_display(self, player1_mana: str, player2_mana: str):
        """
        设置法力值显示

        Args:
            player1_mana: 玩家1法力值文本
            player2_mana: 玩家2法力值文本
        """
        self.player1_mana_display = player1_mana
        self.player2_mana_display = player2_mana

    def get_info(self) -> dict:
        """
        获取HUD信息

        Returns:
            dict: HUD信息
        """
        return {
            'position': self.position,
            'size': self.size,
            'turn_display': self.turn_display,
            'player1_health': self.player1_health_display,
            'player2_health': self.player2_health_display,
            'player1_mana': self.player1_mana_display,
            'player2_mana': self.player2_mana_display
        }

    def animate_health_change(self, player_num: int, damage: int):
        """
        生命值变化动画（简化版本）

        Args:
            player_num: 玩家编号 (1 或 2)
            damage: 伤害值（正数为伤害，负数为治疗）
        """
        # 这里可以添加动画效果，目前只是简单的文本变化
        if player_num == 1:
            current_health = int(self.player1_health_display.split('/')[0])
            new_health = max(0, current_health - damage)
            self.player1_health_display = f"{new_health}/30"
        else:
            current_health = int(self.player2_health_display.split('/')[0])
            new_health = max(0, current_health - damage)
            self.player2_health_display = f"{new_health}/30"

    def animate_mana_change(self, player_num: int, current_mana: int, max_mana: int):
        """
        法力值变化动画（简化版本）

        Args:
            player_num: 玩家编号 (1 或 2)
            current_mana: 当前法力值
            max_mana: 最大法力值
        """
        mana_text = f"{current_mana}/{max_mana}"
        if player_num == 1:
            self.player1_mana_display = mana_text
        else:
            self.player2_mana_display = mana_text