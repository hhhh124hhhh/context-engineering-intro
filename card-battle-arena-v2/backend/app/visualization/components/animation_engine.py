"""
动画引擎
"""

import time
import math
from typing import Dict, List, Optional, Tuple, Any
from app.visualization.design.tokens import DesignTokens


class Animation:
    """动画基类"""

    def __init__(self, duration: float):
        """
        初始化动画

        Args:
            duration: 动画持续时间（秒）
        """
        self.duration = duration
        self.start_time = None
        self.progress = 0.0
        self.completed = False
        self.loop = False
        self.callback = None

    def start(self, start_time: float = None) -> None:
        """
        开始动画

        Args:
            start_time: 开始时间（可选）
        """
        self.start_time = start_time if start_time else time.time()
        self.progress = 0.0
        self.completed = False

    def update(self, current_time: float) -> bool:
        """
        更新动画

        Args:
            current_time: 当前时间

        Returns:
            动画是否完成
        """
        if self.start_time is None:
            self.start(current_time)

        elapsed = current_time - self.start_time
        self.progress = min(1.0, elapsed / self.duration)

        if self.progress >= 1.0:
            self.completed = True
            if self.callback:
                self.callback()
            if self.loop:
                self.start(current_time)
            return True

        return False

    def get_value(self) -> Any:
        """
        获取当前动画值

        Returns:
            当前动画值
        """
        return self.progress

    def is_completed(self) -> bool:
        """动画是否完成"""
        return self.completed

    def is_running(self) -> bool:
        """动画是否正在运行"""
        return self.start_time is not None and not self.completed

    def set_loop(self, loop: bool) -> None:
        """设置循环"""
        self.loop = loop

    def set_callback(self, callback) -> None:
        """设置完成回调"""
        self.callback = callback


class MoveAnimation(Animation):
    """移动动画"""

    def __init__(self, start_pos: Tuple[float, float],
                 end_pos: Tuple[float, float], duration: float,
                 easing: str = 'ease_out_cubic'):
        """
        初始化移动动画

        Args:
            start_pos: 起始位置
            end_pos: 结束位置
            duration: 持续时间
            easing: 缓动函数
        """
        super().__init__(duration)
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.easing = easing
        self.current_pos = start_pos

    def update(self, current_time: float) -> bool:
        """更新动画"""
        completed = super().update(current_time)
        self.current_pos = self.get_position()
        return completed

    def get_position(self) -> Tuple[float, float]:
        """获取当前位置"""
        if self.easing == 'linear':
            return self._linear_interpolation()
        elif self.easing == 'ease_in_out':
            return self._ease_in_out_interpolation()
        elif self.easing == 'ease_out_cubic':
            return self._ease_out_cubic_interpolation()
        else:
            return self._linear_interpolation()

    def _linear_interpolation(self) -> Tuple[float, float]:
        """线性插值"""
        x = self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * self.progress
        y = self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * self.progress
        return (x, y)

    def _ease_in_out_interpolation(self) -> Tuple[float, float]:
        """缓入缓出插值"""
        if self.progress < 0.5:
            t = 2 * self.progress * self.progress
        else:
            t = 1 - 2 * (1 - self.progress) * (1 - self.progress)

        x = self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * t
        y = self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * t
        return (x, y)

    def _ease_out_cubic_interpolation(self) -> Tuple[float, float]:
        """缓出立方插值"""
        t = 1 - (1 - self.progress) ** 3
        x = self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * t
        y = self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * t
        return (x, y)


class FadeAnimation(Animation):
    """淡入淡出动画"""

    def __init__(self, start_alpha: int, end_alpha: int, duration: float):
        """
        初始化淡入淡出动画

        Args:
            start_alpha: 起始透明度
            end_alpha: 结束透明度
            duration: 持续时间
        """
        super().__init__(duration)
        self.start_alpha = start_alpha
        self.end_alpha = end_alpha
        self.current_alpha = start_alpha

    def update(self, current_time: float) -> bool:
        """更新动画"""
        completed = super().update(current_time)
        self.current_alpha = self.get_alpha()
        return completed

    def get_alpha(self) -> int:
        """获取当前透明度"""
        alpha = int(self.start_alpha + (self.end_alpha - self.start_alpha) * self.progress)
        return max(0, min(255, alpha))


class ScaleAnimation(Animation):
    """缩放动画"""

    def __init__(self, start_scale: float, end_scale: float, duration: float):
        """
        初始化缩放动画

        Args:
            start_scale: 起始缩放
            end_scale: 结束缩放
            duration: 持续时间
        """
        super().__init__(duration)
        self.start_scale = start_scale
        self.end_scale = end_scale
        self.current_scale = start_scale

    def update(self, current_time: float) -> bool:
        """更新动画"""
        completed = super().update(current_time)
        self.current_scale = self.get_scale()
        return completed

    def get_scale(self) -> float:
        """获取当前缩放"""
        return self.start_scale + (self.end_scale - self.start_scale) * self.progress


