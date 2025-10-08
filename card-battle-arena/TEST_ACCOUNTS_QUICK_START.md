# 🎮 测试账号快速开始指南

## ⚡ 快速修复

### 问题1: bcrypt密码长度错误
✅ **已修复** - 使用新脚本 `create_test_users_fixed.py`

### 问题2: 数据库关系错误
✅ **已修复** - 更新了User模型中的关系定义

### 问题3: WSL内存限制
✅ **已修复** - 创建了 `.wslconfig` 配置文件

## 🚀 立即使用

### 1. 运行修复后的测试账号脚本

```bash
# 进入后端目录
cd backend

# 激活虚拟环境
venv\Scripts\activate

# 运行修复后的脚本
python scripts/create_test_users_fixed.py
```

### 2. 测试账号列表

| 用户名 | 密码 | ELO | 说明 |
|--------|------|-----|------|
| admin | Test123 | 2500 | 管理员 |
| testuser | Test123 | 1000 | 普通用户 |
| newbie | Test123 | 800 | 新手 |
| master | Test123 | 2800 | 大师 |
| grandmaster | Test123 | 3000 | 宗师 |

### 3. 前端登录测试

1. 访问 http://localhost:5173
2. 使用任意测试账号登录
3. 验证功能正常

## 🔧 WSL内存配置 (可选)

如果Docker仍有内存问题：

1. **复制配置文件**：
   ```bash
   # 将 .wslconfig 复制到用户目录
   cp .wslconfig ~/.wslconfig
   ```

2. **重启WSL**：
   ```bash
   # 在Windows PowerShell中执行
   wsl --shutdown
   wsl
   ```

## 📝 脚本使用选项

```bash
# 创建所有测试账号
python scripts/create_test_users_fixed.py

# 只创建特定账号
python scripts/create_test_users_fixed.py --users admin,testuser

# 使用自定义密码
python scripts/create_test_users_fixed.py --password MyPass123

# 重置测试账号
python scripts/create_test_users_fixed.py --reset
```

## ✅ 验证步骤

1. **脚本运行** - 应该看到"成功创建X个测试用户"
2. **数据库检查** - 验证用户记录存在
3. **前端登录** - 测试登录功能
4. **排行榜** - 检查ELO排名显示

## 🆘 故障排除

### 如果脚本仍有错误：

1. **检查数据库连接**：
   ```bash
   python -c "from app.database.postgres import engine; print('数据库连接正常')"
   ```

2. **检查虚拟环境**：
   ```bash
   venv\Scripts\activate
   pip list | grep sqlalchemy
   ```

3. **使用更简单的密码**：
   ```bash
   python scripts/create_test_users_fixed.py --password "abc123"
   ```

## 🎉 成功标志

看到以下信息表示修复成功：
- ✅ "成功创建 X 个测试用户"
- ✅ 前端登录页面显示正常
- ✅ 排行榜显示不同ELO等级
- ✅ 所有测试账号可以正常登录

---

**🎮 现在您可以开始测试游戏功能了！**