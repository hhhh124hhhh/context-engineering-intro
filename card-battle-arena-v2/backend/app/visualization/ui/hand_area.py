"""
手牌区域组件

管理玩家手牌的显示和交互。
"""

import pygame
from typing import List, Tuple, Optional
from app.game.cards import Card
from .card_component import InteractiveCard
from app.visualization.font_manager import render_text_safely


class HandArea:
    """
    手牌区域组件

    管理玩家手牌的显示和交互
    """

    def __init__(self,
                 position: Tuple[int, int],
                 size: Tuple[int, int] = (1000, 180),
                 max_cards: int = 10):
        """
        初始化手牌区域

        Args:
            position: 手牌区域位置 (x, y)
            size: 手牌区域尺寸 (width, height)
            max_cards: 最大卡牌数量
        """
        self.position = position
        self.size = size
        self.max_cards = max_cards

        # 手牌卡牌组件
        self.card_components: List[InteractiveCard] = []

        # 视觉效果
        self.bg_color = (240, 240, 255)  # 浅蓝色背景
        self.border_color = (100, 100, 200)  # 深蓝色边框

        # 矩形区域
        self.rect = pygame.Rect(position, size)

        # 卡牌布局参数
        self.card_width = 100
        self.card_height = 140
        self.card_spacing = 15
        self.card_hover_offset = 20

    def add_card(self, card: Card,
                 on_click: Optional[callable] = None,
                 on_drag_end: Optional[callable] = None) -> bool:
        """
        添加卡牌到手牌

        Args:
            card: 要添加的卡牌
            on_click: 点击回调函数
            on_drag_end: 拖拽结束回调函数

        Returns:
            bool: 是否成功添加
        """
        if len(self.card_components) >= self.max_cards:
            return False

        # 计算卡牌位置
        card_position = self._calculate_card_position(len(self.card_components))

        # 创建交互式卡牌组件
        card_component = InteractiveCard(
            card=card,
            position=card_position,
            size=(self.card_width, self.card_height),
            on_click=on_click,
            on_drag_end=on_drag_end
        )

        self.card_components.append(card_component)
        return True

    def remove_card(self, card: Card) -> bool:
        """
        从手牌移除卡牌

        Args:
            card: 要移除的卡牌

        Returns:
            bool: 是否成功移除
        """
        for i, component in enumerate(self.card_components):
            if component.card == card:
                del self.card_components[i]
                # 重新排列剩余卡牌位置
                self._rearrange_cards()
                return True
        return False

    def remove_card_at_index(self, index: int) -> Optional[Card]:
        """
        移除指定索引的卡牌

        Args:
            index: 卡牌索引

        Returns:
            Optional[Card]: 被移除的卡牌，如果索引无效则返回None
        """
        if 0 <= index < len(self.card_components):
            card = self.card_components[index].card
            del self.card_components[index]
            self._rearrange_cards()
            return card
        return None

    def clear_cards(self):
        """清空所有手牌"""
        self.card_components.clear()

    def get_card_at_position(self, point: Tuple[int, int]) -> Optional[InteractiveCard]:
        """
        获取指定位置的卡牌组件

        Args:
            point: 检查的点坐标 (x, y)

        Returns:
            Optional[InteractiveCard]: 该位置的卡牌组件，如果没有则返回None
        """
        # 从上到下检查（后添加的卡牌在上层）
        for component in reversed(self.card_components):
            if component.is_point_inside(point):
                return component
        return None

    def get_selected_card(self) -> Optional[InteractiveCard]:
        """
        获取当前选中的卡牌

        Returns:
            Optional[InteractiveCard]: 选中的卡牌组件，如果没有则返回None
        """
        for component in self.card_components:
            if component.is_selected:
                return component
        return None

    def deselect_all_cards(self):
        """取消所有卡牌的选中状态"""
        for component in self.card_components:
            component.deselect()

    def is_full(self) -> bool:
        """
        检查手牌是否已满

        Returns:
            bool: 手牌是否已满
        """
        return len(self.card_components) >= self.max_cards

    def get_card_count(self) -> int:
        """
        获取手牌数量

        Returns:
            int: 手牌数量
        """
        return len(self.card_components)

    def _calculate_card_position(self, index: int) -> Tuple[int, int]:
        """
        计算卡牌位置

        Args:
            index: 卡牌索引

        Returns:
            Tuple[int, int]: 卡牌位置 (x, y)
        """
        # 计算总宽度
        total_width = len(self.card_components) * (self.card_width + self.card_spacing)

        # 如果还有空间添加新卡牌，计算新卡牌的位置
        if len(self.card_components) > 0:
            total_width += self.card_spacing

        # 计算起始位置（居中）
        start_x = self.position[0] + (self.size[0] - total_width) // 2

        # 计算当前卡牌的x位置
        x = start_x + index * (self.card_width + self.card_spacing)

        # y位置固定在手牌区域的底部
        y = self.position[1] + self.size[1] - self.card_height - 10

        return (x, y)

    def _rearrange_cards(self):
        """重新排列所有卡牌位置"""
        for i, component in enumerate(self.card_components):
            new_position = self._calculate_card_position(i)
            component.position = new_position
            component.current_position = new_position
            component.rect = pygame.Rect(new_position, (self.card_width, self.card_height))

    def handle_mouse_motion(self, point: Tuple[int, int]) -> bool:
        """
        处理鼠标移动事件

        Args:
            point: 鼠标位置 (x, y)

        Returns:
            bool: 是否有卡牌状态改变
        """
        changed = False
        for component in self.card_components:
            if component.handle_mouse_motion(point):
                changed = True
        return changed

    def handle_click(self, point: Tuple[int, int]) -> bool:
        """
        处理点击事件

        Args:
            point: 点击位置 (x, y)

        Returns:
            bool: 是否处理了点击事件
        """
        # 从上到下检查（后添加的卡牌在上层）
        for component in reversed(self.card_components):
            if component.handle_click(point):
                return True
        return False

    def start_drag(self, point: Tuple[int, int]) -> Optional[InteractiveCard]:
        """
        开始拖拽卡牌

        Args:
            point: 拖拽起始点 (x, y)

        Returns:
            Optional[InteractiveCard]: 被拖拽的卡牌组件，如果没有则返回None
        """
        card_component = self.get_card_at_position(point)
        if card_component and card_component.start_drag(point):
            return card_component
        return None

    def render(self, surface: pygame.Surface):
        """
        渲染手牌区域

        Args:
            surface: 目标surface
        """
        if not surface:
            return

        # 绘制手牌区域背景
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=8)

        # 绘制边框
        pygame.draw.rect(surface, self.border_color, self.rect, 2, border_radius=8)

        # 渲染所有卡牌组件
        for component in self.card_components:
            component.render(surface)

        # 绘制手牌区域标题
        self._render_title(surface)

    def _render_title(self, surface: pygame.Surface):
        """
        渲染手牌区域标题

        Args:
            surface: 目标surface
        """
        try:
            title_font = pygame.font.Font(None, 20)
            title_text = f"手牌 ({len(self.card_components)}/{self.max_cards})"
            title_surface = render_text_safely(title_text, 20, (50, 50, 150))
            title_rect = title_surface.get_rect(centerx=self.rect.centerx, y=self.rect.y - 20)
            surface.blit(title_surface, title_rect)
        except:
            pass

    def get_info(self) -> dict:
        """
        获取手牌区域信息

        Returns:
            dict: 手牌区域信息
        """
        return {
            'position': self.position,
            'size': self.size,
            'card_count': len(self.card_components),
            'max_cards': self.max_cards,
            'is_full': self.is_full(),
            'cards': [comp.card for comp in self.card_components]
        }