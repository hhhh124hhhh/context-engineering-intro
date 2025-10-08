# 卡牌对战竞技场 - 部署指南

## 概述

本文档详细说明了如何在不同环境中部署卡牌对战竞技场应用。支持开发环境、测试环境和生产环境的部署。

## 系统要求

### 最低硬件要求
- **CPU**: 2核心
- **内存**: 4GB RAM
- **存储**: 20GB 可用空间
- **网络**: 100Mbps 带宽

### 推荐硬件要求
- **CPU**: 4核心或更多
- **内存**: 8GB RAM或更多
- **存储**: 50GB SSD
- **网络**: 1Gbps 带宽

### 软件要求
- **操作系统**: Ubuntu 20.04+ / CentOS 8+ / Windows 10+ / macOS 11+
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Git**: 2.30+
- **Node.js**: 18.0+ (开发环境)
- **Python**: 3.11+ (开发环境)

## 环境配置

### 开发环境

#### 1. 克隆项目
```bash
git clone https://github.com/cardbattle/card-battle-arena.git
cd card-battle-arena
```

#### 2. 环境变量配置
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量
nano .env
```

**开发环境配置示例**:
```bash
NODE_ENV=development
DEBUG=true
LOG_LEVEL=DEBUG

# 数据库配置
POSTGRES_DB=cardbattle_dev
POSTGRES_USER=cardbattle
POSTGRES_PASSWORD=dev_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
DATABASE_URL=postgresql://cardbattle:dev_password@localhost:5432/cardbattle_dev

# Redis配置
REDIS_URL=redis://localhost:6379/0

# 安全配置
SECRET_KEY=dev_secret_key_change_in_production
JWT_SECRET_KEY=dev_jwt_secret_key_change_in_production

# CORS配置
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

#### 3. 启动开发环境
```bash
# 使用Docker Compose启动
docker-compose up -d

# 或者使用本地开发脚本
./scripts/setup.sh
./scripts/dev-start.sh
```

### 测试环境

#### 1. 环境变量配置
```bash
cp .env.example .env.test
```

**测试环境配置示例**:
```bash
NODE_ENV=testing
DEBUG=false
LOG_LEVEL=INFO

# 数据库配置
POSTGRES_DB=cardbattle_test
POSTGRES_USER=cardbattle_test
POSTGRES_PASSWORD=test_password
DATABASE_URL=postgresql://cardbattle_test:test_password@localhost:5432/cardbattle_test

# Redis配置
REDIS_URL=redis://localhost:6379/1

# 安全配置
SECRET_KEY=test_secret_key_unique
JWT_SECRET_KEY=test_jwt_secret_key_unique
```

#### 2. 运行测试
```bash
# 后端测试
cd backend
python -m pytest tests/ -v --cov=app

# 前端测试
cd frontend
npm test -- --coverage --watchAll=false
```

### 生产环境

#### 1. 服务器准备

##### Ubuntu/Debian
```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 重启以应用用户组更改
sudo reboot
```

##### CentOS/RHEL
```bash
# 更新系统
sudo yum update -y

# 安装Docker
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install -y docker-ce docker-ce-cli containerd.io
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 2. 项目部署

##### 克隆和配置
```bash
# 克隆项目
git clone https://github.com/cardbattle/card-battle-arena.git
cd card-battle-arena

# 配置生产环境变量
cp .env.prod.example .env.prod
nano .env.prod
```

**生产环境配置示例**:
```bash
NODE_ENV=production
DEBUG=false
LOG_LEVEL=INFO

# 数据库配置
POSTGRES_DB=cardbattle_prod
POSTGRES_USER=cardbattle_prod
POSTGRES_PASSWORD=super_secure_password_change_this
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
DATABASE_URL=postgresql://cardbattle_prod:super_secure_password_change_this@postgres:5432/cardbattle_prod

# Redis配置
REDIS_URL=redis://redis:6379/0
REDIS_PASSWORD=redis_secure_password

# 安全配置
SECRET_KEY=your_super_secret_key_change_this_in_production
JWT_SECRET_KEY=your_jwt_secret_key_change_this_in_production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# 域名配置
DOMAIN=yourdomain.com
HTTP_PORT=80
HTTPS_PORT=443

# SSL配置
SSL_CERT_PATH=/etc/ssl/certs/yourdomain.crt
SSL_KEY_PATH=/etc/ssl/private/yourdomain.key