class ShakeAnimation(Animation):
    """震动动画"""

    def __init__(self, intensity: float, duration: float):
        """
        初始化震动动画

        Args:
            intensity: 震动强度
            duration: 持续时间
        """
        super().__init__(duration)
        self.intensity = intensity
        self.current_offset = (0, 0)

    def update(self, current_time: float) -> bool:
        """更新动画"""
        completed = super().update(current_time)

        if not self.completed:
            # 生成随机偏移
            import random
            angle = random.random() * 2 * math.pi
            factor = (1 - self.progress)  # 震动逐渐减弱
            offset_x = math.cos(angle) * self.intensity * factor
            offset_y = math.sin(angle) * self.intensity * factor
            self.current_offset = (offset_x, offset_y)
        else:
            self.current_offset = (0, 0)

        return completed

    def get_offset(self) -> Tuple[float, float]:
        """获取当前偏移"""
        return self.current_offset


class AnimationEngine:
    """动画引擎"""

    def __init__(self):
        """初始化动画引擎"""
        self.tokens = DesignTokens()
        self.animations: Dict[str, Animation] = {}
        self.next_id = 1
        self.running = False

    def start(self) -> None:
        """启动动画引擎"""
        self.running = True

    def stop(self) -> None:
        """停止动画引擎"""
        self.running = False
        self.animations.clear()

    def update(self, dt: float = None) -> None:
        """
        更新所有动画

        Args:
            dt: 时间增量（秒）
        """
        if not self.running:
            return

        current_time = time.time()
        completed_animations = []

        for animation_id, animation in self.animations.items():
            if animation.update(current_time):
                if not animation.loop:
                    completed_animations.append(animation_id)

        # 移除完成的动画
        for animation_id in completed_animations:
            del self.animations[animation_id]

    def add_animation(self, animation: Animation, animation_id: str = None) -> str:
        """
        添加动画

        Args:
            animation: 动画对象
            animation_id: 动画ID（可选）

        Returns:
            动画ID
        """
        if animation_id is None:
            animation_id = f"animation_{self.next_id}"
            self.next_id += 1

        self.animations[animation_id] = animation
        animation.start()
        return animation_id

    def remove_animation(self, animation_id: str) -> bool:
        """
        移除动画

        Args:
            animation_id: 动画ID

        Returns:
            是否成功移除
        """
        if animation_id in self.animations:
            del self.animations[animation_id]
            return True
        return False

    def add_card_animation(self, animation_type: str, **kwargs) -> str:
        """
        添加卡牌动画

        Args:
            animation_type: 动画类型
            **kwargs: 动画参数

        Returns:
            动画ID
        """
        if animation_type == 'move':
            start_pos = kwargs.get('start_pos', (0, 0))
            end_pos = kwargs.get('end_pos', (100, 100))
            duration = kwargs.get('duration', self.tokens.ANIMATION['card_play'])
            easing = kwargs.get('easing', 'ease_out_cubic')

            animation = MoveAnimation(start_pos, end_pos, duration, easing)

        elif animation_type == 'fade':
            start_alpha = kwargs.get('start_alpha', 0)
            end_alpha = kwargs.get('end_alpha', 255)
            duration = kwargs.get('duration', self.tokens.ANIMATION['card_draw'])

            animation = FadeAnimation(start_alpha, end_alpha, duration)

        elif animation_type == 'scale':
            start_scale = kwargs.get('start_scale', 1.0)
            end_scale = kwargs.get('end_scale', 1.2)
            duration = kwargs.get('duration', self.tokens.ANIMATION['hover'])

            animation = ScaleAnimation(start_scale, end_scale, duration)

        elif animation_type == 'shake':
            intensity = kwargs.get('intensity', 5)
            duration = kwargs.get('duration', self.tokens.ANIMATION['damage'])

            animation = ShakeAnimation(intensity, duration)

        else:
            raise ValueError(f"Unknown animation type: {animation_type}")

        return self.add_animation(animation)

    def is_animating(self) -> bool:
        """是否有动画正在运行"""
        return len(self.animations) > 0

    def get_animation_count(self) -> int:
        """获取动画数量"""
        return len(self.animations)

    def get_animation(self, animation_id: str) -> Optional[Animation]:
        """获取指定动画"""
        return self.animations.get(animation_id)

    def clear_all_animations(self) -> None:
        """清除所有动画"""
        self.animations.clear()

    def set_animation_callback(self, animation_id: str, callback) -> bool:
        """
        设置动画回调

        Args:
            animation_id: 动画ID
            callback: 回调函数

        Returns:
            是否成功设置
        """
        animation = self.get_animation(animation_id)
        if animation:
            animation.set_callback(callback)
            return True
        return False