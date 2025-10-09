"""
CLI模块的自定义异常类

定义游戏中可能出现的各种异常情况，提供清晰的错误信息。
"""


class GameLauncherError(Exception):
    """游戏启动器基础异常类"""
    pass


class InvalidGameModeError(GameLauncherError):
    """无效的游戏模式异常"""

    def __init__(self, mode: str, available_modes: list):
        self.mode = mode
        self.available_modes = available_modes
        super().__init__(
            f"无效的游戏模式: '{mode}'。可用模式: {', '.join(available_modes)}"
        )


class ConfigurationError(GameLauncherError):
    """配置相关异常"""
    pass


class MissingDependencyError(GameLauncherError):
    """缺少依赖异常"""

    def __init__(self, dependency: str):
        self.dependency = dependency
        super().__init__(f"缺少必需的依赖: {dependency}")


class PygameInitializationError(GameLauncherError):
    """Pygame初始化失败异常"""

    def __init__(self, pygame_error: str):
        self.pygame_error = pygame_error
        super().__init__(f"Pygame初始化失败: {pygame_error}")


class DisplayError(GameLauncherError):
    """显示相关异常"""

    def __init__(self, display_error: str):
        self.display_error = display_error
        super().__init__(f"显示错误: {display_error}")


class GameStartupError(GameLauncherError):
    """游戏启动异常"""

    def __init__(self, startup_error: str):
        self.startup_error = startup_error
        super().__init__(f"游戏启动失败: {startup_error}")