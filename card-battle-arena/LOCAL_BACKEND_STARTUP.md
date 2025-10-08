# 本地启动后端服务指南

本文档说明如何在本地环境中启动Card Battle Arena项目的后端服务，而不是通过Docker容器运行。

## 前提条件

1. 已安装Python 3.11
2. 已安装PostgreSQL和Redis服务（通过Docker运行）

## 步骤

### 1. 启动基础设施服务

首先，确保PostgreSQL和Redis服务正在运行：

```bash
cd d:\context-engineering-intro\card-battle-arena
docker-compose up -d postgres redis
```

### 2. 创建并激活Python虚拟环境

```bash
cd d:\context-engineering-intro\card-battle-arena\backend
python -m venv venv
venv\Scripts\activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

项目根目录已包含.env文件，其中包含必要的环境变量配置。

### 5. 启动后端服务

```bash
python main.py
```

后端服务将在 http://localhost:8000 上运行。

## 验证服务

启动所有服务后，您可以访问以下URL来验证它们是否正常工作：

- 前端：http://localhost:5173
- 后端API文档：http://localhost:8000/docs
- PostgreSQL：localhost:5432
- Redis：localhost:6379

## 停止服务

要停止服务，请执行以下操作：

1. 在后端服务运行的终端中按 `Ctrl+C` 停止后端服务
2. 停止Docker容器：
   ```bash
   cd d:\context-engineering-intro\card-battle-arena
   docker-compose down
   ```

## 故障排除

如果遇到任何问题，请检查：

1. 确保所有环境变量都已正确配置
2. 确保PostgreSQL和Redis服务正在运行
3. 检查是否有端口冲突
4. 确保所有Python依赖都已正确安装