# Card Battle Arena - PowerShell 快速启动脚本

Write-Host "正在启动 Card Battle Arena 开发环境..." -ForegroundColor Green
Write-Host ""

# 检查Docker是否运行
try {
    $dockerInfo = docker info 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "错误: Docker未运行或未安装" -ForegroundColor Red
        Write-Host "请启动Docker Desktop后再运行此脚本" -ForegroundColor Yellow
        pause
        exit 1
    }
} catch {
    Write-Host "错误: Docker未运行或未安装" -ForegroundColor Red
    Write-Host "请启动Docker Desktop后再运行此脚本" -ForegroundColor Yellow
    pause
    exit 1
}

# 启动开发环境
Write-Host "正在启动所有服务..." -ForegroundColor Cyan
docker-compose up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "服务启动成功！" -ForegroundColor Green
    Write-Host ""
    Write-Host "访问地址:" -ForegroundColor Yellow
    Write-Host "  前端应用: http://localhost:5173" -ForegroundColor White
    Write-Host "  后端API:  http://localhost:8000" -ForegroundColor White
    Write-Host "  API文档:  http://localhost:8000/docs" -ForegroundColor White
    Write-Host ""
    Write-Host "要查看日志，请运行: docker-compose logs -f" -ForegroundColor Cyan
    Write-Host "要停止服务，请运行: docker-compose down" -ForegroundColor Cyan
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "启动失败，请检查错误信息" -ForegroundColor Red
    Write-Host ""
}

Write-Host "按任意键退出..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")