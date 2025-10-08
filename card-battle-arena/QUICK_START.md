# 卡牌对战竞技场 - 快速启动指南

## 前言

欢迎使用卡牌对战竞技场！这是一个使用现代Web技术栈构建的多人在线卡牌对战游戏。本指南将帮助您快速启动和运行项目。

## 系统要求

- **Node.js**: 18.0+
- **Python**: 3.11+
- **Docker**: 20.10+ (可选，用于容器化部署)
- **Git**: 用于版本控制

## 快速启动

### 1. 克隆项目
```bash
git clone https://github.com/cardbattle/card-battle-arena.git
cd card-battle-arena
```

### 2. 启动前端应用
```bash
cd frontend
npm install
npm run dev
```

前端将在 `http://localhost:3000` 启动

### 3. 启动后端应用
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload
```

后端API将在 `http://localhost:8000` 启动

### 4. 使用Docker (推荐)
```bash
# 启动数据库服务
docker-compose up -d postgres redis

# 启动完整应用
docker-compose up
```

## 访问地址

启动成功后，您可以访问：

- **前端应用**: http://localhost:3000
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **API交互文档**: http://localhost:8000/redoc

## 常见问题

### 问题1: 前端启动失败
如果遇到 `@tailwindcss/forms` 错误，请查看 `FRONTEND_FIX.md` 文件。

### 问题2: 数据库连接失败
确保PostgreSQL服务正在运行：
```bash
docker-compose up -d postgres
```

### 问题3: 端口冲突
如果端口被占用，可以修改端口配置：
- 前端：修改 `vite.config.ts` 中的 `server.port`
- 后端：修改 `uvicorn` 命令中的 `--port` 参数

## 开发工具

项目提供了多个开发工具脚本：

```bash
# 环境设置
./scripts/setup.sh

# 质量检查
./scripts/quality-check.sh

# 健康检查
./scripts/health-check.sh

# 部署到生产环境
./scripts/deploy.sh
```

## 项目结构

```
card-battle-arena/
├── frontend/          # React前端应用
│   ├── src/
│   │   ├── components/  # React组件
│   │   ├── pages/      # 页面组件
│   │   ├── hooks/      # 自定义Hooks
│   │   └── services/   # API服务
│   └── package.json
├── backend/           # FastAPI后端应用
│   ├── app/
│   │   ├── api/       # API路由
│   │   ├── core/      # 核心业务逻辑
│   │   ├── models/    # 数据模型
│   │   └── utils/     # 工具函数
│   ├── tests/         # 测试文件
│   └── main.py        # 应用入口
├── scripts/           # 部署和工具脚本
├── nginx/            # Nginx配置
├── monitoring/       # 监控配置
└── docker-compose.yml # Docker编排文件
```

## 功能特性

- ✅ **多人实时对战** - WebSocket实现的流畅对战体验
- ✅ **智能匹配系统** - 基于ELO积分的公平匹配
- ✅ **丰富卡牌系统** - 200+卡牌，多种效果组合
- ✅ **卡组编辑器** - 可视化卡组构建工具
- ✅ **用户系统** - 注册、登录、个人资料
- ✅ **响应式设计** - 适配桌面和移动设备

## 技术栈

### 前端
- **React 18** - 现代化UI框架
- **TypeScript** - 类型安全的JavaScript
- **Vite** - 快速构建工具
- **Tailwind CSS** - 实用优先的CSS框架
- **Framer Motion** - 流畅的动画库

### 后端
- **FastAPI** - 高性能异步Web框架
- **Python 3.11+** - 现代Python语言
- **SQLAlchemy** - 强大的ORM框架
- **PostgreSQL** - 可靠的关系型数据库
- **WebSocket** - 实时双向通信

## 开发指南

详细的开发指南请参考：
- [开发指南](DEVELOPMENT.md) - 完整的开发文档
- [API文档](API_DOCS.md) - API接口文档
- [部署指南](DEPLOYMENT.md) - 部署配置说明

## 测试

```bash
# 前端测试
cd frontend
npm test

# 后端测试
cd backend
python -m pytest

# 完整项目验证
./scripts/simple-verification.sh
```

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 支持

如果您遇到问题或有建议，请：

1. 查看 [FRONTEND_FIX.md](FRONTEND_FIX.md) 了解常见问题解决方案
2. 检查 [ISSUES](https://github.com/cardbattle/card-battle-arena/issues) 页面
3. 创建新的 Issue 描述您的问题

## 致谢

感谢所有为这个项目做出贡献的开发者和社区成员！

---

**🎮 祝您游戏愉快！**