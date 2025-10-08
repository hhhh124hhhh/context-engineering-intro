# 卡牌对战竞技场 - 开发指南

## 概述

本文档为卡牌对战竞技场项目的开发者提供详细的开发指南，包括项目结构、开发流程、代码规范、测试策略等内容。

## 项目结构

```
card-battle-arena/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── api/               # API路由
│   │   │   ├── auth.py       # 认证相关API
│   │   │   ├── cards.py      # 卡牌相关API
│   │   │   ├── games.py      # 游戏相关API
│   │   │   ├── matchmaking.py # 匹配相关API
│   │   │   └── users.py      # 用户相关API
│   │   ├── core/             # 核心业务逻辑
│   │   │   ├── game/         # 游戏引擎
│   │   │   │   ├── engine.py # 游戏引擎核心
│   │   │   │   ├── cards.py  # 卡牌逻辑
│   │   │   │   └── rules.py  # 游戏规则
│   │   │   ├── matchmaking/  # 匹配系统
│   │   │   │   ├── matcher.py # 匹配算法
│   │   │   │   └── queue.py   # 匹配队列
│   │   │   └── websocket/     # WebSocket处理
│   │   │       ├── manager.py # 连接管理
│   │   │       └── handlers.py # 消息处理
│   │   ├── database/         # 数据库配置
│   │   │   ├── connection.py # 数据库连接
│   │   │   └── migrations/   # 数据库迁移
│   │   ├── models/           # 数据模型
│   │   │   ├── user.py       # 用户模型
│   │   │   ├── game.py       # 游戏模型
│   │   │   ├── card.py       # 卡牌模型
│   │   │   └── deck.py       # 卡组模型
│   │   ├── schemas/          # Pydantic模式
│   │   │   ├── user.py       # 用户模式
│   │   │   ├── game.py       # 游戏模式
│   │   │   └── card.py       # 卡牌模式
│   │   └── utils/            # 工具函数
│   │       ├── auth.py       # 认证工具
│   │       ├── cache.py      # 缓存工具
│   │       └── logger.py     # 日志工具
│   ├── tests/                # 测试文件
│   │   ├── test_game_engine.py
│   │   ├── test_matchmaking.py
│   │   ├── test_auth.py
│   │   └── conftest.py       # 测试配置
│   ├── requirements.txt      # Python依赖
│   ├── pyproject.toml       # 项目配置
│   └── main.py              # 应用入口
├── frontend/                 # 前端应用
│   ├── public/              # 静态资源
│   │   ├── index.html       # HTML模板
│   │   └── favicon.ico      # 网站图标
│   ├── src/
│   │   ├── components/      # React组件
│   │   │   ├── game/        # 游戏相关组件
│   │   │   │   ├── GameBoard.tsx
│   │   │   │   ├── Hand.tsx
│   │   │   │   └── Battlefield.tsx
│   │   │   ├── ui/          # UI组件
│   │   │   │   ├── Button.tsx
│   │   │   │   ├── Card.tsx
│   │   │   │   └── Modal.tsx
│   │   │   └── layout/      # 布局组件
│   │   │       ├── Header.tsx
│   │   │       └── Footer.tsx
│   │   ├── pages/           # 页面组件
│   │   │   ├── Home.tsx
│   │   │   ├── Login.tsx
│   │   │   ├── Game.tsx
│   │   │   └── DeckEditor.tsx
│   │   ├── hooks/           # 自定义Hooks
│   │   │   ├── useAuth.ts
│   │   │   ├── useGame.ts
│   │   │   └── useWebSocket.ts
│   │   ├── services/        # API服务
│   │   │   ├── api.ts       # API客户端
│   │   │   ├── auth.ts      # 认证服务
│   │   │   └── game.ts      # 游戏服务
│   │   ├── store/           # 状态管理
│   │   │   ├── index.ts     # Store配置
│   │   │   ├── authSlice.ts # 认证状态
│   │   │   └── gameSlice.ts # 游戏状态
│   │   ├── types/           # TypeScript类型
│   │   │   ├── auth.ts
│   │   │   ├── game.ts
│   │   │   └── card.ts
│   │   ├── utils/           # 工具函数
│   │   │   ├── constants.ts
│   │   │   └── helpers.ts
│   │   ├── styles/          # 样式文件
│   │   │   └── globals.css
│   │   ├── App.tsx          # 应用根组件
│   │   └── main.tsx         # 应用入口
│   ├── package.json         # 项目配置
│   ├── tsconfig.json        # TypeScript配置
│   ├── vite.config.ts       # Vite配置
│   └── tailwind.config.js   # Tailwind配置
├── scripts/                 # 部署脚本
│   ├── setup.sh            # 环境设置
│   ├── deploy.sh           # 部署脚本
│   ├── quality-check.sh    # 质量检查
│   └── init-data.py        # 数据初始化
├── nginx/                   # Nginx配置
│   └── conf.d/
│       └── default.conf     # 默认配置
├── monitoring/              # 监控配置
│   ├── prometheus.yml      # Prometheus配置
│   └── grafana/            # Grafana配置
└── docker-compose.yml       # Docker编排
```

