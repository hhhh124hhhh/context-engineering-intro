# 🎮 卡牌对战竞技场 V2

## 🎯 项目概述

基于第一次项目开发的深度反思，采用测试先行 (TDD) 方法重新构建的卡牌对战游戏。

### 核心原则
- ✅ **测试先行** - 每个功能先写测试
- ✅ **最小可用** - MVP优先，逐步扩展
- ✅ **真实验证** - 功能测试而非形式检查
- ✅ **持续集成** - 每次提交都验证

### V2 vs V1 关键改进
- **开发方法**: 先测试后实现 vs 先实现后测试
- **复杂度**: 简单架构 vs 复杂架构
- **质量**: 实际功能 vs 形式验证
- **AI使用**: 辅助工具 vs 主导开发

## 🎮 游戏核心玩法

### 回合制卡牌对战
- **法力值系统**: 每回合递增 (1→10)
- **卡牌类型**: 随从、法术、武器、英雄技能
- **游戏流程**: 起手 → 抽牌 → 出牌 → 战斗 → 结束
- **胜负条件**: 对手英雄生命值降至0

### V1.0 目标
- ✅ 本地单机对战 (玩家 vs AI)
- ✅ 基础卡牌效果
- ✅ 简单用户界面
- ✅ 游戏状态持久化

## 🏗️ 技术架构

```
Frontend (React + TypeScript)
    ↓ HTTP API
Backend (FastAPI + Python)
    ↓
Game Engine (Python)
    ↓
Database (SQLite)
```

### 技术栈
- **前端**: React 18 + TypeScript + Vite + Tailwind CSS
- **后端**: FastAPI + Python 3.11 + SQLAlchemy
- **数据库**: SQLite (简化开发)
- **测试**: pytest + Jest + 端到端测试
- **部署**: Docker + GitHub Actions

## 📁 项目结构

```
card-battle-arena-v2/
├── README.md                    # 项目说明
├── docs/                        # 项目文档
├── backend/                     # 后端代码
│   ├── tests/                   # 测试文件
│   ├── app/
│   │   ├── game/                # 游戏核心逻辑
│   │   ├── api/                 # API层
│   │   └── database/            # 数据层
│   └── main.py                  # 应用入口
├── frontend/                    # 前端代码
│   ├── src/
│   │   ├── components/          # React组件
│   │   ├── pages/               # 页面组件
│   │   └── utils/               # 工具函数
│   └── package.json
├── scripts/                     # 脚本文件
└── .github/workflows/           # CI/CD配置
```

## 🚀 快速开始

### 开发环境设置
```bash
# 克隆项目
git clone <repository-url>
cd card-battle-arena-v2

# 设置环境
./scripts/setup.sh

# 启动开发环境
docker-compose up -d

# 运行测试
./scripts/test.sh
```

### 本地开发
```bash
# 后端开发
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py

# 前端开发
cd frontend
npm install
npm run dev
```

## 🧪 测试策略

### 测试层次
1. **单元测试** - 游戏逻辑测试
2. **集成测试** - API测试
3. **端到端测试** - 完整游戏流程测试

### 运行测试
```bash
# 后端测试
cd backend && python -m pytest tests/ -v

# 前端测试
cd frontend && npm test

# 端到端测试
./scripts/test-e2e.sh
```

## 📋 开发流程

### TDD 循环
1. **红** - 编写失败的测试
2. **绿** - 编写最小代码让测试通过
3. **重构** - 优化代码结构
4. **重复** - 继续下一个功能

### 分支策略
- `main` - 稳定版本
- `develop` - 开发版本
- `feature/*` - 功能分支
- `hotfix/*` - 紧急修复

## 🛡️ 质量保证

### 自动化检查
- ✅ 代码格式检查 (Black/Prettier)
- ✅ 代码质量检查 (Ruff/ESLint)
- ✅ 类型检查 (mypy/TypeScript)
- ✅ 安全扫描 (bandit/safety)
- ✅ 测试覆盖率 (>80%)

### CI/CD 流水线
- 代码提交触发自动测试
- 测试通过后自动部署
- 生产环境健康检查

## 📊 项目状态

### V1.0 开发进度
- [x] 项目初始化
- [ ] 游戏引擎核心 (TDD)
- [ ] API层开发
- [ ] 前端界面
- [ ] 集成测试
- [ ] 部署配置

### 质量指标
- **测试覆盖率**: 目标 >80%
- **构建成功率**: 目标 >95%
- **代码质量**: 目标 A级
- **文档完整性**: 目标 100%

## 🤝 贡献指南

### 开发规范
1. 遵循 TDD 开发流程
2. 保持测试覆盖率 >80%
3. 代码必须通过所有检查
4. 提交前运行完整测试

### 提交规范
```bash
# 功能开发
git commit -m "feat: 实现卡牌出牌功能"

# 问题修复
git commit -m "fix: 修复法力值计算错误"

# 重构
git commit -m "refactor: 优化游戏状态管理"
```

## 📚 文档

- [游戏设计文档](docs/GAME_DESIGN.md)
- [API文档](docs/API.md)
- [部署文档](docs/DEPLOYMENT.md)
- [开发指南](docs/DEVELOPMENT.md)

## 🎯 路线图

### V1.0 (当前)
- ✅ 基础游戏引擎
- ✅ 本地AI对战
- ✅ 简单用户界面

### V1.1 (计划)
- 🔄 在线多人对战
- 🔄 更多卡牌效果
- 🔄 用户系统

### V2.0 (未来)
- 📋 排行榜系统
- 📋 锦标赛模式
- 📋 移动端适配

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

**🎮 让我们构建一个真正可用的卡牌对战游戏！**