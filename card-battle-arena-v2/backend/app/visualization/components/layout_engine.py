"""
响应式布局引擎
"""

from typing import Dict, List, Tuple, Optional
from app.visualization.design.tokens import DesignTokens

try:
    import pygame
except ImportError:
    # 创建Mock pygame.Rect
    class MockRect:
        def __init__(self, x, y, width, height):
            self.x = x
            self.y = y
            self.width = width
            self.height = height
            self.bottom = y + height
            self.center = (x + width // 2, y + height // 2)

        def colliderect(self, other):
            return not (self.right < other.left or self.left > other.right or
                       self.bottom < other.top or self.top > other.bottom)

        @property
        def right(self):
            return self.x + self.width

        @property
        def left(self):
            return self.x

        @property
        def top(self):
            return self.y

        def __eq__(self, other):
            return (isinstance(other, MockRect) and
                   self.x == other.x and self.y == other.y and
                   self.width == other.width and self.height == other.height)

    pygame = type('pygame', (), {'Rect': MockRect})()


class LayoutEngine:
    """响应式布局引擎"""

    def __init__(self, window_width: int = 1200, window_height: int = 800):
        """
        初始化布局引擎

        Args:
            window_width: 窗口宽度
            window_height: 窗口高度
        """
        self.window_width = window_width
        self.window_height = window_height
        self.tokens = DesignTokens()
        self.min_card_spacing = 80
        self.max_card_spacing = 200
        self.max_cards_per_row = 8

    def update_window_size(self, width: int, height: int) -> None:
        """
        更新窗口尺寸

        Args:
            width: 新的窗口宽度
            height: 新的窗口高度
        """
        self.window_width = width
        self.window_height = height

    def calculate_layout(self) -> Dict:
        """
        计算完整的布局配置

        Returns:
            布局配置字典
        """
        layout = {
            'window_size': (self.window_width, self.window_height),
            'card_dimensions': self.calculate_card_dimensions(),
            'spacing': self.calculate_spacing(),
            'regions': self.calculate_regions(),
            'font_sizes': self.calculate_font_sizes(),
        }
        return layout

    def calculate_card_dimensions(self) -> Dict:
        """
        计算自适应卡牌尺寸

        Returns:
            卡牌尺寸配置
        """
        base_sizes = {
            'mobile': {'width': 80, 'height': 110},
            'tablet': {'width': 100, 'height': 140},
            'desktop': {'width': 120, 'height': 160},
            'large': {'width': 140, 'height': 190},
        }

        card_size = self.tokens.get_adaptive_value(base_sizes, self.window_width)
        return {
            'width': card_size['width'],
            'height': card_size['height'],
            'corner_radius': max(6, card_size['width'] // 15),
            'border_width': max(2, card_size['width'] // 60),
        }

    def calculate_spacing(self) -> Dict:
        """
        计算自适应间距

        Returns:
            间距配置
        """
        base_spacing = {
            'mobile': {'card': 60, 'ui': 8},
            'tablet': {'card': 100, 'ui': 12},
            'desktop': {'card': 130, 'ui': 16},
            'large': {'card': 160, 'ui': 20},
        }

        spacing = self.tokens.get_adaptive_value(base_spacing, self.window_width)
        return {
            'card': spacing['card'],
            'ui': spacing['ui'],
            'margin': max(20, self.window_width // 40),
        }

    def calculate_regions(self) -> Dict[str, pygame.Rect]:
        """
        计算界面区域布局

        Returns:
            各区域的矩形配置
        """
        margin = self.calculate_spacing()['margin']
        spacing = self.calculate_spacing()['ui']

        # 标题区域
        title_rect = pygame.Rect(0, 0, self.window_width, 70)
        title_rect.bottom = 70  # 确保Mock对象有bottom属性

        # 玩家信息区域
        info_height = 120
        player_info_rect = pygame.Rect(margin, title_rect.bottom + spacing,
                                      self.window_width // 2 - margin * 2, info_height)
        opponent_info_rect = pygame.Rect(self.window_width // 2 + margin,
                                        title_rect.bottom + spacing,
                                        self.window_width // 2 - margin * 2, info_height)

        # 战场区域
        battlefield_height = 180
        opponent_battlefield_rect = pygame.Rect(margin, player_info_rect.bottom + spacing,
                                              self.window_width - margin * 2, battlefield_height)
        player_battlefield_rect = pygame.Rect(margin, opponent_battlefield_rect.bottom + spacing,
                                             self.window_width - margin * 2, battlefield_height)

        # 手牌区域
        hand_height = 200
        hand_rect = pygame.Rect(margin, self.window_height - hand_height - margin,
                               self.window_width - margin * 2, hand_height)

        # 操作提示区域
        instructions_height = 60
        instructions_rect = pygame.Rect(0, self.window_height - instructions_height,
                                       self.window_width, instructions_height)

        return {
            'title': title_rect,
            'player_info': player_info_rect,
            'opponent_info': opponent_info_rect,
            'player_battlefield': player_battlefield_rect,
            'opponent_battlefield': opponent_battlefield_rect,
            'hand': hand_rect,
            'instructions': instructions_rect,
        }

    def calculate_font_sizes(self) -> Dict:
        """
        计算自适应字体大小

        Returns:
            字体大小配置
        """
        base_sizes = {
            'mobile': {'heading': 18, 'body': 12, 'caption': 10},
            'tablet': {'heading': 22, 'body': 14, 'caption': 11},
            'desktop': {'heading': 24, 'body': 16, 'caption': 12},
            'large': {'heading': 28, 'body': 18, 'caption': 14},
        }

        return self.tokens.get_adaptive_value(base_sizes, self.window_width)

    def calculate_card_spacing(self, card_count: int) -> int:
        """
        计算自适应卡牌间距

        Args:
            card_count: 卡牌数量

        Returns:
            卡牌间距
        """
        if card_count <= 1:
            return 0

        card_dims = self.calculate_card_dimensions()
        total_cards_width = card_count * card_dims['width']
        available_width = self.window_width - 2 * self.calculate_spacing()['margin']

        if total_cards_width >= available_width:
            # 卡牌总宽度超过可用宽度，使用最小间距
            return self.min_card_spacing

        available_spacing = available_width - total_cards_width
        spacing = available_spacing // (card_count - 1)

        # 限制间距范围
        return max(self.min_card_spacing, min(self.max_card_spacing, spacing))

    def calculate_card_positions(self, card_count: int,
                                area_rect: pygame.Rect) -> List[Tuple[int, int]]:
        """
        计算卡牌在指定区域内的位置

        Args:
            card_count: 卡牌数量
            area_rect: 区域矩形

        Returns:
            卡牌位置列表
        """
        if card_count == 0:
            return []

        spacing = self.calculate_card_spacing(card_count)
        card_dims = self.calculate_card_dimensions()

        # 计算总宽度
        total_width = card_count * card_dims['width'] + (card_count - 1) * spacing

        # 计算起始X坐标（居中对齐）
        start_x = area_rect.x + (area_rect.width - total_width) // 2
        start_y = area_rect.y + (area_rect.height - card_dims['height']) // 2

        positions = []
        for i in range(card_count):
            x = start_x + i * (card_dims['width'] + spacing)
            y = start_y
            positions.append((x, y))

        return positions

    def get_max_cards_in_area(self, area_rect: pygame.Rect) -> int:
        """
        计算指定区域最多能显示多少张卡牌

        Args:
            area_rect: 区域矩形

        Returns:
            最大卡牌数量
        """
        card_dims = self.calculate_card_dimensions()
        min_spacing = self.min_card_spacing

        # 使用最小间距计算最大数量
        available_width = area_rect.width
        max_cards = (available_width + min_spacing) // (card_dims['width'] + min_spacing)

        return min(max_cards, self.max_cards_per_row)

    def calculate_center_position(self, area_rect: pygame.Rect,
                                 item_width: int, item_height: int) -> Tuple[int, int]:
        """
        计算项目在区域内的居中位置

        Args:
            area_rect: 区域矩形
            item_width: 项目宽度
            item_height: 项目高度

        Returns:
            居中位置坐标
        """
        x = area_rect.x + (area_rect.width - item_width) // 2
        y = area_rect.y + (area_rect.height - item_height) // 2
        return (x, y)

    def calculate_relative_position(self, base_rect: pygame.Rect,
                                   relative_size: Tuple[float, float],
                                   alignment: str = 'center') -> Tuple[int, int]:
        """
        计算相对位置

        Args:
            base_rect: 基础矩形
            relative_size: 相对尺寸 (width_ratio, height_ratio)
            alignment: 对齐方式 ('center', 'top_left', 'top_right', 'bottom_left', 'bottom_right')

        Returns:
            相对位置坐标
        """
        width = int(base_rect.width * relative_size[0])
        height = int(base_rect.height * relative_size[1])

        if alignment == 'center':
            x = base_rect.x + (base_rect.width - width) // 2
            y = base_rect.y + (base_rect.height - height) // 2
        elif alignment == 'top_left':
            x = base_rect.x
            y = base_rect.y
        elif alignment == 'top_right':
            x = base_rect.x + base_rect.width - width
            y = base_rect.y
        elif alignment == 'bottom_left':
            x = base_rect.x
            y = base_rect.y + base_rect.height - height
        elif alignment == 'bottom_right':
            x = base_rect.x + base_rect.width - width
            y = base_rect.y + base_rect.height - height
        else:
            # 默认居中
            x = base_rect.x + (base_rect.width - width) // 2
            y = base_rect.y + (base_rect.height - height) // 2

        return (x, y)

    def validate_layout(self, layout: Dict) -> bool:
        """
        验证布局是否有效

        Args:
            layout: 布局配置

        Returns:
            是否有效
        """
        # 检查必要字段
        required_fields = ['card_dimensions', 'spacing', 'regions', 'font_sizes']
        for field in required_fields:
            if field not in layout:
                return False

        # 检查区域是否重叠
        regions = layout['regions']
        region_rects = list(regions.values())

        for i, rect1 in enumerate(region_rects):
            for rect2 in region_rects[i+1:]:
                if rect1.colliderect(rect2):
                    # 允许某些区域重叠（如信息区域和战场区域）
                    if not self._allow_overlap(rect1, rect2, regions):
                        return False

        return True

    def _allow_overlap(self, rect1: pygame.Rect, rect2: pygame.Rect,
                      regions: Dict) -> bool:
        """
        检查两个区域是否允许重叠

        Args:
            rect1: 第一个矩形
            rect2: 第二个矩形
            regions: 所有区域

        Returns:
            是否允许重叠
        """
        # 找到区域名称
        name1 = None
        name2 = None
        for name, rect in regions.items():
            if rect == rect1:
                name1 = name
            elif rect == rect2:
                name2 = name

        # 某些区域允许重叠
        allowed_overlaps = [
            ('player_info', 'opponent_info'),
        ]

        return (name1, name2) in allowed_overlaps or (name2, name1) in allowed_overlaps