## 开发环境设置

### 1. 环境要求
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Git
- PostgreSQL (可选，可使用Docker)
- Redis (可选，可使用Docker)

### 2. 克隆项目
```bash
git clone https://github.com/cardbattle/card-battle-arena.git
cd card-battle-arena
```

### 3. 后端开发环境

#### 创建虚拟环境
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

#### 安装依赖
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 开发依赖
```

#### 环境变量配置
```bash
cp ../.env.example ../.env
# 编辑 .env 文件，配置数据库等信息
```

#### 数据库设置
```bash
# 启动PostgreSQL和Redis
docker-compose up -d postgres redis

# 运行数据库迁移
alembic upgrade head

# 初始化基础数据
python scripts/init-data.py
```

#### 启动开发服务器
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. 前端开发环境

#### 安装依赖
```bash
cd frontend
npm install
```

#### 环境变量配置
```bash
cp .env.example .env.local
# 编辑 .env.local 文件
```

#### 启动开发服务器
```bash
npm run dev
```

### 5. 完整开发环境启动
```bash
# 在项目根目录
./scripts/setup.sh      # 一键设置环境
./scripts/dev-start.sh  # 启动所有开发服务
```

## 开发流程

### 1. 分支管理

#### Git Flow模型
```
main                    # 生产分支
├── develop            # 开发分支
├── feature/*          # 功能分支
├── release/*          # 发布分支
└── hotfix/*           # 热修复分支
```

#### 分支命名规范
- `feature/功能名称` - 新功能开发
- `bugfix/问题描述` - Bug修复
- `hotfix/紧急修复` - 生产环境紧急修复
- `release/版本号` - 发布准备

### 2. 提交规范

#### 提交消息格式
```
<类型>(<范围>): <描述>

[可选的正文]

[可选的脚注]
```

#### 类型说明
- `feat`: 新功能
- `fix`: Bug修复
- `docs`: 文档更新
- `style`: 代码格式化
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

#### 示例
```bash
feat(auth): 添加JWT认证功能
fix(game): 修复卡牌出牌逻辑错误
docs(api): 更新API文档
```

### 3. 代码审查流程

#### Pull Request要求
1. 标题清晰描述变更内容
2. 详细的描述说明变更原因和实现方式
3. 关联相关的Issue
4. 通过所有自动化检查
5. 至少一个代码审查者批准

#### PR模板
```markdown
## 变更描述
简要描述本次变更的内容和目的。

## 变更类型
- [ ] Bug修复
- [ ] 新功能
- [ ] 代码重构
- [ ] 文档更新
- [ ] 性能优化
- [ ] 其他

## 测试
- [ ] 单元测试通过
- [ ] 集成测试通过
- [ ] 手动测试完成

## 检查清单
- [ ] 代码符合项目规范
- [ ] 已添加必要的测试
- [ ] 文档已更新
- [ ] 无破坏性变更

## 相关Issue
Closes #issue_number
```

### 4. 开发任务流程

#### 1. 领取任务
- 从项目管理工具中领取任务
- 创建功能分支：`git checkout -b feature/task-name`

#### 2. 开发实现
- 编写代码实现功能
- 遵循代码规范和最佳实践
- 添加必要的测试

#### 3. 本地测试
```bash
# 后端测试
cd backend
python -m pytest tests/ -v

# 前端测试
cd frontend
npm test

# 代码质量检查
./scripts/quality-check.sh
```

#### 4. 提交代码
```bash
git add .
git commit -m "feat: 添加新功能"
git push origin feature/task-name
```

#### 5. 创建PR
- 在GitHub上创建Pull Request
- 填写PR模板
- 等待代码审查

#### 6. 合并代码
- 通过审查后合并到develop分支
- 删除功能分支

## 代码规范

### 1. Python代码规范

#### 基础规范
- 遵循PEP 8规范
- 使用4个空格缩进
- 行长度限制88字符
- 使用类型提示

#### 示例代码
```python
from typing import List, Optional
from pydantic import BaseModel

class Card(BaseModel):
    """卡牌数据模型"""

    id: str
    name: str
    cost: int
    description: str
    image_url: Optional[str] = None

    class Config:
        """Pydantic配置"""
        orm_mode = True

async def get_cards(
    db: Session,
    class_name: Optional[str] = None,
    rarity: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
) -> List[Card]:
    """
    获取卡牌列表

    Args:
        db: 数据库会话
        class_name: 职业过滤
        rarity: 稀有度过滤
        limit: 返回数量限制
        offset: 偏移量

    Returns:
        卡牌列表
    """
    query = db.query(CardModel)

    if class_name:
        query = query.filter(CardModel.class_name == class_name)
    if rarity:
        query = query.filter(CardModel.rarity == rarity)

    return query.offset(offset).limit(limit).all()
```

#### 导入规范
```python
# 标准库导入
import os
import sys
from typing import List, Optional

# 第三方库导入
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import pytest

# 本地导入
from app.models.card import Card
from app.database.connection import get_db
from app.utils.logger import get_logger
```

### 2. TypeScript代码规范

#### 基础规范
- 使用2个空格缩进
- 使用单引号
- 行长度限制100字符
- 强制使用类型检查

#### 示例代码
```typescript
// 类型定义
interface Card {
  id: string;
  name: string;
  cost: number;
  description: string;
  imageUrl?: string;
}

interface GameState {
  id: string;
  status: 'waiting' | 'playing' | 'finished';
  currentPlayer: number;
  turn: number;
  players: Player[];
}

// React组件
interface GameBoardProps {
  gameId: string;
  onCardPlay: (cardId: string, target?: string) => void;
  onTurnEnd: () => void;
}

const GameBoard: React.FC<GameBoardProps> = ({
  gameId,
  onCardPlay,
  onTurnEnd
}) => {
  const [gameState, setGameState] = useState<GameState | null>(null);
  const { user } = useAuth();

  useEffect(() => {
    // 游戏逻辑
  }, [gameId]);

  const handleCardClick = useCallback((card: Card) => {
    if (canPlayCard(card)) {
      onCardPlay(card.id);
    }
  }, [onCardPlay]);

  return (
    <div className="game-board">
      {/* 游戏界面 */}
    </div>
  );
};

