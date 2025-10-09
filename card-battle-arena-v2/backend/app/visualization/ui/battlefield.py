"""
战场区域组件

管理战场上的随从卡牌，处理放置区域检测和目标选择。
"""

import pygame
from typing import List, Tuple, Optional
from app.game.cards import Card
from app.visualization.font_manager import render_text_safely


class BattlefieldZone:
    """
    战场区域组件

    管理战场上的随从卡牌，处理放置区域检测
    """

    def __init__(self,
                 position: Tuple[int, int],
                 size: Tuple[int, int] = (800, 200),
                 max_minions: int = 7):
        """
        初始化战场区域

        Args:
            position: 战场位置 (x, y)
            size: 战场尺寸 (width, height)
            max_minions: 最大随从数量
        """
        self.position = position
        self.size = size
        self.max_minions = max_minions

        # 战场上的随从
        self.minions: List[Card] = []

        # 视觉效果
        self.bg_color = (200, 255, 200)  # 浅绿色背景
        self.border_color = (0, 100, 0)  # 深绿色边框
        self.drop_zone_color = (150, 255, 150)  # 放置区域颜色

        # 矩形区域
        self.rect = pygame.Rect(position, size)

        # 放置区域检测
        self.drop_zones = self._create_drop_zones()

    def _create_drop_zones(self) -> List[pygame.Rect]:
        """
        创建放置区域

        Returns:
            List[pygame.Rect]: 放置区域列表
        """
        zones = []
        zone_width = 100
        zone_height = 140
        spacing = 110

        for i in range(self.max_minions):
            x = self.position[0] + 50 + i * spacing
            y = self.position[1] + (self.size[1] - zone_height) // 2
            zones.append(pygame.Rect(x, y, zone_width, zone_height))

        return zones

    def is_valid_drop_position(self, point: Tuple[int, int]) -> bool:
        """
        检查是否为有效的放置位置

        Args:
            point: 检查的点坐标 (x, y)

        Returns:
            bool: 是否为有效放置位置
        """
        return self.rect.collidepoint(point)

    def get_next_available_zone(self) -> Optional[pygame.Rect]:
        """
        获取下一个可用的放置区域

        Returns:
            Optional[pygame.Rect]: 可用的放置区域，如果没有则返回None
        """
        # 找到第一个没有随从的位置
        for i in range(min(len(self.minions), len(self.drop_zones))):
            if i >= len(self.minions):
                return self.drop_zones[i]

        # 如果随从数量小于最大数量，返回下一个位置
        if len(self.minions) < len(self.drop_zones):
            return self.drop_zones[len(self.minions)]

        return None

    def add_minion(self, minion: Card) -> bool:
        """
        添加随从到战场

        Args:
            minion: 要添加的随从卡牌

        Returns:
            bool: 是否成功添加
        """
        if len(self.minions) >= self.max_minions:
            return False

        self.minions.append(minion)
        return True

    def remove_minion(self, minion: Card) -> bool:
        """
        从战场移除随从

        Args:
            minion: 要移除的随从卡牌

        Returns:
            bool: 是否成功移除
        """
        if minion in self.minions:
            self.minions.remove(minion)
            return True
        return False

    def clear_minions(self):
        """清空战场上的所有随从"""
        self.minions.clear()

    def get_minion_at_position(self, point: Tuple[int, int]) -> Optional[Card]:
        """
        获取指定位置的随从

        Args:
            point: 检查的点坐标 (x, y)

        Returns:
            Optional[Card]: 该位置的随从，如果没有则返回None
        """
        for i, minion in enumerate(self.minions):
            if i < len(self.drop_zones):
                zone = self.drop_zones[i]
                if zone.collidepoint(point):
                    return minion
        return None

    def is_full(self) -> bool:
        """
        检查战场是否已满

        Returns:
            bool: 战场是否已满
        """
        return len(self.minions) >= self.max_minions

    def get_available_slots(self) -> int:
        """
        获取可用槽位数量

        Returns:
            int: 可用槽位数量
        """
        return max(0, self.max_minions - len(self.minions))

    def render(self, surface: pygame.Surface):
        """
        渲染战场区域

        Args:
            surface: 目标surface
        """
        if not surface:
            return

        # 绘制战场背景
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=10)

        # 绘制边框
        pygame.draw.rect(surface, self.border_color, self.rect, 3, border_radius=10)

        # 绘制放置区域
        for i, zone in enumerate(self.drop_zones):
            if i < len(self.minions):
                # 已放置随从的区域使用不同颜色
                zone_color = (180, 235, 180)
            else:
                # 可用放置区域
                zone_color = self.drop_zone_color

            pygame.draw.rect(surface, zone_color, zone, border_radius=5)
            pygame.draw.rect(surface, self.border_color, zone, 2, border_radius=5)

        # 绘制随从信息
        self._render_minions(surface)

        # 绘制战场标题
        self._render_title(surface)

    def _render_minions(self, surface: pygame.Surface):
        """
        渲染战场上的随从

        Args:
            surface: 目标surface
        """
        # 使用安全渲染方法，无需字体对象

        for i, minion in enumerate(self.minions):
            if i < len(self.drop_zones):
                zone = self.drop_zones[i]

                try:
                    # 随从名称
                    name_text = minion.name[:8]  # 限制长度
                    name_surface = render_text_safely(name_text, 18, (0, 0, 0))
                    name_rect = name_surface.get_rect(centerx=zone.centerx, y=zone.y + 10)
                    surface.blit(name_surface, name_rect)

                    # 攻击力和生命值
                    if hasattr(minion, 'attack') and hasattr(minion, 'health'):
                        stats_text = f"{minion.attack}/{minion.health}"
                        stats_surface = render_text_safely(stats_text, 18, (255, 0, 0))
                        stats_rect = stats_surface.get_rect(centerx=zone.centerx, y=zone.bottom - 25)
                        surface.blit(stats_surface, stats_rect)

                    # 状态指示 - 使用安全文本渲染
                    if hasattr(minion, 'can_attack') and minion.can_attack:
                        try:
                            attack_surface = render_text_safely("⚔", 16, (0, 255, 0))
                            attack_rect = attack_surface.get_rect(topright=(zone.right - 5, zone.y + 5))
                            surface.blit(attack_surface, attack_rect)
                        except:
                            # 降级到简单文本
                            try:
                                attack_text = "ATK"
                                attack_surface = render_text_safely(attack_text, 12, (0, 255, 0))
                                attack_rect = attack_surface.get_rect(topright=(zone.right - 5, zone.y + 5))
                                surface.blit(attack_surface, attack_rect)
                            except:
                                pass

                    if hasattr(minion, 'taunt') and minion.taunt:
                        try:
                            taunt_surface = render_text_safely("🛡", 16, (0, 0, 255))
                            taunt_rect = taunt_surface.get_rect(topleft=(zone.x + 5, zone.y + 5))
                            surface.blit(taunt_surface, taunt_rect)
                        except:
                            # 降级到简单文本
                            try:
                                taunt_text = "T"
                                taunt_surface = render_text_safely(taunt_text, 12, (0, 0, 255))
                                taunt_rect = taunt_surface.get_rect(topleft=(zone.x + 5, zone.y + 5))
                                surface.blit(taunt_surface, taunt_rect)
                            except:
                                pass

                except Exception as e:
                    # 如果渲染失败，显示简单的指示
                    error_text = f"M{i+1}"
                    try:
                        error_surface = render_text_safely(error_text, 16, (255, 0, 0))
                        error_rect = error_surface.get_rect(center=zone.center)
                        surface.blit(error_surface, error_rect)
                    except:
                        pass

    def _render_title(self, surface: pygame.Surface):
        """
        渲染战场标题

        Args:
            surface: 目标surface
        """
        try:
            title_font = pygame.font.Font(None, 24)
            title_text = f"战场 ({len(self.minions)}/{self.max_minions})"
            title_surface = render_text_safely(title_text, 24, (0, 100, 0))
            title_rect = title_surface.get_rect(centerx=self.rect.centerx, y=self.rect.y - 25)
            surface.blit(title_surface, title_rect)
        except:
            pass

    def get_info(self) -> dict:
        """
        获取战场信息

        Returns:
            dict: 战场信息
        """
        return {
            'position': self.position,
            'size': self.size,
            'minions_count': len(self.minions),
            'max_minions': self.max_minions,
            'available_slots': self.get_available_slots(),
            'is_full': self.is_full(),
            'minions': self.minions.copy()
        }