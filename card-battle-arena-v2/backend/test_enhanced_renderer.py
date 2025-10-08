#!/usr/bin/env python3
"""
测试增强版渲染器
"""

import sys
import time
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

def test_enhanced_renderer():
    """测试增强版渲染器"""
    print("🎮 测试增强版渲染器...")

    try:
        # Mock pygame for testing
        import sys
        from unittest.mock import Mock

        # 创建pygame mock
        pygame_mock = Mock()
        pygame_mock.init.return_value = None
        pygame_mock.display.set_mode.return_value = Mock()
        pygame_mock.display.set_caption.return_value = None
        pygame_mock.display.flip.return_value = None
        pygame_mock.time.Clock.return_value = Mock()
        pygame_mock.font.Font.return_value = Mock()
        pygame_mock.font.SysFont.return_value = Mock()
        pygame_mock.event.get.return_value = []
        pygame_mock.QUIT = pygame_mock.QUIT = 12
        pygame_mock.VIDEORESIZE = pygame_mock.VIDEORESIZE = 16
        pygame_mock.MOUSEBUTTONDOWN = pygame_mock.MOUSEBUTTONDOWN = 5
        pygame_mock.MOUSEBUTTONUP = pygame_mock.MOUSEBUTTONUP = 6
        pygame_mock.MOUSEMOTION = pygame_mock.MOUSEMOTION = 4
        pygame_mock.KEYDOWN = pygame_mock.KEYDOWN = 2
        pygame_mock.K_ESCAPE = pygame_mock.K_ESCAPE = 27

        sys.modules['pygame'] = pygame_mock

        # 导入增强版渲染器
        from app.visualization.enhanced_renderer import EnhancedRenderer

        # 创建渲染器
        renderer = EnhancedRenderer(1200, 800)

        # 测试基本功能
        assert renderer.width == 1200
        assert renderer.height == 800
        assert renderer.layout_engine is not None
        assert renderer.card_renderer is not None
        assert renderer.animation_engine is not None

        # 测试创建窗口
        surface = renderer.create_window()
        assert surface is not None

        # 测试布局计算
        layout = renderer.layout_engine.calculate_layout()
        assert 'card_dimensions' in layout
        assert 'regions' in layout

        # 测试字体系统
        assert 'default' in renderer.fonts
        assert 'heading' in renderer.fonts
        assert 'body' in renderer.fonts

        # 测试事件处理
        assert renderer.handle_events()  # 默认应该返回True（没有退出事件）

        # 测试动画
        animation_id = renderer.add_card_animation(
            Mock(),  # Mock card
            (0, 0),
            (100, 100)
        )
        assert animation_id is not None
        assert renderer.is_animating()

        # 测试清理
        renderer.cleanup()

        print("✅ 增强版渲染器测试通过")
        return True

    except Exception as e:
        print(f"❌ 增强版渲染器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integration_with_old_renderer():
    """测试与旧渲染器的集成"""
    print("🔄 测试与旧渲染器的集成...")

    try:
        # Mock pygame
        import sys
        from unittest.mock import Mock
        sys.modules['pygame'] = Mock()

        # 导入两个渲染器
        from app.visualization.pygame_renderer import PygameRenderer
        from app.visualization.enhanced_renderer import EnhancedRenderer

        # 创建两个渲染器实例
        old_renderer = PygameRenderer(1200, 800)
        new_renderer = EnhancedRenderer(1200, 800)

        # 比较功能
        assert hasattr(old_renderer, 'render_game_state')
        assert hasattr(new_renderer, 'render_game_state')

        assert hasattr(old_renderer, 'handle_events')
        assert hasattr(new_renderer, 'handle_events')

        # 检查新渲染器有额外的功能
        assert hasattr(new_renderer, 'layout_engine')
        assert hasattr(new_renderer, 'animation_engine')
        assert hasattr(new_renderer, 'add_card_animation')

        print("✅ 与旧渲染器的集成测试通过")
        return True

    except Exception as e:
        print(f"❌ 与旧渲染器的集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """运行所有测试"""
    print("🚀 开始增强版渲染器测试...")
    print("=" * 50)

    tests = [
        test_enhanced_renderer,
        test_integration_with_old_renderer,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print("=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")

    if passed == total:
        print("🎉 所有测试通过！增强版渲染器创建成功！")
        print("💡 增强版渲染器包含以下新功能：")
        print("   • 组件化架构")
        print("   • 响应式布局")
        print("   • 现代化设计系统")
        print("   • 动画引擎")
        print("   • 改进的字体系统")
        return True
    else:
        print("❌ 部分测试失败，需要修复。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)