export default GameBoard;
```

#### Hook规范
```typescript
// 自定义Hook
export function useWebSocket(url: string) {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const ws = new WebSocket(url);

    ws.onopen = () => {
      setIsConnected(true);
      setSocket(ws);
    };

    ws.onclose = () => {
      setIsConnected(false);
      setSocket(null);
    };

    return () => {
      ws.close();
    };
  }, [url]);

  const sendMessage = useCallback((message: any) => {
    if (socket && isConnected) {
      socket.send(JSON.stringify(message));
    }
  }, [socket, isConnected]);

  return { socket, isConnected, sendMessage };
}
```

### 3. 命名规范

#### 文件命名
- Python: `snake_case.py`
- TypeScript: `PascalCase.tsx` (组件) / `camelCase.ts` (工具)
- 配置文件: `kebab-case`

#### 变量命名
```python
# Python
user_name = "player1"
card_list = []
is_game_over = False

def get_user_by_id():
    pass

class CardManager:
    pass
```

```typescript
// TypeScript
const userName = 'player1';
const cardList: Card[] = [];
const isGameOver = false;

function getUserById(): User {
  // 实现
}

class CardManager {
  // 实现
}
```

#### 常量命名
```python
# Python
MAX_HAND_SIZE = 10
DEFAULT_GAME_DURATION = 3600
API_BASE_URL = "https://api.cardbattle.arena"
```

```typescript
// TypeScript
const MAX_HAND_SIZE = 10;
const DEFAULT_GAME_DURATION = 3600;
const API_BASE_URL = 'https://api.cardbattle.arena';
```

## 测试策略

### 1. 测试层次

#### 单元测试
- 测试单个函数或类的功能
- 快速执行，隔离依赖
- 覆盖率目标：80%+

#### 集成测试
- 测试模块间的交互
- 包含数据库、API等集成
- 验证业务流程

#### 端到端测试
- 测试完整用户场景
- 模拟真实用户操作
- 关键路径覆盖

### 2. 后端测试

#### 单元测试示例
```python
# tests/test_game_engine.py
import pytest
from app.core.game.engine import GameEngine
from app.models.game import Game

