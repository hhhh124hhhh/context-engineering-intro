@echo off
title Card Battle Arena - Create Test Users

echo ==========================================
echo Card Battle Arena - Create Test Users
echo ==========================================

REM 检查是否在项目根目录
if not exist "docker-compose.yml" (
    echo Error: Please run this script from the project root directory.
    echo Current directory: %CD%
    pause
    exit /b 1
)

REM 进入后端目录
cd backend

REM 检查虚拟环境是否存在
if not exist "venv" (
    echo Error: Virtual environment not found. Please create it first.
    echo Run 'python -m venv venv' to create the virtual environment.
    pause
    cd ..
    exit /b 1
)

REM 激活虚拟环境
echo Activating virtual environment...
call venv\Scripts\activate

REM 检查并升级bcrypt以解决版本兼容性问题
echo Checking bcrypt version compatibility...
pip show bcrypt >nul 2>&1
if errorlevel 1 (
    echo Installing bcrypt...
    pip install bcrypt
) else (
    echo Upgrading bcrypt to latest version...
    pip install --upgrade bcrypt
)

REM 检查依赖是否已安装
echo Checking if required packages are installed...
pip show sqlalchemy >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
)

REM 运行测试用户创建脚本
echo Running test user creation script...
python scripts/create_test_users.py %*

REM 返回项目根目录
cd ..

echo.
echo Script execution completed.
pause