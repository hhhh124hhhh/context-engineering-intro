@echo off
echo 正在启动 Card Battle Arena 服务...

echo.
echo 1. 启动数据库和缓存服务...
docker-compose up -d postgres redis

echo.
echo 等待数据库和缓存服务启动完成...
timeout /t 10 /nobreak >nul

echo.
echo 2. 启动后端服务...
docker-compose up -d backend

echo.
echo 等待后端服务启动完成...
timeout /t 10 /nobreak >nul

echo.
echo 3. 启动前端服务...
docker-compose up -d frontend

echo.
echo 所有服务已启动!
echo.
echo 访问地址:
echo 后端 API: http://localhost:8000
echo 前端应用: http://localhost:5173
echo.
echo 使用以下命令查看服务状态:
echo docker-compose logs backend
echo docker-compose logs frontend
echo.
echo 要停止所有服务，请运行: docker-compose down
pause