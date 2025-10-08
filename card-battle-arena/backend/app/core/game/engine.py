from typing import Dict, List, Optional, Any, Tuple
import random
import structlog
from datetime import datetime, timezone

from app.core.game.state import GameState, Player, Card, CardType, TurnPhase
from app.core.game.card_effects import CardEffectProcessor
from app.models.card import Card as CardModel
from app.models.user import User as UserModel
from app.models.game import Game as GameModel
from app.database.postgres import AsyncSessionLocal

logger = structlog.get_logger()


class GameEngine:
    """游戏引擎核心"""

    def __init__(self):
        self.effect_processor = CardEffectProcessor()
        self.active_games: Dict[str, GameState] = {}
        self.card_database: Dict[int, CardModel] = {}

    async def initialize(self):
        """初始化游戏引擎"""
        # 加载卡牌数据库
        await self._load_card_database()
        logger.info("Game engine initialized")

    async def create_game(
        self,
        player1_user: UserModel,
        player2_user: UserModel,
        player1_deck: List[CardModel],
        player2_deck: List[CardModel],
        game_settings: Dict[str, Any] = None
    ) -> GameState:
        """创建新游戏"""
        game_settings = game_settings or {}

        # 创建玩家
        player1 = Player(
            user_id=player1_user.id,
            username=player1_user.username,
            player_number=1
        )
        player2 = Player(
            user_id=player2_user.id,
            username=player2_user.username,
            player_number=2
        )

        # 转换卡牌数据
        player1.deck = [self._model_to_card(card_model) for card_model in player1_deck]
        player2.deck = [self._model_to_card(card_model) for card_model in player2_deck]

        # 洗牌
        player1.shuffle_deck()
        player2.shuffle_deck()

        # 抽起始手牌
        for _ in range(3):  # 起始手牌3张
            card1 = player1.draw_card()
            card2 = player2.draw_card()
            if card1:
                player1.hand.append(card1)
            if card2:
                player2.hand.append(card2)

        # 创建游戏状态
        game_state = GameState(
            game_id=game_settings.get("game_id", ""),
            player1=player1,
            player2=player2,
            turn_time_limit=game_settings.get("turn_time_limit", 90),
            format_type=game_settings.get("format_type", "standard"),
            game_mode=game_settings.get("game_mode", "ranked")
        )

        # 设置起手回合
        game_state.phase = "mulligan"
        game_state.started_at = datetime.now(timezone.utc)

        # 保存到活跃游戏列表
        self.active_games[game_state.game_id] = game_state

        logger.info("Game created", game_id=game_state.game_id, player1=player1_user.id, player2=player2_user.id)
        return game_state

    async def play_card(
        self,
        game_id: str,
        player_id: int,
        card_instance_id: str,
        target_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """出牌"""
        game_state = self.active_games.get(game_id)
        if not game_state:
            raise ValueError("Game not found")

        player = game_state.get_player(player_id)
        if not player:
            raise ValueError("Player not in game")

        if game_state.current_player.user_id != player_id:
            raise ValueError("Not your turn")

        # 找到要出的牌
        card = None
        for c in player.hand:
            if c.instance_id == card_instance_id:
                card = c
                break

        if not card:
            raise ValueError("Card not in hand")

        # 验证出牌合法性
        if not self._validate_play(game_state, player, card, target_data):
            raise ValueError("Invalid play")

        # 执行出牌
        result = await self._execute_play(game_state, player, card, target_data)

        # 记录动作
        game_state._add_action("card_played", {
            "card_id": card.id,
            "card_name": card.name,
            "target": target_data,
            "result": result
        })

        return result

    async def attack(
        self,
        game_id: str,
        player_id: int,
        attacker_instance_id: str,
        target_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """攻击"""
        game_state = self.active_games.get(game_id)
        if not game_state:
            raise ValueError("Game not found")

        player = game_state.get_player(player_id)
        if not player:
            raise ValueError("Player not in game")

        if game_state.current_player.user_id != player_id:
            raise ValueError("Not your turn")

        # 找到攻击者
        attacker = None
        for c in player.battlefield:
            if c.instance_id == attacker_instance_id:
                attacker = c
                break

        if not attacker:
            raise ValueError("Attacker not on battlefield")

        # 验证攻击合法性
        if not self._validate_attack(game_state, player, attacker, target_data):
            raise ValueError("Invalid attack")

        # 执行攻击
        result = await self._execute_attack(game_state, player, attacker, target_data)

        # 记录动作
        game_state._add_action("attack", {
            "attacker": attacker.instance_id,
            "target": target_data,
            "result": result
        })

        return result

    async def use_hero_power(
        self,
        game_id: str,
        player_id: int,
        target_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """使用英雄技能"""
        game_state = self.active_games.get(game_id)
        if not game_state:
            raise ValueError("Game not found")

        player = game_state.get_player(player_id)
        if not player:
            raise ValueError("Player not in game")

        if game_state.current_player.user_id != player_id:
            raise ValueError("Not your turn")

        if not player.hero_power:
            raise ValueError("No hero power available")

        # 验证英雄技能使用
        if not self._validate_hero_power(game_state, player, target_data):
            raise ValueError("Cannot use hero power")

        # 执行英雄技能
        result = await self._execute_hero_power(game_state, player, target_data)

        # 记录动作
        game_state._add_action("hero_power_used", {
            "hero_power": player.hero_power.name,
            "target": target_data,
            "result": result
        })

        return result

    async def end_turn(self, game_id: str, player_id: int) -> Dict[str, Any]:
        """结束回合"""
        game_state = self.active_games.get(game_id)
        if not game_state:
            raise ValueError("Game not found")

        player = game_state.get_player(player_id)
        if not player:
            raise ValueError("Player not in game")

        if game_state.current_player.user_id != player_id:
            raise ValueError("Not your turn")

        # 结束当前回合
        game_state.switch_turn()

        # 检查游戏是否结束
        if game_state.is_game_over():
            winner = game_state.get_winner()
            await self._finish_game(game_state, winner)

        return {
            "success": True,
            "new_player": game_state.current_player_number,
            "turn_number": game_state.turn_number,
            "is_game_over": game_state.is_game_over(),
            "winner": winner.user_id if winner else None
        }

    async def concede(self, game_id: str, player_id: int) -> Dict[str, Any]:
        """投降"""
        game_state = self.active_games.get(game_id)
        if not game_state:
            raise ValueError("Game not found")

        player = game_state.get_player(player_id)
        if not player:
            raise ValueError("Player not in game")

        # 设置投降状态
        player.has_conceded = True

        # 结束游戏
        winner = game_state.get_winner()
        await self._finish_game(game_state, winner)

        return {
            "success": True,
            "winner": winner.user_id if winner else None,
            "reason": "concede"
        }

    def get_game_state(self, game_id: str, player_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """获取游戏状态"""
        game_state = self.active_games.get(game_id)
        if not game_state:
            return None

        # 构建状态数据
        state_data = game_state.to_dict()

        # 如果指定了玩家，添加该玩家的私有信息
        if player_id:
            player = game_state.get_player(player_id)
            if player:
                state_data["current_player_hand"] = [
                    {
                        "instance_id": card.instance_id,
                        "id": card.id,
                        "name": card.name,
                        "cost": card.effective_cost,
                        "attack": card.effective_attack,
                        "defense": card.effective_defense,
                        "mechanics": card.mechanics,
                        "location": card.location
                    }
                    for card in player.hand
                ]
                state_data["current_player_mana_available"] = player.available_mana

        return state_data

    async def _load_card_database(self):
        """加载卡牌数据库"""
        async with AsyncSessionLocal() as db:
            result = await db.execute("SELECT * FROM cards")
            cards = result.fetchall()
            for card_row in cards:
                card_model = CardModel(
                    id=card_row.id,
                    name=card_row.name,
                    cost=card_row.cost,
                    attack=card_row.attack,
                    defense=card_row.defense,
                    card_type=card_row.card_type,
                    rarity=card_row.rarity,
                    card_class=card_row.card_class,
                    mechanics=card_row.mechanics or []
                )
                self.card_database[card_row.id] = card_model

    def _model_to_card(self, card_model: CardModel) -> Card:
        """将数据库模型转换为游戏卡牌"""
        return Card(
            id=card_model.id,
            instance_id="",  # 将在游戏中生成
            name=card_model.name,
            card_type=CardType(card_model.card_type),
            rarity=CardRarity(card_model.rarity),
            card_class=CardClass(card_model.card_class),
            cost=card_model.cost,
            attack=card_model.attack,
            defense=card_model.defense,
            mechanics=card_model.mechanics or []
        )

    def _validate_play(
        self,
        game_state: GameState,
        player: Player,
        card: Card,
        target_data: Optional[Dict[str, Any]]
    ) -> bool:
        """验证出牌合法性"""
        # 检查法力值
        if card.effective_cost > player.available_mana:
            return False

        # 检查随从数量限制
        if card.is_minion and len(player.battlefield) >= 7:
            return False

        # 检查武器限制
        if card.is_weapon and player.weapon is not None:
            return False

        # 检查目标要求
        if card.is_spell and target_data:
            # 这里可以添加更多的目标验证逻辑
            pass

        return True

    def _validate_attack(
        self,
        game_state: GameState,
        player: Player,
        attacker: Card,
        target_data: Dict[str, Any]
    ) -> bool:
        """验证攻击合法性"""
        # 检查攻击者是否可以攻击
        if not attacker.can_attack():
            return False

        # 检查目标类型
        target_type = target_data.get("type")
        target_id = target_data.get("id")

        if target_type == "minion":
            # 查找目标随从
            opponent = game_state.opponent
            target = None
            for minion in opponent.battlefield:
                if minion.instance_id == target_id:
                    target = minion
                    break

            if not target:
                return False

            # 检查随从是否有嘲讽（如果没有，不能攻击）
            if "taunt" in target.mechanics:
                # 检查是否有其他嘲讽随从
                for minion in opponent.battlefield:
                    if minion.instance_id != target_id and "taunt" in minion.mechanics:
                        return False

        elif target_type == "hero":
            # 检查是否有嘲讽随从
            opponent = game_state.opponent
            for minion in opponent.battlefield:
                if "taunt" in minion.mechanics:
                    return False

        return True

    def _validate_hero_power(
        self,
        game_state: GameState,
        player: Player,
        target_data: Optional[Dict[str, Any]]
    ) -> bool:
        """验证英雄技能使用"""
        if not player.hero_power:
            return False

        # 检查法力值
        if player.hero_power.effective_cost > player.available_mana:
            return False

        # 这里可以添加更多英雄技能验证逻辑
        return True

    async def _execute_play(
        self,
        game_state: GameState,
        player: Player,
        card: Card,
        target_data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """执行出牌"""
        # 扣除法力值
        player.play_card(card)

        # 根据卡牌类型执行不同逻辑
        if card.is_minion:
            result = await self._play_minion(game_state, player, card, target_data)
        elif card.is_spell:
            result = await self._play_spell(game_state, player, card, target_data)
        elif card.is_weapon:
            result = await self._play_weapon(game_state, player, card, target_data)
        else:
            result = {"success": False, "error": "Unknown card type"}

        return result

    async def _play_minion(
        self,
        game_state: GameState,
        player: Player,
        card: Card,
        target_data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """打出随从"""
        # 将随从放入战场
        player.battlefield.append(card)
        card.location = "battlefield"
        card.position = len(player.battlefield) - 1

        # 处理战吼效果
        if "battlecry" in card.mechanics:
            # 这里应该调用卡牌效果处理器
            await self.effect_processor.process_battlecry(card, game_state, player, target_data)

        return {
            "success": True,
            "card": card.instance_id,
            "location": "battlefield",
            "position": card.position
        }

    async def _play_spell(
        self,
        game_state: GameState,
        player: Player,
        card: Card,
        target_data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """打出法术"""
        # 处理法术效果
        await self.effect_processor.process_spell(card, game_state, player, target_data)

        # 法术进入墓地
        player.graveyard.append(card)
        card.location = "graveyard"

        return {
            "success": True,
            "card": card.instance_id,
            "location": "graveyard"
        }

    async def _play_weapon(
        self,
        game_state: GameState,
        player: Player,
        card: Card,
        target_data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """装备武器"""
        # 如果已有武器，摧毁旧武器
        if player.weapon:
            player.weapon.location = "graveyard"
            player.graveyard.append(player.weapon)

        # 装备新武器
        player.weapon = card
        card.location = "weapon"

        return {
            "success": True,
            "card": card.instance_id,
            "location": "weapon"
        }

    async def _execute_attack(
        self,
        game_state: GameState,
        player: Player,
        attacker: Card,
        target_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行攻击"""
        target_type = target_data.get("type")
        target_id = target_data.get("id")

        # 增加攻击次数
        attacker.attack_count += 1

        if target_type == "minion":
            # 攻击随从
            opponent = game_state.opponent
            target = None
            for minion in opponent.battlefield:
                if minion.instance_id == target_id:
                    target = minion
                    break

            if target:
                # 计算伤害
                damage_to_target = attacker.effective_attack
                damage_to_attacker = target.effective_attack

                # 造成伤害
                target.current_defense -= damage_to_target
                attacker.current_defense -= damage_to_attacker

                # 检查死亡
                if target.effective_defense <= 0:
                    opponent.battlefield.remove(target)
                    target.location = "graveyard"
                    opponent.graveyard.append(target)

                if attacker.effective_defense <= 0:
                    player.battlefield.remove(attacker)
                    attacker.location = "graveyard"
                    player.graveyard.append(attacker)

                return {
                    "success": True,
                    "damage_dealt": damage_to_target,
                    "damage_taken": damage_to_attacker,
                    "target_survived": target.effective_defense > 0,
                    "attacker_survived": attacker.effective_defense > 0
                }

        elif target_type == "hero":
            # 攻击英雄
            opponent = game_state.opponent
            damage = attacker.effective_attack
            actual_damage = opponent.take_damage(damage)

            return {
                "success": True,
                "damage_dealt": actual_damage,
                "target_health": opponent.health,
                "target_armor": opponent.armor
            }

        return {"success": False, "error": "Invalid target"}

    async def _execute_hero_power(
        self,
        game_state: GameState,
        player: Player,
        target_data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """执行英雄技能"""
        # 扣除法力值
        player.mana -= player.hero_power.effective_cost

        # 处理英雄技能效果
        await self.effect_processor.process_hero_power(player.hero_power, game_state, player, target_data)

        return {
            "success": True,
            "hero_power": player.hero_power.name,
            "mana_remaining": player.mana
        }

    async def _finish_game(self, game_state: GameState, winner: Player):
        """结束游戏"""
        # 这里应该保存游戏结果到数据库
        # 计算ELO变化等
        logger.info("Game finished", game_id=game_state.game_id, winner=winner.user_id)

        # 从活跃游戏列表中移除
        if game_state.game_id in self.active_games:
            del self.active_games[game_state.game_id]


# 全局游戏引擎实例
game_engine = GameEngine()