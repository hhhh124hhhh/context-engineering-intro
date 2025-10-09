"""
通用UI组件
"""

import pygame
from typing import Tuple, Optional, Callable
from app.visualization.design.tokens import DesignTokens
from app.visualization.font_manager import render_text_safely


class Button:
    """按钮组件"""

    def __init__(self, text: str, position: Tuple[int, int],
                 size: Tuple[int, int], surface: pygame.Surface,
                 on_click: Optional[Callable] = None):
        """
        初始化按钮

        Args:
            text: 按钮文字
            position: 按钮位置
            size: 按钮尺寸
            surface: 目标surface
            on_click: 点击回调函数
        """
        self.text = text
        self.position = position
        self.size = size
        self.surface = surface
        self.on_click = on_click
        self.tokens = DesignTokens()

        # 状态
        self.hovered = False
        self.pressed = False
        self.enabled = True

        # 字体（使用安全渲染，无需初始化字体对象）
        self.font_size = self.tokens.TYPOGRAPHY['button']

        # 矩形区域
        self.rect = pygame.Rect(position, size)

    def render(self) -> None:
        """渲染按钮"""
        # 选择颜色
        if not self.enabled:
            bg_color = self.tokens.adjust_brightness(
                self.tokens.COLORS['ui']['button'], 0.6)
            text_color = self.tokens.adjust_brightness(
                self.tokens.COLORS['ui']['text'], 0.6)
        elif self.pressed:
            bg_color = self.tokens.adjust_brightness(
                self.tokens.COLORS['ui']['button'], 0.8)
            text_color = self.tokens.COLORS['ui']['text']
        elif self.hovered:
            bg_color = self.tokens.adjust_brightness(
                self.tokens.COLORS['ui']['button'], 1.2)
            text_color = self.tokens.COLORS['ui']['text']
        else:
            bg_color = self.tokens.COLORS['ui']['button']
            text_color = self.tokens.COLORS['ui']['text']

        # 绘制按钮背景
        pygame.draw.rect(self.surface, bg_color, self.rect, border_radius=4)

        # 绘制边框
        border_color = self.tokens.adjust_brightness(bg_color, 0.8)
        pygame.draw.rect(self.surface, border_color, self.rect, 2, border_radius=4)

        # 绘制文字（使用安全文本渲染）
        try:
            text_surface = render_text_safely(self.text, self.font_size, text_color)
            text_rect = text_surface.get_rect(center=self.rect.center)
            self.surface.blit(text_surface, text_rect)
        except Exception as e:
            # 降级到最简单的文本渲染
            try:
                font = pygame.font.Font(None, self.font_size)
                text_surface = font.render(self.text, True, text_color)
                text_rect = text_surface.get_rect(center=self.rect.center)
                self.surface.blit(text_surface, text_rect)
            except:
                pass  # 如果所有渲染都失败，跳过文本显示

    def handle_click(self, pos: Tuple[int, int]) -> bool:
        """
        处理点击事件

        Args:
            pos: 鼠标位置

        Returns:
            是否点击了按钮
        """
        if not self.enabled:
            return False

        if self.rect.collidepoint(pos):
            if self.on_click:
                self.on_click()
            return True
        return False

    def handle_mouse_motion(self, pos: Tuple[int, int]) -> None:
        """
        处理鼠标移动事件

        Args:
            pos: 鼠标位置
        """
        if self.enabled:
            self.hovered = self.rect.collidepoint(pos)

    def set_pressed(self, pressed: bool) -> None:
        """设置按下状态"""
        self.pressed = pressed

    def set_hover(self, hover: bool) -> None:
        """设置悬停状态"""
        self.hovered = hover

    def set_enabled(self, enabled: bool) -> None:
        """设置启用状态"""
        self.enabled = enabled

    def is_hovered(self) -> bool:
        """是否悬停"""
        return self.hovered

    def is_pressed(self) -> bool:
        """是否按下"""
        return self.pressed

    def is_enabled(self) -> bool:
        """是否启用"""
        return self.enabled


