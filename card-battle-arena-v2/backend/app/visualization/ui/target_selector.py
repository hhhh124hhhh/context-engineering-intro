"""
目标选择器组件

处理卡牌技能和攻击时的目标选择逻辑。
"""

import pygame
from typing import List, Optional, Tuple, Any
from app.game.cards import Card, CardType
from app.game.state import GameState, Player


class TargetSelector:
    """
    目标选择器

    处理卡牌技能和攻击时的目标选择逻辑
    """

    def __init__(self, game: GameState):
        """
        初始化目标选择器

        Args:
            game: 游戏状态
        """
        self.game = game
        self.is_selecting = False
        self.current_action = None  # 'attack', 'spell', 'hero_power'
        self.source_card = None
        self.valid_targets = []
        self.selected_target = None

        # 视觉效果
        self.highlight_color = (255, 255, 100)  # 黄色高亮
        self.invalid_color = (100, 100, 100)    # 灰色（无效目标）

    def start_target_selection(self,
                              action: str,
                              source_card: Optional[Card] = None) -> List[Card]:
        """
        开始目标选择

        Args:
            action: 动作类型 ('attack', 'spell', 'hero_power')
            source_card: 源卡牌（对于攻击和法术）

        Returns:
            List[Card]: 有效目标列表
        """
        self.is_selecting = True
        self.current_action = action
        self.source_card = source_card
        self.selected_target = None

        # 根据动作类型获取有效目标
        self.valid_targets = self.get_valid_targets(source_card, action)

        return self.valid_targets

    def get_valid_targets(self, source_card: Optional[Card], action: str) -> List[Card]:
        """
        获取有效目标

        Args:
            source_card: 源卡牌
            action: 动作类型

        Returns:
            List[Card]: 有效目标列表
        """
        targets = []
        current_player = self.game.current_player
        opponent = self.game.opponent

        if action == "attack":
            # 攻击目标：对手英雄和对手的随从
            if source_card and source_card.can_attack:
                targets.append(opponent.hero)
                targets.extend(opponent.battlefield)

        elif action == "spell":
            # 法术目标：取决于法术类型
            if source_card:
                # 这里可以根据法术的具体效果来决定目标
                # 简化处理：假设法术可以 targeting 任何角色
                targets.append(opponent.hero)
                targets.extend(opponent.battlefield)

                # 有些法术也可以 targeting 自己的随从或英雄
                if hasattr(source_card, 'can_target_friendly') and source_card.can_target_friendly:
                    targets.append(current_player.hero)
                    targets.extend(current_player.battlefield)

        elif action == "hero_power":
            # 英雄技能目标
            targets.append(opponent.hero)
            targets.extend(opponent.battlefield)

        return targets

    def select_target(self, point: Tuple[int, int], target_components: List[Any]) -> Optional[Card]:
        """
        选择目标

        Args:
            point: 点击位置
            target_components: 目标组件列表（用于位置检测）

        Returns:
            Optional[Card]: 选中的目标，如果没有有效目标则返回None
        """
        if not self.is_selecting:
            return None

        # 找到点击位置的目标
        clicked_target = None
        for component in target_components:
            if hasattr(component, 'is_point_inside') and component.is_point_inside(point):
                if hasattr(component, 'card'):
                    clicked_target = component.card
                elif hasattr(component, 'hero'):
                    clicked_target = component.hero
                break

        # 检查是否为有效目标
        if clicked_target and clicked_target in self.valid_targets:
            self.selected_target = clicked_target
            self.end_selection()
            return clicked_target

        return None

    def cancel_selection(self):
        """取消目标选择"""
        self.is_selecting = False
        self.current_action = None
        self.source_card = None
        self.valid_targets = []
        self.selected_target = None

    def end_selection(self):
        """结束目标选择"""
        self.is_selecting = False

    def is_valid_target(self, target: Card) -> bool:
        """
        检查目标是否有效

        Args:
            target: 要检查的目标

        Returns:
            bool: 目标是否有效
        """
        return target in self.valid_targets

    def get_targets_by_type(self, target_type: str) -> List[Card]:
        """
        按类型获取目标

        Args:
            target_type: 目标类型 ('hero', 'minion', 'friendly', 'enemy')

        Returns:
            List[Card]: 指定类型的目标列表
        """
        filtered_targets = []
        current_player = self.game.current_player
        opponent = self.game.opponent

        for target in self.valid_targets:
            is_hero = hasattr(target, 'health') and not hasattr(target, 'card_type')
            is_minion = hasattr(target, 'card_type') and target.card_type == CardType.MINION
            is_friendly = (target in current_player.battlefield or target == current_player.hero)
            is_enemy = (target in opponent.battlefield or target == opponent.hero)

            if target_type == "hero" and is_hero:
                filtered_targets.append(target)
            elif target_type == "minion" and is_minion:
                filtered_targets.append(target)
            elif target_type == "friendly" and is_friendly:
                filtered_targets.append(target)
            elif target_type == "enemy" and is_enemy:
                filtered_targets.append(target)

        return filtered_targets

    def render_highlights(self, surface: pygame.Surface, target_components: List[Any]):
        """
        渲染目标高亮

        Args:
            surface: 目标surface
            target_components: 目标组件列表
        """
        if not self.is_selecting or not surface:
            return

        for component in target_components:
            target = None
            rect = None

            # 获取组件的目标和矩形区域
            if hasattr(component, 'card'):
                target = component.card
                rect = component.get_current_rect() if hasattr(component, 'get_current_rect') else component.rect
            elif hasattr(component, 'hero'):
                target = component.hero
                rect = component.hero_rect if hasattr(component, 'hero_rect') else component.rect

            if target and rect:
                # 检查是否为有效目标
                is_valid = self.is_valid_target(target)

                # 选择高亮颜色
                if is_valid:
                    color = self.highlight_color
                    width = 3
                else:
                    color = self.invalid_color
                    width = 1

                # 绘制高亮边框
                pygame.draw.rect(surface, color, rect, width, border_radius=5)

                # 如果是有效目标，添加闪烁效果
                if is_valid:
                    time = pygame.time.get_ticks()
                    if (time // 500) % 2 == 0:  # 每500ms闪烁一次
                        pygame.draw.rect(surface, (255, 255, 255), rect, 1, border_radius=5)

    def get_selection_info(self) -> dict:
        """
        获取选择信息

        Returns:
            dict: 选择状态信息
        """
        return {
            'is_selecting': self.is_selecting,
            'current_action': self.current_action,
            'source_card': self.source_card,
            'valid_targets_count': len(self.valid_targets),
            'selected_target': self.selected_target,
            'valid_target_types': {
                'heroes': len(self.get_targets_by_type('hero')),
                'minions': len(self.get_targets_by_type('minion')),
                'friendly': len(self.get_targets_by_type('friendly')),
                'enemy': len(self.get_targets_by_type('enemy'))
            }
        }

    def can_target_enemy_hero(self) -> bool:
        """
        检查是否可以 targeting 敌方英雄

        Returns:
            bool: 是否可以 targeting 敌方英雄
        """
        enemy_heroes = self.get_targets_by_type('enemy')
        for target in enemy_heroes:
            if hasattr(target, 'health') and not hasattr(target, 'card_type'):
                return True
        return False

    def can_target_enemy_minions(self) -> bool:
        """
        检查是否可以 targeting 敌方随从

        Returns:
            bool: 是否可以 targeting 敌方随从
        """
        enemy_minions = self.get_targets_by_type('enemy')
        for target in enemy_minions:
            if hasattr(target, 'card_type') and target.card_type == CardType.MINION:
                return True
        return False

    def get_priority_targets(self) -> List[Card]:
        """
        获取优先目标（有嘲讽的随从优先）

        Returns:
            List[Card]: 优先目标列表
        """
        priority_targets = []
        normal_targets = []

        for target in self.valid_targets:
            if hasattr(target, 'taunt') and target.taunt:
                priority_targets.append(target)
            else:
                normal_targets.append(target)

        return priority_targets + normal_targets