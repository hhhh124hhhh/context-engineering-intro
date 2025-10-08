# 卡牌对战竞技场 (Card Battle Arena)

一个基于Web的多人在线卡牌对战游戏，采用现代技术栈构建，提供流畅的游戏体验和实时对战功能。

## 🎮 游戏特色

- **实时多人对战** - 基于WebSocket的实时游戏通信
- **智能匹配系统** - 基于ELO积分的公平匹配算法
- **丰富的卡牌系统** - 多种职业、稀有度和技能组合
- **卡组编辑器** - 直观的卡组构建和管理工具
- **观战模式** - 观看其他玩家的精彩对局
- **天梯排名** - 竞技排名和赛季奖励系统

## 🏗️ 技术架构

### 前端技术栈
- **React 18** - 现代化UI框架
- **TypeScript** - 类型安全的JavaScript
- **Vite** - 快速的构建工具
- **Tailwind CSS** - 实用优先的CSS框架
- **Framer Motion** - 流畅的动画库
- **React Query** - 数据获取和状态管理
- **Socket.io Client** - WebSocket客户端

### 后端技术栈
- **FastAPI** - 高性能异步Web框架
- **Python 3.11+** - 现代Python语言
- **SQLAlchemy** - 强大的ORM框架
- **PostgreSQL** - 可靠的关系型数据库
- **Redis** - 高性能缓存和会话存储
- **WebSocket** - 实时双向通信
- **JWT** - 安全的身份认证
- **Docker** - 容器化部署

## 🚀 快速开始

### 环境要求

- Node.js 18+
- Python 3.11+
- PostgreSQL 14+
- Redis 6+
- Docker & Docker Compose (可选)

### 本地开发设置

1. **克隆项目**
```bash
git clone <repository-url>
cd card-battle-arena
```

2. **后端设置**
```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 设置环境变量
cp .env.example .env
# 编辑 .env 文件，配置数据库连接等

# 运行数据库迁移
alembic upgrade head

# 启动后端服务
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

3. **前端设置**
```bash
cd frontend

# 安装依赖
npm install

# 设置环境变量
cp .env.example .env.local
# 编辑 .env.local 文件

# 启动开发服务器
npm run dev
```

4. **数据库初始化**
```bash
cd backend

# 创建基础数据
python scripts/init_data.py

# 启动Redis服务
redis-server
```

### 使用Docker Compose

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### Windows环境快速启动

项目提供了专门的Windows启动脚本：

```powershell
# 使用批处理脚本启动（交互式菜单）
scripts\start-windows.bat

# 使用简化脚本快速启动
scripts\quick-start.bat

# 使用PowerShell脚本启动
powershell -ExecutionPolicy Bypass -File scripts\quick-start.ps1
```

## 📁 项目结构

```
card-battle-arena/
├── backend/                 # 后端服务
│   ├── app/
│   │   ├── core/           # 核心功能模块
│   │   │   ├── auth/       # 认证授权
│   │   │   ├── game/       # 游戏引擎
│   │   │   └── matchmaking/ # 匹配系统
│   │   ├── models/         # 数据模型
│   │   ├── routes/         # API路由
│   │   ├── schemas/        # Pydantic模型
│   │   └── utils/          # 工具函数
│   ├── tests/              # 测试文件
│   ├── alembic/            # 数据库迁移
│   ├── scripts/            # 脚本文件
│   └── main.py             # 应用入口
├── frontend/               # 前端应用
│   ├── src/
│   │   ├── components/     # React组件
│   │   │   ├── ui/         # 基础UI组件
│   │   │   ├── game/       # 游戏界面组件
│   │   │   ├── deck/       # 卡组管理组件
│   │   │   └── matchmaking/ # 匹配系统组件
│   │   ├── hooks/          # 自定义Hook
│   │   ├── types/          # TypeScript类型
│   │   ├── utils/          # 工具函数
│   │   └── assets/         # 静态资源
│   ├── public/             # 公共文件
│   └── tests/              # 测试文件
├── docs/                   # 文档
├── docker-compose.yml      # Docker编排文件
├── .gitignore             # Git忽略文件
└── README.md              # 项目说明
```

## 🎯 核心功能

### 游戏玩法
- **回合制对战** - 玩家轮流出牌和攻击
- **法力值系统** - 每回合获得法力值用于出牌
- **多种卡牌类型** - 随从、法术、武器、英雄技能
- **特殊效果** - 战吼、亡语、圣盾、风怒等
- **胜负条件** - 将对手生命值降至0

### 匹配系统
- **ELO积分匹配** - 根据玩家水平匹配对手
- **多种游戏模式** - 天梯、休闲、练习、友谊赛
- **动态扩展** - 根据等待时间扩大匹配范围
- **实时状态** - WebSocket实时更新匹配状态

### 卡组管理
- **可视化编辑器** - 拖拽式卡组构建
- **卡牌筛选** - 多条件筛选和搜索
- **统计分析** - 法力曲线、类型分布等
- **导入导出** - 支持多种格式的卡组分享

## 🔧 API文档

启动后端服务后，访问以下地址查看API文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 主要API端点

#### 认证相关
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/refresh` - 刷新令牌
- `GET /api/auth/me` - 获取当前用户信息

