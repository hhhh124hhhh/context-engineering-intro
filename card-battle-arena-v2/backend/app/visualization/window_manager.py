"""
动态窗口配置管理器

统一管理游戏窗口尺寸、响应式布局和UI组件配置。
解决窗口设置不一致和缺乏响应式适配的问题。
"""

import pygame
from typing import Dict, Tuple, Optional, Any
from dataclasses import dataclass


@dataclass
class WindowConfig:
    """窗口配置类"""
    width: int = 1200
    height: int = 800
    title: str = "Card Battle Arena - 卡牌对战竞技场"
    fps: int = 60
    fullscreen: bool = False
    resizable: bool = True


@dataclass
class LayoutConfig:
    """布局配置类"""
    # 区域高度定义 (统一解决冲突)
    hud_height: int = 80  # 统一HUD高度 (解决60px vs 80px冲突)
    opponent_info_height: int = 70
    battlefield_height: int = 180
    player_info_height: int = 70
    hand_area_height: int = 240  # 增加手牌区域高度 (原210px -> 240px)
    controls_height: int = 50

    # 间距和边距
    margin: int = 50
    spacing: int = 20

    # 卡牌尺寸
    card_width: int = 120
    card_height: int = 160


class WindowManager:
    """
    动态窗口配置管理器

    提供统一的窗口尺寸管理和响应式布局计算功能。
    """

    def __init__(self, window_config: Optional[WindowConfig] = None):
        """
        初始化窗口管理器

        Args:
            window_config: 窗口配置，为None时使用默认配置
        """
        self.window_config = window_config or WindowConfig()
        self.layout_config = LayoutConfig()

        # Pygame相关
        self.screen = None
        self.clock = None

        # 缓存计算结果
        self._layout_cache: Dict[str, Any] = {}
        self._cache_valid = False

    def create_window(self) -> bool:
        """
        创建游戏窗口

        Returns:
            bool: 是否成功创建窗口
        """
        try:
            pygame.init()

            # 设置窗口尺寸
            if self.window_config.fullscreen:
                self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            else:
                self.screen = pygame.display.set_mode(
                    (self.window_config.width, self.window_config.height),
                    pygame.RESIZABLE if self.window_config.resizable else 0
                )

            # 设置窗口标题
            pygame.display.set_caption(self.window_config.title)

            # 创建时钟
            self.clock = pygame.time.Clock()

            # 清除缓存
            self._cache_valid = False

            print(f"✓ 窗口创建成功: {self.window_config.width}x{self.window_config.height}")
            return True

        except Exception as e:
            print(f"❌ 窗口创建失败: {e}")
            return False

    def handle_resize(self, new_width: int, new_height: int):
        """
        处理窗口大小变化

        Args:
            new_width: 新宽度
            new_height: 新高度
        """
        # 更新窗口配置
        self.window_config.width = new_width
        self.window_config.height = new_height

        # 重新创建窗口surface
        self.screen = pygame.display.set_mode(
            (new_width, new_height),
            pygame.RESIZABLE if self.window_config.resizable else 0
        )

        # 清除缓存，强制重新计算布局
        self._cache_valid = False

        print(f"🔄 窗口大小已调整: {new_width}x{new_height}")

    def get_layout_regions(self) -> Dict[str, Tuple[int, int, int, int]]:
        """
        获取所有UI区域的布局配置

        Returns:
            Dict[str, Tuple[int, int, int, int]]: 区域名称到 (x, y, width, height) 的映射
        """
        if self._cache_valid and 'regions' in self._layout_cache:
            return self._layout_cache['regions']

        regions = {}
        w, h = self.window_config.width, self.window_config.height
        l = self.layout_config

        # HUD区域 (顶部)
        regions['hud'] = (0, 0, w, l.hud_height)

        # 对手信息区域
        regions['opponent_info'] = (
            l.margin,
            l.hud_height + l.spacing,
            w - 2 * l.margin,
            l.opponent_info_height
        )

        # 对手战场区域
        regions['opponent_battlefield'] = (
            l.margin,
            l.hud_height + l.opponent_info_height + 2 * l.spacing,
            w - 2 * l.margin,
            l.battlefield_height
        )

        # 中央战斗区域 (剩余空间)
        central_y_start = l.hud_height + l.opponent_info_height + l.battlefield_height + 3 * l.spacing
        central_height = h - central_y_start - l.player_info_height - l.hand_area_height - l.controls_height - 4 * l.spacing
        regions['battle_area'] = (0, central_y_start, w, max(0, central_height))

        # 玩家信息区域
        player_info_y = central_y_start + central_height + l.spacing
        regions['player_info'] = (
            l.margin,
            player_info_y,
            w - 2 * l.margin,
            l.player_info_height
        )

        # 玩家战场区域
        player_battlefield_y = player_info_y + l.player_info_height + l.spacing
        regions['player_battlefield'] = (
            l.margin,
            player_battlefield_y,
            w - 2 * l.margin,
            l.battlefield_height
        )

        # 手牌区域
        hand_y = h - l.hand_area_height - l.controls_height - l.spacing
        regions['hand_area'] = (
            l.margin,
            hand_y,
            w - 2 * l.margin,
            l.hand_area_height
        )

        # 游戏控制区域
        regions['game_controls'] = (
            0,
            h - l.controls_height,
            w,
            l.controls_height
        )

        # 缓存结果
        self._layout_cache['regions'] = regions
        self._cache_valid = True

        return regions

    def get_end_turn_button_rect(self) -> Tuple[int, int, int, int]:
        """
        获取结束回合按钮的位置和尺寸

        Returns:
            Tuple[int, int, int, int]: (x, y, width, height)
        """
        if self._cache_valid and 'end_turn_button' in self._layout_cache:
            return self._layout_cache['end_turn_button']

        w, h = self.window_config.width, self.window_config.height
        l = self.layout_config

        # 按钮居中显示在底部控制区域
        button_width = 200
        button_height = 40
        button_x = (w - button_width) // 2
        button_y = h - l.controls_height + 5

        button_rect = (button_x, button_y, button_width, button_height)

        # 缓存结果
        self._layout_cache['end_turn_button'] = button_rect

        return button_rect

    def calculate_card_positions(self, card_count: int, region_name: str) -> list:
        """
        计算卡牌在指定区域的位置

        Args:
            card_count: 卡牌数量
            region_name: 区域名称 ('hand_area', 'player_battlefield', 'opponent_battlefield')

        Returns:
            list: 卡牌位置列表 [(x, y), ...]
        """
        regions = self.get_layout_regions()

        if region_name not in regions:
            return []

        region_x, region_y, region_width, region_height = regions[region_name]
        l = self.layout_config

        # 计算总宽度
        total_width = card_count * l.card_width + (card_count - 1) * l.spacing

        # 如果总宽度超过区域宽度，调整间距
        if total_width > region_width and card_count > 1:
            l.spacing = max(10, (region_width - card_count * l.card_width) // (card_count - 1))
            total_width = card_count * l.card_width + (card_count - 1) * l.spacing

        # 计算起始X坐标（居中对齐）
        start_x = region_x + (region_width - total_width) // 2

        # 计算Y坐标（垂直居中）
        start_y = region_y + (region_height - l.card_height) // 2

        # 生成所有卡牌位置
        positions = []
        for i in range(card_count):
            x = start_x + i * (l.card_width + l.spacing)
            y = start_y
            positions.append((x, y))

        return positions

    def is_valid_window_size(self, width: int, height: int) -> bool:
        """
        检查窗口尺寸是否有效

        Args:
            width: 窗口宽度
            height: 窗口高度

        Returns:
            bool: 是否有效
        """
        # 最小尺寸要求
        min_width = 800
        min_height = 600

        # 计算最小所需高度
        l = self.layout_config
        min_required_height = (
            l.hud_height +
            l.opponent_info_height +
            l.battlefield_height +
            l.player_info_height +
            l.hand_area_height +
            l.controls_height +
            8 * l.spacing  # 间距总和
        )

        return width >= min_width and height >= max(min_height, min_required_height)

    def get_optimal_window_size(self, target_width: Optional[int] = None,
                               target_height: Optional[int] = None) -> Tuple[int, int]:
        """
        获取最优的窗口尺寸

        Args:
            target_width: 目标宽度
            target_height: 目标高度

        Returns:
            Tuple[int, int]: 优化的窗口尺寸 (width, height)
        """
        # 使用默认值或目标值
        width = target_width or self.window_config.width
        height = target_height or self.window_config.height

        # 确保满足最小尺寸要求
        if not self.is_valid_window_size(width, height):
            # 计算最小所需高度
            l = self.layout_config
            min_height = (
                l.hud_height +
                l.opponent_info_height +
                l.battlefield_height +
                l.player_info_height +
                l.hand_area_height +
                l.controls_height +
                8 * l.spacing
            )

            width = max(800, width)
            height = max(600, min_height)

        return (width, height)

    def update_from_settings(self, settings_dict: Dict[str, Any]):
        """
        从设置字典更新窗口配置

        Args:
            settings_dict: 设置字典
        """
        if 'window_width' in settings_dict:
            self.window_config.width = settings_dict['window_width']

        if 'window_height' in settings_dict:
            self.window_config.height = settings_dict['window_height']

        if 'fullscreen' in settings_dict:
            self.window_config.fullscreen = settings_dict['fullscreen']

        if 'fps' in settings_dict:
            self.window_config.fps = settings_dict['fps']

        # 清除缓存，强制重新计算
        self._cache_valid = False

    def get_info(self) -> Dict[str, Any]:
        """
        获取窗口管理器信息

        Returns:
            Dict[str, Any]: 窗口管理器信息
        """
        return {
            'window_config': {
                'width': self.window_config.width,
                'height': self.window_config.height,
                'title': self.window_config.title,
                'fullscreen': self.window_config.fullscreen,
                'fps': self.window_config.fps
            },
            'layout_config': {
                'hud_height': self.layout_config.hud_height,
                'hand_area_height': self.layout_config.hand_area_height,
                'controls_height': self.layout_config.controls_height,
                'margin': self.layout_config.margin,
                'spacing': self.layout_config.spacing
            },
            'regions': self.get_layout_regions(),
            'cache_valid': self._cache_valid
        }


# 全局窗口管理器实例
_global_window_manager: Optional[WindowManager] = None


def get_window_manager() -> WindowManager:
    """
    获取全局窗口管理器实例

    Returns:
        WindowManager: 全局窗口管理器
    """
    global _global_window_manager
    if _global_window_manager is None:
        _global_window_manager = WindowManager()
    return _global_window_manager


def create_window_manager(width: int = 1200, height: int = 800,
                         fullscreen: bool = False) -> WindowManager:
    """
    创建窗口管理器实例

    Args:
        width: 窗口宽度
        height: 窗口高度
        fullscreen: 是否全屏

    Returns:
        WindowManager: 窗口管理器实例
    """
    config = WindowConfig(width=width, height=height, fullscreen=fullscreen)
    return WindowManager(config)