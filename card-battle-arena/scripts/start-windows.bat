@echo off
REM Card Battle Arena - Windows 启动脚本
REM 作者: Card Battle Arena Team
REM 版本: 1.0.0

REM 设置颜色
color 0A

REM 显示标题
echo.
echo ==========================================================
echo        卡牌对战竞技场 (Card Battle Arena)
echo                  Windows 启动脚本
echo ==========================================================
echo.

REM 检查是否在项目根目录
if not exist "docker-compose.yml" (
    echo 错误: 请在项目根目录运行此脚本
    echo 当前目录: %cd%
    echo.
    pause
    exit /b 1
)

REM 显示选项菜单
:menu
echo 请选择要执行的操作:
echo.
echo 1. 启动开发环境 (docker-compose up -d)
echo 2. 启动生产环境 (docker-compose -f docker-compose.prod.yml up -d)
echo 3. 查看服务日志 (docker-compose logs -f)
echo 4. 停止所有服务 (docker-compose down)
echo 5. 停止生产环境服务 (docker-compose -f docker-compose.prod.yml down)
echo 6. 查看服务状态 (docker-compose ps)
echo 7. 运行健康检查
echo 8. 退出
echo.
set /p choice=请输入选项 (1-8): 

REM 处理用户选择
if "%choice%"=="1" goto start_dev
if "%choice%"=="2" goto start_prod
if "%choice%"=="3" goto view_logs
if "%choice%"=="4" goto stop_services
if "%choice%"=="5" goto stop_prod_services
if "%choice%"=="6" goto service_status
if "%choice%"=="7" goto health_check
if "%choice%"=="8" goto exit_script

echo.
echo 无效选项，请重新选择
echo.
goto menu

:start_dev
echo.
echo 正在启动开发环境...
echo.
docker-compose up -d
if %errorlevel% equ 0 (
    echo.
    echo 开发环境启动成功！
    echo.
    echo 访问地址:
    echo   前端应用: http://localhost:5173
    echo   后端API:  http://localhost:8000
    echo   API文档:  http://localhost:8000/docs
    echo.
) else (
    echo.
    echo 启动失败，请检查错误信息
    echo.
)
pause
goto menu

:start_prod
echo.
echo 正在启动生产环境...
echo.
docker-compose -f docker-compose.prod.yml up -d
if %errorlevel% equ 0 (
    echo.
    echo 生产环境启动成功！
    echo.
    echo 访问地址:
    echo   前端应用: http://localhost
    echo   后端API:  http://localhost/api
    echo   API文档:  http://localhost/docs
    echo.
) else (
    echo.
    echo 启动失败，请检查错误信息
    echo.
)
pause
goto menu

:view_logs
echo.
echo 正在查看服务日志 (按 Ctrl+C 停止)...
echo.
docker-compose logs -f
echo.
pause
goto menu

:stop_services
echo.
echo 正在停止所有开发环境服务...
echo.
docker-compose down
if %errorlevel% equ 0 (
    echo.
    echo 所有开发环境服务已停止
    echo.
) else (
    echo.
    echo 停止服务时出错
    echo.
)
pause
goto menu

:stop_prod_services
echo.
echo 正在停止所有生产环境服务...
echo.
docker-compose -f docker-compose.prod.yml down
if %errorlevel% equ 0 (
    echo.
    echo 所有生产环境服务已停止
    echo.
) else (
    echo.
    echo 停止服务时出错
    echo.
)
pause
goto menu

:service_status
echo.
echo 当前服务状态:
echo.
docker-compose ps
echo.
pause
goto menu

:health_check
echo.
echo 正在执行健康检查...
echo.
echo 检查后端服务...
curl -f http://localhost:8000/health
if %errorlevel% equ 0 (
    echo.
    echo 后端服务健康检查: 通过
) else (
    echo.
    echo 后端服务健康检查: 失败
)

echo.
echo 检查前端服务...
curl -f http://localhost:5173
if %errorlevel% equ 0 (
    echo.
    echo 前端服务健康检查: 通过
) else (
    echo.
    echo 前端服务健康检查: 失败
)
echo.
pause
goto menu

:exit_script
echo.
echo 感谢使用卡牌对战竞技场！
echo.
pause
exit /b 0