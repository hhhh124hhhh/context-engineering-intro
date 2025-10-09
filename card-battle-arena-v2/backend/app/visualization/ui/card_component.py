"""
交互式卡牌组件

提供可点击、可拖拽的卡牌UI组件，支持悬停、选中、拖拽等交互状态。
"""

import pygame
from typing import Tuple, Optional, Callable
from app.game.cards import Card
from app.visualization.font_manager import get_best_font, render_text_safely


class InteractiveCard:
    """
    交互式卡牌组件

    支持点击、悬停、拖拽等交互功能的卡牌UI组件
    """

    def __init__(self,
                 card: Card,
                 position: Tuple[int, int],
                 size: Tuple[int, int] = (120, 160),
                 on_click: Optional[Callable] = None,
                 on_drag_end: Optional[Callable] = None):
        """
        初始化交互式卡牌组件

        Args:
            card: 卡牌数据
            position: 卡牌位置 (x, y)
            size: 卡牌尺寸 (width, height)
            on_click: 点击回调函数
            on_drag_end: 拖拽结束回调函数
        """
        self.card = card
        self.position = position
        self.size = size
        self.on_click = on_click
        self.on_drag_end = on_drag_end

        # 交互状态
        self.is_hovered = False
        self.is_selected = False
        self.is_draggable = True
        self.is_dragging = False
        self.is_target_highlighted = False

        # 拖拽相关
        self.drag_offset = (0, 0)
        self.current_position = position
        self.original_position = position

        # 视觉效果
        self.hover_scale = 1.1
        self.selected_offset = 10

        # 颜色定义
        self.bg_color = (255, 255, 255)  # 白色背景
        self.border_color = (0, 0, 0)    # 黑色边框
        self.hover_color = (255, 255, 200)  # 悬停背景色
        self.selected_color = (200, 200, 255)  # 选中背景色
        self.target_color = (255, 200, 200)    # 目标高亮色

        # 字体（延迟加载）
        self.font = None
        self.title_font = None
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
            self.font = get_best_font(16, prefer_chinese=True)
            self.title_font = get_best_font(18, prefer_chinese=True)
            self.fonts_loaded = True
        except Exception as e:
            # 如果加载失败，使用安全渲染方法
            print(f"卡牌字体加载警告: {e}")
            self.font = None
            self.title_font = None
            self.fonts_loaded = True

    def is_point_inside(self, point: Tuple[int, int]) -> bool:
        """
        检查点是否在卡牌区域内

        Args:
            point: 检查的点坐标 (x, y)

        Returns:
            bool: 是否在卡牌区域内
        """
        current_rect = pygame.Rect(self.current_position, self.size)
        return current_rect.collidepoint(point)

    def handle_click(self, point: Tuple[int, int]) -> bool:
        """
        处理点击事件

        Args:
            point: 点击位置 (x, y)

        Returns:
            bool: 是否处理了点击事件
        """
        if self.is_point_inside(point):
            if self.on_click:
                self.on_click(self.card)
            return True
        return False

    def handle_mouse_motion(self, point: Tuple[int, int]) -> bool:
        """
        处理鼠标移动事件

        Args:
            point: 鼠标位置 (x, y)

        Returns:
            bool: 鼠标是否在卡牌上
        """
        was_hovered = self.is_hovered
        self.is_hovered = self.is_point_inside(point)
        return self.is_hovered != was_hovered

    def select(self):
        """选中卡牌"""
        self.is_selected = True
        # 选中时向上偏移
        self.current_position = (
            self.position[0],
            self.position[1] - self.selected_offset
        )
        self.rect = pygame.Rect(self.current_position, self.size)

    def deselect(self):
        """取消选中卡牌"""
        self.is_selected = False
        self.current_position = self.position
        self.rect = pygame.Rect(self.current_position, self.size)

    def set_as_target(self, is_target: bool):
        """
        设置是否为目标

        Args:
            is_target: 是否为目标
        """
        self.is_target_highlighted = is_target

    def start_drag(self, point: Tuple[int, int]) -> bool:
        """
        开始拖拽

        Args:
            point: 拖拽起始点 (x, y)

        Returns:
            bool: 是否成功开始拖拽
        """
        if not self.is_draggable or not self.is_point_inside(point):
            return False

        self.is_dragging = True
        self.drag_offset = (
            point[0] - self.current_position[0],
            point[1] - self.current_position[1]
        )
        return True

    def move_drag(self, point: Tuple[int, int]):
        """
        移动拖拽

        Args:
            point: 当前鼠标位置 (x, y)
        """
        if self.is_dragging:
            self.current_position = (
                point[0] - self.drag_offset[0],
                point[1] - self.drag_offset[1]
            )
            self.rect = pygame.Rect(self.current_position, self.size)

    def end_drag(self, point: Tuple[int, int]) -> bool:
        """
        结束拖拽

        Args:
            point: 拖拽结束位置 (x, y)

        Returns:
            bool: 是否成功结束拖拽
        """
        if not self.is_dragging:
            return False

        self.is_dragging = False

        # 调用拖拽结束回调
        if self.on_drag_end:
            self.on_drag_end(self.card, point)

        # 重置位置
        self.current_position = self.position
        self.rect = pygame.Rect(self.current_position, self.size)

        return True

    def get_current_rect(self) -> pygame.Rect:
        """获取当前矩形区域"""
        return pygame.Rect(self.current_position, self.size)

    def render(self, surface: pygame.Surface):
        """
        渲染卡牌

        Args:
            surface: 目标surface
        """
        if not surface:
            return

        # 确保字体已加载
        self._load_fonts()

        current_rect = self.get_current_rect()

        # 选择背景颜色
        if self.is_target_highlighted:
            bg_color = self.target_color
        elif self.is_selected:
            bg_color = self.selected_color
        elif self.is_hovered:
            bg_color = self.hover_color
        else:
            bg_color = self.bg_color

        # 绘制卡牌背景
        pygame.draw.rect(surface, bg_color, current_rect, border_radius=8)

        # 绘制边框
        border_width = 3 if self.is_selected else 2
        pygame.draw.rect(surface, self.border_color, current_rect, border_width, border_radius=8)

        # 如果悬停，添加阴影效果
        if self.is_hovered:
            shadow_rect = current_rect.copy()
            shadow_rect.x += 3
            shadow_rect.y += 3
            pygame.draw.rect(surface, (100, 100, 100), shadow_rect, border_radius=8)
            # 重新绘制主体以覆盖阴影的一部分
            pygame.draw.rect(surface, bg_color, current_rect, border_radius=8)
            pygame.draw.rect(surface, self.border_color, current_rect, border_width, border_radius=8)

        # 渲染卡牌内容
        self._render_card_content(surface, current_rect)

    def _render_card_content(self, surface: pygame.Surface, rect: pygame.Rect):
        """
        渲染卡牌内容

        Args:
            surface: 目标surface
            rect: 卡牌矩形区域
        """
        try:
            # 卡牌名称 (使用安全渲染)
            name_text = self.card.name[:10] if len(self.card.name) > 10 else self.card.name
            name_surface = render_text_safely(name_text, 18, (0, 0, 0))
            name_rect = name_surface.get_rect(centerx=rect.centerx, y=rect.y + 5)
            surface.blit(name_surface, name_rect)

            # 法力成本
            cost_text = str(self.card.cost)
            cost_surface = render_text_safely(cost_text, 16, (0, 0, 255))
            cost_rect = cost_surface.get_rect(topleft=(rect.x + 5, rect.y + 5))
            surface.blit(cost_surface, cost_rect)

            # 卡牌类型
            type_text = self.card.card_type.value[:3]
            type_surface = render_text_safely(type_text, 14, (100, 100, 100))
            type_rect = type_surface.get_rect(bottomleft=(rect.x + 5, rect.bottom - 5))
            surface.blit(type_surface, type_rect)

            # 攻击力和生命值（如果是随从或武器）
            if hasattr(self.card, 'attack') and hasattr(self.card, 'health'):
                stats_text = f"{self.card.attack}/{self.card.health}"
                stats_surface = render_text_safely(stats_text, 16, (255, 0, 0))
                stats_rect = stats_surface.get_rect(bottomright=(rect.right - 5, rect.bottom - 5))
                surface.blit(stats_surface, stats_rect)

        except Exception as e:
            # 如果渲染失败，显示简单的文本
            error_text = f"Card #{self.card.id}"
            try:
                error_surface = render_text_safely(error_text, 16, (255, 0, 0))
                error_rect = error_surface.get_rect(center=rect.center)
                surface.blit(error_surface, error_rect)
            except:
                pass  # 如果连错误文本都无法渲染，就跳过

    def update_card(self, card: Card):
        """
        更新卡牌数据

        Args:
            card: 新的卡牌数据
        """
        self.card = card

    def get_info(self) -> dict:
        """
        获取卡牌信息

        Returns:
            dict: 卡牌信息
        """
        return {
            'card': self.card,
            'position': self.position,
            'current_position': self.current_position,
            'is_hovered': self.is_hovered,
            'is_selected': self.is_selected,
            'is_dragging': self.is_dragging,
            'is_target_highlighted': self.is_target_highlighted
        }