#### 游戏相关
- `POST /api/game/create` - 创建游戏
- `GET /api/game/{game_id}` - 获取游戏状态
- `POST /api/game/{game_id}/play` - 出牌
- `POST /api/game/{game_id}/attack` - 攻击
- `POST /api/game/{game_id}/end-turn` - 结束回合

#### 卡组相关
- `GET /api/decks` - 获取卡组列表
- `POST /api/decks` - 创建卡组
- `PUT /api/decks/{deck_id}` - 更新卡组
- `DELETE /api/decks/{deck_id}` - 删除卡组

#### 匹配相关
- `POST /api/matchmaking/request` - 开始匹配
- `DELETE /api/matchmaking/request` - 取消匹配
- `GET /api/matchmaking/status` - 获取匹配状态

## 🧪 测试

### 后端测试
```bash
cd backend

# 安装测试依赖
pip install -r requirements-test.txt

# 运行所有测试
python run_tests.py test

# 运行特定测试
python run_tests.py unit
python run_tests.py integration
python run_tests.py coverage

# 代码检查
python run_tests.py lint
python run_tests.py format
```

### 前端测试
```bash
cd frontend

# 运行所有测试
npm test

# 运行测试并生成覆盖率报告
npm run test:coverage

# 交互式测试模式
npm run test:watch

# 代码检查
npm run lint
npm run type-check
```

## 📦 部署

### 生产环境部署

1. **使用Docker Compose**
```bash
# 构建生产镜像
docker-compose -f docker-compose.prod.yml build

# 启动生产服务
docker-compose -f docker-compose.prod.yml up -d

# 查看服务状态
docker-compose -f docker-compose.prod.yml ps
```

2. **环境变量配置**
```bash
# 生产环境变量
NODE_ENV=production
DATABASE_URL=postgresql://user:pass@localhost:5432/cardbattle
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
```

3. **反向代理配置 (Nginx)**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 开发规范
- 遵循 PEP8 (Python) 和 ESLint (JavaScript) 代码规范
- 编写单元测试覆盖新功能
- 提交信息使用清晰的格式
- 更新相关文档

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🆘 支持

如果您遇到问题或有建议，请：

1. 查看 [FAQ](docs/FAQ.md)
2. 搜索现有的 [Issues](../../issues)
3. 创建新的 Issue 描述问题
4. 加入我们的 [Discord 社区](https://discord.gg/cardbattle)

## 🗺️ 路线图

### v1.0 (当前版本)
- ✅ 基础游戏功能
- ✅ 实时对战系统
- ✅ 卡组编辑器
- ✅ 匹配系统

### v1.1 (计划中)
- 🔄 锦标赛模式
- 🔄 观战模式增强
- 🔄 排行榜系统
- 🔄 成就系统

### v1.2 (未来版本)
- 📋 公会系统
- 📋 卡牌收集系统
- 📋 皮肤和装饰品
- 📋 移动端适配

## 📊 项目统计

- **代码行数**: ~15,000+ 行
- **测试覆盖率**: 80%+
- **支持语言**: 中文、英文
- **支持平台**: Web, 移动端 (计划中)

---

**开发者**: Card Battle Arena Team
**最后更新**: 2024年1月
**版本**: 1.0.0