@pytest.fixture
def game_engine():
    """创建游戏引擎实例"""
    return GameEngine()

@pytest.fixture
def sample_game():
    """创建示例游戏"""
    return Game(
        id="test_game",
        player1_id=1,
        player2_id=2
    )

class TestGameEngine:
    """游戏引擎测试类"""

    def test_create_game(self, game_engine):
        """测试创建游戏"""
        game = game_engine.create_game(1, 2)

        assert game.id is not None
        assert game.player1_id == 1
        assert game.player2_id == 2
        assert game.status == "waiting"

    def test_play_card(self, game_engine, sample_game):
        """测试出牌功能"""
        # 模拟出牌
        result = game_engine.play_card(
            game_id=sample_game.id,
            player_id=1,
            card_id="fireball_001"
        )

        assert result is True
        assert sample_game.current_player == 2

    @pytest.mark.asyncio
    async def test_async_game_action(self, game_engine):
        """测试异步游戏动作"""
        game_id = await game_engine.start_async_game(1, 2)

        assert game_id is not None

        game_state = await game_engine.get_game_state(game_id)
        assert game_state.status == "playing"
```

#### 集成测试示例
```python
# tests/test_api_integration.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    """创建测试客户端"""
    return TestClient(app)

@pytest.fixture
def test_user_token(client):
    """创建测试用户并获取token"""
    # 注册用户
    client.post("/api/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass"
    })

    # 登录获取token
    response = client.post("/api/auth/login", json={
        "username": "testuser",
        "password": "testpass"
    })

    return response.json()["access_token"]

class TestGameAPI:
    """游戏API集成测试"""

    def test_start_game(self, client, test_user_token):
        """测试开始游戏"""
        headers = {"Authorization": f"Bearer {test_user_token}"}

        response = client.post(
            "/api/games/start",
            headers=headers,
            json={"deck_id": 1}
        )

        assert response.status_code == 200
        data = response.json()
        assert "game_id" in data
        assert data["status"] == "waiting"

    def test_play_card_endpoint(self, client, test_user_token):
        """测试出牌API端点"""
        headers = {"Authorization": f"Bearer {test_user_token}"}

        # 先开始游戏
        game_response = client.post(
            "/api/games/start",
            headers=headers,
            json={"deck_id": 1}
        )
        game_id = game_response.json()["game_id"]

        # 出牌
        response = client.post(
            f"/api/games/{game_id}/play-card",
            headers=headers,
            json={
                "card_id": "fireball_001",
                "target_player_id": 2
            }
        )

        assert response.status_code == 200
