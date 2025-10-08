"""
设计token系统
统一管理所有视觉设计元素
"""

from typing import Dict, Tuple
try:
    import pygame
except ImportError:
    pygame = None


class DesignTokens:
    """设计令牌系统 - 统一管理所有视觉元素"""

    # 颜色系统
    COLORS = {
        'primary': {
            'main': (41, 98, 255),      # 主色调
            'light': (130, 177, 255),   # 浅色
            'dark': (25, 55, 155),      # 深色
        },
        'surface': {
            'card': (248, 248, 250),     # 卡牌背景
            'board': (56, 34, 18),       # 棋盘背景
            'ui': (255, 255, 255),       # UI背景
        },
        'mana': {
            'blue': (0, 119, 190),       # 法力值蓝
            'gold': (255, 215, 0),       # 法力值金
            'empty': (128, 128, 128),    # 空法力水晶
        },
        'card': {
            'background': (248, 248, 250),    # 卡牌背景
            'border': (64, 64, 64),           # 边框
            'text': (0, 0, 0),                # 文字
            'selected': (255, 215, 0),        # 选中状态
            'hover': (200, 200, 200),         # 悬停状态
        },
        'health': {
            'full': (0, 255, 0),          # 满血
            'half': (255, 255, 0),        # 半血
            'low': (255, 0, 0),           # 低血量
        },
        'ui': {
            'background': (240, 240, 240),  # UI背景
            'border': (200, 200, 200),      # 边框
            'text': (0, 0, 0),              # 文字
            'button': (100, 149, 237),      # 按钮颜色
        }
    }

    # 间距系统
    SPACING = {
        'xs': 4,    # 极小间距
        'sm': 8,    # 小间距
        'md': 16,   # 中等间距
        'lg': 24,   # 大间距
        'xl': 32,   # 极大间距
        'xxl': 48,  # 超大间距
    }

    # 字体系统
    TYPOGRAPHY = {
        'heading': 24,    # 标题字体
        'subtitle': 18,   # 副标题字体
        'body': 14,       # 正文字体
        'caption': 12,    # 说明文字
        'button': 16,     # 按钮文字
    }

    # 卡牌尺寸
    CARD = {
        'width': 120,
        'height': 160,
        'corner_radius': 8,
        'border_width': 2,
    }

    # 动画时长（秒）
    ANIMATION = {
        'card_play': 0.5,      # 出牌动画
        'card_draw': 0.3,      # 抽牌动画
        'attack': 0.4,         # 攻击动画
        'damage': 0.6,         # 伤害显示
        'heal': 0.4,           # 治疗效果
        'hover': 0.1,          # 悬停效果
    }

    # 断点系统（响应式设计）
    BREAKPOINTS = {
        'mobile': 768,     # 移动设备
        'tablet': 1024,    # 平板设备
        'desktop': 1200,   # 桌面设备
        'large': 1600,     # 大屏幕
    }

    @staticmethod
    def get_contrast_ratio(color1: Tuple[int, int, int],
                          color2: Tuple[int, int, int]) -> float:
        """
        计算两个颜色之间的对比度

        Args:
            color1: 第一个颜色 (R, G, B)
            color2: 第二个颜色 (R, G, B)

        Returns:
            对比度比值
        """
        def get_luminance(color):
            """计算颜色的亮度"""
            r, g, b = [c / 255.0 for c in color]
            # 应用gamma校正
            r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
            g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
            b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
            return 0.2126 * r + 0.7152 * g + 0.0722 * b

        l1 = get_luminance(color1)
        l2 = get_luminance(color2)

        # 返回对比度比值
        lighter = max(l1, l2)
        darker = min(l1, l2)

        return (lighter + 0.05) / (darker + 0.05)

    @staticmethod
    def adjust_brightness(color: Tuple[int, int, int], factor: float) -> Tuple[int, int, int]:
        """
        调整颜色亮度

        Args:
            color: 原始颜色 (R, G, B)
            factor: 亮度因子 (0.0-2.0, 1.0为原始亮度)

        Returns:
            调整后的颜色
        """
        r, g, b = color
        r = max(0, min(255, int(r * factor)))
        g = max(0, min(255, int(g * factor)))
        b = max(0, min(255, int(b * factor)))
        return (r, g, b)

    @staticmethod
    def get_gradient_colors(start_color: Tuple[int, int, int],
                           end_color: Tuple[int, int, int],
                           steps: int) -> list:
        """
        生成渐变颜色序列

        Args:
            start_color: 起始颜色
            end_color: 结束颜色
            steps: 渐变步数

        Returns:
            渐变颜色列表
        """
        colors = []
        for i in range(steps):
            factor = i / (steps - 1) if steps > 1 else 0
            r = start_color[0] + (end_color[0] - start_color[0]) * factor
            g = start_color[1] + (end_color[1] - start_color[1]) * factor
            b = start_color[2] + (end_color[2] - start_color[2]) * factor
            colors.append((int(r), int(g), int(b)))
        return colors

    @classmethod
    def get_adaptive_value(cls, base_values: Dict[str, int],
                          window_width: int) -> int:
        """
        根据窗口大小获取自适应值

        Args:
            base_values: 基础值字典 {'mobile': int, 'tablet': int, 'desktop': int}
            window_width: 当前窗口宽度

        Returns:
            适配的值
        """
        if window_width < cls.BREAKPOINTS['mobile']:
            return base_values.get('mobile', list(base_values.values())[0])
        elif window_width < cls.BREAKPOINTS['tablet']:
            return base_values.get('tablet', list(base_values.values())[1])
        elif window_width < cls.BREAKPOINTS['desktop']:
            return base_values.get('desktop', list(base_values.values())[2])
        else:
            return base_values.get('large', list(base_values.values())[-1])

    @staticmethod
    def interpolate_color(color1: Tuple[int, int, int],
                         color2: Tuple[int, int, int],
                         t: float) -> Tuple[int, int, int]:
        """
        在两个颜色之间插值

        Args:
            color1: 第一个颜色
            color2: 第二个颜色
            t: 插值参数 (0.0-1.0)

        Returns:
            插值后的颜色
        """
        r = int(color1[0] + (color2[0] - color1[0]) * t)
        g = int(color1[1] + (color2[1] - color1[1]) * t)
        b = int(color1[2] + (color2[2] - color1[2]) * t)
        return (r, g, b)