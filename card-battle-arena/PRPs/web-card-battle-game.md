name: "Web端多人联机卡牌对战游戏 - 完整全栈实现"
description: |

## Purpose
构建一个现代化的Web端多人联机卡牌对战游戏，包含完整的前后端技术栈、实时对战系统、智能匹配算法和丰富的用户界面。

## Core Principles
1. **Context is King**: Include ALL necessary documentation, examples, and caveats
2. **Validation Loops**: Provide executable tests/lints the AI can run and fix
3. **Information Dense**: Use keywords and patterns from the codebase
4. **Progressive Success**: Start simple, validate, then enhance
5. **Global rules**: Be sure to follow all rules in CLAUDE.md

---

## Goal
构建一个功能完整的Web端多人卡牌对战游戏，支持实时对战、排位赛系统、卡组构建、社交功能等核心特性。游戏应该具有现代化的UI设计、流畅的用户体验和稳定的后端服务。

## Why
- **商业价值**: 卡牌游戏市场庞大，有稳定的付费用户群体
- **技术展示**: 展示现代Web技术栈的最佳实践
- **用户需求**: 提供随时随地可玩的多人卡牌游戏体验
- **社区建设**: 建立活跃的玩家社区和电竞赛事

## What
一个完整的全栈Web应用，包含：
- React前端界面，支持桌面和移动端
- FastAPI后端服务，提供RESTful API和WebSocket实时通信
- PostgreSQL数据库存储用户数据和游戏记录
- Redis缓存提供高性能会话管理
- 完整的用户系统、匹配系统、游戏逻辑

### Success Criteria
- [ ] 前端应用成功构建并运行在localhost:5173
- [ ] 后端API服务运行在localhost:8000，所有端点正常响应
- [ ] WebSocket连接稳定，支持实时游戏状态同步
- [ ] 数据库模型完整，支持用户注册、卡牌数据、游戏记录
- [ ] 基础游戏逻辑实现，支持卡牌出牌、回合切换、胜负判定
- [ ] 前端界面响应式设计，在不同设备上正常显示
- [ ] 所有测试通过，代码质量符合规范
- [ ] Docker容器化部署成功

## All Needed Context

### Documentation & References
```yaml
# MUST READ - Include these in your context window
- url: https://react.dev/
  why: React 18新特性、Hooks最佳实践、并发渲染模式

- url: https://fastapi.tiangolo.com/
  why: FastAPI异步编程、WebSocket实现、依赖注入系统

- url: https://socket.io/docs/
  why: WebSocket连接管理、房间系统、实时事件处理

- url: https://tailwindcss.com/docs/
  why: 原子化CSS设计、响应式布局、组件样式

- url: https://www.framer.com/motion/
  why: 动画库使用、手势识别、性能优化技巧

- url: https://www.postgresql.org/docs/
  why: 数据库设计、索引优化、事务处理

- url: https://redis.io/documentation
  why: 缓存策略、数据结构选择、持久化配置

- url: https://pydantic.dev/
  why: 数据验证、序列化、模式设计

- url: https://www.typescriptlang.org/docs/
  why: TypeScript类型系统、接口定义、泛型使用

- file: CLAUDE.md
  why: 项目编码规范、文件结构要求、测试标准

- file: INITIAL.md
  why: 详细的功能需求、技术栈要求、特殊注意事项
```

### Current Codebase tree
```bash
card-battle-arena/
├── README.md                    # 项目说明文档
├── INITIAL.md                   # 功能需求文档
├── package.json                 # 项目根配置
├── docker-compose.yml           # Docker编排配置
├── .gitignore                   # Git忽略文件
├── frontend/                    # React前端应用目录
│   ├── src/
│   │   ├── components/          # React组件
│   │   ├── pages/              # 页面组件
│   │   ├── hooks/              # 自定义Hooks
│   │   ├── stores/             # 状态管理
│   │   ├── services/           # API服务
│   │   ├── types/              # TypeScript类型
│   │   └── utils/              # 工具函数
│   └── public/                 # 静态资源
├── backend/                     # FastAPI后端应用目录
│   └── app/
│       ├── api/                # API路由
│       ├── core/               # 核心逻辑
│       ├── models/             # 数据库模型
│       ├── schemas/            # Pydantic模式
│       └── database/           # 数据库配置
├── shared/                      # 前后端共享代码
├── docs/                        # 项目文档
└── assets/                      # 项目资源
```

