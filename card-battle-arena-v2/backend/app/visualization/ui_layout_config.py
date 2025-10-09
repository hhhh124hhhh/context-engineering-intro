"""
UI布局配置文件
基于UI布局分析与改进方案的具体实施参数
"""

from typing import Dict, Tuple

# 主要UI布局配置
UI_LAYOUT_CONFIG = {
    "window": {
        "width": 1200,
        "height": 800,
        "title": "Card Battle Arena"
    },

    "regions": {
        "hud": {
            "position": (0, 0),
            "size": (1200, 80),
            "background_color": (45, 45, 48),
            "border_color": (30, 30, 32),
            "border_width": 2
        },

        "opponent_info": {
            "position": (50, 90),
            "size": (1100, 70),
            "background_color": (60, 60, 65),
            "border_color": (40, 40, 44),
            "border_width": 1,
            "corner_radius": 8
        },

        "opponent_battlefield": {
            "position": (50, 170),
            "size": (1100, 170),
            "background_color": (56, 34, 18),
            "border_color": (40, 25, 12),
            "border_width": 2,
            "corner_radius": 12
        },

        "player_battlefield": {
            "position": (50, 350),
            "size": (1100, 170),
            "background_color": (56, 34, 18),
            "border_color": (40, 25, 12),
            "border_width": 2,
            "corner_radius": 12
        },

        "game_controls": {
            "position": (50, 530),
            "size": (1100, 50),
            "background_color": (40, 40, 44),
            "border_color": (30, 30, 32),
            "border_width": 1,
            "corner_radius": 6
        },

        "player_hand": {
            "position": (50, 590),
            "size": (1100, 210),
            "background_color": (35, 35, 38),
            "border_color": (25, 25, 28),
            "border_width": 2,
            "corner_radius": 12
        }
    },

    "components": {
        "end_turn_button": {
            "position": (1050, 540),
            "size": (120, 40),
            "text": "结束回合",
            "background_color": (100, 149, 237),
            "hover_color": (130, 177, 255),
            "pressed_color": (70, 119, 197),
            "disabled_color": (80, 80, 80),
            "text_color": (255, 255, 255),
            "corner_radius": 6,
            "border_width": 2,
            "font_size": 16,
            "enabled": True
        },

        "turn_indicator": {
            "position": (500, 20),
            "size": (200, 40),
            "text_format": "回合 {turn} - {player}",
            "background_color": (50, 50, 55),
            "text_color": (255, 255, 255),
            "corner_radius": 20,
            "font_size": 18,
            "border_width": 1
        },

        "action_hints": {
            "position": (50, 540),
            "size": (300, 40),
            "text": "拖拽卡牌到战场或点击使用",
            "background_color": (45, 45, 48),
            "text_color": (200, 200, 200),
            "corner_radius": 6,
            "font_size": 14
        },

        "health_bar": {
            "position": (100, 100),
            "size": (200, 20),
            "background_color": (64, 64, 64),
            "border_color": (32, 32, 32),
            "border_width": 2,
            "corner_radius": 10,
            "text_color": (255, 255, 255),
            "font_size": 12
        },

        "mana_crystals": {
            "position": (300, 100),
            "crystal_size": 20,
            "crystal_spacing": 25,
            "full_color": (0, 119, 190),
            "empty_color": (128, 128, 128),
            "border_color": (0, 0, 0),
            "border_width": 2
        }
    },

    "card": {
        "dimensions": (120, 160),
        "corner_radius": 8,
        "border_width": 2,
        "border_color": (64, 64, 64),
        "background_color": (248, 248, 250),
        "text_color": (0, 0, 0),

        # 手牌区域特殊配置
        "hand": {
            "hover_height": 180,  # 悬停时高度
            "drag_height": 200,   # 拖拽时高度
            "selected_y_offset": -20,  # 选中时的Y轴偏移
            "spacing": {
                "minimum": 20,
                "maximum": 40,
                "default": 30
            }
        },

        # 动画配置
        "animation": {
            "hover_speed": 0.1,
            "drag_speed": 0.05,
            "play_speed": 0.3,
            "draw_speed": 0.2
        }
    },

    "text": {
        "font_sizes": {
            "title": 24,
            "heading": 18,
            "body": 14,
            "caption": 12,
            "button": 16
        },
        "colors": {
            "primary": (255, 255, 255),
            "secondary": (200, 200, 200),
            "accent": (100, 149, 237),
            "warning": (255, 165, 0),
            "error": (255, 0, 0),
            "success": (0, 255, 0)
        }
    },

    "spacing": {
        "small": 8,
        "medium": 16,
        "large": 24,
        "xlarge": 32,
        "margin": 50  # 主边距
    },

    # 验证标准
    "validation": {
        "min_touch_target": 44,  # 最小触摸目标尺寸
        "min_card_space": 50,    # 卡牌最小操作空间
        "min_text_size": 12,     # 最小文字尺寸
        "max_overlap_ratio": 0.1 # 最大重叠比例
    }
}

