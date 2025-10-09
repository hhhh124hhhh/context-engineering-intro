"""
游戏配置设置

定义游戏的各种配置选项和默认值。
"""

from typing import Dict, Any, Optional, Union
from pathlib import Path

try:
    from config.exceptions import (
        ConfigFileNotFoundError,
        ConfigFileParseError,
        InvalidConfigError
    )
except ImportError:
    # 如果作为独立脚本运行，使用相对导入
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from config.exceptions import (
        ConfigFileNotFoundError,
        ConfigFileParseError,
        InvalidConfigError
    )


class GameSettings:
    """游戏配置类"""

    # 默认显示设置
    DEFAULT_WINDOW_WIDTH = 1200
    DEFAULT_WINDOW_HEIGHT = 800
    DEFAULT_FPS = 60
    DEFAULT_FULLSCREEN = False

    # 默认AI设置
    DEFAULT_AI_THINKING_TIME = 1.5
    DEFAULT_AI_DIFFICULTY = "normal"
    DEFAULT_AI_PERSONALITY = "balanced"

    # 默认游戏设置
    DEFAULT_MAX_TURNS = 15
    DEFAULT_TURN_TIME_LIMIT = 30
    DEFAULT_SOUND_ENABLED = True
    DEFAULT_MUSIC_VOLUME = 0.7
    DEFAULT_SFX_VOLUME = 0.8

    # 默认调试设置
    DEFAULT_DEBUG_MODE = False
    DEFAULT_VERBOSE_LOGGING = False
    DEFAULT_SHOW_FPS = False

    def __init__(self):
        """初始化游戏设置"""
        self._settings: Dict[str, Any] = {}
        self._load_defaults()

    def _load_defaults(self):
        """加载默认设置"""
        # 显示设置
        self._settings['window_width'] = self.DEFAULT_WINDOW_WIDTH
        self._settings['window_height'] = self.DEFAULT_WINDOW_HEIGHT
        self._settings['fps'] = self.DEFAULT_FPS
        self._settings['fullscreen'] = self.DEFAULT_FULLSCREEN
        self._settings['vsync'] = True

        # AI设置
        self._settings['ai_thinking_time'] = self.DEFAULT_AI_THINKING_TIME
        self._settings['ai_difficulty'] = self.DEFAULT_AI_DIFFICULTY
        self._settings['ai_personality'] = self.DEFAULT_AI_PERSONALITY

        # 游戏设置
        self._settings['max_turns'] = self.DEFAULT_MAX_TURNS
        self._settings['turn_time_limit'] = self.DEFAULT_TURN_TIME_LIMIT
        self._settings['sound_enabled'] = self.DEFAULT_SOUND_ENABLED
        self._settings['music_volume'] = self.DEFAULT_MUSIC_VOLUME
        self._settings['sfx_volume'] = self.DEFAULT_SFX_VOLUME

        # 调试设置
        self._settings['debug_mode'] = self.DEFAULT_DEBUG_MODE
        self._settings['verbose_logging'] = self.DEFAULT_VERBOSE_LOGGING
        self._settings['show_fps'] = self.DEFAULT_SHOW_FPS

        # 路径设置
        self._settings['assets_path'] = 'assets'
        self._settings['logs_path'] = 'logs'
        self._settings['saves_path'] = 'saves'

    def load_from_file(self, file_path: str):
        """
        从文件加载配置

        Args:
            file_path (str): 配置文件路径

        Raises:
            ConfigFileNotFoundError: 文件不存在
            ConfigFileParseError: 文件解析失败
            InvalidConfigError: 配置项无效
        """
        if not os.path.exists(file_path):
            raise ConfigFileNotFoundError(file_path)

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigFileParseError(file_path, str(e)) from e
        except Exception as e:
            raise ConfigFileParseError(file_path, f"读取文件失败: {str(e)}") from e

        # 验证并应用配置
        self._validate_and_apply_config(config_data)

    def _validate_and_apply_config(self, config_data: Dict[str, Any]):
        """验证并应用配置数据"""
        for key, value in config_data.items():
            try:
                self.validate_setting(key, value)
                self._settings[key] = value
            except InvalidConfigError as e:
                raise InvalidConfigError(key, value, f"验证失败: {str(e)}") from e

    def validate_setting(self, key: str, value: Any):
        """
        验证单个配置项

        Args:
            key (str): 配置项键
            value (Any): 配置项值

        Raises:
            InvalidConfigError: 配置项无效
        """
        # 窗口尺寸验证
        if key == 'window_width':
            if not isinstance(value, int) or value <= 0:
                raise InvalidConfigError(key, value, "窗口宽度必须为正整数")
            if value < 800:
                raise InvalidConfigError(key, value, "窗口宽度不能小于800像素")
        elif key == 'window_height':
            if not isinstance(value, int) or value <= 0:
                raise InvalidConfigError(key, value, "窗口高度必须为正整数")
            if value < 600:
                raise InvalidConfigError(key, value, "窗口高度不能小于600像素")

        # FPS验证
        elif key == 'fps':
            if not isinstance(value, int) or value <= 0:
                raise InvalidConfigError(key, value, "FPS必须为正整数")
            if value > 240:
                raise InvalidConfigError(key, value, "FPS不应超过240")

        # AI相关验证
        elif key == 'ai_thinking_time':
            if not isinstance(value, (int, float)) or value <= 0:
                raise InvalidConfigError(key, value, "AI思考时间必须大于0")
            if value > 10:
                raise InvalidConfigError(key, value, "AI思考时间不应超过10秒")
        elif key == 'ai_difficulty':
            valid_difficulties = ['easy', 'normal', 'hard']
            if value not in valid_difficulties:
                raise InvalidConfigError(key, value, f"AI难度必须是: {', '.join(valid_difficulties)}")

        # 游戏相关验证
        elif key == 'max_turns':
            if not isinstance(value, int) or value <= 0:
                raise InvalidConfigError(key, value, "最大回合数必须为正整数")
            if value > 100:
                raise InvalidConfigError(key, value, "最大回合数不应超过100")
        elif key == 'turn_time_limit':
            if not isinstance(value, (int, float)) or value <= 0:
                raise InvalidConfigError(key, value, "回合时间限制必须大于0")
        elif key in ['music_volume', 'sfx_volume']:
            if not isinstance(value, (int, float)) or not 0 <= value <= 1:
                raise InvalidConfigError(key, value, "音量必须在0.0到1.0之间")

        # 布尔值验证
        elif key in ['fullscreen', 'sound_enabled', 'debug_mode', 'verbose_logging', 'show_fps', 'vsync']:
            if not isinstance(value, bool):
                raise InvalidConfigError(key, value, f"{key} 必须是布尔值")

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置项

        Args:
            key (str): 配置项键
            default (Any): 默认值

        Returns:
            Any: 配置项值
        """
        return self._settings.get(key, default)

    def set(self, key: str, value: Any):
        """
        设置配置项

        Args:
            key (str): 配置项键
            value (Any): 配置项值

        Raises:
            InvalidConfigError: 配置项无效
        """
        self.validate_setting(key, value)
        self._settings[key] = value

    def save_to_file(self, file_path: str):
        """
        保存配置到文件

        Args:
            file_path (str): 配置文件路径
        """
        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self._settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise ConfigFileParseError(file_path, f"保存文件失败: {str(e)}") from e

    def update_from_dict(self, updates: Dict[str, Any]):
        """
        从字典更新配置

        Args:
            updates (Dict[str, Any]): 配置更新字典
        """
        for key, value in updates.items():
            self.set(key, value)

    def get_display_settings(self) -> Dict[str, Any]:
        """获取显示相关设置"""
        return {
            'window_width': self._settings['window_width'],
            'window_height': self._settings['window_height'],
            'fps': self._settings['fps'],
            'fullscreen': self._settings['fullscreen'],
            'vsync': self._settings['vsync']
        }

    def get_ai_settings(self) -> Dict[str, Any]:
        """获取AI相关设置"""
        return {
            'thinking_time': self._settings['ai_thinking_time'],
            'difficulty': self._settings['ai_difficulty'],
            'personality': self._settings['ai_personality']
        }

    def get_game_settings(self) -> Dict[str, Any]:
        """获取游戏相关设置"""
        return {
            'max_turns': self._settings['max_turns'],
            'turn_time_limit': self._settings['turn_time_limit'],
            'sound_enabled': self._settings['sound_enabled'],
            'music_volume': self._settings['music_volume'],
            'sfx_volume': self._settings['sfx_volume']
        }

    def get_debug_settings(self) -> Dict[str, Any]:
        """获取调试相关设置"""
        return {
            'debug_mode': self._settings['debug_mode'],
            'verbose_logging': self._settings['verbose_logging'],
            'show_fps': self._settings['show_fps']
        }

    def __str__(self) -> str:
        """返回配置的字符串表示"""
        return json.dumps(self._settings, indent=2, ensure_ascii=False)

    def __repr__(self) -> str:
        """返回配置的详细表示"""
        return f"GameSettings({self._settings})"


# 全局配置实例
_global_settings: Optional[GameSettings] = None


def get_global_settings() -> GameSettings:
    """
    获取全局配置实例

    Returns:
        GameSettings: 全局配置实例
    """
    global _global_settings
    if _global_settings is None:
        _global_settings = GameSettings()
    return _global_settings


def load_config(config_file: Optional[str] = None) -> GameSettings:
    """
    加载配置的便捷函数

    Args:
        config_file (Optional[str]): 配置文件路径，None表示使用默认配置

    Returns:
        GameSettings: 加载后的配置实例
    """
    settings = get_global_settings()

    if config_file:
        settings.load_from_file(config_file)

    return settings


def save_config(config_file: str, settings: Optional[GameSettings] = None):
    """
    保存配置的便捷函数

    Args:
        config_file (str): 配置文件路径
        settings (Optional[GameSettings]): 要保存的配置实例
    """
    if settings is None:
        settings = get_global_settings()

    settings.save_to_file(config_file)


if __name__ == '__main__':
    # 如果直接运行此脚本，显示默认配置
    settings = GameSettings()
    print("默认游戏配置:")
    print(settings)