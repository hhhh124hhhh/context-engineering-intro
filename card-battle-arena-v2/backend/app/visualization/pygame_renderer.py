"""
Pygame可视化渲染器
用于渲染卡牌游戏的可视化界面
"""

import pygame
import sys
import os
from typing import Tuple, Optional, List
from pathlib import Path
from app.game.cards import Card


class PygameRenderer:
    """Pygame渲染器类"""
    
    def __init__(self, width: int = 1200, height: int = 800):
        """初始化渲染器"""
        self.width = width
        self.height = height
        self.screen = None
        self.clock = None
        self.font = None
        self.small_font = None
        self.large_font = None
        self.medium_font = None
        
        # 卡牌尺寸和间距
        self.card_width = 120
        self.card_height = 160
        self.card_spacing = 150  # 增加默认间距
        self.min_card_spacing = 130
        self.max_cards_per_row = 8
        
        # 游戏区域布局
        self.hand_area_y = self.height - 220
        self.player_battlefield_y = 350
        self.opponent_battlefield_y = 550
        self.player_info_y = 80
        self.opponent_info_y = 80
        self.mana_bar_y = 170
        
        # 颜色定义
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 0, 255)
        self.YELLOW = (255, 255, 0)
        self.GOLD = (255, 215, 0)  # 金色
        self.GRAY = (128, 128, 128)
        self.LIGHT_GRAY = (220, 220, 220)
        self.DARK_GRAY = (64, 64, 64)
        self.ORANGE = (255, 165, 0)
        self.PURPLE = (128, 0, 128)
        self.LIGHT_BLUE = (173, 216, 230)
        self.DARK_GREEN = (0, 100, 0)
        self.BROWN = (139, 69, 19)
        
        # 选中的卡牌
        self.selected_card = None
        self.selected_card_index = -1
        self.dragging = False
        self.drag_offset = (0, 0)
        self.drag_start_pos = (0, 0)
        
        # 键盘选择
        self.keyboard_selected_index = 0
        
        # 出牌目标
        self.play_target = None
        
        # 文本重叠防止
        self.rendered_texts = {}  # 缓存已渲染的文本
    
    def create_window(self, title: str = "卡牌对战竞技场"):
        """创建游戏窗口"""
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()
        
        # 尝试加载中文字体
        self._load_chinese_fonts()
        
        return self.screen
    
    def _load_chinese_fonts(self):
        """加载中文字体"""
        # 尝试几种常见的中文字体
        font_names = [
            "simhei.ttf",  # 黑体
            "simsun.ttc",  # 宋体
            "msyh.ttc",    # 微软雅黑
            "arialuni.ttf", # Arial Unicode
        ]
        
        # Pygame字体路径
        font_paths = [
            pygame.font.get_default_font(),
        ]
        
        # Windows系统字体路径
        if os.name == "nt":
            font_paths.extend([
                "C:/Windows/Fonts/simhei.ttf",
                "C:/Windows/Fonts/simsun.ttc",
                "C:/Windows/Fonts/msyh.ttc",
                "C:/Windows/Fonts/arialuni.ttf",
            ])
        
        # 尝试加载字体
        font_loaded = False
        for font_path in font_paths:
            try:
                if os.path.exists(font_path):
                    self.large_font = pygame.font.Font(font_path, 36)
                    self.medium_font = pygame.font.Font(font_path, 28)
                    self.font = pygame.font.Font(font_path, 24)
                    self.small_font = pygame.font.Font(font_path, 20)
                    font_loaded = True
                    break
            except:
                continue
        
        # 如果无法加载中文字体，使用系统默认字体
        if not font_loaded:
            self.large_font = pygame.font.SysFont("simhei", 36)  # 尝试黑体
            self.medium_font = pygame.font.SysFont("simhei", 28)
            self.font = pygame.font.SysFont("simhei", 24)
            self.small_font = pygame.font.SysFont("simhei", 20)
            
            # 如果还是不行，使用默认字体
            if not self.large_font:
                self.large_font = pygame.font.Font(None, 36)
                self.medium_font = pygame.font.Font(None, 28)
                self.font = pygame.font.Font(None, 24)
                self.small_font = pygame.font.Font(None, 20)
    
    def handle_events(self, game_state=None, engine=None):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_n and game_state and engine:  # 结束回合
                    engine.end_turn()
                    engine.start_turn()
                    engine.check_win_condition()
                elif event.key == pygame.K_a and game_state and engine:  # 切换AI模式
                    # 这里可以添加AI模式切换逻辑
                    pass
                elif event.key == pygame.K_d and game_state and engine:  # 抽牌
                    current = game_state.current_player
                    if current.deck:
                        card = current.deck.pop(0)
                        current.hand.append(card)
                elif event.key == pygame.K_SPACE and game_state:  # 空格键选择卡牌
                    self._select_card_with_keyboard(game_state)
                elif event.key == pygame.K_RETURN and game_state and engine:  # 回车键出牌
                    self._play_card_with_keyboard(game_state, engine)
                elif event.key == pygame.K_LEFT and game_state:  # 左箭头键
                    self._move_selection_left(game_state)
                elif event.key == pygame.K_RIGHT and game_state:  # 右箭头键
                    self._move_selection_right(game_state)
                elif event.key == pygame.K_c and game_state and engine:  # C键确认出牌
                    self._confirm_card_play(game_state, engine)
            elif event.type == pygame.VIDEORESIZE:
                # 窗口大小调整
                self.width, self.height = event.size
                self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
                # 更新布局参数
                self._update_layout()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左键点击
                    self.handle_mouse_click(event.pos, game_state, engine)
                elif event.button == 3:  # 右键点击
                    # 取消选择
                    self.selected_card = None
                    self.selected_card_index = -1
                    self.dragging = False
                    self.keyboard_selected_index = 0
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # 左键释放
                    self.handle_mouse_release(event.pos, game_state, engine)
            elif event.type == pygame.MOUSEMOTION:
                if self.dragging and self.selected_card:
                    # 拖拽卡牌
                    pass
                    
        return True
    
    def _update_layout(self):
        """更新布局参数"""
        # 根据窗口大小调整布局
        self.hand_area_y = self.height - 220
        self.player_battlefield_y = 350
        self.opponent_battlefield_y = 550
        self.player_info_y = 80
        self.opponent_info_y = 80
        self.mana_bar_y = 170
        
        # 根据窗口宽度调整卡牌间距
        self._improve_layout_spacing()
    
    def _improve_layout_spacing(self):
        """改进布局间距"""
        # 计算最优卡牌间距
        available_width = self.width - 100  # 两边各留50像素边距
        max_cards_displayed = min(self.max_cards_per_row, max(1, available_width // self.min_card_spacing))
        if max_cards_displayed > 0:
            self.card_spacing = min(self.min_card_spacing, available_width // max(1, max_cards_displayed))
        else:
            self.card_spacing = self.min_card_spacing
    
    def _select_card_with_keyboard(self, game_state):
        """使用键盘选择卡牌"""
        if not game_state or not game_state.current_player.hand:
            return
            
        current = game_state.current_player
        hand_size = len(current.hand)
        
        if hand_size > 0:
            # 确保索引在有效范围内
            self.keyboard_selected_index = max(0, min(self.keyboard_selected_index, hand_size - 1))
            self.selected_card = current.hand[self.keyboard_selected_index]
            self.selected_card_index = self.keyboard_selected_index
    
    def _move_selection_left(self, game_state):
        """向左移动选择"""
        if not game_state or not game_state.current_player.hand:
            return
            
        current = game_state.current_player
        hand_size = len(current.hand)
        
        if hand_size > 0:
            self.keyboard_selected_index = max(0, self.keyboard_selected_index - 1)
            self.selected_card = current.hand[self.keyboard_selected_index]
            self.selected_card_index = self.keyboard_selected_index
    
    def _move_selection_right(self, game_state):
        """向右移动选择"""
        if not game_state or not game_state.current_player.hand:
            return
            
        current = game_state.current_player
        hand_size = len(current.hand)
        
        if hand_size > 0:
            self.keyboard_selected_index = min(hand_size - 1, self.keyboard_selected_index + 1)
            self.selected_card = current.hand[self.keyboard_selected_index]
            self.selected_card_index = self.keyboard_selected_index
    
    def _play_card_with_keyboard(self, game_state, engine):
        """使用键盘出牌"""
        if not self.selected_card or not game_state or not engine:
            return
            
        current = game_state.current_player
        if self.can_play_card(self.selected_card, current):
            # 直接出牌，不需要额外确认
            result = engine.play_card(self.selected_card)
            if result.success:
                # 从手牌移除
                if self.selected_card in current.hand:
                    current.hand.remove(self.selected_card)
                # 取消选择
                self.selected_card = None
                self.selected_card_index = -1
                self.keyboard_selected_index = 0
                return True
        return False
    
    def _confirm_card_play(self, game_state, engine):
        """确认出牌"""
        # 这个方法现在和_play_card_with_keyboard功能相同
        return self._play_card_with_keyboard(game_state, engine)
    
    def _show_play_confirmation(self):
        """显示出牌确认提示"""
        # 这里可以添加视觉提示，比如闪烁选中的卡牌
        pass
    
    def _cancel_card_play(self):
        """取消出牌"""
        self.selected_card = None
        self.selected_card_index = -1
        self.keyboard_selected_index = 0
    
    def handle_mouse_click(self, pos: Tuple[int, int], game_state=None, engine=None):
        """处理鼠标点击事件"""
        if not game_state:
            return
            
        x, y = pos
        current = game_state.current_player
        
        # 检查是否点击了手牌
        hand_start_x = 50
        max_cards_displayed = min(len(current.hand), self.max_cards_per_row)
        
        for i, card in enumerate(current.hand[:max_cards_displayed]):
            card_x = hand_start_x + i * self.card_spacing
            card_rect = pygame.Rect(card_x, self.hand_area_y, self.card_width, self.card_height)
            
            if card_rect.collidepoint(x, y):
                # 如果已经有选中的卡牌，则尝试出牌
                if self.selected_card and self.selected_card == card:
                    # 点击已选中的卡牌，尝试出牌
                    if engine and self.can_play_card(card, current):
                        result = engine.play_card(card)
                        if result.success:
                            # 从手牌移除
                            if card in current.hand:
                                current.hand.remove(card)
                        self.selected_card = None
                        self.selected_card_index = -1
                        self.keyboard_selected_index = 0
                else:
                    # 选择新的卡牌
                    self.selected_card = card
                    self.selected_card_index = i
                    self.keyboard_selected_index = i
                    self.dragging = True
                    self.drag_start_pos = pos
                    self.drag_offset = (x - card_x, y - self.hand_area_y)
                return
        
        # 检查是否点击了战场区域（出牌目标）
        if self.selected_card:
            # 检查是否点击了对手战场（攻击目标）
            opponent_battlefield_start_x = 50
            for i, minion in enumerate(game_state.opponent.battlefield):
                minion_x = opponent_battlefield_start_x + i * self.card_spacing
                minion_rect = pygame.Rect(minion_x, self.opponent_battlefield_y, self.card_width, self.card_height)
                
                if minion_rect.collidepoint(x, y):
                    # 攻击对手随从
                    if engine:
                        result = engine.attack_with_minion(self.selected_card, minion)
                        if result.success:
                            # 取消选择
                            self.selected_card = None
                            self.selected_card_index = -1
                            self.keyboard_selected_index = 0
                            self.dragging = False
                    return
            
            # 检查是否点击了对手英雄
            opponent_hero_rect = pygame.Rect(self.width - 200, self.opponent_info_y, 150, 60)
            if opponent_hero_rect.collidepoint(x, y):
                # 攻击对手英雄
                if engine:
                    result = engine.attack_with_minion(self.selected_card, game_state.opponent.hero)
                    if result.success:
                        # 取消选择
                        self.selected_card = None
                        self.selected_card_index = -1
                        self.keyboard_selected_index = 0
                        self.dragging = False
                return
        
        # 如果没有点击手牌或目标，取消选择
        self.selected_card = None
        self.selected_card_index = -1
        self.keyboard_selected_index = 0
        self.dragging = False
    
    def handle_mouse_release(self, pos: Tuple[int, int], game_state=None, engine=None):
        """处理鼠标释放事件"""
        if self.dragging:
            self.dragging = False
            # 这里可以添加放置卡牌的逻辑
            
            # 重置选择
            self.selected_card = None
            self.selected_card_index = -1
            self.keyboard_selected_index = 0
    
    def can_play_card(self, card, player):
        """检查是否可以打出卡牌"""
        return card.cost <= player.current_mana
    
    def play_selected_card(self, game_state, engine):
        """打出选中的卡牌"""
        if not self.selected_card or not game_state or not engine:
            return False
            
        current = game_state.current_player
        if self.can_play_card(self.selected_card, current):
            result = engine.play_card(self.selected_card)
            if result.success:
                # 从手牌移除
                if self.selected_card in current.hand:
                    current.hand.remove(self.selected_card)
                # 取消选择
                self.selected_card = None
                self.selected_card_index = -1
                self.keyboard_selected_index = 0
                return True
        return False
    
    def get_card_at_position(self, pos: Tuple[int, int], hand: List[Card]) -> Optional[Tuple[Card, int]]:
        """获取指定位置的卡牌"""
        x, y = pos
        hand_start_x = 50
        
        for i, card in enumerate(hand):
            card_x = hand_start_x + i * self.card_spacing
            card_rect = pygame.Rect(card_x, self.hand_area_y, self.card_width, self.card_height)
            
            if card_rect.collidepoint(x, y):
                return (card, i)
                
        return None
    
    def calculate_card_positions(self, card_count: int, area_width: int, start_x: int = 50) -> List[int]:
        """计算卡牌位置以防止重叠"""
        if card_count == 0:
            return []
            
        # 计算合适的间距
        available_width = area_width - start_x * 2
        if card_count * self.card_width <= available_width:
            # 有足够的空间，使用标准间距
            spacing = self.card_width + 20
        else:
            # 空间不足，计算最小间距
            spacing = max(self.min_card_spacing, available_width // max(1, card_count))
        
        positions = []
        for i in range(card_count):
            positions.append(start_x + i * spacing)
        return positions
    
    def prevent_text_overlap(self, texts: List[Tuple[str, Tuple[int, int]]]) -> List[Tuple[str, Tuple[int, int]]]:
        """防止文本重叠"""
        # 简单实现：检查Y坐标重叠
        adjusted_texts = []
        for i, (text, pos) in enumerate(texts):
            x, y = pos
            # 检查是否与之前的文本重叠
            overlap = False
            for prev_text, (prev_x, prev_y) in adjusted_texts:
                if abs(y - prev_y) < 35:  # 如果Y坐标相差小于35像素，认为重叠
                    y = prev_y + 35  # 调整Y坐标
                    overlap = True
                    break
            
            adjusted_texts.append((text, (x, y)))
        return adjusted_texts
    
    def _ai_play_card(self, game_state, engine):
        """AI自动出牌"""
        current = game_state.current_player
        if current.hand:
            # AI简单出牌逻辑
            for card in current.hand[:]:
                if self.can_play_card(card, current):
                    result = engine.play_card(card)
                    if result.success:
                        if card in current.hand:
                            current.hand.remove(card)
                        break
    
    def render_card(self, card, position: Tuple[int, int], selected: bool = False, keyboard_selected: bool = False):
        """渲染单张卡牌"""
        if not self.screen:
            return
            
        x, y = position
        card_width, card_height = self.card_width, self.card_height
        
        # 卡牌背景
        card_rect = pygame.Rect(x, y, card_width, card_height)
        if selected or keyboard_selected:
            # 选中状态使用黄色背景
            color = self.YELLOW
        else:
            # 未选中状态使用白色背景
            color = self.WHITE
        pygame.draw.rect(self.screen, color, card_rect)
        pygame.draw.rect(self.screen, self.BLACK, card_rect, 2)
        
        # 卡牌边框颜色根据类型
        border_color = self.BLACK
        border_width = 2
        if hasattr(card, 'taunt') and card.taunt:
            border_color = self.BLUE  # 嘲讽蓝色边框
            border_width = 4
        elif hasattr(card, 'divine_shield') and card.divine_shield:
            border_color = self.GOLD  # 圣盾金色边框
            border_width = 4
        elif hasattr(card, 'charge') and card.charge:
            border_color = self.GREEN  # 冲锋绿色边框
            border_width = 4
        elif hasattr(card, 'windfury') and card.windfury:
            border_color = self.LIGHT_BLUE  # 风怒浅蓝色边框
            border_width = 4
        
        pygame.draw.rect(self.screen, border_color, card_rect, border_width)
        
        # 卡牌名称
        if self.small_font:
            try:
                name_text = self.small_font.render(card.name[:12], True, self.BLACK)
            except:
                # 如果中文渲染失败，使用英文名称或ID
                name_text = self.small_font.render(f"Card {card.id}", True, self.BLACK)
            if self.screen:
                self.screen.blit(name_text, (x + 5, y + 5))
        
        # 费用（右上角）
        cost_bg = pygame.Rect(x + card_width - 30, y + 5, 25, 25)
        pygame.draw.circle(self.screen, self.BLUE, (x + card_width - 17, y + 17), 12)
        if self.small_font:
            try:
                cost_text = self.small_font.render(str(card.cost), True, self.WHITE)
            except:
                cost_text = self.small_font.render(str(card.cost), True, self.WHITE)
            cost_rect = cost_text.get_rect(center=(x + card_width - 17, y + 17))
            if self.screen:
                self.screen.blit(cost_text, cost_rect)
        
        # 攻击力/生命值（左下角和右下角）
        if hasattr(card, 'attack') and hasattr(card, 'health') and self.small_font:
            # 攻击力
            try:
                attack_text = self.small_font.render(str(card.attack), True, self.BLACK)
            except:
                attack_text = self.small_font.render(str(card.attack), True, self.BLACK)
            if self.screen:
                self.screen.blit(attack_text, (x + 5, y + card_height - 25))
            
            # 生命值
            try:
                health_text = self.small_font.render(str(card.health), True, self.RED)
            except:
                health_text = self.small_font.render(str(card.health), True, self.RED)
            if self.screen:
                self.screen.blit(health_text, (x + card_width - 25, y + card_height - 25))
        
        # 特殊技能图标
        skill_x = x + 5
        skill_y = y + 30
        skill_spacing = 15
        
        skill_index = 0
        if hasattr(card, 'taunt') and card.taunt and self.small_font:
            try:
                taunt_text = self.small_font.render("🛡️", True, self.BLUE)
                if self.screen:
                    self.screen.blit(taunt_text, (skill_x + skill_index * skill_spacing, skill_y))
                skill_index += 1
            except:
                pass
        if hasattr(card, 'divine_shield') and card.divine_shield and self.small_font:
            try:
                shield_text = self.small_font.render("⭐", True, self.GOLD)
                if self.screen:
                    self.screen.blit(shield_text, (skill_x + skill_index * skill_spacing, skill_y))
                skill_index += 1
            except:
                pass
        if hasattr(card, 'windfury') and card.windfury and self.small_font:
            try:
                wind_text = self.small_font.render("💨", True, self.LIGHT_BLUE)
                if self.screen:
                    self.screen.blit(wind_text, (skill_x + skill_index * skill_spacing, skill_y))
                skill_index += 1
            except:
                pass
        if hasattr(card, 'charge') and card.charge and self.small_font:
            try:
                charge_text = self.small_font.render("⚡", True, self.GREEN)
                if self.screen:
                    self.screen.blit(charge_text, (skill_x + skill_index * skill_spacing, skill_y))
                skill_index += 1
            except:
                pass
    
    def render_game_state(self, game_state):
        """渲染游戏状态"""
        if not self.screen:
            return
            
        # 清屏
        self.screen.fill(self.LIGHT_GRAY)
        
        # 绘制标题背景
        title_bg = pygame.Rect(0, 0, self.width, 70)
        pygame.draw.rect(self.screen, self.DARK_GREEN, title_bg)
        
        # 绘制标题
        if self.large_font and self.screen:
            try:
                title_text = self.large_font.render(f"卡牌对战竞技场 - 回合 {game_state.turn_number}", True, self.WHITE)
            except:
                title_text = self.large_font.render(f"Card Battle Arena - Turn {game_state.turn_number}", True, self.WHITE)
            title_rect = title_text.get_rect(center=(self.width // 2, 35))
            self.screen.blit(title_text, title_rect)
        
        # 绘制玩家信息区域
        pygame.draw.rect(self.screen, self.LIGHT_BLUE, (0, 70, self.width // 2, 120))
        pygame.draw.rect(self.screen, self.LIGHT_BLUE, (self.width // 2, 70, self.width // 2, 120))
        
        # 绘制玩家信息
        current = game_state.current_player
        opponent = game_state.opponent
        
        # 当前玩家信息（左侧）
        if self.medium_font and self.screen:
            try:
                player_name = self.medium_font.render(f"{current.name}", True, self.BLACK)
            except:
                player_name = self.medium_font.render(f"Player", True, self.BLACK)
            self.screen.blit(player_name, (50, self.player_info_y))
        
        if self.font and self.screen:
            try:
                player_health = self.font.render(f"生命值: {current.hero.health}", True, self.RED)
            except:
                player_health = self.font.render(f"HP: {current.hero.health}", True, self.RED)
            self.screen.blit(player_health, (50, self.player_info_y + 40))
        
        # 对手玩家信息（右侧）
        if self.medium_font and self.screen:
            try:
                opponent_name = self.medium_font.render(f"{opponent.name}", True, self.BLACK)
            except:
                opponent_name = self.medium_font.render(f"Opponent", True, self.BLACK)
            self.screen.blit(opponent_name, (self.width - 200, self.opponent_info_y))
        
        if self.font and self.screen:
            try:
                opponent_health = self.font.render(f"生命值: {opponent.hero.health}", True, self.RED)
            except:
                opponent_health = self.font.render(f"HP: {opponent.hero.health}", True, self.RED)
            self.screen.blit(opponent_health, (self.width - 200, self.opponent_info_y + 40))
        
        # 法力值显示
        mana_text = f"法力值: {current.current_mana}/{current.max_mana}"
        mana_bar_width = min(250, self.width // 3)
        mana_bar_height = 25
        mana_bar_x = 50
        mana_bar_y = self.mana_bar_y
        
        # 法力值背景条
        pygame.draw.rect(self.screen, self.DARK_GRAY, 
                        (mana_bar_x, mana_bar_y, mana_bar_width, mana_bar_height))
        
        # 当前法力值条
        current_mana_width = int((current.current_mana / current.max_mana) * mana_bar_width)
        pygame.draw.rect(self.screen, self.BLUE, 
                        (mana_bar_x, mana_bar_y, current_mana_width, mana_bar_height))
        
        # 法力值文字
        if self.font and self.screen:
            try:
                mana_text_render = self.font.render(mana_text, True, self.BLACK)
            except:
                mana_text_render = self.font.render(mana_text, True, self.BLACK)
            self.screen.blit(mana_text_render, (mana_bar_x, mana_bar_y - 35))
        
        # 手牌显示区域背景
        hand_area_bg = pygame.Rect(0, self.hand_area_y - 50, self.width, 220)
        pygame.draw.rect(self.screen, self.GRAY, hand_area_bg, 3)
        
        # 手牌显示
        self._render_hand(current.hand, (50, self.hand_area_y))
        
        # 战场显示区域背景
        player_battlefield_bg = pygame.Rect(0, self.player_battlefield_y - 50, self.width, 180)
        opponent_battlefield_bg = pygame.Rect(0, self.opponent_battlefield_y - 50, self.width, 180)
        pygame.draw.rect(self.screen, self.LIGHT_BLUE, player_battlefield_bg, 2)
        pygame.draw.rect(self.screen, self.LIGHT_BLUE, opponent_battlefield_bg, 2)
        
        # 战场显示（当前玩家）
        self._render_battlefield(current.battlefield, (50, self.player_battlefield_y), "你的战场")
        
        # 战场显示（对手）
        self._render_battlefield(opponent.battlefield, (50, self.opponent_battlefield_y), "对手战场")
        
        # 操作提示区域
        instructions_bg = pygame.Rect(0, self.height - 60, self.width, 60)
        pygame.draw.rect(self.screen, self.DARK_GRAY, instructions_bg)
        
        # 操作提示
        if self.small_font and self.screen:
            try:
                instructions = self.small_font.render("鼠标: 左键选择/出牌, 右键取消 | 键盘: ←→选择, 空格选中, 回车出牌, C确认 | 按键: N-结束回合, A-AI出牌, D-抽牌, ESC-退出", True, self.WHITE)
            except:
                instructions = self.small_font.render("Mouse: Left-Select/Play, Right-Cancel | Keys: ←→Select, Space-Select, Enter-Play, C-Confirm | Keys: N-End Turn, A-AI Play, D-Draw, ESC-Exit", True, self.WHITE)
            instructions_rect = instructions.get_rect(center=(self.width // 2, self.height - 30))
            self.screen.blit(instructions, instructions_rect)
        
        # 更新显示
        pygame.display.flip()
    
    def _render_hand(self, hand, position: Tuple[int, int]):
        """渲染手牌"""
        x, y = position
        if self.font and self.screen:
            try:
                hand_title = self.font.render("手牌:", True, self.BLACK)
            except:
                hand_title = self.font.render("Hand:", True, self.BLACK)
            self.screen.blit(hand_title, (x, y - 40))
        
        # 计算手牌位置以防止重叠
        max_displayed_cards = min(len(hand), self.max_cards_per_row)
        displayed_hand = hand[:max_displayed_cards]
        
        for i, card in enumerate(displayed_hand):
            card_x = x + i * self.card_spacing
            # 如果是选中的卡牌，稍微抬高一些
            card_y = y - 25 if (self.selected_card and i == self.selected_card_index) else y
            is_keyboard_selected = (i == self.keyboard_selected_index)
            self.render_card(card, (card_x, card_y), i == self.selected_card_index, is_keyboard_selected)
    
    def _render_battlefield(self, battlefield, position: Tuple[int, int], title: str):
        """渲染战场"""
        x, y = position
        if self.font and self.screen:
            try:
                battlefield_title = self.font.render(title, True, self.BLACK)
            except:
                battlefield_title = self.font.render("Battlefield", True, self.BLACK)
            self.screen.blit(battlefield_title, (x, y - 40))
        
        # 计算战场卡牌位置
        max_displayed_cards = min(len(battlefield), self.max_cards_per_row)
        displayed_battlefield = battlefield[:max_displayed_cards]
        
        for i, card in enumerate(displayed_battlefield):
            card_x = x + i * self.card_spacing
            self.render_card(card, (card_x, y))
    
    def update_display(self):
        """更新显示"""
        if self.clock:
            self.clock.tick(60)

    def render_ai_thinking(self, is_thinking: bool = False):
        """渲染AI思考状态"""
        if not self.screen:
            return

        if is_thinking:
            # 显示AI思考中的提示
            font = getattr(self, 'small_font', None)
            if font:
                try:
                    thinking_text = font.render("🤖 AI思考中...", True, self.RED)
                    thinking_rect = thinking_text.get_rect(center=(self.width // 2, 200))
                    self.screen.blit(thinking_text, thinking_rect)
                except:
                    pass
        else:
            # 清除AI思考提示（通过重新渲染游戏状态）
            pass

    def highlight_card(self, card, highlight: bool = True):
        """高亮显示卡牌"""
        # 这个方法可以在渲染时被调用来高亮特定的卡牌
        # 实际的高亮效果需要在render_card方法中实现
        pass

    def show_ai_action_result(self, action: str, card_name: str = None, success: bool = True):
        """显示AI操作结果"""
        # 可以在控制台显示或界面上显示AI操作结果
        if success:
            print(f"✅ AI {action}: {card_name}")
        else:
            print(f"❌ AI {action} 失败: {card_name}")