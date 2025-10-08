"""
测试Pygame组件化架构
"""

import pytest
import pygame
from unittest.mock import Mock, patch
from app.visualization.pygame_renderer import PygameRenderer


class TestDesignTokens:
    """测试设计token系统"""

    def test_design_tokens_exist(self):
        """测试设计token系统是否存在"""
        # 这个测试会失败，因为我们还没有创建设计token系统
        from app.visualization.design.tokens import DesignTokens

        # 验证基础颜色定义
        assert hasattr(DesignTokens, 'COLORS')
        assert hasattr(DesignTokens, 'SPACING')
        assert hasattr(DesignTokens, 'TYPOGRAPHY')

        # 验证颜色系统
        assert 'primary' in DesignTokens.COLORS
        assert 'surface' in DesignTokens.COLORS
        assert 'mana' in DesignTokens.COLORS

    def test_card_colors_consistency(self):
        """测试卡牌颜色一致性"""
        from app.visualization.design.tokens import DesignTokens

        # 验证卡牌相关颜色
        card_colors = DesignTokens.COLORS['card']
        assert 'background' in card_colors
        assert 'border' in card_colors
        assert 'text' in card_colors

        # 验证颜色对比度
        assert DesignTokens.get_contrast_ratio(
            card_colors['text'],
            card_colors['background']
        ) > 4.5  # WCAG AA标准

    def test_spacing_system(self):
        """测试间距系统"""
        from app.visualization.design.tokens import DesignTokens

        spacing = DesignTokens.SPACING
        assert 'xs' in spacing
        assert 'sm' in spacing
        assert 'md' in spacing
        assert 'lg' in spacing
        assert 'xl' in spacing

        # 验证间距递增关系
        assert spacing['xs'] < spacing['sm'] < spacing['md'] < spacing['lg'] < spacing['xl']


class TestComponentizedCardRenderer:
    """测试组件化卡牌渲染器"""

    def test_card_renderer_component_exists(self):
        """测试卡牌渲染器组件是否存在"""
        from app.visualization.components.card_renderer import CardRenderer

        # 验证组件可以实例化
        renderer = CardRenderer()
        assert renderer is not None
        assert hasattr(renderer, 'render_card')
        assert hasattr(renderer, 'render_card_background')
        assert hasattr(renderer, 'render_card_content')

    def test_card_rendering_with_gradients(self):
        """测试卡牌渐变渲染"""
        from app.visualization.components.card_renderer import CardRenderer
        from app.game.cards import Card, CardType

        # 创建测试卡牌
        card = Card(1, "测试卡牌", 3, 4, 5, CardType.MINION)

        # 模拟Pygame surface
        mock_surface = Mock()

        renderer = CardRenderer()
        renderer.render_card(card, (100, 100), mock_surface)

        # 验证渲染方法被调用
        assert mock_surface.blit.called

    def test_card_highlight_states(self):
        """测试卡牌高亮状态"""
        from app.visualization.components.card_renderer import CardRenderer

        renderer = CardRenderer()

        # 测试不同状态的颜色
        normal_color = renderer.get_card_color('normal')
        selected_color = renderer.get_card_color('selected')
        hover_color = renderer.get_card_color('hover')

        assert normal_color != selected_color
        assert normal_color != hover_color
        assert selected_color != hover_color


class TestResponsiveLayoutEngine:
    """测试响应式布局引擎"""

    def test_layout_engine_exists(self):
        """测试布局引擎是否存在"""
        from app.visualization.components.layout_engine import LayoutEngine

        engine = LayoutEngine(1200, 800)
        assert engine is not None
        assert hasattr(engine, 'calculate_layout')
        assert hasattr(engine, 'update_window_size')

    def test_adaptive_card_spacing(self):
        """测试自适应卡牌间距"""
        from app.visualization.components.layout_engine import LayoutEngine

        engine = LayoutEngine(1200, 800)

        # 测试不同数量卡牌的间距
        spacing_3_cards = engine.calculate_card_spacing(3)
        spacing_7_cards = engine.calculate_card_spacing(7)
        spacing_10_cards = engine.calculate_card_spacing(10)

        # 验证间距递减
        assert spacing_3_cards > spacing_7_cards > spacing_10_cards

        # 验证最小间距限制
        assert spacing_10_cards >= 80  # 最小间距

    def test_responsive_layout_calculation(self):
        """测试响应式布局计算"""
        from app.visualization.components.layout_engine import LayoutEngine

        # 测试不同窗口尺寸
        engine_small = LayoutEngine(800, 600)
        engine_large = LayoutEngine(1920, 1080)

        layout_small = engine_small.calculate_layout()
        layout_large = engine_large.calculate_layout()

        # 验证大屏幕有更大的卡牌尺寸
        assert layout_large['card_width'] > layout_small['card_width']
        assert layout_large['card_height'] > layout_small['card_height']

    def test_layout_region_calculation(self):
        """测试布局区域计算"""
        from app.visualization.components.layout_engine import LayoutEngine

        engine = LayoutEngine(1200, 800)
        regions = engine.calculate_regions()

        # 验证必要区域存在
        assert 'hand_area' in regions
        assert 'battlefield_area' in regions
        assert 'player_info' in regions
        assert 'opponent_info' in regions

        # 验证区域不重叠
        hand_rect = regions['hand_area']
        battlefield_rect = regions['battlefield_area']

        assert hand_rect.bottom < battlefield_rect.top or \
               battlefield_rect.bottom < hand_rect.top


