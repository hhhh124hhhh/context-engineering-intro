## FEATURE:
构建一个现代化的Web端多人联机卡牌对战游戏：

### 前端技术栈要求：
- **React 18 + TypeScript** - 现代化UI框架，类型安全
- **Tailwind CSS + Framer Motion** - 响应式设计和流畅动画效果
- **Socket.io-client** - 实时WebSocket通信
- **React Query + Zustand** - 数据管理和轻量级状态管理
- **React Hook Form** - 表单处理和验证

### 后端技术栈要求：
- **FastAPI + WebSocket** - 高性能异步后端框架
- **SQLAlchemy + PostgreSQL** - 数据持久化和关系型数据库
- **Redis** - 会话管理和实时数据缓存
- **Pydantic** - 数据验证和序列化
- **JWT** - 安全的身份认证系统

### 核心游戏功能：
- **实时对战系统**：1v1实时卡牌对战，WebSocket低延迟通信
- **卡牌机制**：200+张独特卡牌，包含法术、随从、武器等类型
- **智能匹配系统**：基于ELO积分的公平匹配算法
- **排位赛系统**：完整的赛季、段位、奖励机制
- **卡组构建器**：拖拽式可视化卡组编辑界面
- **社交功能**：好友系统、实时聊天、观战模式

### 用户体验要求：
- **响应式设计**：完美支持桌面和移动端
- **性能优化**：首屏加载<3秒，游戏动画60fps
- **离线功能**：PWA支持，离线卡组编辑
- **国际化**：中英文双语界面
- **无障碍访问**：符合WCAG 2.1 AA标准

## EXAMPLES:
在 `examples/` 文件夹中包含以下参考示例：

- `examples/frontend/` - React组件最佳实践、状态管理模式、TypeScript类型定义
- `examples/websocket/` - WebSocket连接管理、实时事件处理、断线重连机制
- `examples/game_logic/` - 游戏状态同步、回合制逻辑、卡牌效果处理
- `examples/ai_systems/` - 匹配算法、平衡性分析、玩家行为预测

这些示例展示了项目应该遵循的代码架构、设计模式和最佳实践。请参考这些示例来构建具有相似架构和质量的应用。

## DOCUMENTATION:
需要参考以下技术文档：

- React 18文档：https://react.dev/ - 现代React特性、Hooks使用、并发渲染
- FastAPI文档：https://fastapi.tiangolo.com/ - 异步编程、WebSocket支持、依赖注入
- Socket.io文档：https://socket.io/docs/ - 实时通信、房间管理、事件处理
- Tailwind CSS：https://tailwindcss.com/docs/ - 原子化CSS、响应式设计
- Framer Motion：https://www.framer.com/motion/ - 动画库、手势识别、性能优化
- PostgreSQL文档：https://www.postgresql.org/docs/ - 数据库设计、索引优化、事务处理
- Redis文档：https://redis.io/documentation - 缓存策略、数据结构、持久化

## OTHER CONSIDERATIONS:
- **防作弊机制**：服务端验证所有游戏操作，随机数种子同步
- **可扩展架构**：微服务设计，支持水平扩展和负载均衡
- **数据安全**：GDPR合规，数据加密，安全审计
- **监控和日志**：性能监控、错误追踪、用户行为分析
- **CI/CD流水线**：自动化测试、构建、部署流程
- **成本控制**：云资源优化，CDN使用，数据库查询优化
- **用户留存**：成就系统、每日任务、赛季奖励机制
- **社区建设**：玩家论坛、攻略分享、电竞赛事支持

特别注意避免常见的游戏开发陷阱：
- 不要在前端进行关键游戏逻辑计算
- 不要忽视网络延迟和断线处理
- 不要过度承诺无法实现的功能
- 忽略移动端适配和性能优化
- 忘记数据备份和灾难恢复方案