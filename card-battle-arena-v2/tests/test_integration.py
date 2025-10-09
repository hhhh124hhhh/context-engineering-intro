"""
集成测试

测试主脚本和各个模块之间的集成。
"""

import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestBasicIntegration:
    """基础集成测试"""

    def test_cli_parser_import(self):
        """测试CLI解析器可以正常导入"""
        try:
            from cli.parser import create_parser, main_parser
            parser = create_parser()
            assert parser is not None
            print("✓ CLI解析器导入成功")
        except ImportError as e:
            print(f"❌ CLI解析器导入失败: {e}")
            raise

    def test_config_settings_import(self):
        """测试配置设置可以正常导入"""
        try:
            from config.settings import GameSettings
            settings = GameSettings()
            assert settings is not None
            assert hasattr(settings, 'get')
            print("✓ 配置设置导入成功")
        except ImportError as e:
            print(f"❌ 配置设置导入失败: {e}")
            raise

    def test_game_modes_import(self):
        """测试游戏模式可以正常导入"""
        try:
            from config.game_modes import GameMode, get_game_mode_config
            assert GameMode.AI_VS_PLAYER == 'ai-vs-player'
            print("✓ 游戏模式导入成功")
        except ImportError as e:
            print(f"❌ 游戏模式导入失败: {e}")
            raise

    def test_launcher_import(self):
        """测试游戏启动器可以正常导入"""
        try:
            from cli.launcher import GameLauncher
            launcher = GameLauncher()
            assert launcher is not None
            print("✓ 游戏启动器导入成功")
        except ImportError as e:
            print(f"❌ 游戏启动器导入失败: {e}")
            raise

    def test_main_script_import(self):
        """测试主脚本可以正常导入"""
        try:
            import main
            assert hasattr(main, 'main')
            print("✓ 主脚本导入成功")
        except ImportError as e:
            print(f"❌ 主脚本导入失败: {e}")
            raise

    def test_configuration_loading(self):
        """测试配置加载功能"""
        try:
            from config.settings import GameSettings

            settings = GameSettings()

            # 测试默认设置
            assert settings.get('window_width') == 1200
            assert settings.get('window_height') == 800
            assert settings.get('fps') == 60

            # 测试设置更新
            settings.set('window_width', 1920)
            assert settings.get('window_width') == 1920

            print("✓ 配置加载功能正常")
        except Exception as e:
            print(f"❌ 配置加载功能失败: {e}")
            raise

    def test_game_mode_configuration(self):
        """测试游戏模式配置"""
        try:
            from config.game_modes import GameMode, get_game_mode_config

            # 测试每个游戏模式
            for mode in GameMode:
                config = get_game_mode_config(mode.value)
                assert config is not None
                assert config.mode == mode
                assert hasattr(config, 'script_path')

            print("✓ 游戏模式配置正常")
        except Exception as e:
            print(f"❌ 游戏模式配置失败: {e}")
            raise

    def test_argument_parsing(self):
        """测试命令行参数解析"""
        try:
            from cli.parser import main_parser

            # 测试默认参数
            args = main_parser(['--mode', 'demo'])
            assert args.mode == 'demo'
            assert args.verbose is False

            # 测试详细模式
            args = main_parser(['--mode', 'ai', '--verbose'])
            assert args.mode == 'ai'
            assert args.verbose is True

            print("✓ 命令行参数解析正常")
        except Exception as e:
            print(f"❌ 命令行参数解析失败: {e}")
            raise

    def test_exception_handling(self):
        """测试异常处理"""
        try:
            from cli.exceptions import (
                InvalidGameModeError,
                MissingDependencyError,
                GameStartupError
            )

            # 测试异常创建
            error1 = InvalidGameModeError('invalid', ['ai', 'demo'])
            assert 'invalid' in str(error1)

            error2 = MissingDependencyError('pygame')
            assert 'pygame' in str(error2)

            error3 = GameStartupError('启动失败')
            assert '启动失败' in str(error3)

            print("✓ 异常处理正常")
        except Exception as e:
            print(f"❌ 异常处理失败: {e}")
            raise


def run_all_tests():
    """运行所有集成测试"""
    print("🧪 开始运行集成测试...")
    print("=" * 50)

    test_instance = TestBasicIntegration()

    tests = [
        test_instance.test_cli_parser_import,
        test_instance.test_config_settings_import,
        test_instance.test_game_modes_import,
        test_instance.test_launcher_import,
        test_instance.test_main_script_import,
        test_instance.test_configuration_loading,
        test_instance.test_game_mode_configuration,
        test_instance.test_argument_parsing,
        test_instance.test_exception_handling
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"❌ 测试失败: {test.__name__}")
            print(f"   错误: {e}")

    print("=" * 50)
    print(f"测试结果: {passed} 通过, {failed} 失败")

    if failed == 0:
        print("🎉 所有集成测试通过！")
        return True
    else:
        print("⚠️  部分测试失败")
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)