# 监控配置
PROMETHEUS_PORT=9090
GRAFANA_PORT=3001
GRAFANA_PASSWORD=secure_grafana_password
```

##### SSL证书配置

**使用Let's Encrypt (推荐)**:
```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx

# 获取SSL证书
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# 设置自动续期
sudo crontab -e
# 添加以下行
0 12 * * * /usr/bin/certbot renew --quiet
```

**使用自签名证书 (仅开发测试)**:
```bash
# 创建SSL目录
sudo mkdir -p /etc/ssl/private

# 生成自签名证书
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/ssl/private/yourdomain.key \
    -out /etc/ssl/certs/yourdomain.crt \
    -subj "/C=CN/ST=State/L=City/O=Organization/CN=yourdomain.com"
```

##### 部署应用
```bash
# 使用生产部署脚本
chmod +x scripts/deploy.sh
./scripts/deploy.sh

# 或者手动部署
docker-compose -f docker-compose.prod.yml up -d --build

# 等待服务启动
sleep 30

# 检查服务状态
docker-compose -f docker-compose.prod.yml ps

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f
```

## Docker配置

### 开发环境Dockerfile

**后端 (docker/development/Dockerfile.backend)**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 开发模式启动
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

**前端 (docker/development/Dockerfile.frontend)**:
```dockerfile
FROM node:18-alpine

WORKDIR /app

# 安装依赖
COPY package*.json ./
RUN npm install

# 复制源代码
COPY . .

# 开发模式启动
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
```

### 生产环境Dockerfile

**后端 (docker/production/Dockerfile.backend)**:
```dockerfile
FROM python:3.11-slim as builder

WORKDIR /app

# 安装构建依赖
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 生产环境
FROM python:3.11-slim

WORKDIR /app

# 安装运行时依赖
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 从构建阶段复制依赖
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 创建非root用户
RUN useradd --create-home --shell /bin/bash app
USER app

# 复制应用代码
COPY --chown=app:app . .

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 生产模式启动
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

**前端 (docker/production/Dockerfile.frontend)**:
```dockerfile
FROM node:18-alpine as builder

WORKDIR /app

# 安装依赖
COPY package*.json ./
RUN npm ci --only=production

# 复制源代码并构建
COPY . .
RUN npm run build

# 生产环境
FROM nginx:alpine

# 复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制nginx配置
COPY nginx.conf /etc/nginx/nginx.conf

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:80/health || exit 1

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

## 数据库管理

### PostgreSQL配置

#### 主从复制配置
**主数据库 (postgres-master.conf)**:
```conf
# 连接设置
listen_addresses = '*'
port = 5432

# 复制设置
wal_level = replica
max_wal_senders = 3
max_replication_slots = 3
synchronous_commit = on
synchronous_standby_names = 'standby1'
```

**从数据库 (postgres-slave.conf)**:
```conf
# 连接设置
listen_addresses = '*'
port = 5432

# 复制设置
hot_standby = on
max_standby_streaming_delay = 30s
max_standby_archive_delay = 30s
```

#### 备份策略
```bash
#!/bin/bash
# backup-database.sh

BACKUP_DIR="/backups/postgres"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="cardbattle_prod"

# 创建备份目录
mkdir -p $BACKUP_DIR

# 执行备份
docker exec postgres-container pg_dump -U cardbattle_prod $DB_NAME > $BACKUP_DIR/backup_$DATE.sql

# 压缩备份文件
gzip $BACKUP_DIR/backup_$DATE.sql

# 删除7天前的备份
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete

echo "数据库备份完成: backup_$DATE.sql.gz"
```

### Redis配置

#### Redis集群配置
```conf
# redis-cluster.conf
port 7000
cluster-enabled yes
cluster-config-file nodes.conf
cluster-node-timeout 5000
appendonly yes

# 持久化配置
save 900 1
save 300 10
save 60 10000
```

## 监控和日志

### Prometheus配置

**prometheus.yml**:
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "rules/*.yml"

scrape_configs:
  - job_name: 'cardbattle-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'

  - job_name: 'cardbattle-frontend'
    static_configs:
      - targets: ['frontend:80']

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']

  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx-exporter:9113']
```

### Grafana仪表板

#### 系统监控仪表板
- CPU使用率
- 内存使用率
- 磁盘使用率
- 网络流量

#### 应用监控仪表板
- API响应时间
- 请求成功率
- 并发用户数
- 游戏会话数

#### 数据库监控仪表板
- 数据库连接数
- 查询性能
- 复制延迟
- 备份状态

### 日志配置

