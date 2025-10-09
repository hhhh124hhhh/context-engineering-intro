"""
配置模块的自定义异常类

定义配置加载、验证过程中可能出现的异常情况。
"""


class ConfigError(Exception):
    """配置系统基础异常类"""
    pass


class InvalidConfigError(ConfigError):
    """无效配置异常"""

    def __init__(self, setting_name: str, value, reason: str):
        self.setting_name = setting_name
        self.value = value
        self.reason = reason
        super().__init__(
            f"配置项 '{setting_name}' 的值 '{value}' 无效: {reason}"
        )


class ConfigFileNotFoundError(ConfigError):
    """配置文件未找到异常"""

    def __init__(self, file_path: str):
        self.file_path = file_path
        super().__init__(f"配置文件未找到: {file_path}")


class ConfigFileParseError(ConfigError):
    """配置文件解析错误异常"""

    def __init__(self, file_path: str, parse_error: str):
        self.file_path = file_path
        self.parse_error = parse_error
        super().__init__(
            f"配置文件解析失败 '{file_path}': {parse_error}"
        )


class InvalidGameModeConfigError(ConfigError):
    """无效游戏模式配置异常"""

    def __init__(self, mode: str):
        self.mode = mode
        super().__init__(f"无效的游戏模式配置: {mode}")