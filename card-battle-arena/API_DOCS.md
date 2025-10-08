# 卡牌对战竞技场 - API 文档

## 概述

卡牌对战竞技场后端API基于FastAPI框架构建，提供RESTful API和WebSocket实时通信接口。

## 基础信息

- **基础URL**: `http://localhost:8000/api`
- **API版本**: v1
- **认证方式**: JWT Bearer Token
- **数据格式**: JSON
- **字符编码**: UTF-8

## 认证

### 用户注册
```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "player123",
  "email": "player@example.com",
  "password": "securepassword"
}
```

**响应**:
```json
{
  "message": "用户注册成功",
  "user": {
    "id": 1,
    "username": "player123",
    "email": "player@example.com",
    "rating": 1000,
    "created_at": "2024-10-07T12:00:00Z"
  }
}
```

### 用户登录
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "player123",
  "password": "securepassword"
}
```

**响应**:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 1,
    "username": "player123",
    "rating": 1000
  }
}
```

### 刷新令牌
```http
POST /api/auth/refresh
Authorization: Bearer <refresh_token>
```

## 用户管理

### 获取用户信息
```http
GET /api/users/me
Authorization: Bearer <access_token>
```

### 更新用户信息
```http
PUT /api/users/me
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "email": "newemail@example.com",
  "avatar": "avatar_url"
}
```

### 获取用户统计
```http
GET /api/users/me/stats
Authorization: Bearer <access_token>
```

**响应**:
```json
{
  "games_played": 42,
  "wins": 25,
  "losses": 17,
  "win_rate": 0.595,
  "current_rating": 1150,
  "peak_rating": 1200
}
```

## 卡牌系统

### 获取所有卡牌
```http
GET /api/cards?page=1&limit=20&class=mage&rarity=legendary
```

**查询参数**:
- `page`: 页码 (默认: 1)
- `limit`: 每页数量 (默认: 20, 最大: 100)
- `class`: 职业过滤 (warrior, mage, hunter, etc.)
- `rarity`: 稀有度过滤 (common, rare, epic, legendary)
- `cost`: 法力值过滤
- `type`: 卡牌类型过滤 (minion, spell, weapon)
- `search`: 搜索关键词

**响应**:
```json
{
  "cards": [
    {
      "id": "fireball_001",
      "name": "火球术",
      "description": "造成4点伤害",
      "cost": 4,
      "class": "mage",
      "rarity": "common",
      "type": "spell",
      "image_url": "/images/cards/fireball.png"
    }
  ],
  "total": 200,
  "page": 1,
  "limit": 20,
  "pages": 10
}
```

### 获取单张卡牌
```http
GET /api/cards/{card_id}
```

### 获取卡组
```http
GET /api/decks
Authorization: Bearer <access_token>
```

**响应**:
```json
{
  "decks": [
    {
      "id": 1,
      "name": "法师控制卡组",
      "class": "mage",
      "cards": [
        {
          "id": "fireball_001",
          "count": 2
        }
      ],
      "created_at": "2024-10-07T12:00:00Z",
      "updated_at": "2024-10-07T12:00:00Z"
    }
  ]
}
```

### 创建卡组
```http
POST /api/decks
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "新卡组",
  "class": "mage",
  "cards": [
    {"card_id": "fireball_001", "count": 2},
    {"card_id": "frostbolt_002", "count": 2}
  ]
}
```

### 更新卡组
```http
PUT /api/decks/{deck_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "更新的卡组",
  "cards": [
    {"card_id": "fireball_001", "count": 2}
  ]
}
```

### 删除卡组
```http
DELETE /api/decks/{deck_id}
Authorization: Bearer <access_token>
```

## 匹配系统

### 开始匹配
```http
POST /api/matchmaking/start
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "deck_id": 1,
  "game_mode": "ranked"
}
```

**响应**:
```json
{
  "match_id": "match_12345",
  "status": "searching",
  "estimated_wait_time": 30
}
```

### 取消匹配
```http
POST /api/matchmaking/cancel
Authorization: Bearer <access_token>
```

### 获取匹配状态
```http
GET /api/matchmaking/status
Authorization: Bearer <access_token>
```

## 游戏系统

### 获取游戏状态
```http
GET /api/games/{game_id}
Authorization: Bearer <access_token>
```

**响应**:
```json
{
  "id": "game_12345",
  "status": "in_progress",
  "current_player": 1,
  "turn": 5,
  "players": [
    {
      "id": 1,
      "username": "player1",
      "hero": {
        "id": "jaina_001",
        "name": "吉安娜·普罗德摩尔",
        "health": 25,
        "max_health": 30,
        "armor": 5,
        "attack": 0
      },
      "hand_size": 4,
      "deck_size": 20,
      "mana": 6,
      "max_mana": 6
    }
  ],
  "board": {
    "minions": [
      {
        "id": "minion_123",
        "card_id": "chillwind_yeti",
        "player": 1,
        "health": 5,
        "attack": 4,
        "cost": 4,
        "can_attack": true
      }
    ]
  }
}
```