```

### 3. 前端测试

#### 组件测试示例
```typescript
// src/components/__tests__/GameBoard.test.tsx
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { Provider } from 'react-redux';
import { store } from '../../store';
import GameBoard from '../GameBoard';

// Mock WebSocket
jest.mock('../../services/websocket', () => ({
  useWebSocket: () => ({
    sendMessage: jest.fn(),
    isConnected: true
  })
}));

describe('GameBoard', () => {
  const renderWithProvider = (component: React.ReactElement) => {
    return render(
      <Provider store={store}>
        {component}
      </Provider>
    );
  };

  test('renders game board correctly', () => {
    renderWithProvider(<GameBoard gameId="test-game" />);

    expect(screen.getByTestId('game-board')).toBeInTheDocument();
    expect(screen.getByTestId('hand-area')).toBeInTheDocument();
    expect(screen.getByTestId('battlefield-area')).toBeInTheDocument();
  });

  test('handles card play when card is clicked', () => {
    const mockOnCardPlay = jest.fn();

    renderWithProvider(
      <GameBoard
        gameId="test-game"
        onCardPlay={mockOnCardPlay}
      />
    );

    const card = screen.getByTestId('card-fireball');
    fireEvent.click(card);

    expect(mockOnCardPlay).toHaveBeenCalledWith('fireball_001');
  });

  test('shows current player indicator', () => {
    renderWithProvider(<GameBoard gameId="test-game" />);

    const indicator = screen.getByTestId('current-player-indicator');
    expect(indicator).toHaveTextContent('Your Turn');
  });
});
```

#### Hook测试示例
```typescript
// src/hooks/__tests__/useAuth.test.ts
import { renderHook, act } from '@testing-library/react';
import { Provider } from 'react-redux';
import { store } from '../../store';
import { useAuth } from '../useAuth';

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <Provider store={store}>{children}</Provider>
);

describe('useAuth', () => {
  test('should initialize with empty user', () => {
    const { result } = renderHook(() => useAuth(), { wrapper });

    expect(result.current.user).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
  });

  test('should login successfully with valid credentials', async () => {
    const { result } = renderHook(() => useAuth(), { wrapper });

    await act(async () => {
      await result.current.login('testuser', 'testpass');
    });

    expect(result.current.user).not.toBeNull();
    expect(result.current.isAuthenticated).toBe(true);
  });

  test('should logout and clear user data', async () => {
    const { result } = renderHook(() => useAuth(), { wrapper });

    // 先登录
    await act(async () => {
      await result.current.login('testuser', 'testpass');
    });

    // 然后登出
    act(() => {
      result.current.logout();
    });

    expect(result.current.user).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
  });
});
```

### 4. 运行测试

#### 后端测试
```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_game_engine.py

# 运行带覆盖率的测试
pytest --cov=app --cov-report=html

# 运行集成测试
pytest -m integration

# 监视模式
pytest -f
```

#### 前端测试
```bash
# 运行所有测试
npm test

# 运行带覆盖率的测试
npm run test:coverage

# 运行特定测试文件
npm test GameBoard.test.tsx

# 监视模式
npm test -- --watch
```

## 调试技巧

### 1. 后端调试

#### 使用调试器
```python
# 在代码中设置断点
import pdb; pdb.set_trace()

# 或者使用更现代的调试器
import ipdb; ipdb.set_trace()
```

#### 日志调试
```python
import logging

logger = logging.getLogger(__name__)

def play_card(game_id: str, player_id: int, card_id: str):
    logger.info(f"Playing card {card_id} in game {game_id} by player {player_id}")

    try:
        # 游戏逻辑
        result = execute_card_play(game_id, player_id, card_id)
        logger.info(f"Card play result: {result}")
        return result
    except Exception as e:
        logger.error(f"Card play failed: {e}")
        raise
