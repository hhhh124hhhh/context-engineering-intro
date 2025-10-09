"""
游戏模式定义

定义所有支持的游戏模式及其相关配置。
"""

from enum import Enum
from typing import Dict, Any
from dataclasses import dataclass


class GameMode(str, Enum):
    """游戏模式枚举"""
    AI_VS_PLAYER = "ai-vs-player"
    AI = "ai"
    INTERACTIVE = "interactive"
    DEMO = "demo"

    @classmethod
    def all_modes(cls) -> list[str]:
        """获取所有可用模式"""
        return [mode.value for mode in cls]

    @classmethod
    def is_valid_mode(cls, mode: str) -> bool:
        """检查模式是否有效"""
        return mode in cls.all_modes()

    def get_description(self) -> str:
        """获取模式描述"""
        descriptions = {
            GameMode.AI_VS_PLAYER: "AI对战模式 - 与智能AI进行策略对战",
            GameMode.AI: "简化AI模式 - 快速体验AI对战功能",
            GameMode.INTERACTIVE: "交互式模式 - 手动操作卡牌进行对战",
            GameMode.DEMO: "演示模式 - 自动展示游戏各种功能"
        }
        return descriptions.get(self, "未知模式")

    def get_demo_script_name(self) -> str:
        """获取对应的演示脚本名称"""
        script_mapping = {
            GameMode.AI_VS_PLAYER: "pygame_vs_ai_demo.py",
            GameMode.AI: "simple_ai_demo.py",
            GameMode.INTERACTIVE: "interactive_demo.py",
            GameMode.DEMO: "visual_demo.py"
        }
        return script_mapping.get(self, "visual_demo.py")


@dataclass
class GameModeConfig:
    """游戏模式配置类"""
    mode: GameMode
    name: str
    description: str
    script_path: str
    requires_user_input: bool = False
    supports_ai: bool = True
    max_players: int = 2
    default_settings: Dict[str, Any] = None

    def __post_init__(self):
        if self.default_settings is None:
            self.default_settings = {}


class GameModeRegistry:
    """游戏模式注册表"""

    def __init__(self):
        self._modes: Dict[GameMode, GameModeConfig] = {}
        self._register_default_modes()

    def _register_default_modes(self):
        """注册默认游戏模式"""
        default_configs = {
            GameMode.AI_VS_PLAYER: GameModeConfig(
                mode=GameMode.AI_VS_PLAYER,
                name="AI对战",
                description="与智能AI进行策略对战，体验完整的游戏功能",
                script_path="backend/pygame_vs_ai_demo.py",
                requires_user_input=True,
                supports_ai=True,
                max_players=2,
                default_settings={
                    "ai_thinking_time": 1.5,
                    "max_turns": 15,
                    "window_width": 1200,
                    "window_height": 800
                }
            ),
            GameMode.AI: GameModeConfig(
                mode=GameMode.AI,
                name="简化AI",
                description="快速体验AI对战功能，简化版游戏流程",
                script_path="backend/simple_ai_demo.py",
                requires_user_input=False,
                supports_ai=True,
                max_players=2,
                default_settings={
                    "ai_thinking_time": 1.0,
                    "max_turns": 10,
                    "window_width": 800,
                    "window_height": 600
                }
            ),
            GameMode.INTERACTIVE: GameModeConfig(
                mode=GameMode.INTERACTIVE,
                name="交互式",
                description="手动操作卡牌进行对战，完全自由的游戏体验",
                script_path="backend/interactive_game.py",
                requires_user_input=True,
                supports_ai=False,
                max_players=2,
                default_settings={
                    "turn_time_limit": 30,
                    "window_width": 1200,
                    "window_height": 800
                }
            ),
            GameMode.DEMO: GameModeConfig(
                mode=GameMode.DEMO,
                name="演示模式",
                description="自动展示游戏各种功能和特效",
                script_path="backend/visual_demo.py",
                requires_user_input=False,
                supports_ai=False,
                max_players=2,
                default_settings={
                    "auto_play": True,
                    "show_tutorial": True,
                    "window_width": 1200,
                    "window_height": 800
                }
            )
        }

        for mode, config in default_configs.items():
            self.register_mode(mode, config)

    def register_mode(self, mode: GameMode, config: GameModeConfig):
        """注册游戏模式"""
        self._modes[mode] = config

    def get_config(self, mode: GameMode) -> GameModeConfig:
        """获取游戏模式配置"""
        if mode not in self._modes:
            raise ValueError(f"未注册的游戏模式: {mode}")
        return self._modes[mode]

    def get_all_configs(self) -> Dict[GameMode, GameModeConfig]:
        """获取所有游戏模式配置"""
        return self._modes.copy()

    def is_mode_available(self, mode: GameMode) -> bool:
        """检查游戏模式是否可用"""
        import os
        if mode not in self._modes:
            return False

        config = self._modes[mode]
        return os.path.exists(config.script_path)

    def get_available_modes(self) -> list[GameMode]:
        """获取所有可用的游戏模式"""
        return [mode for mode in self._modes if self.is_mode_available(mode)]

    def print_mode_list(self):
        """打印所有可用游戏模式"""
        print("可用的游戏模式:")
        print("-" * 60)

        available_modes = self.get_available_modes()
        if not available_modes:
            print("  没有可用的游戏模式")
            return

        for mode in available_modes:
            config = self.get_config(mode)
            status = "✓" if self.is_mode_available(mode) else "✗"
            print(f"  {status} {mode.value:15} - {config.name}")
            print(f"    {config.description}")
            print()


# 全局游戏模式注册表实例
game_mode_registry = GameModeRegistry()


def get_game_mode_config(mode: str) -> GameModeConfig:
    """
    获取游戏模式配置的便捷函数

    Args:
        mode (str): 游戏模式字符串

    Returns:
        GameModeConfig: 游戏模式配置

    Raises:
        ValueError: 如果模式无效
    """
    if not GameMode.is_valid_mode(mode):
        raise ValueError(f"无效的游戏模式: {mode}")

    game_mode_enum = GameMode(mode)
    return game_mode_registry.get_config(game_mode_enum)


def list_available_modes() -> list[str]:
    """
    获取所有可用游戏模式的便捷函数

    Returns:
        list[str]: 可用游戏模式列表
    """
    return [mode.value for mode in game_mode_registry.get_available_modes()]


if __name__ == '__main__':
    # 如果直接运行此脚本，显示游戏模式信息
    game_mode_registry.print_mode_list()