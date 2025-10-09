"""
Windows 11 字体管理器

专门针对Windows 11环境优化的字体管理系统，解决中文字符显示问题。
"""

import pygame
import os
from typing import Dict, Optional, Tuple, Any
from functools import lru_cache


class WindowsFontManager:
    """
    Windows 11 优化的字体管理器

    提供中文字符支持、智能字体降级和性能优化功能。
    """

    # Windows 11 字体优先级 (按中文支持质量排序)
    WINDOWS_FONT_PRIORITY = [
        'microsoftyahei',    # 微软雅黑 - Windows 11 默认中文字体
        'simhei',           # 黑体 - 传统中文字体
        'simsun',           # 宋体 - 传统中文字体
        'kaiti',            # 楷体 - 中文艺术字体
        'fangsong',         # 仿宋体 - 中文艺术字体
        'notosanscjk',      # 思源黑体 - 现代中文字体
        'arial',            # Arial - 国际通用字体
        'ubuntu',           # Ubuntu - Linux 常见字体
        'dejavusans',       # DejaVu Sans - 开源字体
        'freesansbold'      # 最后降级选项
    ]

    # Windows 系统字体文件路径
    WINDOWS_FONT_PATHS = [
        'C:/Windows/Fonts/msyh.ttc',      # 微软雅黑
        'C:/Windows/Fonts/simhei.ttf',    # 黑体
        'C:/Windows/Fonts/simsun.ttc',    # 宋体
        'C:/Windows/Fonts/simkai.ttf',    # 楷体
        'C:/Windows/Fonts/simfang.ttf',   # 仿宋体
    ]

    # 字体缓存 (提高性能)
    _font_cache: Dict[Tuple[int, bool], pygame.font.Font] = {}
    _font_cache_enabled = True

    # 测试文本 (用于检测中文支持)
    CHINESE_TEST_TEXTS = ['测试', '中文', '游戏', '卡牌', '玩家']
    ENGLISH_TEST_TEXTS = ['Test', 'Game', 'Card', 'Player']

    @classmethod
    def test_font_chinese_support(cls, font_name: str, size: int = 20) -> bool:
        """
        测试字体是否支持中文

        Args:
            font_name: 字体名称
            size: 字体大小

        Returns:
            bool: 是否支持中文
        """
        try:
            font = pygame.font.SysFont(font_name, size)
            # 测试中文字符渲染
            for test_text in cls.CHINESE_TEST_TEXTS:
                surface = font.render(test_text, True, (0, 0, 0))
                if surface.get_width() == 0:
                    return False
            return True
        except Exception:
            return False

    @classmethod
    def test_font_english_support(cls, font_name: str, size: int = 20) -> bool:
        """
        测试字体是否支持英文

        Args:
            font_name: 字体名称
            size: 字体大小

        Returns:
            bool: 是否支持英文
        """
        try:
            font = pygame.font.SysFont(font_name, size)
            # 测试英文字符渲染
            for test_text in cls.ENGLISH_TEST_TEXTS:
                surface = font.render(test_text, True, (0, 0, 0))
                if surface.get_width() == 0:
                    return False
            return True
        except Exception:
            return False

    @classmethod
    def get_best_font(cls, size: int, prefer_chinese: bool = True) -> pygame.font.Font:
        """
        获取最佳可用字体

        Args:
            size: 字体大小
            prefer_chinese: 是否优先选择支持中文的字体

        Returns:
            pygame.font.Font: 最佳字体
        """
        # 检查缓存
        cache_key = (size, prefer_chinese)
        if cls._font_cache_enabled and cache_key in cls._font_cache:
            return cls._font_cache[cache_key]

        font = None

        # 首先尝试加载系统字体文件
        if prefer_chinese:
            for font_path in cls.WINDOWS_FONT_PATHS:
                if os.path.exists(font_path):
                    try:
                        font = pygame.font.Font(font_path, size)
                        # 测试中文支持
                        test_surface = font.render("测试", True, (0, 0, 0))
                        if test_surface.get_width() > 0:
                            break
                        else:
                            font = None
                    except Exception:
                        font = None

        if font is None and prefer_chinese:
            # 优先选择支持中文的字体
            for font_name in cls.WINDOWS_FONT_PRIORITY:
                if cls.test_font_chinese_support(font_name, size):
                    font = pygame.font.SysFont(font_name, size)
                    break

        # 如果没有找到支持中文的字体或不需要中文支持
        if font is None:
            for font_name in cls.WINDOWS_FONT_PRIORITY:
                if cls.test_font_english_support(font_name, size):
                    font = pygame.font.SysFont(font_name, size)
                    break

        # 最后降级到默认字体
        if font is None:
            try:
                font = pygame.font.Font(None, size)
            except Exception:
                # 如果连默认字体都失败，使用最小的字体
                font = pygame.font.SysFont('arial', size)

        # 缓存字体
        if cls._font_cache_enabled:
            cls._font_cache[cache_key] = font

        return font

    @classmethod
    def get_chinese_font(cls, size: int) -> pygame.font.Font:
        """
        获取支持中文的字体

        Args:
            size: 字体大小

        Returns:
            pygame.font.Font: 支持中文的字体
        """
        return cls.get_best_font(size, prefer_chinese=True)

    @classmethod
    @lru_cache(maxsize=128)
    def render_chinese_text(cls, text: str, size: int, color: Tuple[int, int, int]) -> pygame.Surface:
        """
        渲染中文文本 (带缓存优化)

        Args:
            text: 要渲染的文本
            size: 字体大小
            color: 文字颜色

        Returns:
            pygame.Surface: 渲染后的文本表面
        """
        font = cls.get_chinese_font(size)
        return font.render(text, True, color)

    @classmethod
    @lru_cache(maxsize=128)
    def render_text_safely(cls, text: str, size: int, color: Tuple[int, int, int]) -> pygame.Surface:
        """
        安全渲染文本，带有降级机制

        Args:
            text: 要渲染的文本
            size: 字体大小
            color: 文字颜色

        Returns:
            pygame.Surface: 渲染后的文本表面
        """
        try:
            # 尝试使用最佳字体渲染
            font = cls.get_best_font(size, prefer_chinese=True)
            return font.render(text, True, color)
        except Exception:
            try:
                # 降级到英文显示
                english_text = ''.join(c for c in text if ord(c) < 128)
                if english_text:
                    font = cls.get_best_font(size, prefer_chinese=False)
                    return font.render(english_text, True, color)
                else:
                    # 如果连英文都没有，使用简单标识
                    font = cls.get_best_font(size, prefer_chinese=False)
                    return font.render("Card", True, color)
            except Exception:
                # 最后的降级选项
                try:
                    font = pygame.font.Font(None, size)
                    return font.render("Card", True, color)
                except Exception:
                    # 创建一个最小的表面
                    surface = pygame.Surface((100, 20))
                    surface.fill(color)
                    return surface

    @classmethod
    def clear_font_cache(cls):
        """清空字体缓存"""
        cls._font_cache.clear()
        cls.render_chinese_text.cache_clear()
        cls.render_text_safely.cache_clear()

    @classmethod
    def enable_font_cache(cls, enabled: bool = True):
        """
        启用/禁用字体缓存

        Args:
            enabled: 是否启用缓存
        """
        cls._font_cache_enabled = enabled
        if not enabled:
            cls.clear_font_cache()

    @classmethod
    def get_font_info(cls) -> Dict[str, Any]:
        """
        获取字体管理器信息

        Returns:
            Dict[str, any]: 字体管理器状态信息
        """
        available_chinese_fonts = []
        available_english_fonts = []

        for font_name in cls.WINDOWS_FONT_PRIORITY:
            if cls.test_font_chinese_support(font_name):
                available_chinese_fonts.append(font_name)
            if cls.test_font_english_support(font_name):
                available_english_fonts.append(font_name)

        return {
            'chinese_fonts': available_chinese_fonts,
            'english_fonts': available_english_fonts,
            'cache_enabled': cls._font_cache_enabled,
            'cache_size': len(cls._font_cache),
            'platform': 'Windows'
        }

    @classmethod
    def debug_render_sample(cls, surface: pygame.Surface, x: int, y: int) -> None:
        """
        在指定表面渲染字体示例 (用于调试)

        Args:
            surface: 目标表面
            x: 起始X坐标
            y: 起始Y坐标
        """
        if not surface:
            return

        try:
            # 渲染不同字体的示例
            sample_text = "中文字体测试"
            y_offset = 0

            for font_name in cls.WINDOWS_FONT_PRIORITY[:5]:  # 只显示前5个
                if cls.test_font_chinese_support(font_name, 16):
                    font = pygame.font.SysFont(font_name, 16)
                    text_surface = font.render(f"{font_name}: {sample_text}", True, (0, 0, 0))
                    surface.blit(text_surface, (x, y + y_offset))
                    y_offset += 25

            # 显示当前最佳字体
            best_font = cls.get_best_font(16)
            best_surface = best_font.render(f"当前字体: {sample_text}", True, (255, 0, 0))
            surface.blit(best_surface, (x, y + y_offset + 10))

        except Exception as e:
            # 如果调试渲染失败，显示错误信息
            try:
                error_font = pygame.font.Font(None, 16)
                error_surface = error_font.render(f"字体调试错误: {str(e)}", True, (255, 0, 0))
                surface.blit(error_surface, (x, y))
            except:
                pass


# 全局字体管理器实例
font_manager = WindowsFontManager()

# 便捷函数
def get_best_font(size: int, prefer_chinese: bool = True) -> pygame.font.Font:
    """获取最佳字体的便捷函数"""
    return WindowsFontManager.get_best_font(size, prefer_chinese)

def render_chinese_text(text: str, size: int, color: Tuple[int, int, int]) -> pygame.Surface:
    """渲染中文文本的便捷函数"""
    return WindowsFontManager.render_chinese_text(text, size, color)

def render_text_safely(text: str, size: int, color: Tuple[int, int, int]) -> pygame.Surface:
    """安全渲染文本的便捷函数"""
    return WindowsFontManager.render_text_safely(text, size, color)