### Desired Codebase tree with files to be added and responsibility of file
```bash
card-battle-arena/
├── frontend/                    # React前端应用
│   ├── package.json            # 前端依赖和脚本
│   ├── vite.config.ts          # Vite构建配置
│   ├── tailwind.config.js      # Tailwind CSS配置
│   ├── tsconfig.json           # TypeScript配置
│   ├── src/
│   │   ├── components/
│   │   │   ├── ui/             # 基础UI组件
│   │   │   │   ├── Button.tsx
│   │   │   │   ├── Card.tsx
│   │   │   │   ├── Modal.tsx
│   │   │   │   └── AnimatedCard.tsx
│   │   │   ├── game/           # 游戏相关组件
│   │   │   │   ├── GameBoard.tsx
│   │   │   │   ├── Hand.tsx
│   │   │   │   ├── Battlefield.tsx
│   │   │   │   └── TurnTimer.tsx
│   │   │   ├── deck/           # 卡组编辑组件
│   │   │   │   ├── DeckEditor.tsx
│   │   │   │   ├── CardLibrary.tsx
│   │   │   │   └── DragDropCard.tsx
│   │   │   └── social/         # 社交功能组件
│   │   │       ├── FriendsList.tsx
│   │   │       ├── Chat.tsx
│   │   │       └── SpectatorMode.tsx
│   │   ├── pages/
│   │   │   ├── HomePage.tsx    # 首页
│   │   │   ├── LobbyPage.tsx   # 游戏大厅
│   │   │   ├── GamePage.tsx    # 对战页面
│   │   │   ├── DeckPage.tsx    # 卡组页面
│   │   │   └── ProfilePage.tsx # 个人资料
│   │   ├── hooks/
│   │   │   ├── useSocket.ts    # WebSocket钩子
│   │   │   ├── useGameState.ts # 游戏状态管理
│   │   │   └── useAuth.ts      # 认证状态
│   │   ├── stores/
│   │   │   ├── gameStore.ts    # 游戏状态
│   │   │   ├── authStore.ts    # 认证状态
│   │   │   └── uiStore.ts      # UI状态
│   │   ├── services/
│   │   │   ├── api.ts          # API客户端
│   │   │   ├── websocket.ts    # WebSocket服务
│   │   │   └── gameLogic.ts    # 游戏逻辑
│   │   ├── types/
│   │   │   ├── card.ts         # 卡牌类型定义
│   │   │   ├── game.ts         # 游戏类型定义
│   │   │   └── user.ts         # 用户类型定义
│   │   └── utils/
│   │       ├── animations.ts   # 动画工具
│   │       └── formatters.ts   # 格式化工具
│   └── public/
│       ├── assets/
│       │   ├── cards/          # 卡牌图片资源
│       │   ├── effects/        # 特效图片
│       │   └── sounds/         # 音效文件
│       └── locales/            # 国际化文件
├── backend/                     # FastAPI后端应用
│   ├── requirements.txt        # Python依赖
│   ├── alembic.ini            # 数据库迁移配置
│   ├── main.py                # 应用入口
│   └── app/
│       ├── __init__.py
│       ├── api/
│       │   ├── __init__.py
│       │   ├── dependencies.py # 依赖注入
│       │   └── routes/
│       │       ├── __init__.py
│       │       ├── auth.py     # 认证路由
│       │       ├── game.py     # 游戏路由
│       │       ├── deck.py     # 卡组路由
│       │       └── social.py   # 社交路由
│       ├── core/
│       │   ├── __init__.py
│       │   ├── game/
│       │   │   ├── __init__.py
│       │   │   ├── engine.py   # 游戏引擎
│       │   │   ├── card_effects.py # 卡牌效果
│       │   │   └── matchmaking.py # 匹配算法
│       │   ├── websocket/
│       │   │   ├── __init__.py
│       │   │   ├── manager.py  # WebSocket管理
│       │   │   ├── events.py   # 事件处理
│       │   │   └── rooms.py    # 房间管理
│       │   └── security.py     # 安全相关
│       ├── models/
│       │   ├── __init__.py
│       │   ├── user.py         # 用户模型
│       │   ├── card.py         # 卡牌模型
│       │   ├── deck.py         # 卡组模型
│       │   └── game.py         # 游戏模型
│       ├── schemas/
│       │   ├── __init__.py
│       │   ├── user.py         # 用户模式
│       │   ├── card.py         # 卡牌模式
│       │   └── game.py         # 游戏模式
│       └── database/
│           ├── __init__.py
│           ├── postgres.py     # PostgreSQL配置
│           └── redis.py        # Redis配置
├── shared/                      # 共享代码
│   ├── __init__.py
│   ├── types/                  # 共享类型定义
│   │   ├── __init__.py
│   │   ├── card.py
│   │   ├── game.py
│   │   └── user.py
│   └── constants/              # 常量定义
│       ├── __init__.py
│       └── game_constants.py
├── tests/                       # 测试文件
│   ├── __init__.py
│   ├── test_backend.py         # 后端测试
│   └── test_frontend.py        # 前端测试
└── docs/                        # 项目文档
    ├── API.md                  # API文档
    ├── DEPLOYMENT.md           # 部署文档
    └── CONTRIBUTING.md         # 贡献指南
```

