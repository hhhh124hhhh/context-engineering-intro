# 前端依赖修复指南

## 问题描述

在运行前端开发服务器时，可能会遇到以下错误：

```
[plugin:vite:css] [postcss] Cannot find module '@tailwindcss/forms'
```

## 临时解决方案 (已实施)

为了快速解决依赖问题，我已经修改了 `tailwind.config.js` 文件，移除了插件依赖。现在前端应该可以正常启动，无需安装额外的插件。

## 解决方案

### 方法1: 直接启动 (推荐)

```bash
cd frontend
npm install
npm run dev
```

### 方法2: 如果仍需要完整的插件功能

如果你想使用 `@tailwindcss/forms` 和 `@tailwindcss/typography` 插件的完整功能，可以按以下步骤操作：

```bash
# 进入前端目录
cd frontend

# 安装缺失的依赖
npm install @tailwindcss/forms@^0.5.3 @tailwindcss/typography@^0.5.9

# 更新 tailwind.config.js 文件，在 plugins 数组中添加：
// plugins: [
//   require('@tailwindcss/forms'),
//   require('@tailwindcss/typography'),
// ],

# 启动开发服务器
npm run dev
```

## 配置文件说明

项目现在使用简化的 `tailwind.config.js` 配置文件，移除了插件依赖以确保开箱即用。如果需要完整插件功能，可以按方法2安装插件并更新配置。

## 验证修复

修复完成后，你应该能看到：

1. 依赖安装成功，没有错误
2. `npm run dev` 正常启动
3. Tailwind CSS 样式正常加载
4. 浏览器中显示正确的样式

## 如果仍有问题

如果修复后仍有问题，请尝试：

```bash
# 清理缓存
npm cache clean --force

# 删除所有可能的缓存文件
rm -rf node_modules package-lock.json .vite dist

# 重新安装
npm install

# 重新启动
npm run dev
```

## 其他可能的问题

### 1. Node.js 版本问题
确保使用 Node.js 18+：
```bash
node --version  # 应该显示 v18.x.x 或更高
```

### 2. 网络问题
如果 npm 安装失败，可以尝试：
```bash
# 使用淘宝镜像
npm config set registry https://registry.npmmirror.com/

# 或者使用 yarn
yarn install
```

### 3. 权限问题
如果遇到权限错误：
```bash
# 使用 npx (推荐)
npx tailwindcss -i ./src/index.css -o ./dist/output.css

# 或者修复 npm 权限
npm config set prefix ~/.npm-global
export PATH=~/.npm-global/bin:$PATH
```

## 完整的开发环境启动

修复完成后，启动完整开发环境：

```bash
# 启动后端 (在另一个终端)
cd backend
source venv/bin/activate  # 或 Windows: venv\Scripts\activate
uvicorn main:app --reload

# 启动前端
cd frontend
npm run dev

# 启动数据库 (如果需要)
docker-compose up -d postgres redis
```

访问 `http://localhost:3000` 查看应用。