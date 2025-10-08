# 测试账号说明

本文档说明如何使用测试账号脚本创建和管理测试用户账号。

## 🚀 快速开始

### 基础用法

```bash
# 进入后端目录
cd backend

# 创建所有测试账号
python scripts/create_test_users.py

# 创建特定测试账号
python scripts/create_test_users.py --users admin,testuser

# 使用自定义密码
python scripts/create_test_users.py --password MyPass123
```

### 查看和删除

```bash
# 列出测试账号状态
python scripts/create_test_users.py --list

# 重置所有测试账号（先删除再创建）
python scripts/create_test_users.py --reset

# 只删除测试账号
python scripts/create_test_users.py --delete-only
```

## 👥 测试账号列表

| 用户名 | 密码 | ELO | 等级 | 角色 | 说明 |
|--------|------|-----|------|------|------|
| admin | Test@123456 | 2500 | 50 | 管理员 | 系统管理测试 |
| testuser | Test@123456 | 1000 | 10 | 普通用户 | 基础功能测试 |
| newbie | Test@123456 | 800 | 3 | 新手 | 新手体验测试 |
| master | Test@123456 | 2800 | 80 | 高手 | 高段位功能测试 |
| grandmaster | Test@123456 | 3000 | 100 | 宗师 | 顶级玩家测试 |
| banned | Test@123456 | 1200 | 15 | 被封禁 | 封禁功能测试 |
| inactive | Test@123456 | 900 | 5 | 不活跃 | 长期未登录测试 |

## 🎮 测试场景

### 1. 基础功能测试
- **账号**: `testuser`
- **用途**: 测试注册、登录、个人资料编辑等基础功能

### 2. 管理员功能测试
- **账号**: `admin`
- **用途**: 测试管理员面板、用户管理、系统设置等

### 3. 新手体验测试
- **账号**: `newbie`
- **用途**: 测试新手引导、教程、初始奖励等

### 4. 高段位功能测试
- **账号**: `master`, `grandmaster`
- **用途**: 测试高级功能、特殊奖励、排行榜显示等

### 5. 特殊状态测试
- **被封禁账号**: `banned` - 测试登录限制、封禁提示等
- **不活跃账号**: `inactive` - 测试回归用户处理、重新激活等

## 🔧 命令行参数

### 完整参数列表

```bash
python scripts/create_test_users.py [选项]

选项:
  -h, --help            显示帮助信息
  -u USERS, --users USERS
                        要创建的用户名，用逗号分隔
  -p PASSWORD, --password PASSWORD
                        测试用户密码 (默认: Test@123456)
  -r, --reset           先删除已存在的测试用户
  -d, --delete-only     只删除测试用户，不创建新的
  -l, --list           列出测试用户状态
```

### 使用示例

```bash
# 创建管理员和测试用户
python scripts/create_test_users.py --users admin,testuser

# 重置特定用户
python scripts/create_test_users.py --users admin --reset

# 使用强密码
python scripts/create_test_users.py --password "SecurePass123!"

# 查看哪些测试账号已存在
python scripts/create_test_users.py --list

# 删除特定测试账号
python scripts/create_test_users.py --users newbie,master --delete-only
```

## ⚠️ 安全注意事项

### 生产环境保护
- 脚本会检查环境变量，禁止在生产环境运行
- 测试账号使用明显的标识性用户名
- 请勿在生产环境使用这些测试账号

### 密码安全
- 默认密码 `Test@123456` 满足系统密码要求
- 建议在测试环境中修改为更安全的密码
- 可以通过 `--password` 参数自定义密码

### 数据库安全
- 脚本直接操作数据库，请谨慎使用
- `--reset` 参数会删除所有测试用户数据
- 建议在测试前备份重要数据

## 🐛 故障排除

### 常见问题

**1. 数据库连接错误**
```
❌ 错误: could not connect to database
```
**解决**: 确保PostgreSQL服务正在运行，数据库配置正确

**2. 权限错误**
```
❌ 错误: permission denied
```
**解决**: 确保数据库用户有足够的权限创建和修改用户表

**3. 密码强度不足**
```
❌ 错误: 密码强度不足
```
**解决**: 使用更复杂的密码，包含大小写字母、数字和特殊字符

**4. 用户已存在**
```
⚠️ 用户 'admin' 已存在，跳过创建
```
**解决**: 使用 `--reset` 参数先删除已有用户，或使用其他用户名

### 调试技巧

```bash
# 查看详细错误信息
python scripts/create_test_users.py 2>&1 | tee debug.log

# 检查数据库连接
python -c "from app.database.postgres import engine; print('数据库连接正常')" 2>&1

# 检查用户表结构
python -c "
from app.database.postgres import get_async_session
from app.models.user import User
import asyncio

async def check_users():
    async with get_async_session() as session:
        result = await session.execute('SELECT COUNT(*) FROM users')
        count = result.scalar()
        print(f'当前用户数量: {count}')

asyncio.run(check_users())
"
```

## 📝 自定义扩展

### 添加新的测试账号类型

1. 编辑 `scripts/create_test_users.py`
2. 在 `test_users` 列表中添加新的用户配置
3. 重新运行脚本

```python
# 示例：添加新的测试账号
{
    "username": "vip_user",
    "email": "vip@cardbattle.arena",
    "display_name": "VIP用户",
    "elo_rating": 1500.0,
    "level": 25,
    # ... 其他配置
}
```

### 批量操作

```bash
# 创建多个管理员账号
for i in {1..5}; do
    python scripts/create_test_users.py --users admin$i --password "AdminPass123!"
done

# 清理所有测试账号
python scripts/create_test_users.py --delete-only
```

---

**📞 如有问题，请查看项目文档或联系开发团队。**