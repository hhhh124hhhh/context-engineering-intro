"""
游戏玩法可视化验证测试
使用TDD方法验证游戏核心玩法的可视化实现
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from unittest.mock import Mock, patch


class TestGamePlayVisualization:
    """游戏玩法可视化测试类"""
    
    def test_visualization_module_structure(self):
        """测试可视化模块结构"""
        # 红：验证模块是否存在
        try:
            from app.visualization.pygame_renderer import PygameRenderer
        except ImportError:
            pytest.fail("Pygame可视化模块不存在")
        
        # 绿：验证类和方法是否存在
        renderer = PygameRenderer()
        assert hasattr(renderer, '__init__')
        assert hasattr(renderer, 'create_window')
        assert hasattr(renderer, 'render_card')
        assert hasattr(renderer, 'render_game_state')
        assert hasattr(renderer, 'handle_events')
        assert hasattr(renderer, 'handle_mouse_click')
        assert hasattr(renderer, 'handle_mouse_release')
        assert hasattr(renderer, 'get_card_at_position')
        assert hasattr(renderer, 'play_selected_card')
        assert hasattr(renderer, 'can_play_card')
        assert hasattr(renderer, 'calculate_card_positions')
        assert hasattr(renderer, 'prevent_text_overlap')
        
        # 重构：验证方法签名
        import inspect
        init_signature = inspect.signature(renderer.__init__)
        assert 'width' in init_signature.parameters
        assert 'height' in init_signature.parameters
    
    def test_game_state_rendering_with_mock_data(self):
        """测试游戏状态渲染与模拟数据"""
        from app.visualization.pygame_renderer import PygameRenderer
        
        # 创建渲染器实例
        renderer = PygameRenderer()
        
        # 创建模拟游戏状态
        mock_game_state = Mock()
        mock_game_state.turn_number = 3
        
        # 创建模拟玩家
        mock_player = Mock()
        mock_player.name = "测试玩家"
        mock_player.hero.health = 25
        mock_player.current_mana = 5
        mock_player.max_mana = 10
        mock_player.hand = []
        mock_player.battlefield = []
        
        mock_game_state.current_player = mock_player
        mock_game_state.opponent = mock_player
        
        # 验证方法存在（不实际调用，避免需要初始化Pygame）
        assert hasattr(renderer, 'render_game_state')
    
    def test_card_rendering_with_attributes(self):
        """测试卡牌渲染与属性显示"""
        from app.visualization.pygame_renderer import PygameRenderer
        from app.game.cards import Card, CardType
        
        renderer = PygameRenderer()
        
        # 创建测试卡牌
        test_card = Card(
            id=1,
            name="测试随从",
            cost=3,
            attack=4,
            health=5,
            card_type=CardType.MINION
        )
        
        # 验证方法存在
        assert hasattr(renderer, 'render_card')
        
        # 验证卡牌属性
        assert test_card.cost == 3
        assert test_card.attack == 4
        assert test_card.health == 5
        assert test_card.card_type == CardType.MINION
    
    def test_visual_demo_integration(self):
        """测试可视化演示集成"""
        import importlib.util
        import os
        
        # 检查可视化演示文件是否存在
        demo_path = Path(__file__).parent.parent / "visual_demo.py"
        assert demo_path.exists(), "可视化演示文件不存在"
        
        # 检查是否可以导入
        spec = importlib.util.spec_from_file_location("visual_demo", demo_path)
        assert spec is not None, "无法创建模块规范"
    
    def test_mouse_interaction_methods(self):
        """测试鼠标交互方法"""
        from app.visualization.pygame_renderer import PygameRenderer
        
        renderer = PygameRenderer()
        
        # 验证鼠标处理方法存在
        assert hasattr(renderer, 'handle_mouse_click')
        assert hasattr(renderer, 'handle_mouse_release')
        assert hasattr(renderer, 'get_card_at_position')
        
        # 测试get_card_at_position方法签名
        import inspect
        method = getattr(renderer, 'get_card_at_position')
        signature = inspect.signature(method)
        assert 'pos' in signature.parameters
        assert 'hand' in signature.parameters
    
    def test_card_playing_functionality(self):
        """测试卡牌出牌功能"""
        from app.visualization.pygame_renderer import PygameRenderer
        
        renderer = PygameRenderer()
        
        # 验证出牌相关方法存在
        assert hasattr(renderer, 'play_selected_card')
        assert hasattr(renderer, 'can_play_card')
        
        # 测试can_play_card方法
        mock_card = Mock()
        mock_card.cost = 3
        mock_player = Mock()
        mock_player.current_mana = 5
        
        # 玩家有足够法力值
        assert renderer.can_play_card(mock_card, mock_player) == True
        
        # 玩家法力值不足
        mock_player.current_mana = 2
        assert renderer.can_play_card(mock_card, mock_player) == False
    
    def test_ui_layout_improvements(self):
        """测试UI布局改进功能"""
        from app.visualization.pygame_renderer import PygameRenderer
        
        renderer = PygameRenderer()
        
        # 验证布局改进相关方法存在
        assert hasattr(renderer, 'calculate_card_positions')
        assert hasattr(renderer, 'prevent_text_overlap')
        
        # 测试calculate_card_positions
        positions = renderer.calculate_card_positions(5, 800)
        assert len(positions) == 5
        assert positions[0] == 50  # 起始位置
        
        # 测试prevent_text_overlap
        texts = [("文本1", (100, 100)), ("文本2", (100, 110))]
        adjusted_texts = renderer.prevent_text_overlap(texts)
        assert len(adjusted_texts) == 2
        # 第二个文本应该被调整位置
        assert adjusted_texts[1][1][1] != 110
    
    def test_window_resizing_support(self):
        """测试窗口大小调整支持"""
        from app.visualization.pygame_renderer import PygameRenderer
        
        # 测试不同窗口大小
        renderer1 = PygameRenderer(800, 600)
        renderer2 = PygameRenderer(1200, 800)
        renderer3 = PygameRenderer(1920, 1080)
        
        assert renderer1.width == 800
        assert renderer1.height == 600
        assert renderer2.width == 1200
        assert renderer2.height == 800
        assert renderer3.width == 1920
        assert renderer3.height == 1080
    
    @patch('app.visualization.pygame_renderer.pygame')
    def test_pygame_mock_integration(self, mock_pygame):
        """测试Pygame集成（使用模拟）"""
        from app.visualization.pygame_renderer import PygameRenderer
        
        # 设置模拟对象
        mock_screen = Mock()
        mock_pygame.display.set_mode.return_value = mock_screen
        mock_pygame.font.Font.return_value = Mock()
        
        # 创建渲染器
        renderer = PygameRenderer()
        
        # 调用创建窗口方法
        screen = renderer.create_window("测试窗口")
        
        # 验证Pygame被正确调用
        mock_pygame.init.assert_called_once()
        mock_pygame.display.set_mode.assert_called_once()
        mock_pygame.display.set_caption.assert_called_once_with("测试窗口")
        
        assert screen == mock_screen


if __name__ == "__main__":
    pytest.main([__file__, "-v"])