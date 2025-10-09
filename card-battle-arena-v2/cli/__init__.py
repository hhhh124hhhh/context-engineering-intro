"""
CLI模块

提供统一的命令行接口和游戏启动功能。
"""

from .parser import create_parser, main_parser
from .launcher import GameLauncher
from .exceptions import (
    GameLauncherError,
    InvalidGameModeError,
    ConfigurationError,
    MissingDependencyError,
    PygameInitializationError,
    DisplayError,
    GameStartupError
)

__all__ = [
    'create_parser',
    'main_parser',
    'GameLauncher',
    'GameLauncherError',
    'InvalidGameModeError',
    'ConfigurationError',
    'MissingDependencyError',
    'PygameInitializationError',
    'DisplayError',
    'GameStartupError'
]