class TestUIComponents:
    """测试通用UI组件"""

    def test_button_component_exists(self):
        """测试按钮组件是否存在"""
        from app.visualization.components.ui_components import Button

        mock_surface = Mock()
        button = Button("测试按钮", (100, 100), (200, 50), mock_surface)

        assert button is not None
        assert hasattr(button, 'render')
        assert hasattr(button, 'handle_click')
        assert hasattr(button, 'is_hovered')

    def test_button_interaction_states(self):
        """测试按钮交互状态"""
        from app.visualization.components.ui_components import Button

        mock_surface = Mock()
        button = Button("测试按钮", (100, 100), (200, 50), mock_surface)

        # 测试默认状态
        assert not button.is_hovered()
        assert not button.is_pressed()

        # 测试悬停状态
        button.set_hover(True)
        assert button.is_hovered()

        # 测试按下状态
        button.set_pressed(True)
        assert button.is_pressed()

    def test_health_bar_component(self):
        """测试血条组件"""
        from app.visualization.components.ui_components import HealthBar

        mock_surface = Mock()
        health_bar = HealthBar((100, 100), (200, 20), mock_surface)

        # 测试血条设置
        health_bar.set_health(25, 30)  # 25/30 HP

        assert health_bar.get_current_health() == 25
        assert health_bar.get_max_health() == 30
        assert health_bar.get_health_percentage() == 25/30

    def test_mana_crystal_component(self):
        """测试法力水晶组件"""
        from app.visualization.components.ui_components import ManaCrystal

        mock_surface = Mock()
        mana_crystal = ManaCrystal((100, 100), mock_surface)

        # 测试法力值设置
        mana_crystal.set_mana(7, 10)  # 7/10 法力

        assert mana_crystal.get_current_mana() == 7
        assert mana_crystal.get_max_mana() == 10
        assert mana_crystal.get_mana_percentage() == 0.7


class TestAnimationEngine:
    """测试动画引擎"""

    def test_animation_engine_exists(self):
        """测试动画引擎是否存在"""
        from app.visualization.components.animation_engine import AnimationEngine

        engine = AnimationEngine()
        assert engine is not None
        assert hasattr(engine, 'update')
        assert hasattr(engine, 'add_animation')
        assert hasattr(engine, 'is_animating')

    def test_card_play_animation(self):
        """测试卡牌出牌动画"""
        from app.visualization.components.animation_engine import AnimationEngine

        engine = AnimationEngine()

        # 添加卡牌移动动画
        animation_id = engine.add_card_animation(
            'move',
            start_pos=(100, 600),
            end_pos=(400, 300),
            duration=0.5
        )

        assert animation_id is not None
        assert engine.is_animating()

    def test_animation_timing(self):
        """测试动画时序"""
        from app.visualization.components.animation_engine import AnimationEngine
        import time

        engine = AnimationEngine()

        # 添加快速动画用于测试
        engine.add_card_animation(
            'test',
            start_pos=(0, 0),
            end_pos=(100, 100),
            duration=0.1  # 100ms
        )

        start_time = time.time()

        # 更新动画直到完成
        while engine.is_animating():
            engine.update(0.016)  # 60fps
            time.sleep(0.001)

        elapsed_time = time.time() - start_time

        # 验证动画时长合理（允许一些误差）
        assert 0.08 < elapsed_time < 0.15


if __name__ == "__main__":
    pytest.main([__file__, "-v"])