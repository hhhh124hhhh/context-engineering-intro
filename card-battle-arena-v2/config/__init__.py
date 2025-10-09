"""
配置模块

提供游戏配置管理、游戏模式定义等功能。
"""

from .settings import GameSettings, get_global_settings, load_config, save_config
from .game_modes import (
    GameMode,
    GameModeConfig,
    GameModeRegistry,
    get_game_mode_config,
    list_available_modes,
    game_mode_registry
)
from .exceptions import (
    ConfigError,
    InvalidConfigError,
    ConfigFileNotFoundError,
    ConfigFileParseError,
    InvalidGameModeConfigError
)

__all__ = [
    'GameSettings',
    'get_global_settings',
    'load_config',
    'save_config',
    'GameMode',
    'GameModeConfig',
    'GameModeRegistry',
    'get_game_mode_config',
    'list_available_modes',
    'game_mode_registry',
    'ConfigError',
    'InvalidConfigError',
    'ConfigFileNotFoundError',
    'ConfigFileParseError',
    'InvalidGameModeConfigError'
]