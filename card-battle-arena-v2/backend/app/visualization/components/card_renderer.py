"""
组件化卡牌渲染器
"""

import pygame
from typing import Tuple, Optional
from app.game.cards import Card
from app.visualization.design.tokens import DesignTokens
from app.visualization.font_manager import render_text_safely


class CardRenderer:
    """组件化卡牌渲染器"""

    def __init__(self):
        """初始化卡牌渲染器"""
        self.tokens = DesignTokens()
        self.card_width = self.tokens.CARD['width']
        self.card_height = self.tokens.CARD['height']
        self.corner_radius = self.tokens.CARD['corner_radius']
        self.border_width = self.tokens.CARD['border_width']

    def render_card(self, card: Card, position: Tuple[int, int],
                   surface: pygame.Surface, selected: bool = False,
                   hover: bool = False) -> None:
        """
        渲染单张卡牌

        Args:
            card: 要渲染的卡牌
            position: 卡牌位置 (x, y)
            surface: 目标surface
            selected: 是否选中
            hover: 是否悬停
        """
        x, y = position

        # 渲染卡牌背景
        self.render_card_background(surface, position, selected, hover)

        # 渲染卡牌内容
        self.render_card_content(surface, card, position)

        # 渲染卡牌边框
        self.render_card_border(surface, card, position, selected, hover)

    def render_card_background(self, surface: pygame.Surface,
                             position: Tuple[int, int],
                             selected: bool = False,
                             hover: bool = False) -> None:
        """
        渲染卡牌背景

        Args:
            surface: 目标surface
            position: 卡牌位置
            selected: 是否选中
            hover: 是否悬停
        """
        x, y = position

        # 选择背景颜色
        if selected:
            bg_color = self.tokens.COLORS['card']['selected']
        elif hover:
            bg_color = self.tokens.COLORS['card']['hover']
        else:
            bg_color = self.tokens.COLORS['card']['background']

        # 创建渐变背景
        gradient_colors = self.tokens.get_gradient_colors(
            bg_color,
            self.tokens.adjust_brightness(bg_color, 0.9),
            5
        )

        # 绘制渐变背景
        for i, color in enumerate(gradient_colors):
            rect_height = self.card_height // len(gradient_colors)
            rect_y = y + i * rect_height
            pygame.draw.rect(surface, color,
                           (x, rect_y, self.card_width, rect_height))

        # 绘制圆角效果
        if self.corner_radius > 0:
            # 简化版圆角效果
            corner_size = self.corner_radius * 2
            for corner_x, corner_y in [(x, y), (x + self.card_width - corner_size, y),
                                     (x, y + self.card_height - corner_size),
                                     (x + self.card_width - corner_size, y + self.card_height - corner_size)]:
                pygame.draw.circle(surface, bg_color,
                                 (corner_x + self.corner_radius, corner_y + self.corner_radius),
                                 self.corner_radius)

    def render_card_content(self, surface: pygame.Surface,
                           card: Card, position: Tuple[int, int]) -> None:
        """
        渲染卡牌内容

        Args:
            surface: 目标surface
            card: 卡牌对象
            position: 卡牌位置
        """
        x, y = position

        # 渲染卡牌名称
        self.render_card_name(surface, card, position)

        # 渲染费用
        self.render_card_cost(surface, card, position)

        # 渲染攻击力和生命值
        if card.card_type.value in ["minion", "weapon"]:
            self.render_card_stats(surface, card, position)

        # 渲染技能图标
        self.render_card_abilities(surface, card, position)

    def render_card_name(self, surface: pygame.Surface,
                        card: Card, position: Tuple[int, int]) -> None:
        """渲染卡牌名称"""
        x, y = position

        # 截断过长的名称
        display_name = card.name[:10] + "..." if len(card.name) > 10 else card.name

        try:
            text_surface = render_text_safely(display_name, 16, self.tokens.COLORS['card']['text'])
            surface.blit(text_surface, (x + 8, y + 8))
        except:
            # 如果安全渲染失败，显示卡牌ID
            try:
                id_surface = render_text_safely(f"Card {card.id}", 16, self.tokens.COLORS['card']['text'])
                surface.blit(id_surface, (x + 8, y + 8))
            except:
                # 最后的降级选项
                try:
                    font = pygame.font.Font(None, 16)
                    text = font.render(f"C{card.id}", True, self.tokens.COLORS['card']['text'])
                    surface.blit(text, (x + 8, y + 8))
                except:
                    pass  # 如果所有渲染都失败，跳过名称显示

    def render_card_cost(self, surface: pygame.Surface,
                        card: Card, position: Tuple[int, int]) -> None:
        """渲染卡牌费用"""
        x, y = position

        # 费用背景圆圈
        cost_center = (x + self.card_width - 20, y + 20)
        pygame.draw.circle(surface, self.tokens.COLORS['mana']['blue'], cost_center, 15)

        # 费用文字（使用安全文本渲染）
        try:
            cost_surface = render_text_safely(str(card.cost), 20, (255, 255, 255))
            cost_rect = cost_surface.get_rect(center=cost_center)
            surface.blit(cost_surface, cost_rect)
        except Exception as e:
            # 降级到最简单的文本渲染
            try:
                font = pygame.font.Font(None, 20)
                cost_text = font.render(str(card.cost), True, (255, 255, 255))
                cost_rect = cost_text.get_rect(center=cost_center)
                surface.blit(cost_text, cost_rect)
            except:
                pass  # 如果所有渲染都失败，跳过费用显示

    def render_card_stats(self, surface: pygame.Surface,
                         card: Card, position: Tuple[int, int]) -> None:
        """渲染卡牌属性（攻击力/生命值）"""
        x, y = position

        try:
            # 攻击力（左下角）
            attack_surface = render_text_safely(str(card.attack), 18, (0, 0, 0))
            surface.blit(attack_surface, (x + 8, y + self.card_height - 25))

            # 生命值（右下角）
            health_color = self.get_health_color(card.health)
            health_surface = render_text_safely(str(card.health), 18, health_color)
            surface.blit(health_surface, (x + self.card_width - 25, y + self.card_height - 25))
        except Exception as e:
            # 降级到最简单的文本渲染
            try:
                font = pygame.font.Font(None, 18)
                # 攻击力（左下角）
                attack_text = font.render(str(card.attack), True, (0, 0, 0))
                surface.blit(attack_text, (x + 8, y + self.card_height - 25))

                # 生命值（右下角）
                health_color = self.get_health_color(card.health)
                health_text = font.render(str(card.health), True, health_color)
                surface.blit(health_text, (x + self.card_width - 25, y + self.card_height - 25))
            except:
                pass  # 如果所有渲染都失败，跳过属性显示

    def render_card_abilities(self, surface: pygame.Surface,
                            card: Card, position: Tuple[int, int]) -> None:
        """渲染卡牌技能图标"""
        x, y = position
        skill_x = x + 8
        skill_y = y + 35
        skill_spacing = 18

        # 技能图标映射
        skill_icons = {
            'taunt': ('🛡️', self.tokens.COLORS['primary']['main']),
            'divine_shield': ('⭐', self.tokens.COLORS['mana']['gold']),
            'windfury': ('💨', self.tokens.COLORS['primary']['light']),
            'charge': ('⚡', self.tokens.COLORS['health']['full']),
            'stealth': ('👁️', self.tokens.COLORS['primary']['dark']),
        }

        skill_index = 0

        for skill, (icon, color) in skill_icons.items():
            if hasattr(card, skill) and getattr(card, skill):
                try:
                    # 使用安全文本渲染emoji
                    skill_surface = render_text_safely(icon, 14, color)
                    surface.blit(skill_surface, (skill_x + skill_index * skill_spacing, skill_y))
                    skill_index += 1
                except:
                    # 如果emoji渲染失败，使用文字替代
                    text_map = {
                        'taunt': 'T',
                        'divine_shield': 'S',
                        'windfury': 'W',
                        'charge': 'C',
                        'stealth': 'S',
                    }
                    try:
                        fallback_surface = render_text_safely(text_map.get(skill, '?'), 14, color)
                        surface.blit(fallback_surface, (skill_x + skill_index * skill_spacing, skill_y))
                        skill_index += 1
                    except:
                        # 最后的降级选项
                        try:
                            font = pygame.font.Font(None, 14)
                            text = font.render(text_map.get(skill, '?'), True, color)
                            surface.blit(text, (skill_x + skill_index * skill_spacing, skill_y))
                            skill_index += 1
                        except:
                            pass  # 如果所有渲染都失败，跳过该技能图标

    def render_card_border(self, surface: pygame.Surface,
                          card: Card, position: Tuple[int, int],
                          selected: bool = False,
                          hover: bool = False) -> None:
        """渲染卡牌边框"""
        x, y = position

        # 选择边框颜色
        if selected:
            border_color = self.tokens.COLORS['card']['selected']
            border_width = 4
        elif hover:
            border_color = self.tokens.COLORS['primary']['light']
            border_width = 3
        elif hasattr(card, 'taunt') and card.taunt:
            border_color = self.tokens.COLORS['primary']['main']
            border_width = 4
        elif hasattr(card, 'divine_shield') and card.divine_shield:
            border_color = self.tokens.COLORS['mana']['gold']
            border_width = 4
        else:
            border_color = self.tokens.COLORS['card']['border']
            border_width = self.border_width

        # 绘制边框
        pygame.draw.rect(surface, border_color,
                        (x, y, self.card_width, self.card_height),
                        border_width)

    def get_health_color(self, health: int) -> Tuple[int, int, int]:
        """根据血量返回对应颜色"""
        if health >= 7:
            return self.tokens.COLORS['health']['full']
        elif health >= 4:
            return self.tokens.COLORS['health']['half']
        else:
            return self.tokens.COLORS['health']['low']

    def get_card_color(self, state: str) -> Tuple[int, int, int]:
        """获取不同状态下的卡牌颜色"""
        color_map = {
            'normal': self.tokens.COLORS['card']['background'],
            'selected': self.tokens.COLORS['card']['selected'],
            'hover': self.tokens.COLORS['card']['hover'],
        }
        return color_map.get(state, self.tokens.COLORS['card']['background'])

    def calculate_card_rect(self, position: Tuple[int, int]) -> pygame.Rect:
        """计算卡牌的矩形区域"""
        x, y = position
        return pygame.Rect(x, y, self.card_width, self.card_height)