class HealthBar:
    """血条组件"""

    def __init__(self, position: Tuple[int, int], size: Tuple[int, int],
                 surface: pygame.Surface, max_health: int = 30):
        """
        初始化血条

        Args:
            position: 血条位置
            size: 血条尺寸
            surface: 目标surface
            max_health: 最大血量
        """
        self.position = position
        self.size = size
        self.surface = surface
        self.max_health = max_health
        self.current_health = max_health
        self.tokens = DesignTokens()

        # 矩形区域
        self.rect = pygame.Rect(position, size)

        # 字体（使用安全渲染，无需初始化字体对象）
        self.font_size = 14

    def set_health(self, current: int, maximum: int = None) -> None:
        """
        设置血量

        Args:
            current: 当前血量
            maximum: 最大血量（可选）
        """
        self.current_health = max(0, min(current, self.max_health))
        if maximum is not None:
            self.max_health = maximum

    def render(self) -> None:
        """渲染血条"""
        # 计算血量百分比
        health_percentage = self.current_health / self.max_health

        # 选择颜色
        if health_percentage > 0.7:
            health_color = self.tokens.COLORS['health']['full']
        elif health_percentage > 0.3:
            health_color = self.tokens.COLORS['health']['half']
        else:
            health_color = self.tokens.COLORS['health']['low']

        # 绘制背景
        pygame.draw.rect(self.surface, (64, 64, 64), self.rect, border_radius=3)

        # 绘制血条
        if health_percentage > 0:
            health_width = int(self.rect.width * health_percentage)
            health_rect = pygame.Rect(self.rect.x, self.rect.y,
                                     health_width, self.rect.height)
            pygame.draw.rect(self.surface, health_color, health_rect, border_radius=3)

        # 绘制边框
        pygame.draw.rect(self.surface, (32, 32, 32), self.rect, 2, border_radius=3)

        # 绘制血量文字（使用安全文本渲染）
        try:
            health_text = f"{self.current_health}/{self.max_health}"
            text_surface = render_text_safely(health_text, self.font_size, (255, 255, 255))
            text_rect = text_surface.get_rect(center=self.rect.center)
            self.surface.blit(text_surface, text_rect)
        except Exception as e:
            # 降级到最简单的文本渲染
            try:
                font = pygame.font.Font(None, self.font_size)
                health_text = f"{self.current_health}/{self.max_health}"
                text_surface = font.render(health_text, True, (255, 255, 255))
                text_rect = text_surface.get_rect(center=self.rect.center)
                self.surface.blit(text_surface, text_rect)
            except:
                pass  # 如果所有渲染都失败，跳过文本显示

    def get_current_health(self) -> int:
        """获取当前血量"""
        return self.current_health

    def get_max_health(self) -> int:
        """获取最大血量"""
        return self.max_health

    def get_health_percentage(self) -> float:
        """获取血量百分比"""
        return self.current_health / self.max_health