### Known Gotchas of our codebase & Library Quirks
```python
# CRITICAL: FastAPI requires async functions for WebSocket endpoints
# CRITICAL: React 18 uses createRoot instead of ReactDOM.render
# CRITICAL: Pydantic v2 has different syntax than v1
# CRITICAL: Socket.io client must connect with proper transports configuration
# CRITICAL: PostgreSQL connection pooling required for production
# CRITICAL: Redis connection must handle connection failures gracefully
# CRITICAL: TypeScript strict mode enabled - all types must be properly defined
# CRITICAL: Tailwind CSS requires PostCSS configuration
# CRITICAL: CORS must be properly configured for WebSocket connections
# CRITICAL: JWT tokens must have proper expiration and refresh mechanism
```

## Implementation Blueprint

### Data models and structure

创建核心数据模型，确保类型安全和数据一致性：
```python
# 后端SQLAlchemy模型示例
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    elo_rating = Column(Integer, default=1000)
    created_at = Column(DateTime, default=datetime.utcnow)

class Card(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    cost = Column(Integer)
    attack = Column(Integer)
    defense = Column(Integer)
    card_type = Column(String)  # minion, spell, weapon
    rarity = Column(String)     # common, rare, epic, legendary
    effect_text = Column(Text)
    image_url = Column(String)

# 前端TypeScript类型示例
interface Card {
  id: number;
  name: string;
  cost: number;
  attack: number;
  defense: number;
  cardType: 'minion' | 'spell' | 'weapon';
  rarity: 'common' | 'rare' | 'epic' | 'legendary';
  effectText: string;
  imageUrl: string;
}

interface GameState {
  currentPlayer: string;
  turnNumber: number;
  playerHand: Card[];
  opponentHand: number;
  battlefield: BattlefieldCard[];
  playerHealth: number;
  opponentHealth: number;
  mana: ManaState;
}
```

### List of tasks to be completed to fulfill the PRP in the order they should be completed

