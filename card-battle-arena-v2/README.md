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
main.py (统一游戏入口)
    ↓
CLI模块 (命令行接口 + 游戏启动器)
    ↓
配置系统 (游戏设置 + 模式定义)
    ↓
游戏引擎 (核心逻辑 + Pygame渲染)
    ↓
Demo脚本 (各种游戏模式演示)
```

### 技术栈
- **主语言**: Python 3.12
- **游戏引擎**: Pygame 2.6+
- **数值计算**: NumPy
- **架构模式**: TDD (测试驱动开发)
- **代码质量**: 模块化设计，每个文件<500行
- **测试框架**: pytest
- **开发方法**: RED-GREEN-REFACTOR循环

## 📁 项目结构

```
card-battle-arena-v2/
├── README.md                    # 项目说明
├── main.py                      # 🎯 统一游戏入口
├── cli/                         # 命令行接口模块
│   ├── __init__.py
│   ├── parser.py                # 命令行参数解析
│   ├── launcher.py              # 游戏启动器
│   └── exceptions.py            # CLI异常定义
├── config/                      # 配置系统模块
│   ├── __init__.py
│   ├── settings.py              # 游戏配置管理
│   ├── game_modes.py            # 游戏模式定义
│   ├── exceptions.py            # 配置异常定义
│   └── default_settings.json    # 默认配置文件
├── tests/                       # 测试模块
│   ├── __init__.py
│   ├── test_main.py             # 主脚本TDD测试
│   └── test_integration.py      # 集成测试
├── scripts/                     # 脚本文件
│   └── start_game.sh            # 游戏启动脚本
└── backend/                     # 游戏核心代码
    ├── app/                     # 游戏引擎
    │   ├── game/                # 游戏核心逻辑
    │   └── visualization/       # 渲染系统
    │       ├── ui/              # UI组件系统
    │       └── tests/           # UI测试
    ├── interactive_game.py      # 新建：真正可玩的交互式游戏
    └── *demo*.py               # 各种演示脚本
```

## 🚀 快速开始

### 系统要求
- Python 3.8+
- Pygame 2.0+

### 安装依赖
```bash
# 安装游戏依赖
pip install pygame
```

### 启动游戏

#### 方法1: 使用统一入口 (推荐)
```bash
# 默认AI对战模式
python main.py

# 选择游戏模式
python main.py --mode ai-vs-player    # AI对战模式
python main.py --mode interactive     # 交互式模式
python main.py --mode demo            # 演示模式

# 使用自定义配置
python main.py --config config/custom.json

# 启用详细输出
python main.py --verbose

# 查看帮助
python main.py --help
```

#### 方法2: 使用启动脚本
```bash
# 使用启动脚本 (Linux/Mac)
./scripts/start_game.sh --mode demo

# 或直接运行
bash scripts/start_game.sh --help
```

### 配置游戏
```bash
# 复制默认配置
cp config/default_settings.json config/my_settings.json

# 编辑配置文件
nano config/my_settings.json

# 使用自定义配置启动
python main.py --config config/my_settings.json```

### 运行测试
```bash
# 运行集成测试
python tests/test_integration.py

# 运行TDD测试 (需要pytest)
python -m pytest tests/ -v
```

## 🎮 游戏模式

### AI对战模式 (ai-vs-player)
- **描述**: 与智能AI进行策略对战，体验完整的游戏功能
- **脚本**: `backend/pygame_vs_ai_demo.py`
- **特点**: 完整UI设计，视觉反馈，智能AI对手
- **启动**: `python main.py --mode ai-vs-player`

### 简化AI模式 (ai)
- **描述**: 快速体验AI对战功能，简化版游戏流程
- **脚本**: `backend/simple_ai_demo.py`
- **特点**: 快速对战，简洁界面，基础AI逻辑
- **启动**: `python main.py --mode ai`

### 交互式模式 (interactive)
- **描述**: 真正可玩的卡牌游戏，支持鼠标点击和拖拽操作
- **脚本**: `backend/interactive_game.py`
- **特点**: 鼠标点击选牌、拖拽出牌、实时UI更新
- **启动**: `python main.py --mode interactive`
- **操作**:
  - 鼠标左键：选择/取消选择卡牌
  - 鼠标拖拽：将手牌拖拽到战场出牌
  - 空格键：结束回合
  - ESC键：取消选择

### 演示模式 (demo)
- **描述**: 自动展示游戏各种功能和特效
- **脚本**: `backend/visual_demo.py`
- **特点**: 自动播放，教学展示，功能演示
- **启动**: `python main.py --mode demo`

## ⚙️ 配置选项

### 显示设置
- `window_width`: 窗口宽度 (默认: 1200)
- `window_height`: 窗口高度 (默认: 800)
- `fps`: 帧率 (默认: 60)
- `fullscreen`: 全屏模式 (默认: false)

### AI设置
- `ai_thinking_time`: AI思考时间秒数 (默认: 1.5)
- `ai_difficulty`: AI难度 easy/normal/hard (默认: normal)
- `ai_personality`: AI性格 (默认: balanced)

### 游戏设置
- `max_turns`: 最大回合数 (默认: 15)
- `turn_time_limit`: 回合时间限制秒数 (默认: 30)
- `sound_enabled`: 启用声音 (默认: true)
- `music_volume`: 音乐音量 0.0-1.0 (默认: 0.7)

## 🛠️ 开发指南

### TDD开发流程
1. **RED阶段**: 编写失败的测试用例
2. **GREEN阶段**: 实现最小功能让测试通过
3. **REFACTOR阶段**: 重构优化代码结构

### 代码规范
- 每个文件不超过500行代码
- 函数必须有文档字符串
- 使用类型提示
- 遵循PEP8格式规范

### 添加新游戏模式
1. 在`config/game_modes.py`中定义新模式
2. 在`backend/`中创建对应的demo脚本
3. 在`cli/launcher.py`中添加启动逻辑
4. 编写对应的测试用例

### 扩展配置选项
1. 在`config/settings.py`中添加新的配置项
2. 更新`default_settings.json`
3. 添加配置验证逻辑
4. 在CLI解析器中添加对应参数
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