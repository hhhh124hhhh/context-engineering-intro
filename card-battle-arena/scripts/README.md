# 启动脚本说明

本目录包含用于在Windows环境下启动Card Battle Arena项目的各种脚本。

## 脚本列表

### 1. start-windows.bat
交互式启动脚本，提供菜单选项：
- 启动开发环境
- 启动生产环境
- 查看服务日志
- 停止服务
- 查看服务状态
- 运行健康检查

**使用方法:**
双击运行或在命令行中执行：
```cmd
scripts\start-windows.bat
```

### 2. quick-start.bat
简化版启动脚本，一键启动开发环境。

**使用方法:**
双击运行或在命令行中执行：
```cmd
scripts\quick-start.bat
```

### 3. quick-start.ps1
PowerShell版本的简化启动脚本。

**使用方法:**
在PowerShell中执行：
```powershell
powershell -ExecutionPolicy Bypass -File scripts\quick-start.ps1
```

## 使用建议

1. **日常开发**: 推荐使用 `start-windows.bat`，它提供了完整的交互式菜单
2. **快速启动**: 推荐使用 `quick-start.bat`，一键启动所有服务
3. **PowerShell环境**: 在PowerShell环境中可使用 `quick-start.ps1`

## 注意事项

1. 运行脚本前请确保Docker Desktop已启动
2. 首次运行可能需要较长时间来下载和构建Docker镜像
3. 确保端口 5432、6379、8000、5173 未被其他应用占用
4. 如遇到权限问题，请以管理员身份运行脚本