```yaml
Task 1: 设置前端开发环境和配置
CREATE frontend/package.json:
  - 配置React 18 + TypeScript + Vite
  - 添加Tailwind CSS、Framer Motion、Socket.io客户端
  - 配置ESLint、Prettier代码规范

CREATE frontend/vite.config.ts:
  - 配置开发服务器和构建选项
  - 设置路径别名和代理配置

CREATE frontend/tailwind.config.js:
  - 配置Tailwind CSS主题和扩展
  - 定义自定义颜色和动画

Task 2: 设置后端开发环境和配置
CREATE backend/requirements.txt:
  - 添加FastAPI、SQLAlchemy、PostgreSQL驱动
  - 添加Redis、JWT、WebSocket依赖
  - 添加测试和开发工具

CREATE backend/main.py:
  - 配置FastAPI应用和CORS
  - 设置WebSocket连接和路由

CREATE backend/app/database/postgres.py:
  - 配置PostgreSQL连接池
  - 设置数据库会话管理

Task 3: 创建数据库模型和基础数据
CREATE backend/app/models/user.py:
  - 用户模型，包含认证和排位信息
  - 添加索引和约束

CREATE backend/app/models/card.py:
  - 卡牌模型，包含属性和效果
  - 定义卡牌类型和稀有度

CREATE backend/app/models/game.py:
  - 游戏记录模型
  - 对战历史和统计数据

CREATE alembic迁移文件:
  - 创建数据库表结构
  - 插入初始卡牌数据

Task 4: 实现用户认证系统
CREATE backend/app/api/routes/auth.py:
  - JWT认证端点
  - 注册、登录、刷新令牌

CREATE backend/app/core/security.py:
  - 密码哈希和验证
  - JWT令牌生成和验证

CREATE frontend/src/hooks/useAuth.ts:
  - 认证状态管理
  - 自动令牌刷新

Task 5: 实现WebSocket实时通信系统
CREATE backend/app/core/websocket/manager.py:
  - WebSocket连接管理
  - 房间系统和消息广播

CREATE backend/app/core/websocket/events.py:
  - 游戏事件处理
  - 状态同步和错误处理

CREATE frontend/src/hooks/useSocket.ts:
  - WebSocket连接管理
  - 自动重连和错误处理

Task 6: 实现核心游戏引擎
CREATE backend/app/core/game/engine.py:
  - 游戏状态管理
  - 回合制逻辑和规则验证

CREATE backend/app/core/game/card_effects.py:
  - 卡牌效果处理系统
  - 伤害、治疗、召唤等效果

CREATE frontend/src/services/gameLogic.ts:
  - 前端游戏逻辑验证
  - 动画和交互处理

Task 7: 创建基础UI组件
CREATE frontend/src/components/ui/Button.tsx:
  - 可复用按钮组件
  - 支持不同样式和状态

CREATE frontend/src/components/ui/Card.tsx:
  - 卡牌显示组件
  - 支持动画和交互

CREATE frontend/src/components/ui/Modal.tsx:
  - 模态框组件
  - 支持动画和可访问性

Task 8: 实现游戏界面组件
CREATE frontend/src/components/game/GameBoard.tsx:
  - 游戏主界面
  - 整合所有游戏组件

CREATE frontend/src/components/game/Hand.tsx:
  - 手牌显示和管理
  - 拖拽和出牌交互

CREATE frontend/src/components/game/Battlefield.tsx:
  - 战场区域显示
  - 随从和状态管理

Task 9: 实现卡组编辑器
CREATE frontend/src/components/deck/DeckEditor.tsx:
  - 卡组构建界面
  - 拖拽添加和移除卡牌

CREATE backend/app/api/routes/deck.py:
  - 卡组CRUD操作
  - 卡牌验证和保存

Task 10: 实现匹配系统
CREATE backend/app/core/game/matchmaking.py:
  - ELO匹配算法
  - 队列管理和房间创建

CREATE frontend/src/pages/LobbyPage.tsx:
  - 游戏大厅界面
  - 匹配状态和模式选择

Task 11: 添加测试用例
CREATE tests/test_backend.py:
  - API端点测试
  - 游戏逻辑测试

CREATE tests/test_frontend.py:
  - 组件渲染测试
  - 用户交互测试

Task 12: 完善文档和部署配置
CREATE docs/API.md:
  - API端点文档
  - WebSocket事件说明

CREATE docker-compose.yml:
  - 生产环境配置
  - 服务编排和负载均衡
```

### Per task pseudocode as needed added to each task

