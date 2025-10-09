"""
主脚本TDD测试用例

严格遵循TDD方法：
1. RED阶段 - 先写失败的测试
2. GREEN阶段 - 实现最小功能让测试通过
3. REFACTOR阶段 - 重构优化代码结构
"""
import pytest
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from unittest.mock import patch, MagicMock
import argparse


class TestMainScript:
    """主脚本功能测试"""

    def test_main_script_imports(self):
        """测试主脚本能够正确导入所有依赖"""
        # RED: 这个测试会失败，因为main.py还不存在
        from main import main
        assert callable(main)

    def test_main_script_starts_without_arguments(self):
        """测试主脚本在无参数时能够正确启动"""
        # RED: 这个测试会失败，因为main.py还不存在
        from main import main

        with patch('sys.argv', ['main.py']):
            # 应该正常启动，不抛出异常
            try:
                main()
            except SystemExit:
                pass  # 允许正常的系统退出

    def test_command_line_arguments_parsing(self):
        """测试不同命令行参数的处理"""
        # RED: 这个测试会失败，因为CLI解析器还不存在
        from cli.parser import create_parser

        parser = create_parser()

        # 测试默认参数
        args = parser.parse_args([])
        assert args.mode == 'ai-vs-player'

        # 测试不同模式
        args = parser.parse_args(['--mode', 'ai'])
        assert args.mode == 'ai'

        args = parser.parse_args(['--mode', 'interactive'])
        assert args.mode == 'interactive'

        args = parser.parse_args(['--mode', 'demo'])
        assert args.mode == 'demo'

    def test_game_mode_selection(self):
        """测试AI对战、交互式等模式的启动"""
        # RED: 这个测试会失败，因为游戏启动器还不存在
        from cli.launcher import GameLauncher

        launcher = GameLauncher()

        # 测试AI对战模式
        with patch.object(launcher, 'launch_ai_vs_player') as mock_ai:
            launcher.launch('ai-vs-player')
            mock_ai.assert_called_once()

        # 测试交互式模式
        with patch.object(launcher, 'launch_interactive') as mock_interactive:
            launcher.launch('interactive')
            mock_interactive.assert_called_once()

        # 测试演示模式
        with patch.object(launcher, 'launch_demo') as mock_demo:
            launcher.launch('demo')
            mock_demo.assert_called_once()

    def test_configuration_loading(self):
        """测试游戏配置的加载和应用"""
        # RED: 这个测试会失败，因为配置系统还不存在
        from config.settings import GameSettings

        settings = GameSettings()

        # 测试默认配置
        assert settings.WINDOW_WIDTH == 1200
        assert settings.WINDOW_HEIGHT == 800
        assert settings.AI_THINKING_TIME == 1.5
        assert settings.MAX_TURNS == 15

    def test_game_mode_definitions(self):
        """测试游戏模式定义"""
        # RED: 这个测试会失败，因为游戏模式定义还不存在
        from config.game_modes import GameMode

        # 测试游戏模式常量
        assert GameMode.AI_VS_PLAYER == 'ai-vs-player'
        assert GameMode.INTERACTIVE == 'interactive'
        assert GameMode.DEMO == 'demo'

    def test_error_handling_invalid_mode(self):
        """测试无效游戏模式的错误处理"""
        # RED: 这个测试会失败，因为错误处理还不存在
        from cli.launcher import GameLauncher
        from cli.exceptions import InvalidGameModeError

        launcher = GameLauncher()

        # 测试无效模式抛出异常
        with pytest.raises(InvalidGameModeError):
            launcher.launch('invalid-mode')

    def test_error_handling_missing_dependencies(self):
        """测试缺少依赖时的错误处理"""
        # RED: 这个测试会失败，因为依赖检查还不存在
        from main import check_dependencies

        # 模拟缺少pygame的情况
        with patch.dict('sys.modules', {'pygame': None}):
            with pytest.raises(ImportError):
                check_dependencies()

    def test_help_message_display(self):
        """测试帮助信息的显示"""
        # RED: 这个测试会失败，因为帮助系统还不存在
        from cli.parser import create_parser

        parser = create_parser()

        # 测试帮助信息包含必要内容
        help_text = parser.format_help()
        assert 'Card Battle Arena' in help_text
        assert '--mode' in help_text
        assert 'ai-vs-player' in help_text
        assert 'interactive' in help_text
        assert 'demo' in help_text

    def test_integration_full_workflow(self):
        """测试完整工作流程的集成"""
        # RED: 这个测试会失败，因为完整流程还不存在
        from main import main

        # 模拟完整的命令行执行
        test_args = ['main.py', '--mode', 'demo', '--config', 'test_config.json']

        with patch('sys.argv', test_args):
            with patch('main.GameLauncher') as mock_launcher:
                with patch('main.load_config') as mock_config:
                    # 应该正常执行完整流程
                    try:
                        main()
                    except SystemExit:
                        pass

                    # 验证调用链
                    mock_config.assert_called_once()
                    mock_launcher.return_value.launch.assert_called_once_with('demo')