# 响应式断点配置
RESPONSIVE_BREAKPOINTS = {
    "mobile": 768,
    "tablet": 1024,
    "desktop": 1200,
    "large": 1600
}

# 颜色主题
COLOR_THEME = {
    "background": {
        "primary": (45, 45, 48),
        "secondary": (35, 35, 38),
        "accent": (56, 34, 18)
    },
    "ui": {
        "button": (100, 149, 237),
        "button_hover": (130, 177, 255),
        "button_pressed": (70, 119, 197),
        "button_disabled": (80, 80, 80)
    },
    "text": {
        "primary": (255, 255, 255),
        "secondary": (200, 200, 200),
        "accent": (100, 149, 237)
    },
    "status": {
        "health_full": (0, 255, 0),
        "health_half": (255, 255, 0),
        "health_low": (255, 0, 0),
        "mana_full": (0, 119, 190),
        "mana_empty": (128, 128, 128)
    }
}

def get_region_config(region_name: str) -> Dict:
    """获取指定区域的配置"""
    return UI_LAYOUT_CONFIG["regions"].get(region_name, {})

def get_component_config(component_name: str) -> Dict:
    """获取指定组件的配置"""
    return UI_LAYOUT_CONFIG["components"].get(component_name, {})

def validate_layout(layout_config: Dict) -> bool:
    """验证布局配置是否符合标准"""
    validation = UI_LAYOUT_CONFIG["validation"]

    # 检查手牌区域高度
    hand_config = get_region_config("player_hand")
    if hand_config:
        hand_height = hand_config["size"][1]
        card_height = UI_LAYOUT_CONFIG["card"]["dimensions"][1]
        min_space = validation["min_card_space"]

        if hand_height < card_height + min_space:
            print(f"警告: 手牌区域高度 {hand_height}px 小于推荐值 {card_height + min_space}px")
            return False

    return True

def calculate_card_positions(card_count: int, region_name: str) -> list:
    """计算卡牌在指定区域的位置"""
    region_config = get_region_config(region_name)
    if not region_config:
        return []

    region_pos = region_config["position"]
    region_size = region_config["size"]
    card_config = UI_LAYOUT_CONFIG["card"]
    card_dims = card_config["dimensions"]
    spacing = card_config["hand"]["spacing"]["default"]

    # 计算总宽度
    total_width = card_count * card_dims[0] + (card_count - 1) * spacing

    # 如果总宽度超过区域宽度，调整间距
    if total_width > region_size[0]:
        spacing = max(card_config["hand"]["spacing"]["minimum"],
                     (region_size[0] - card_count * card_dims[0]) // (card_count - 1))
        total_width = card_count * card_dims[0] + (card_count - 1) * spacing

    # 计算起始X坐标（居中对齐）
    start_x = region_pos[0] + (region_size[0] - total_width) // 2
    start_y = region_pos[1] + (region_size[1] - card_dims[1]) // 2

    positions = []
    for i in range(card_count):
        x = start_x + i * (card_dims[0] + spacing)
        y = start_y
        positions.append((x, y))

    return positions

if __name__ == "__main__":
    # 验证配置
    print("UI布局配置验证:")
    is_valid = validate_layout(UI_LAYOUT_CONFIG)
    print(f"配置有效性: {'✅ 通过' if is_valid else '❌ 失败'}")

    # 示例：计算5张卡牌在手牌区域的位置
    positions = calculate_card_positions(5, "player_hand")
    print(f"\n5张卡牌在手牌区域的位置:")
    for i, pos in enumerate(positions):
        print(f"卡牌 {i+1}: ({pos[0]}, {pos[1]})")