```python
# Task 5: WebSocket Manager
class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.game_rooms: Dict[str, List[str]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        # CRITICAL: Accept connection and store reference
        await websocket.accept()
        self.active_connections[user_id] = websocket

    async def join_game_room(self, user_id: str, game_id: str):
        # PATTERN: Add user to game room
        if game_id not in self.game_rooms:
            self.game_rooms[game_id] = []
        self.game_rooms[game_id].append(user_id)

    async def broadcast_to_room(self, game_id: str, message: dict):
        # PATTERN: Send message to all players in room
        for user_id in self.game_rooms.get(game_id, []):
            if user_id in self.active_connections:
                await self.active_connections[user_id].send_text(json.dumps(message))

# Task 6: Game Engine
class GameEngine:
    async def play_card(self, game_state: GameState, card_id: str, target: str = None):
        # PATTERN: Validate play before executing
        if not self._validate_play(game_state, card_id, target):
            raise InvalidPlayError("Invalid card play")

        # CRITICAL: Execute card effect
        card = self._get_card_by_id(card_id)
        effect_result = await self.card_effects_processor.process(card, game_state, target)

        # PATTERN: Update game state atomically
        new_state = self._update_game_state(game_state, effect_result)
        return new_state

# Task 8: React Game Components
const GameBoard: React.FC<GameBoardProps> = ({ gameId, playerId }) => {
  const socket = useSocket();
  const { gameState, playCard, endTurn } = useGameState(gameId);

  // PATTERN: Handle socket events
  useEffect(() => {
    socket.on('game_state_update', (newState) => {
      // CRITICAL: Update local state with server state
      setGameState(newState);
    });

    return () => socket.off('game_state_update');
  }, [socket]);

  const handleCardPlay = async (cardId: string, target?: string) => {
    try {
      // PATTERN: Validate on client before sending to server
      await playCard(cardId, target);
      socket.emit('play_card', { gameId, cardId, target });
    } catch (error) {
      console.error('Play card failed:', error);
    }
  };

  return (
    <motion.div className="game-board">
      {/* Game UI components */}
    </motion.div>
  );
};
```

### Integration Points
```yaml
DATABASE:
  - migration: "Create users, cards, games, decks tables"
  - indexes: "users(username, email), cards(name, type), games(created_at)"
  - seed_data: "Insert 200+ cards with various types and rarities"

CONFIG:
  - backend: .env file with DATABASE_URL, REDIS_URL, SECRET_KEY
  - frontend: .env file with VITE_API_URL, VITE_WS_URL
  - pattern: Environment-specific configurations

ROUTES:
  - auth: /api/auth/register, /api/auth/login, /api/auth/refresh
  - game: /api/game/matchmaking, /api/game/history
  - deck: /api/deck/create, /api/deck/list, /api/deck/{id}

WEBSOCKET_EVENTS:
  - connection: connect, disconnect, error
  - game: game_start, play_card, turn_end, game_over
  - matchmaking: match_found, match_cancelled

FRONTEND_STATE:
  - auth: user info, token, authentication status
  - game: current game state, hand, battlefield, mana
  - ui: modals, notifications, loading states
```

## Validation Loop

### Level 1: Syntax & Style
```bash
# Frontend validation
cd frontend
npm run lint                    # ESLint检查
npm run type-check              # TypeScript类型检查
npm run build                   # 构建检查

# Backend validation
cd backend
ruff check . --fix              # Python代码格式化
mypy .                          # 类型检查
black .                         # 代码格式化

# Expected: No errors. If errors exist, fix them before proceeding.
```

