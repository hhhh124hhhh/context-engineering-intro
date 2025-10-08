@echo off
REM Card Battle Arena - 快速启动脚本
REM 用于快速启动开发环境

echo 正在启动 Card Battle Arena 开发环境...
echo.

REM 检查Docker是否运行
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: Docker未运行或未安装
    echo 请启动Docker Desktop后再运行此脚本
    pause
    exit /b 1
)

REM 启动开发环境
echo 正在启动所有服务...
docker-compose up -d

if %errorlevel% equ 0 (
    echo.
    echo 服务启动成功！
    echo.
    echo 访问地址:
    echo   前端应用: http://localhost:5173
    echo   后端API:  http://localhost:8000
    echo   API文档:  http://localhost:8000/docs
    echo.
    echo 要查看日志，请运行: docker-compose logs -f
    echo 要停止服务，请运行: docker-compose down
    echo.
) else (
    echo.
    echo 启动失败，请检查错误信息
    echo.
)

pause