@echo off
title Card Battle Arena - Local Backend Startup

echo ==========================================
echo Card Battle Arena - Local Backend Startup
echo ==========================================

REM 检查是否在项目根目录
if not exist "docker-compose.yml" (
    echo Error: Please run this script from the project root directory.
    echo Current directory: %CD%
    pause
    exit /b 1
)

REM 启动基础设施服务 (PostgreSQL 和 Redis)
echo Starting infrastructure services...
docker-compose up -d postgres redis

REM 等待服务启动
echo Waiting for services to start...
timeout /t 10 /nobreak >nul

REM 进入后端目录
cd backend

REM 检查虚拟环境是否存在，如果不存在则创建
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
)

REM 激活虚拟环境
echo Activating virtual environment...
call venv\Scripts\activate

REM 检查依赖是否已安装
echo Checking dependencies...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
)

REM 启动后端服务
echo Starting backend service...
echo Backend will be available at http://localhost:8000
echo API documentation will be available at http://localhost:8000/docs
python main.py

REM 返回项目根目录
cd ..

echo.
echo Backend service stopped.
pause