### 出牌
```http
POST /api/games/{game_id}/play-card
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "card_id": "fireball_001",
  "target_player_id": 2,
  "target_minion_id": "minion_456"
}
```

### 攻击
```http
POST /api/games/{game_id}/attack
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "attacker_id": "minion_123",
  "target_id": "minion_456",
  "target_player_id": 2
}
```

### 结束回合
```http
POST /api/games/{game_id}/end-turn
Authorization: Bearer <access_token>
```

### 认输
```http
POST /api/games/{game_id}/concede
Authorization: Bearer <access_token>
```

## WebSocket接口

### 连接
```
ws://localhost:8000/ws/{user_id}
```

### 消息格式
```json
{
  "type": "game_update",
  "data": {
    "game_id": "game_12345",
    "action": "card_played",
    "player": 1,
    "details": {
      "card_id": "fireball_001",
      "target": "hero_2"
    }
  }
}
```

### 消息类型
- `game_update`: 游戏状态更新
- `match_found`: 找到对手
- `player_connected`: 玩家连接
- `player_disconnected`: 玩家断开连接
- `turn_start`: 回合开始
- `turn_end`: 回合结束
- `game_over`: 游戏结束

## 排行榜

### 获取排行榜
```http
GET /api/leaderboard?region=global&class=all&page=1&limit=50
```

**响应**:
```json
{
  "rankings": [
    {
      "rank": 1,
      "player": {
        "id": 42,
        "username": "ProPlayer",
        "rating": 1850
      },
      "stats": {
        "wins": 156,
        "losses": 44,
        "win_rate": 0.780
      }
    }
  ],
  "total_players": 10000,
  "page": 1,
  "pages": 200
}
```

## 好友系统

### 获取好友列表
```http
GET /api/friends
Authorization: Bearer <access_token>
```

### 添加好友
```http
POST /api/friends
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "username": "friend_username"
}
```

### 删除好友
```http
DELETE /api/friends/{friend_id}
Authorization: Bearer <access_token>
```

## 错误处理

### 错误响应格式
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "输入数据验证失败",
    "details": {
      "field": "email",
      "reason": "邮箱格式不正确"
    }
  }
}
```

### 常见错误码
- `400`: 请求参数错误
- `401`: 未认证或认证失败
- `403`: 权限不足
- `404`: 资源不存在
- `409`: 资源冲突
- `422`: 数据验证失败
- `429`: 请求频率限制
- `500`: 服务器内部错误

## 速率限制

| 端点类型 | 限制 | 时间窗口 |
|---------|------|----------|
| 认证相关 | 5次/IP | 1分钟 |
| 游戏操作 | 100次/用户 | 1分钟 |
| 匹配系统 | 10次/用户 | 1分钟 |
| 一般API | 1000次/用户 | 1小时 |

## API版本控制

- 当前版本: `v1`
- 版本策略: URL路径版本控制 (`/api/v1/`)
- 向后兼容性: 支持前一个主版本

## 开发工具

### Swagger UI
访问 `http://localhost:8000/docs` 查看交互式API文档

### ReDoc
访问 `http://localhost:8000/redoc` 查看API文档

### OpenAPI规范
访问 `http://localhost:8000/openapi.json` 获取OpenAPI规范文件

## SDK示例

### Python
```python
import requests

class CardBattleAPI:
    def __init__(self, base_url, token=None):
        self.base_url = base_url
        self.token = token
        self.headers = {}
        if token:
            self.headers['Authorization'] = f'Bearer {token}'

    def login(self, username, password):
        response = requests.post(
            f'{self.base_url}/auth/login',
            json={'username': username, 'password': password}
        )
        data = response.json()
        self.token = data['access_token']
        self.headers['Authorization'] = f'Bearer {self.token}'
        return data

    def get_cards(self, **params):
        response = requests.get(
            f'{self.base_url}/cards',
            headers=self.headers,
            params=params
        )
        return response.json()

# 使用示例
api = CardBattleAPI('http://localhost:8000/api')
api.login('player123', 'password')
cards = api.get_cards(class_='mage', rarity='legendary')
```

### JavaScript/TypeScript
```typescript
class CardBattleAPI {
  private baseUrl: string;
  private token?: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  async login(username: string, password: string) {
    const response = await fetch(`${this.baseUrl}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password }),
    });
    const data = await response.json();
    this.token = data.access_token;
    return data;
  }

  async getCards(params?: Record<string, any>) {
    const url = new URL(`${this.baseUrl}/cards`);
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        url.searchParams.append(key, value.toString());
      });
    }

    const response = await fetch(url.toString(), {
      headers: {
        'Authorization': `Bearer ${this.token}`,
      },
    });
    return response.json();
  }
}

// 使用示例
const api = new CardBattleAPI('http://localhost:8000/api');
await api.login('player123', 'password');
const cards = await api.getCards({ class: 'mage', rarity: 'legendary' });
```

## 更新日志

### v1.0.0 (2024-10-07)
- 初始API版本发布
- 实现用户认证系统
- 实现卡牌和卡组管理
- 实现匹配和游戏系统
- 实现WebSocket实时通信
- 添加排行榜和好友系统