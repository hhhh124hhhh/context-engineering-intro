# 🧮 TDD开发过程演示

## 📋 TDD循环演示
真正的TDD是：**红 → 绿 → 重构** 的循环

### 当前状态
我们已经有了一些基础的测试用例，现在来演示完整的TDD开发新功能的过程。

## 🎯 新功能演示：英雄技能

让我们为游戏添加英雄技能功能，完整演示TDD流程。

## 🔴 第1步：写失败的测试（RED）

```python
# 在 tests/test_hero_power.py 中添加
def test_hero_power_usage():
    """测试英雄技能使用"""
    engine = GameEngine()
    game = engine.create_game("Player1", "Player2")

    current = game.current_player

    # 初始状态：没有使用过英雄技能
    assert not current.used_hero_power
    assert current.current_mana >= 2  # 需要至少2点法力值

    # 使用英雄技能
    result = engine.use_hero_power()

    # 验证结果
    assert result.success
    assert current.used_hero_power
    assert current.current_mana == current.max_mana - 2

    # 不能重复使用
    result2 = engine.use_hero_power()
    assert not result2.success
    assert "already used" in result2.error.lower()
```

运行这个测试：
```bash
# 应该失败，因为use_hero_power方法不存在
AttributeError: 'GameEngine' object has no attribute 'use_hero_power'
```

## 🟢 第2步：最小实现（GREEN）

现在只写足够的代码让测试通过：

```python
# 在 app/game/engine.py 中添加
def use_hero_power(self) -> PlayResult:
    """使用英雄技能"""
    game = self._get_current_game()
    if not game:
        return PlayResult(False, error="No active game")

    current = game.current_player

    # 检查是否已经使用过
    if current.used_hero_power:
        return PlayResult(False, error="Hero power already used this turn")

    # 检查法力值是否足够
    if current.current_mana < 2:
        return PlayResult(False, error="Insufficient mana for hero power")

    # 消耗法力值并标记已使用
    current.current_mana -= 2
    current.used_hero_power = True

    # 简单的英雄技能效果：造成1点伤害
    game.opponent.hero.health -= 1

    return PlayResult(True, "Hero power used successfully")
```

运行测试：应该通过！

## 🔄 第3步：重构（REFACTOR）

现在代码可以工作了，让我们重构使其更清晰：

```python
def use_hero_power(self) -> PlayResult:
    """使用英雄技能"""
    game = self._get_current_game()
    if not game:
        return PlayResult(False, error="No active game")

    current = game.current_player

    # 验证使用条件
    if current.used_hero_power:
        return PlayResult(False, error="Hero power already used this turn")

    if current.current_mana < 2:
        return PlayResult(False, error="Insufficient mana for hero power")

    # 消耗法力值
    current.current_mana -= 2
    current.used_hero_power = True

    # 应用英雄技能效果
    self._apply_hero_power_effect(current, game.opponent)

    # 记录历史
    game.history.append({
        'action': 'use_hero_power',
        'player': current.player_id,
        'cost': 2
    })

    return PlayResult(True, "Hero power used successfully")

def _apply_hero_power_effect(self, player: Player, opponent: Player):
    """应用英雄技能效果"""
    # 基础英雄技能：造成1点伤害
    opponent.hero.health -= 1

    # 记录到历史
    print(f"{player.name} 使用英雄技能，造成1点伤害")
```

## 📋 完整TDD演示

### 新功能：卡牌搜索

#### 🔴 RED: 写失败的测试
```python
def test_card_search():
    """测试卡牌搜索功能"""
    engine = GameEngine()
    game = engine.create_game("Player1", "Player2")

    current = game.current_player

    # 初始手牌有3张卡
    assert len(current.hand) == 3

    # 搜索1费卡牌
    found_cards = engine.search_cards(cost=1)

    # 应该找到1费卡牌
    assert len(found_cards) > 0
    assert all(card.cost == 1 for card in found_cards)

    # 搜索不存在的卡牌类型
    found_none = engine.search_cards(card_type="nonexistent")
    assert len(found_none) == 0
```

#### 🟢 GREEN: 最小实现
```python
def search_cards(self, cost=None, card_type=None, name=None):
    """搜索手牌中的卡牌"""
    game = self._get_current_game()
    if not game:
        return []

    current = game.current_player
    results = []

    for card in current.hand:
        match = True

        if cost is not None and card.cost != cost:
            match = False
        if card_type is not None and card.card_type != card_type:
            match = False
        if name is not None and name.lower() not in card.name.lower():
            match = False

        if match:
            results.append(card)

    return results
```

#### 🔄 REFACTOR: 添加更多功能
```python
def search_cards(self, cost=None, card_type=None, name=None, min_attack=None, max_attack=None):
    """搜索手牌中的卡牌（增强版）"""
    game = self._get_current_game()
    if not game:
        return []

    current = game.current_player
    results = []

    for card in current.hand:
        if self._card_matches_criteria(card, cost, card_type, name, min_attack, max_attack):
            results.append(card)

    return results

def _card_matches_criteria(self, card, cost, card_type, name, min_attack, max_attack):
    """检查卡牌是否匹配搜索条件"""
    if cost is not None and card.cost != cost:
        return False
    if card_type is not None and card.card_type != card_type:
        return False
    if name is not None and name.lower() not in card.name.lower():
        return False
    if min_attack is not None and card.attack < min_attack:
        return False
    if max_attack is not None and card.attack > max_attack:
        return False
    return True
```

## 📚 TDD的实际价值

### 1. 设计清晰
- **测试即文档**: 测试用例定义了功能的预期行为
- **接口简洁**: 为满足测试而设计的接口自然简洁
- **职责明确**: 每个方法都有明确的单一职责

### 2. 质量保证
- **持续验证**: 每次修改都能立即验证
- **回归保护**: 修改不会破坏已有功能
- **边界条件**: 测试覆盖各种边界情况

### 3. 开发效率
- **快速反馈**: 编写代码后立即知道是否成功
- **问题定位**: 错误信息精确定位问题
- **重构信心**: 有测试保护，可以安全重构

## 🎭 下一步演示

现在您可以要求我演示：
1. **新卡牌效果**：如冲锋、圣盾、嘲讽等
2. **AI对手**：简单的决策逻辑
3. **游戏状态持久化**：保存和加载游戏
4. **API接口**：HTTP端点设计

每个功能都将遵循完整的TDD循环：**失败测试 → 最小实现 → 重构优化**。

---
**这就是真正的TDD！每个功能都经过精心设计和验证。**