### Level 2: Unit Tests
```python
# CREATE tests/test_backend.py
def test_user_registration():
    """Test user registration endpoint"""
    response = client.post("/api/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword"
    })
    assert response.status_code == 201
    assert response.json()["username"] == "testuser"

def test_card_play_validation():
    """Test card play validation"""
    game_state = create_test_game_state()
    engine = GameEngine()

    # Test valid play
    result = engine.play_card(game_state, "fireball", "enemy_minion")
    assert result.success == True

    # Test invalid play (not enough mana)
    with pytest.raises(InvalidPlayError):
        engine.play_card(game_state, "legendary_card", "enemy")

def test_websocket_connection():
    """Test WebSocket connection and messaging"""
    with client.websocket_connect("/ws") as websocket:
        websocket.send_json({"type": "join_game", "game_id": "test_game"})
        data = websocket.receive_json()
        assert data["type"] == "game_state_update"

# CREATE tests/test_frontend.js
import { render, screen, fireEvent } from '@testing-library/react';
import { GameBoard } from '../src/components/game/GameBoard';

test('Game board renders correctly', () => {
  render(<GameBoard gameId="test" playerId="player1" />);
  expect(screen.getByTestId('game-board')).toBeInTheDocument();
});

test('Card play interaction works', () => {
  const mockPlayCard = jest.fn();
  render(<GameBoard gameId="test" playerId="player1" onCardPlay={mockPlayCard} />);

  const card = screen.getByTestId('card-1');
  fireEvent.click(card);

  expect(mockPlayCard).toHaveBeenCalledWith('card-1');
});
```

```bash
# Run and iterate until passing:
cd backend && pytest tests/ -v --cov=app
cd frontend && npm test

# If failing: Read error messages, fix code, re-run tests
```

### Level 3: Integration Test
```bash
# Start all services
docker-compose up -d

# Wait for services to be ready
sleep 10

# Test API endpoints
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "password": "testpass"}'

# Expected: {"id": 1, "username": "testuser", "email": "test@example.com"}

# Test WebSocket connection
curl -i -N -H "Connection: Upgrade" \
  -H "Upgrade: websocket" \
  -H "Sec-WebSocket-Key: test" \
  -H "Sec-WebSocket-Version: 13" \
  http://localhost:8000/ws

# Test frontend build
cd frontend && npm run build

# Expected: Build completes without errors, dist/ folder created
```

### Level 4: End-to-End Game Flow Test
```bash
# Start development servers
cd backend && uvicorn main:app --reload &
cd frontend && npm run dev &

# Manual testing steps:
# 1. Open http://localhost:5173 in browser
# 2. Register new user account
# 3. Login and navigate to deck builder
# 4. Create a valid deck with 30 cards
# 5. Go to lobby and start matchmaking
# 6. Accept match and play against opponent
# 7. Play cards, end turns, verify game state sync
# 8. Complete game and verify result recording

# Expected: Complete game flow works without errors
```

## Final Validation Checklist
- [ ] All tests pass: `pytest tests/ -v --cov=app`
- [ ] Frontend builds successfully: `npm run build`
- [ ] No linting errors: `ruff check .` and `npm run lint`
- [ ] No type errors: `mypy .` and `npm run type-check`
- [ ] Database migrations run: `alembic upgrade head`
- [ ] WebSocket connections stable: Test with multiple clients
- [ ] Game logic works correctly: Manual gameplay testing
- [ ] UI responsive on different screen sizes
- [ ] Docker containers start properly: `docker-compose up`
- [ ] API documentation accessible: http://localhost:8000/docs
- [ ] Performance acceptable: <3s load time, <100ms API response

---

## Anti-Patterns to Avoid
- ❌ Don't store game state only on frontend - must be server authoritative
- ❌ Don't ignore WebSocket error handling and reconnection logic
- ❌ Don't hardcode card effects - use configurable effect system
- ❌ Don't skip input validation - validate on both client and server
- ❌ Don't use synchronous operations in async contexts
- ❌ Don't ignore CORS and security headers configuration
- ❌ Don't commit sensitive data like API keys or passwords
- ❌ Don't ignore mobile responsiveness and accessibility
- ❌ Don't skip error boundaries and error logging
- ❌ Don't ignore database indexing and query optimization

## Confidence Score: 9/10

High confidence due to:
- Comprehensive technical requirements provided in INITIAL.md
- Clear project structure and well-defined milestones
- Extensive documentation available for all technologies
- Modern, well-supported technology stack
- Detailed validation and testing strategy
- Realistic scope with progressive implementation approach

Minor uncertainty on WebSocket scaling performance and card game balance tuning, but these can be addressed through iterative development and testing.