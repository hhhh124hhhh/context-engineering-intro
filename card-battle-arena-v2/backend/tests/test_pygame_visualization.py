"""
Pygame可视化版本的测试文件
遵循TDD开发模式：红→绿→重构
"""

import sys
import os
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_pygame_visualization_module_exists():
    """测试Pygame可视化模块是否存在"""
    try:
        from app.visualization.pygame_renderer import PygameRenderer
    except ImportError:
        assert False, "Pygame可视化模块不存在，需要先创建"


def test_pygame_renderer_initialization():
    """测试Pygame渲染器初始化"""
    try:
        from app.visualization.pygame_renderer import PygameRenderer
        renderer = PygameRenderer()
        assert renderer is not None
    except Exception as e:
        assert False, f"Pygame渲染器初始化失败: {e}"


def test_pygame_window_creation():
    """测试Pygame窗口创建"""
    try:
        from app.visualization.pygame_renderer import PygameRenderer
        renderer = PygameRenderer()
        # 不实际创建窗口，只测试方法存在
        assert hasattr(renderer, 'create_window')
    except Exception as e:
        assert False, f"Pygame窗口创建方法不存在或出错: {e}"


def test_card_rendering_method():
    """测试卡牌渲染方法"""
    try:
        from app.visualization.pygame_renderer import PygameRenderer
        renderer = PygameRenderer()
        # 不实际渲染，只测试方法存在
        assert hasattr(renderer, 'render_card')
    except Exception as e:
        assert False, f"卡牌渲染方法不存在或出错: {e}"


def test_game_state_rendering():
    """测试游戏状态渲染方法"""
    try:
        from app.visualization.pygame_renderer import PygameRenderer
        renderer = PygameRenderer()
        # 不实际渲染，只测试方法存在
        assert hasattr(renderer, 'render_game_state')
    except Exception as e:
        assert False, f"游戏状态渲染方法不存在或出错: {e}"


def test_mouse_interaction_methods():
    """测试鼠标交互方法"""
    try:
        from app.visualization.pygame_renderer import PygameRenderer
        renderer = PygameRenderer()
        # 测试鼠标处理方法存在
        assert hasattr(renderer, 'handle_mouse_click')
        assert hasattr(renderer, 'get_card_at_position')
    except Exception as e:
        assert False, f"鼠标交互方法不存在或出错: {e}"


def test_window_resizing():
    """测试窗口大小调整功能"""
    try:
        from app.visualization.pygame_renderer import PygameRenderer
        # 测试可以创建不同大小的窗口
        renderer1 = PygameRenderer(800, 600)
        renderer2 = PygameRenderer(1200, 800)
        assert renderer1.width == 800
        assert renderer1.height == 600
        assert renderer2.width == 1200
        assert renderer2.height == 800
    except Exception as e:
        assert False, f"窗口大小调整功能测试失败: {e}"


def test_card_playing_functionality():
    """测试卡牌出牌功能"""
    try:
        from app.visualization.pygame_renderer import PygameRenderer
        renderer = PygameRenderer()
        # 测试出牌相关方法存在
        assert hasattr(renderer, 'play_selected_card')
        assert hasattr(renderer, 'can_play_card')
    except Exception as e:
        assert False, f"卡牌出牌功能方法不存在或出错: {e}"


def test_ui_layout_improvements():
    """测试UI布局改进功能"""
    try:
        from app.visualization.pygame_renderer import PygameRenderer
        renderer = PygameRenderer()
        # 测试布局改进相关方法存在
        assert hasattr(renderer, 'calculate_card_positions')
        assert hasattr(renderer, 'prevent_text_overlap')
    except Exception as e:
        assert False, f"UI布局改进功能方法不存在或出错: {e}"


def test_keyboard_selection():
    """测试键盘选择功能"""
    try:
        from app.visualization.pygame_renderer import PygameRenderer
        renderer = PygameRenderer()
        # 测试键盘选择相关方法存在
        assert hasattr(renderer, '_select_card_with_keyboard')
        assert hasattr(renderer, '_move_selection_left')
        assert hasattr(renderer, '_move_selection_right')
    except Exception as e:
        assert False, f"键盘选择功能方法不存在或出错: {e}"


def test_layout_spacing():
    """测试布局间距改进功能"""
    try:
        from app.visualization.pygame_renderer import PygameRenderer
        renderer = PygameRenderer()
        # 测试布局间距相关方法存在
        assert hasattr(renderer, '_improve_layout_spacing')
        assert hasattr(renderer, '_update_layout')
    except Exception as e:
        assert False, f"布局间距改进功能方法不存在或出错: {e}"


def test_card_play_confirmation():
    """测试卡牌出牌确认功能"""
    try:
        from app.visualization.pygame_renderer import PygameRenderer
        renderer = PygameRenderer()
        # 测试出牌确认相关方法存在
        assert hasattr(renderer, '_confirm_card_play')
        assert hasattr(renderer, '_cancel_card_play')
    except Exception as e:
        assert False, f"卡牌出牌确认功能方法不存在或出错: {e}"


def test_visual_demo_execution():
    """测试可视化演示是否能正常执行"""
    import subprocess
    import time
    
    # 启动可视化演示，运行几秒后终止
    try:
        process = subprocess.Popen([
            sys.executable, 
            str(Path(__file__).parent.parent / "visual_demo.py")
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # 等待2秒
        time.sleep(2)
        
        # 检查进程是否仍在运行
        if process.poll() is None:
            # 终止进程
            process.terminate()
            process.wait()
            assert True, "可视化演示正常启动"
        else:
            # 进程已退出，检查返回码
            stdout, stderr = process.communicate()
            if process.returncode == 0:
                assert True, "可视化演示正常执行"
            else:
                assert False, f"可视化演示执行出错: {stderr.decode()}"
    except Exception as e:
        assert False, f"可视化演示执行失败: {e}"


if __name__ == "__main__":
    # 手动运行测试
    tests = [
        ("Pygame可视化模块存在", test_pygame_visualization_module_exists),
        ("Pygame渲染器初始化", test_pygame_renderer_initialization),
        ("Pygame窗口创建", test_pygame_window_creation),
        ("卡牌渲染方法", test_card_rendering_method),
        ("游戏状态渲染方法", test_game_state_rendering),
        ("鼠标交互方法", test_mouse_interaction_methods),
        ("窗口大小调整", test_window_resizing),
        ("卡牌出牌功能", test_card_playing_functionality),
        ("UI布局改进", test_ui_layout_improvements),
        ("键盘选择功能", test_keyboard_selection),
        ("布局间距改进", test_layout_spacing),
        ("卡牌出牌确认", test_card_play_confirmation),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            test_func()
            print(f"✓ {test_name}测试通过")
            passed += 1
        except Exception as e:
            print(f"✗ {test_name}测试失败: {e}")
            failed += 1
    
    print(f"\n测试结果: {passed} 通过, {failed} 失败")
    
    if failed > 0:
        print("需要实现缺失的功能...")
    else:
        print("所有测试执行完成！")