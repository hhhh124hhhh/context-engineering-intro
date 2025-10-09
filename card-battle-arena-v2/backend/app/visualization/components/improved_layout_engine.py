"""
改进的响应式布局引擎
基于UI布局分析与改进方案的实现
"""

from typing import Dict, List, Tuple, Optional
from app.visualization.design.tokens import DesignTokens
from app.visualization.ui_layout_config import UI_LAYOUT_CONFIG, validate_layout

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


class ImprovedLayoutEngine:
    """改进的响应式布局引擎"""

    def __init__(self, window_width: int = 1200, window_height: int = 800):
        """
        初始化改进的布局引擎

        Args:
            window_width: 窗口宽度
            window_height: 窗口高度
        """
        self.window_width = window_width
        self.window_height = window_height
        self.tokens = DesignTokens()
        self.layout_config = UI_LAYOUT_CONFIG

        # 验证配置
        self._validate_configuration()

    def _validate_configuration(self) -> None:
        """验证布局配置"""
        if not validate_layout(self.layout_config):
            print("警告: 布局配置验证失败，使用默认配置")

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
        计算完整的改进布局配置

        Returns:
            布局配置字典
        """
        layout = {
            'window_size': (self.window_width, self.window_height),
            'card_dimensions': self.calculate_card_dimensions(),
            'regions': self.calculate_improved_regions(),
            'components': self.calculate_component_positions(),
            'font_sizes': self.calculate_font_sizes(),
            'validation_status': self._validate_current_layout()
        }
        return layout

    def calculate_card_dimensions(self) -> Dict:
        """
        计算改进的卡牌尺寸配置

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
            'hand_hover_height': min(card_size['height'] + 20, 180),
            'hand_drag_height': min(card_size['height'] + 40, 200),
        }

    def calculate_improved_regions(self) -> Dict[str, pygame.Rect]:
        """
        计算改进后的界面区域布局

        Returns:
            各区域的矩形配置
        """
        regions = {}

        # 从配置文件中获取区域定义
        for region_name, config in self.layout_config['regions'].items():
            position = config['position']
            size = config['size']

            # 创建矩形区域
            rect = pygame.Rect(position[0], position[1], size[0], size[1])
            regions[region_name] = rect

        return regions

    def calculate_component_positions(self) -> Dict:
        """
        计算UI组件位置

        Returns:
            组件位置配置
        """
        components = {}

        for component_name, config in self.layout_config['components'].items():
            position = config['position']

            # 处理特殊组件（如mana_crystals可能没有size属性）
            if 'size' in config:
                size = config['size']
            elif component_name == 'mana_crystals':
                # 为mana_crystals计算一个合理的size
                crystal_count = 10  # 默认10个水晶
                crystal_size = config.get('crystal_size', 20)
                crystal_spacing = config.get('crystal_spacing', 25)
                total_width = crystal_count * crystal_size + (crystal_count - 1) * crystal_spacing
                size = (total_width, crystal_size)
            else:
                # 默认尺寸
                size = (100, 30)

            # 创建组件矩形
            rect = pygame.Rect(position[0], position[1], size[0], size[1])
            components[component_name] = {
                'rect': rect,
                'config': config
            }

        return components

    def calculate_font_sizes(self) -> Dict:
        """
        计算自适应字体大小

        Returns:
            字体大小配置
        """
        base_sizes = {
            'mobile': {'title': 18, 'heading': 16, 'body': 12, 'caption': 10},
            'tablet': {'title': 20, 'heading': 18, 'body': 14, 'caption': 11},
            'desktop': {'title': 24, 'heading': 20, 'body': 16, 'caption': 12},
            'large': {'title': 28, 'heading': 24, 'body': 18, 'caption': 14},
        }

        return self.tokens.get_adaptive_value(base_sizes, self.window_width)

    def calculate_card_positions(self, card_count: int,
                                region_name: str) -> List[Tuple[int, int]]:
        """
        计算卡牌在指定区域内的位置（改进版）

        Args:
            card_count: 卡牌数量
            region_name: 区域名称

        Returns:
            卡牌位置列表
        """
        if card_count == 0:
            return []

        # 获取区域配置
        region_config = self.layout_config['regions'].get(region_name)
        if not region_config:
            return []

        area_rect = pygame.Rect(
            region_config['position'][0],
            region_config['position'][1],
            region_config['size'][0],
            region_config['size'][1]
        )

        card_dims = self.calculate_card_dimensions()

        # 根据区域类型调整间距计算
        if region_name == 'player_hand':
            # 手牌区域需要更大的操作空间
            spacing = self._calculate_hand_spacing(card_count, area_rect)
            # 手牌区域的Y位置需要考虑悬停和拖拽空间
            start_y = area_rect.y + 30  # 预留顶部空间
        else:
            spacing = self._calculate_battlefield_spacing(card_count, area_rect)
            start_y = area_rect.y + (area_rect.height - card_dims['height']) // 2

        # 计算总宽度
        total_width = card_count * card_dims['width'] + (card_count - 1) * spacing

        # 计算起始X坐标（居中对齐）
        start_x = area_rect.x + (area_rect.width - total_width) // 2

        positions = []
        for i in range(card_count):
            x = start_x + i * (card_dims['width'] + spacing)
            y = start_y
            positions.append((x, y))

        return positions

    def _calculate_hand_spacing(self, card_count: int, area_rect: pygame.Rect) -> int:
        """
        计算手牌区域的卡牌间距

        Args:
            card_count: 卡牌数量
            area_rect: 区域矩形

        Returns:
            卡牌间距
        """
        card_dims = self.calculate_card_dimensions()
        min_spacing = 20
        max_spacing = 40

        if card_count <= 1:
            return 0

        total_cards_width = card_count * card_dims['width']
        available_width = area_rect.width - 100  # 预留边距

        if total_cards_width >= available_width:
            return min_spacing

        available_spacing = available_width - total_cards_width
        spacing = available_spacing // (card_count - 1)

        return max(min_spacing, min(max_spacing, spacing))

    def _calculate_battlefield_spacing(self, card_count: int, area_rect: pygame.Rect) -> int:
        """
        计算战场区域的卡牌间距

        Args:
            card_count: 卡牌数量
            area_rect: 区域矩形

        Returns:
            卡牌间距
        """
        card_dims = self.calculate_card_dimensions()
        min_spacing = 15
        max_spacing = 30

        if card_count <= 1:
            return 0

        total_cards_width = card_count * card_dims['width']
        available_width = area_rect.width - 80  # 预留边距

        if total_cards_width >= available_width:
            return min_spacing

        available_spacing = available_width - total_cards_width
        spacing = available_spacing // (card_count - 1)

        return max(min_spacing, min(max_spacing, spacing))

    def get_max_cards_in_area(self, region_name: str) -> int:
        """
        计算指定区域最多能显示多少张卡牌

        Args:
            region_name: 区域名称

        Returns:
            最大卡牌数量
        """
        region_config = self.layout_config['regions'].get(region_name)
        if not region_config:
            return 0

        area_rect = pygame.Rect(
            region_config['position'][0],
            region_config['position'][1],
            region_config['size'][0],
            region_config['size'][1]
        )

        card_dims = self.calculate_card_dimensions()

        # 根据区域类型使用不同的最小间距
        if region_name == 'player_hand':
            min_spacing = 20
            margin = 100
        else:
            min_spacing = 15
            margin = 80

        available_width = area_rect.width - margin
        max_cards = (available_width + min_spacing) // (card_dims['width'] + min_spacing)

        # 手牌区域最多7张，战场最多8张
        if region_name == 'player_hand':
            return min(max_cards, 7)
        else:
            return min(max_cards, 8)

    def calculate_hover_position(self, base_position: Tuple[int, int],
                                card_index: int, total_cards: int) -> Tuple[int, int]:
        """
        计算卡牌悬停时的位置

        Args:
            base_position: 基础位置
            card_index: 卡牌索引
            total_cards: 总卡牌数

        Returns:
            悬停位置
        """
        card_dims = self.calculate_card_dimensions()
        x, y = base_position

        # 悬停时卡牌上移，并且略微放大
        hover_y_offset = -20
        hover_height = card_dims['hand_hover_height']

        # 居中对齐Y坐标
        hand_region = self.layout_config['regions']['player_hand']
        region_height = hand_region['size'][1]
        hover_y = hand_region['position'][1] + (region_height - hover_height) // 2

        return (x, hover_y)

    def calculate_drag_position(self, mouse_pos: Tuple[int, int]) -> Tuple[int, int]:
        """
        计算拖拽时卡牌的位置

        Args:
            mouse_pos: 鼠标位置

        Returns:
            拖拽位置
        """
        card_dims = self.calculate_card_dimensions()
        drag_height = card_dims['hand_drag_height']

        # 卡牌跟随鼠标，但居中对齐
        x = mouse_pos[0] - card_dims['width'] // 2
        y = mouse_pos[1] - drag_height // 2

        return (x, y)

    def _validate_current_layout(self) -> Dict:
        """
        验证当前布局的有效性

        Returns:
            验证结果字典
        """
        validation_result = {
            'is_valid': True,
            'warnings': [],
            'errors': []
        }

        # 检查手牌区域
        hand_config = self.layout_config['regions']['player_hand']
        hand_height = hand_config['size'][1]
        card_dims = self.calculate_card_dimensions()

        if hand_height < card_dims['height'] + 50:
            validation_result['errors'].append(
                f"手牌区域高度 {hand_height}px 不足，推荐至少 {card_dims['height'] + 50}px"
            )
            validation_result['is_valid'] = False

        # 检查组件重叠
        regions = self.calculate_improved_regions()
        region_names = list(regions.keys())

        for i, name1 in enumerate(region_names):
            for name2 in region_names[i+1:]:
                rect1 = regions[name1]
                rect2 = regions[name2]

                if rect1.colliderect(rect2):
                    validation_result['warnings'].append(
                        f"区域 {name1} 和 {name2} 可能存在重叠"
                    )

        # 检查按钮可点击性
        button_config = self.layout_config['components']['end_turn_button']
        button_size = button_config['size']
        min_touch_target = 44

        if button_size[0] < min_touch_target or button_size[1] < min_touch_target:
            validation_result['warnings'].append(
                f"结束回合按钮尺寸 {button_size} 小于推荐最小触摸目标 {min_touch_target}px"
            )

        return validation_result

    def get_layout_improvements(self) -> List[str]:
        """
        获取布局改进建议

        Returns:
            改进建议列表
        """
        improvements = []

        # 基于验证结果提供建议
        validation = self._validate_current_layout()

        if not validation['is_valid']:
            improvements.extend(validation['errors'])

        # 通用改进建议
        card_dims = self.calculate_card_dimensions()
        hand_config = self.layout_config['regions']['player_hand']

        if hand_config['size'][1] > card_dims['height'] + 80:
            improvements.append("手牌区域高度充足，可以添加卡牌动画效果")

        if self.window_width >= 1400:
            improvements.append("窗口宽度较大，可以考虑添加侧边栏信息面板")

        return improvements

    def export_layout_config(self) -> Dict:
        """
        导出当前布局配置（用于保存或分享）

        Returns:
            完整的布局配置
        """
        return {
            'window_size': (self.window_width, self.window_height),
            'layout_timestamp': '2024-01-01',  # 实际使用时应该是当前时间
            'config': self.layout_config,
            'calculated_layout': self.calculate_layout(),
            'validation': self._validate_current_layout()
        }