```

#### 数据库调试
```python
# 查看SQL查询
import sqlalchemy as sa
from app.database.connection import engine

# 启用SQL日志
import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# 执行原始SQL查询
with engine.connect() as conn:
    result = conn.execute(sa.text("SELECT * FROM games WHERE status = 'playing'"))
    for row in result:
        print(row)
```

### 2. 前端调试

#### React DevTools
- 安装React Developer Tools浏览器扩展
- 检查组件状态和props
- 分析组件渲染性能

#### Redux DevTools
- 安装Redux DevTools浏览器扩展
- 查看状态变化历史
- 时间旅行调试

#### 控制台调试
```typescript
// 组件调试
const GameBoard: React.FC<GameBoardProps> = ({ gameId }) => {
  console.log('GameBoard render:', { gameId });

  useEffect(() => {
    console.log('GameBoard mounted');
    return () => console.log('GameBoard unmounted');
  }, []);

  const handleCardPlay = useCallback((cardId: string) => {
    console.log('Card played:', cardId);
    // 调试出牌逻辑
  }, []);

  return (
    <div>
      {/* 调试信息显示 */}
      {process.env.NODE_ENV === 'development' && (
        <div data-testid="debug-info">
          Game ID: {gameId}
        </div>
      )}
    </div>
  );
};
```

#### 网络调试
```typescript
// API调试
import { api } from '../services/api';

const fetchCards = async () => {
  try {
    console.time('fetchCards');
    const response = await api.get('/cards');
    console.timeEnd('fetchCards');
    console.log('Cards response:', response.data);
    return response.data;
  } catch (error) {
    console.error('Fetch cards failed:', error);
    throw error;
  }
};
```

## 性能优化

### 1. 后端性能优化

#### 数据库优化
```python
# 使用索引
class GameModel(Base):
    __tablename__ = "games"

    id = Column(String, primary_key=True, index=True)
    status = Column(String, index=True)  # 添加索引
    created_at = Column(DateTime, index=True)  # 添加索引

# 批量查询
def get_games_with_players(db: Session, limit: int = 20):
    return db.query(GameModel)\
             .options(joinedload(GameModel.players))\
             .limit(limit)\
             .all()

# 使用连接池
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)
```

#### 缓存优化
```python
import redis
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(ttl: int = 3600):
    """缓存装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"

            # 尝试从缓存获取
            cached_result = redis_client.get(cache_key)
            if cached_result:
                return json.loads(cached_result)

            # 执行函数并缓存结果
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, ttl, json.dumps(result))

            return result
        return wrapper
    return decorator

@cache_result(ttl=1800)
async def get_leaderboard():
    """获取排行榜（缓存30分钟）"""
    # 查询数据库
    pass
```

#### 异步优化
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=4)

async def process_multiple_cards(cards: List[Card]):
    """并行处理多张卡牌"""
    tasks = []
    for card in cards:
        task = asyncio.create_task(process_card_async(card))
        tasks.append(task)

    results = await asyncio.gather(*tasks)
    return results

async def process_card_async(card: Card):
    """异步处理单张卡牌"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, process_card, card)
```

### 2. 前端性能优化

#### 组件优化
```typescript
import React, { memo, useMemo, useCallback } from 'react';

// 使用React.memo防止不必要的重渲染
const Card = memo<CardProps>(({ card, onPlay, isPlayable }) => {
  // 使用useMemo缓存计算结果
  const cardCost = useMemo(() => {
    return calculateModifiedCost(card);
  }, [card]);

  // 使用useCallback缓存函数
  const handlePlay = useCallback(() => {
    if (isPlayable) {
      onPlay(card.id);
    }
  }, [card.id, onPlay, isPlayable]);

  return (
    <div onClick={handlePlay}>
      Cost: {cardCost}
      Name: {card.name}
    </div>
  );
});

// 虚拟化长列表
import { FixedSizeList as List } from 'react-window';