**logrotate配置**:
```
/var/log/cardbattle/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 app app
    postrotate
        docker kill -s USR1 cardbattle-backend
    endscript
}
```

## 性能优化

### 数据库优化
```sql
-- 创建索引
CREATE INDEX idx_users_rating ON users(rating DESC);
CREATE INDEX idx_games_status ON games(status);
CREATE INDEX idx_game_moves_timestamp ON game_moves(timestamp);

-- 分区表
CREATE TABLE game_moves_2024_01 PARTITION OF game_moves
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
```

### 缓存策略
```python
# Redis缓存配置
CACHE_CONFIG = {
    'user_profile': {'ttl': 3600},      # 1小时
    'card_data': {'ttl': 86400},        # 24小时
    'leaderboard': {'ttl': 300},        # 5分钟
    'game_state': {'ttl': 7200},        # 2小时
}
```

### CDN配置
```nginx
# 静态资源CDN配置
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
    add_header X-CDN "Cloudflare";
}
```

## 安全配置

### 防火墙设置
```bash
# UFW配置
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### SSL/TLS配置
```nginx
# SSL配置
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
ssl_prefer_server_ciphers off;
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;
```

### 安全头配置
```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header X-Frame-Options DENY always;
add_header X-Content-Type-Options nosniff always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

## 故障排除

### 常见问题

#### 1. 容器启动失败
```bash
# 检查容器状态
docker-compose ps

# 查看容器日志
docker-compose logs <service_name>

# 重启容器
docker-compose restart <service_name>
```

#### 2. 数据库连接失败
```bash
# 检查数据库容器
docker exec -it postgres-container psql -U cardbattle_prod -d cardbattle_prod

# 测试连接
docker exec postgres-container pg_isready
```

#### 3. SSL证书问题
```bash
# 检查证书有效期
openssl x509 -in /etc/ssl/certs/yourdomain.crt -text -noout

# 测试nginx配置
nginx -t

# 重新加载nginx
nginx -s reload
```

#### 4. 性能问题
```bash
# 检查系统资源
htop
iostat -x 1
free -h

# 检查数据库性能
docker exec postgres-container psql -U cardbattle_prod -d cardbattle_prod -c "SELECT * FROM pg_stat_activity;"

# 检查应用日志
docker-compose logs -f backend | grep ERROR
```

### 监控告警
```yaml
# Prometheus告警规则
groups:
  - name: cardbattle
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "高错误率告警"
          description: "错误率超过5%"

      - alert: DatabaseDown
        expr: up{job="postgres"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "数据库服务下线"
          description: "PostgreSQL数据库无法访问"
```

## 维护操作

### 滚动更新
```bash
# 零停机更新
docker-compose -f docker-compose.prod.yml up -d --no-deps backend
docker-compose -f docker-compose.prod.yml up -d --no-deps frontend
```

### 数据迁移
```bash
# 运行数据库迁移
docker exec backend-container alembic upgrade head

# 回滚迁移
docker exec backend-container alembic downgrade -1
```

### 定期维护
```bash
#!/bin/bash
# maintenance.sh

# 清理Docker镜像
docker system prune -f

# 清理日志文件
find /var/log/cardbattle -name "*.log" -mtime +30 -delete

# 更新系统
sudo apt update && sudo apt upgrade -y

echo "维护任务完成"
```

## 扩展部署

### 水平扩展
```yaml
# docker-compose.scale.yml
version: '3.8'
services:
  backend:
    deploy:
      replicas: 3

  nginx:
    depends_on:
      - backend
    configs:
      - source: nginx_lb_config
        target: /etc/nginx/conf.d/load-balancer.conf
```

### 多区域部署
```bash
# 配置多区域负载均衡
# 1. 设置多个地理位置的服务器
# 2. 配置DNS轮询或GeoDNS
# 3. 设置数据库同步
# 4. 配置跨区域缓存同步
```

## 总结

本部署指南涵盖了卡牌对战竞技场应用的完整部署流程，包括：

1. **环境准备**: 系统要求和软件依赖
2. **配置管理**: 开发、测试、生产环境配置
3. **容器化**: Docker配置和镜像构建
4. **数据库**: PostgreSQL配置、备份和优化
5. **监控**: Prometheus、Grafana和日志管理
6. **安全**: SSL/TLS、防火墙和安全头配置
7. **运维**: 故障排除、维护操作和扩展部署

遵循本指南可以确保应用在不同环境中的稳定、安全和高效运行。