class ManaCrystal:
    """法力水晶组件"""

    def __init__(self, position: Tuple[int, int], surface: pygame.Surface,
                 max_mana: int = 10):
        """
        初始化法力水晶

        Args:
            position: 水晶位置
            surface: 目标surface
            max_mana: 最大法力值
        """
        self.position = position
        self.surface = surface
        self.max_mana = max_mana
        self.current_mana = max_mana
        self.tokens = DesignTokens()

        # 字体（使用安全渲染，无需初始化字体对象）
        self.font_size = 16

    def set_mana(self, current: int, maximum: int = None) -> None:
        """
        设置法力值

        Args:
            current: 当前法力值
            maximum: 最大法力值（可选）
        """
        self.current_mana = max(0, min(current, self.max_mana))
        if maximum is not None:
            self.max_mana = maximum

    def render(self) -> None:
        """渲染法力水晶"""
        crystal_size = 20
        crystal_spacing = 25

        for i in range(self.max_mana):
            # 计算水晶位置
            x = self.position[0] + i * crystal_spacing
            y = self.position[1]

            # 选择颜色
            if i < self.current_mana:
                color = self.tokens.COLORS['mana']['blue']
            else:
                color = self.tokens.COLORS['mana']['empty']

            # 绘制水晶（简化为菱形）
            points = [
                (x, y - crystal_size // 2),      # 上
                (x + crystal_size // 2, y),      # 右
                (x, y + crystal_size // 2),      # 下
                (x - crystal_size // 2, y),      # 左
            ]
            pygame.draw.polygon(self.surface, color, points)
            pygame.draw.polygon(self.surface, (0, 0, 0), points, 2)

    def render_text(self) -> None:
        """渲染法力值文字"""
        try:
            mana_text = f"法力值: {self.current_mana}/{self.max_mana}"
            text_surface = render_text_safely(mana_text, self.font_size, self.tokens.COLORS['ui']['text'])
            self.surface.blit(text_surface, (self.position[0], self.position[1] - 25))
        except Exception as e:
            # 降级到最简单的文本渲染
            try:
                font = pygame.font.Font(None, self.font_size)
                mana_text = f"法力值: {self.current_mana}/{self.max_mana}"
                text_surface = font.render(mana_text, True, self.tokens.COLORS['ui']['text'])
                self.surface.blit(text_surface, (self.position[0], self.position[1] - 25))
            except:
                pass  # 如果所有渲染都失败，跳过文本显示

    def get_current_mana(self) -> int:
        """获取当前法力值"""
        return self.current_mana

    def get_max_mana(self) -> int:
        """获取最大法力值"""
        return self.max_mana

    def get_mana_percentage(self) -> float:
        """获取法力值百分比"""
        return self.current_mana / self.max_mana


class ProgressBar:
    """进度条组件"""

    def __init__(self, position: Tuple[int, int], size: Tuple[int, int],
                 surface: pygame.Surface, color: Tuple[int, int, int] = None):
        """
        初始化进度条

        Args:
            position: 进度条位置
            size: 进度条尺寸
            surface: 目标surface
            color: 进度条颜色
        """
        self.position = position
        self.size = size
        self.surface = surface
        self.tokens = DesignTokens()
        self.progress = 0.0

        if color is None:
            self.color = self.tokens.COLORS['primary']['main']
        else:
            self.color = color

        # 矩形区域
        self.rect = pygame.Rect(position, size)

    def set_progress(self, progress: float) -> None:
        """
        设置进度

        Args:
            progress: 进度值 (0.0 - 1.0)
        """
        self.progress = max(0.0, min(1.0, progress))

    def render(self) -> None:
        """渲染进度条"""
        # 绘制背景
        pygame.draw.rect(self.surface, (64, 64, 64), self.rect, border_radius=3)

        # 绘制进度
        if self.progress > 0:
            progress_width = int(self.rect.width * self.progress)
            progress_rect = pygame.Rect(self.rect.x, self.rect.y,
                                       progress_width, self.rect.height)
            pygame.draw.rect(self.surface, self.color, progress_rect, border_radius=3)

        # 绘制边框
        pygame.draw.rect(self.surface, (32, 32, 32), self.rect, 2, border_radius=3)

        # 绘制百分比文字（使用安全文本渲染）
        try:
            percentage_text = f"{int(self.progress * 100)}%"
            text_surface = render_text_safely(percentage_text, 12, (255, 255, 255))
            text_rect = text_surface.get_rect(center=self.rect.center)
            self.surface.blit(text_surface, text_rect)
        except Exception as e:
            # 降级到最简单的文本渲染
            try:
                font = pygame.font.Font(None, 12)
                percentage_text = f"{int(self.progress * 100)}%"
                text_surface = font.render(percentage_text, True, (255, 255, 255))
                text_rect = text_surface.get_rect(center=self.rect.center)
                self.surface.blit(text_surface, text_rect)
            except:
                pass  # 如果所有渲染都失败，跳过文本显示

    def get_progress(self) -> float:
        """获取当前进度"""
        return self.progress