const CardList: React.FC<{ cards: Card[] }> = ({ cards }) => {
  const Row = ({ index, style }: { index: number; style: any }) => (
    <div style={style}>
      <Card card={cards[index]} />
    </div>
  );

  return (
    <List
      height={400}
      itemCount={cards.length}
      itemSize={120}
    >
      {Row}
    </List>
  );
};
```

#### 状态管理优化
```typescript
// 使用RTK Query缓存API数据
import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

export const gameApi = createApi({
  reducerPath: 'gameApi',
  baseQuery: fetchBaseQuery({
    baseUrl: '/api/games',
    prepareHeaders: (headers, { getState }) => {
      const token = (getState() as RootState).auth.token;
      if (token) {
        headers.set('authorization', `Bearer ${token}`);
      }
      return headers;
    },
  }),
  tagTypes: ['Game', 'Player'],
  endpoints: (builder) => ({
    getGame: builder.query<Game, string>({
      query: (gameId) => `/${gameId}`,
      providesTags: ['Game'],
    }),
    playCard: builder.mutation<void, PlayCardRequest>({
      query: ({ gameId, ...body }) => ({
        url: `/${gameId}/play-card`,
        method: 'POST',
        body,
      }),
      invalidatesTags: ['Game'],
    }),
  }),
});
```

## 部署和发布

### 1. 构建流程

#### 后端构建
```bash
# 创建requirements.txt锁定版本
pip freeze > requirements.txt

# 构建Docker镜像
docker build -f docker/production/Dockerfile.backend -t cardbattle-backend:latest .

# 推送到镜像仓库
docker push cardbattle-backend:latest
```

#### 前端构建
```bash
# 安装依赖
npm ci --only=production

# 构建生产版本
npm run build

# 构建Docker镜像
docker build -f docker/production/Dockerfile.frontend -t cardbattle-frontend:latest .

# 推送到镜像仓库
docker push cardbattle-frontend:latest
```

### 2. CI/CD流程

#### GitHub Actions配置
```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
          npm install --prefix frontend

      - name: Run tests
        run: |
          cd backend && python -m pytest
          cd ../frontend && npm test

      - name: Code quality check
        run: |
          cd backend && black --check . && isort --check-only .
          cd ../frontend && npm run lint

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3

      - name: Build and push Docker images
        run: |
          docker build -f docker/production/Dockerfile.backend -t cardbattle-backend:${{ github.sha }} .
          docker build -f docker/production/Dockerfile.frontend -t cardbattle-frontend:${{ github.sha }} .

          # 推送到镜像仓库
          echo "${{ secrets.DOCKER_PASSWORD }}" | docker login -u "${{ secrets.DOCKER_USERNAME }}" --password-stdin
          docker push cardbattle-backend:${{ github.sha }}
          docker push cardbattle-frontend:${{ github.sha }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to production
        run: |
          # 部署脚本
          ssh user@server 'cd /app && git pull && docker-compose up -d --build'
```

### 3. 版本管理

#### 语义化版本
```
MAJOR.MINOR.PATCH

MAJOR: 不兼容的API变更
MINOR: 向后兼容的功能新增
PATCH: 向后兼容的问题修正
```

#### 发布流程
1. 更新版本号
2. 更新CHANGELOG.md
3. 创建Git标签
4. 触发CI/CD流程
5. 部署到生产环境

## 总结

本开发指南涵盖了卡牌对战竞技场项目的完整开发流程，包括：

1. **项目结构**: 清晰的代码组织和模块划分
2. **开发环境**: 完整的环境设置和工具配置
3. **开发流程**: 规范的分支管理和代码审查流程
4. **代码规范**: 统一的编码标准和命名规范
5. **测试策略**: 多层次的测试覆盖和质量保证
6. **调试技巧**: 有效的调试方法和工具使用
7. **性能优化**: 前后端性能优化的最佳实践
8. **部署发布**: 自动化的构建、测试和部署流程

遵循本指南可以确保团队开发的高效性和代码质量，为项目的长期维护和发展奠定坚实基础。