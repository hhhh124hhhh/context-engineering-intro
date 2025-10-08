@echo off
title Card Battle Arena - Stop Local Services

echo ==========================================
echo Card Battle Arena - Stop Local Services
echo ==========================================

REM 检查是否在项目根目录
if not exist "docker-compose.yml" (
    echo Error: Please run this script from the project root directory.
    echo Current directory: %CD%
    pause
    exit /b 1
)

REM 停止Docker容器
echo Stopping Docker containers...
docker-compose down

echo.
echo All services stopped.
echo You may need to manually stop the backend service if it's still running in another terminal.
pause