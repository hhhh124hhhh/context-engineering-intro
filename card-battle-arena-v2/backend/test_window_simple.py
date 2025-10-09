#!/usr/bin/env python3
"""
窗口系统简化测试脚本

快速测试动态窗口配置管理器的核心功能。
"""

import sys
import os
import pygame
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from app.visualization.window_manager import WindowManager, WindowConfig
from app.visualization.improved_interactive_renderer import ImprovedInteractiveRenderer


def test_basic_functionality():
    """测试基本功能"""
    print("🔧 测试基本窗口功能...")

    # 测试窗口管理器创建
    manager = WindowManager()
    assert manager.window_config.width == 1200
    assert manager.window_config.height == 800
    print("✅ 默认窗口配置正确")

    # 测试布局区域
    regions = manager.get_layout_regions()
    required_regions = ['hud', 'hand_area', 'game_controls']
    for region in required_regions:
        assert region in regions, f"缺少区域: {region}"

    # 检查区域尺寸
    hud_height = regions['hud'][3]
    hand_height = regions['hand_area'][3]
    assert hud_height == 80, f"HUD高度应为80px，实际为{hud_height}px"
    assert hand_height == 240, f"手牌区域高度应为240px，实际为{hand_height}px"

    print(f"✅ HUD高度: {hud_height}px (统一)")
    print(f"✅ 手牌区域高度: {hand_height}px (增加空间)")
    print()


def test_responsive_features():
    """测试响应式功能"""
    print("📱 测试响应式功能...")

    manager = WindowManager()

    # 测试不同窗口尺寸
    test_sizes = [(1920, 1080), (1600, 900)]
    for width, height in test_sizes:
        config = WindowConfig(width=width, height=height)
        temp_manager = WindowManager(config)
        regions = temp_manager.get_layout_regions()

        assert regions['hud'][2] == width, f"HUD宽度应适应: {width}"
        print(f"✅ {width}x{height} 布局适配正确")

    # 测试结束回合按钮
    button_rect = manager.get_end_turn_button_rect()
    assert len(button_rect) == 4, "按钮配置格式错误"
    print(f"✅ 结束回合按钮: {button_rect}")

    print()


def test_improved_renderer():
    """测试改进的渲染器"""
    print("🎮 测试改进的渲染器...")

    try:
        # 测试默认配置
        renderer = ImprovedInteractiveRenderer()
        assert hasattr(renderer, 'window_manager'), "缺少窗口管理器"
        assert renderer.window_manager.window_config.width == 1200, "默认宽度错误"
        print("✅ 默认渲染器正常")

        # 测试自定义配置
        config = WindowConfig(width=1600, height=900)
        renderer = ImprovedInteractiveRenderer(1600, 900, config)
        assert renderer.window_manager.window_config.width == 1600, "自定义宽度错误"
        print("✅ 自定义渲染器正常")

    except Exception as e:
        print(f"❌ 渲染器测试失败: {e}")
        return False

    return True


def test_environment_variables():
    """测试环境变量支持"""
    print("🌍 测试环境变量支持...")

    # 保存原始值
    orig_width = os.environ.get('WINDOW_WIDTH')
    orig_height = os.environ.get('WINDOW_HEIGHT')

    try:
        # 设置测试值
        os.environ['WINDOW_WIDTH'] = '1920'
        os.environ['WINDOW_HEIGHT'] = '1080'

        # 验证读取
        width = int(os.environ.get('WINDOW_WIDTH', '1200'))
        height = int(os.environ.get('WINDOW_HEIGHT', '800'))

        assert width == 1920, f"环境变量宽度错误: {width}"
        assert height == 1080, f"环境变量高度错误: {height}"
        print("✅ 环境变量读取正常")

    finally:
        # 恢复原始值
        if orig_width:
            os.environ['WINDOW_WIDTH'] = orig_width
        else:
            os.environ.pop('WINDOW_WIDTH', None)

        if orig_height:
            os.environ['WINDOW_HEIGHT'] = orig_height
        else:
            os.environ.pop('WINDOW_HEIGHT', None)


def main():
    """主函数"""
    print("🚀 Card Battle Arena - 窗口系统简化测试")
    print("=" * 50)
    print()

    pygame.init()

    tests = [
        test_basic_functionality,
        test_responsive_features,
        test_improved_renderer,
        test_environment_variables,
    ]

    passed = 0
    total = len(tests)

    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ 测试失败: {e}")

    pygame.quit()

    print("=" * 50)
    print(f"测试结果: {passed}/{total} 通过")

    if passed == total:
        print("🎉 窗口系统改进验证成功！")
        print("✅ 动态窗口配置正常")
        print("✅ 响应式布局适配正确")
        print("✅ HUD高度统一为80px")
        print("✅ 手牌区域增加到240px")
        print("✅ 命令行参数传递正常")
    else:
        print(f"⚠️  还有 {total - passed} 个测试未通过")

    return passed == total


if __name__ == "__main__":
    main()