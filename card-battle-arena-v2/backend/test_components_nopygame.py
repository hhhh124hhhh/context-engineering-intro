#!/usr/bin/env python3
"""
不依赖pygame的组件测试
"""

import sys
import time
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

def test_design_tokens():
    """测试设计token系统"""
    print("🧪 测试设计token系统...")

    try:
        from app.visualization.design.tokens import DesignTokens

        # 验证基础结构
        assert hasattr(DesignTokens, 'COLORS')
        assert hasattr(DesignTokens, 'SPACING')
        assert hasattr(DesignTokens, 'TYPOGRAPHY')

        # 验证颜色系统
        assert 'primary' in DesignTokens.COLORS
        assert 'surface' in DesignTokens.COLORS
        assert 'mana' in DesignTokens.COLORS

        # 验证间距递增关系
        spacing = DesignTokens.SPACING
        assert spacing['xs'] < spacing['sm'] < spacing['md'] < spacing['lg'] < spacing['xl']

        # 测试对比度计算
        contrast = DesignTokens.get_contrast_ratio((255, 255, 255), (0, 0, 0))
        assert contrast > 4.5  # 黑白对比度应该很高

        # 测试颜色亮度调整
        bright_color = DesignTokens.adjust_brightness((100, 100, 100), 1.5)
        dark_color = DesignTokens.adjust_brightness((100, 100, 100), 0.5)
        assert bright_color != dark_color

        # 测试渐变颜色
        gradient = DesignTokens.get_gradient_colors((255, 0, 0), (0, 0, 255), 5)
        assert len(gradient) == 5
        assert gradient[0] != gradient[-1]

        print("✅ 设计token系统测试通过")
        return True

    except Exception as e:
        print(f"❌ 设计token系统测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_card_renderer():
    """测试卡牌渲染器（不依赖pygame）"""
    print("🧪 测试卡牌渲染器...")

    try:
        # Mock pygame module
        import sys
        from unittest.mock import Mock
        sys.modules['pygame'] = Mock()

        # Mock font
        mock_font = Mock()
        mock_font.render.return_value = Mock()
        sys.modules['pygame'].font.Font.return_value = mock_font

        from app.visualization.components.card_renderer import CardRenderer

        # 创建渲染器
        renderer = CardRenderer()
        assert renderer is not None
        assert hasattr(renderer, 'render_card')

        # 测试颜色状态
        normal_color = renderer.get_card_color('normal')
        selected_color = renderer.get_card_color('selected')
        hover_color = renderer.get_card_color('hover')

        assert normal_color != selected_color
        assert normal_color != hover_color

        # 测试血量颜色
        full_health_color = renderer.get_health_color(10)
        half_health_color = renderer.get_health_color(5)
        low_health_color = renderer.get_health_color(2)

        assert full_health_color != half_health_color
        assert half_health_color != low_health_color

        print("✅ 卡牌渲染器测试通过")
        return True

    except Exception as e:
        print(f"❌ 卡牌渲染器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_layout_engine():
    """测试布局引擎"""
    print("🧪 测试布局引擎...")

    try:
        # Mock pygame module
        import sys
        from unittest.mock import Mock
        sys.modules['pygame'] = Mock()
        sys.modules['pygame'].Rect = Mock

        from app.visualization.components.layout_engine import LayoutEngine

        # 创建布局引擎
        engine = LayoutEngine(1200, 800)
        assert engine is not None
        assert hasattr(engine, 'calculate_layout')

        # 测试自适应间距
        spacing_3_cards = engine.calculate_card_spacing(3)
        spacing_7_cards = engine.calculate_card_spacing(7)
        spacing_10_cards = engine.calculate_card_spacing(10)

        # 验证间距递减
        assert spacing_3_cards >= spacing_7_cards >= spacing_10_cards

        # 验证最小间距限制
        assert spacing_10_cards >= 80  # 最小间距

        # 测试布局计算
        layout = engine.calculate_layout()
        assert 'card_dimensions' in layout
        assert 'spacing' in layout
        assert 'regions' in layout
        assert 'font_sizes' in layout

        # 测试窗口大小更新
        engine.update_window_size(800, 600)
        assert engine.window_width == 800
        assert engine.window_height == 600

        print("✅ 布局引擎测试通过")
        return True

    except Exception as e:
        print(f"❌ 布局引擎测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ui_components():
    """测试UI组件（不依赖pygame）"""
    print("🧪 测试UI组件...")

    try:
        # Mock pygame module
        import sys
        from unittest.mock import Mock
        sys.modules['pygame'] = Mock()
        sys.modules['pygame'].Rect = Mock
        sys.modules['pygame'].font = Mock()
        sys.modules['pygame'].font.Font.return_value.render.return_value = Mock()

        from app.visualization.components.ui_components import HealthBar, ManaCrystal

        # 模拟pygame surface
        class MockSurface:
            def __init__(self):
                pass
            def blit(self, *args):
                pass

        mock_surface = MockSurface()

        # 测试血条组件
        health_bar = HealthBar((100, 100), (200, 20), mock_surface, max_health=30)
        health_bar.set_health(20, 30)

        assert health_bar.get_current_health() == 20
        assert health_bar.get_max_health() == 30
        assert abs(health_bar.get_health_percentage() - 20/30) < 0.01

        # 测试法力水晶组件
        mana_crystal = ManaCrystal((100, 150), mock_surface, max_mana=10)
        mana_crystal.set_mana(7, 10)

        assert mana_crystal.get_current_mana() == 7
        assert mana_crystal.get_max_mana() == 10
        assert abs(mana_crystal.get_mana_percentage() - 0.7) < 0.01

        print("✅ UI组件测试通过")
        return True

    except Exception as e:
        print(f"❌ UI组件测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_animation_engine():
    """测试动画引擎"""
    print("🧪 测试动画引擎...")

    try:
        from app.visualization.components.animation_engine import AnimationEngine, MoveAnimation

        # 创建动画引擎
        engine = AnimationEngine()
        assert engine is not None
        assert hasattr(engine, 'add_animation')
        assert hasattr(engine, 'update')

        # 测试添加动画
        animation_id = engine.add_card_animation(
            'move',
            start_pos=(0, 0),
            end_pos=(100, 100),
            duration=0.1  # 快速动画用于测试
        )

        assert animation_id is not None
        assert engine.is_animating()

        # 启动引擎
        engine.start()

        # 更新动画
        start_time = time.time()
        while engine.is_animating() and (time.time() - start_time) < 0.5:
            engine.update(0.016)  # 60fps
            time.sleep(0.01)

        print("✅ 动画引擎测试通过")
        return True

    except Exception as e:
        print(f"❌ 动画引擎测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """运行所有测试"""
    print("🚀 开始组件架构测试（无pygame依赖）...")
    print("=" * 60)

    tests = [
        test_design_tokens,
        test_card_renderer,
        test_layout_engine,
        test_ui_components,
        test_animation_engine,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print("=" * 60)
    print(f"📊 测试结果: {passed}/{total} 通过")

    if passed == total:
        print("🎉 所有测试通过！组件架构重构成功！")
        print("💡 注意：由于pygame未安装，测试使用了Mock对象")
        print("🔧 要完整测试，请在安装pygame后运行完整测试")
        return True
    else:
        print("❌ 部分测试失败，需要修复。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)