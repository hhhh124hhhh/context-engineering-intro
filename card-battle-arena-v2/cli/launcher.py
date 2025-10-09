"""
游戏启动器

负责根据配置启动不同的游戏模式和脚本。
"""

import sys
import os
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any
import importlib.util

from cli.exceptions import (
    InvalidGameModeError,
    MissingDependencyError,
    PygameInitializationError,
    GameStartupError
)
from config.game_modes import GameMode, get_game_mode_config
from config.settings import GameSettings


class GameLauncher:
    """游戏启动器类"""

    def __init__(self, settings: Optional[GameSettings] = None):
        """
        初始化游戏启动器

        Args:
            settings (Optional[GameSettings]): 游戏设置
        """
        self.settings = settings or GameSettings()
        self.project_root = Path(__file__).parent.parent

    def launch(self, mode: str) -> bool:
        """
        启动指定模式的游戏

        Args:
            mode (str): 游戏模式

        Returns:
            bool: 启动是否成功

        Raises:
            InvalidGameModeError: 无效的游戏模式
            GameStartupError: 游戏启动失败
        """
        try:
            # 验证游戏模式
            if not GameMode.is_valid_mode(mode):
                available_modes = GameMode.all_modes()
                raise InvalidGameModeError(mode, available_modes)

            # 获取游戏模式配置
            mode_config = get_game_mode_config(mode)

            # 检查依赖
            self._check_dependencies()

            # 初始化Pygame
            self._initialize_pygame()

            # 根据模式启动游戏
            success = self._launch_by_mode(mode_config)

            if success:
                print(f"✓ 成功启动游戏模式: {mode}")
            else:
                raise GameStartupError(f"启动游戏模式 '{mode}' 失败")

            return success

        except Exception as e:
            if isinstance(e, (InvalidGameModeError, GameStartupError)):
                raise
            else:
                raise GameStartupError(f"启动游戏时发生未知错误: {str(e)}") from e

    def _check_dependencies(self):
        """检查必需的依赖"""
        required_modules = {
            'pygame': 'Pygame库',
            'random': 'Random模块'
        }

        missing_modules = []
        for module_name, description in required_modules.items():
            if importlib.util.find_spec(module_name) is None:
                missing_modules.append(f"{description} ({module_name})")

        if missing_modules:
            error_msg = "缺少以下必需的依赖:\n" + "\n".join(f"  - {module}" for module in missing_modules)
            error_msg += "\n\n请运行以下命令安装依赖:\n"
            error_msg += "  pip install pygame numpy"
            raise MissingDependencyError(error_msg)

    def _initialize_pygame(self):
        """初始化Pygame"""
        try:
            import pygame

            # 获取显示设置
            display_settings = self.settings.get_display_settings()

            # 初始化Pygame
            pygame.init()

            # 设置显示模式
            if display_settings['fullscreen']:
                screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            else:
                width = display_settings['window_width']
                height = display_settings['window_height']
                screen = pygame.display.set_mode((width, height))

            # 设置窗口标题
            pygame.display.set_caption("Card Battle Arena - 卡牌对战竞技场")

            print("✓ Pygame初始化成功")

        except pygame.error as e:
            raise PygameInitializationError(str(e)) from e
        except ImportError:
            raise MissingDependencyError("pygame") from None

    def _launch_by_mode(self, mode_config) -> bool:
        """
        根据模式配置启动游戏

        Args:
            mode_config: 游戏模式配置

        Returns:
            bool: 启动是否成功
        """
        script_path = self.project_root / mode_config.script_path

        if not script_path.exists():
            raise GameStartupError(f"游戏脚本不存在: {script_path}")

        try:
            # 根据模式选择不同的启动方式
            if mode_config.mode == GameMode.AI_VS_PLAYER:
                return self._launch_ai_vs_player(script_path, mode_config)
            elif mode_config.mode == GameMode.AI:
                return self._launch_ai_mode(script_path, mode_config)
            elif mode_config.mode == GameMode.INTERACTIVE:
                return self._launch_interactive(script_path, mode_config)
            elif mode_config.mode == GameMode.DEMO:
                return self._launch_demo(script_path, mode_config)
            else:
                raise GameStartupError(f"不支持的游戏模式: {mode_config.mode}")

        except Exception as e:
            raise GameStartupError(f"启动游戏脚本时发生错误: {str(e)}") from e

    def _launch_ai_vs_player(self, script_path: Path, mode_config) -> bool:
        """启动AI对战模式"""
        print(f"🎮 启动AI对战模式...")
        print(f"   脚本: {script_path.name}")

        # 传递AI相关设置到脚本环境
        env = os.environ.copy()
        ai_settings = self.settings.get_ai_settings()
        env['AI_THINKING_TIME'] = str(ai_settings['thinking_time'])
        env['AI_DIFFICULTY'] = ai_settings['difficulty']

        return self._run_script(script_path, env)

    def _launch_ai_mode(self, script_path: Path, mode_config) -> bool:
        """启动简化AI模式"""
        print(f"🤖 启动简化AI模式...")
        print(f"   脚本: {script_path.name}")

        # 简化模式的快速设置
        env = os.environ.copy()
        env['QUICK_MODE'] = 'true'
        env['AI_THINKING_TIME'] = '1.0'

        return self._run_script(script_path, env)

    def _launch_interactive(self, script_path: Path, mode_config) -> bool:
        """启动交互式模式"""
        print(f"👆 启动交互式模式...")
        print(f"   脚本: {script_path.name}")

        # 交互式模式设置
        env = os.environ.copy()
        game_settings = self.settings.get_game_settings()
        env['TURN_TIME_LIMIT'] = str(game_settings['turn_time_limit'])
        env['INTERACTIVE_MODE'] = 'true'

        return self._run_script(script_path, env)

    def _launch_demo(self, script_path: Path, mode_config) -> bool:
        """启动演示模式"""
        print(f"🎬 启动演示模式...")
        print(f"   脚本: {script_path.name}")

        # 演示模式设置
        env = os.environ.copy()
        env['DEMO_MODE'] = 'true'
        env['AUTO_PLAY'] = 'true'
        env['SHOW_TUTORIAL'] = 'true'

        return self._run_script(script_path, env)

    def _run_script(self, script_path: Path, env: Dict[str, str]) -> bool:
        """
        运行游戏脚本

        Args:
            script_path (Path): 脚本路径
            env (Dict[str, str]): 环境变量

        Returns:
            bool: 是否运行成功
        """
        try:
            # 获取脚本的绝对路径
            absolute_script_path = script_path.resolve()

            # 切换到脚本所在目录
            original_cwd = os.getcwd()
            script_dir = absolute_script_path.parent
            os.chdir(script_dir)

            try:
                # 运行脚本
                result = subprocess.run(
                    [sys.executable, str(absolute_script_path)],
                    env=env,
                    capture_output=False,
                    text=True
                )

                return result.returncode == 0

            finally:
                # 恢复原始工作目录
                os.chdir(original_cwd)

        except FileNotFoundError:
            raise GameStartupError(f"找不到Python解释器: {sys.executable}")
        except Exception as e:
            raise GameStartupError(f"运行脚本时发生错误: {str(e)}") from e

    def launch_ai_vs_player(self) -> bool:
        """启动AI对战模式的便捷方法"""
        return self.launch(GameMode.AI_VS_PLAYER)

    def launch_interactive(self) -> bool:
        """启动交互式模式的便捷方法"""
        return self.launch(GameMode.INTERACTIVE)

    def launch_demo(self) -> bool:
        """启动演示模式的便捷方法"""
        return self.launch(GameMode.DEMO)

    def list_available_modes(self):
        """列出所有可用的游戏模式"""
        print("🎮 Card Battle Arena - 可用游戏模式")
        print("=" * 50)

        for mode in GameMode:
            config = get_game_mode_config(mode.value)
            script_path = self.project_root / config.script_path
            status = "✓ 可用" if script_path.exists() else "✗ 脚本缺失"

            print(f"\n{mode.value}:")
            print(f"  名称: {config.name}")
            print(f"  描述: {config.description}")
            print(f"  脚本: {config.script_path}")
            print(f"  状态: {status}")

            if config.requires_user_input:
                print(f"  需要用户输入: 是")
            if config.supports_ai:
                print(f"  支持AI: 是")

    def print_system_info(self):
        """打印系统信息"""
        print("🖥️  系统信息:")
        print(f"  Python版本: {sys.version}")
        print(f"  工作目录: {os.getcwd()}")
        print(f"  项目根目录: {self.project_root}")

        try:
            import pygame
            print(f"  Pygame版本: {pygame.version.ver}")
        except ImportError:
            print("  Pygame: 未安装")

        try:
            import numpy
            print(f"  NumPy版本: {numpy.__version__}")
        except ImportError:
            print("  NumPy: 未安装")


if __name__ == '__main__':
    # 如果直接运行此脚本，显示可用模式
    launcher = GameLauncher()
    launcher.list_available_modes()
    print("\n" + "=" * 50)
    launcher.print_system_info()