class TestCLIArguments:
    """命令行参数详细测试"""

    def test_mode_argument_validation(self):
        """测试模式参数的验证"""
        from cli.parser import create_parser

        parser = create_parser()

        # 测试有效模式
        valid_modes = ['ai-vs-player', 'ai', 'interactive', 'demo']
        for mode in valid_modes:
            args = parser.parse_args(['--mode', mode])
            assert args.mode == mode

        # 测试无效模式
        with pytest.raises(SystemExit):
            parser.parse_args(['--mode', 'invalid-mode'])

    def test_config_argument_handling(self):
        """测试配置文件参数的处理"""
        from cli.parser import create_parser

        parser = create_parser()

        # 测试默认配置
        args = parser.parse_args([])
        assert args.config is None

        # 测试自定义配置
        args = parser.parse_args(['--config', 'custom.json'])
        assert args.config == 'custom.json'

    def test_verbose_flag(self):
        """测试详细输出标志"""
        from cli.parser import create_parser

        parser = create_parser()

        # 测试默认不详细
        args = parser.parse_args([])
        assert args.verbose is False

        # 测试启用详细输出
        args = parser.parse_args(['--verbose'])
        assert args.verbose is True


class TestConfigurationSystem:
    """配置系统测试"""

    def test_default_settings_creation(self):
        """测试默认设置的创建"""
        from config.settings import GameSettings

        settings = GameSettings()

        # 验证所有默认设置
        assert hasattr(settings, 'WINDOW_WIDTH')
        assert hasattr(settings, 'WINDOW_HEIGHT')
        assert hasattr(settings, 'AI_THINKING_TIME')
        assert hasattr(settings, 'MAX_TURNS')
        assert hasattr(settings, 'FPS')

    def test_config_file_loading(self):
        """测试配置文件的加载"""
        from config.settings import GameSettings
        import tempfile
        import json

        # 创建临时配置文件
        config_data = {
            'WINDOW_WIDTH': 1920,
            'WINDOW_HEIGHT': 1080,
            'AI_THINKING_TIME': 2.0
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            settings = GameSettings()
            settings.load_from_file(config_path)

            assert settings.WINDOW_WIDTH == 1920
            assert settings.WINDOW_HEIGHT == 1080
            assert settings.AI_THINKING_TIME == 2.0
        finally:
            os.unlink(config_path)

    def test_config_validation(self):
        """测试配置验证"""
        from config.settings import GameSettings
        from config.exceptions import InvalidConfigError

        settings = GameSettings()

        # 测试无效配置
        with pytest.raises(InvalidConfigError):
            settings.validate_setting('WINDOW_WIDTH', -100)  # 负数宽度

        with pytest.raises(InvalidConfigError):
            settings.validate_setting('AI_THINKING_TIME', -1.0)  # 负数时间


if __name__ == '__main__':
    # 运行所有测试
    pytest.main([__file__, '-v'])