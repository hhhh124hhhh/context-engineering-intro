"""
UI组件模块

提供可交互的UI组件系统，支持卡牌游戏的所有交互功能。
"""

from .card_component import InteractiveCard
from .hand_area import HandArea
from .battlefield import BattlefieldZone
from .game_hud import GameHUD
from .target_selector import TargetSelector

__all__ = [
    'InteractiveCard',
    'HandArea',
    'BattlefieldZone',
    'GameHUD',
    'TargetSelector'
]