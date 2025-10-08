# 卡牌对战竞技场 Windows 部署脚本
# 作者: Card Battle Arena Team
# 版本: 1.0.0

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("deploy", "update", "rollback", "start", "stop", "restart", "status", "logs", "health", "backup", "cleanup", "help")]
    [string]$Action = "help",

    [Parameter(Mandatory=$false)]
    [string]$Service = "",

    [Parameter(Mandatory=$false)]
    [switch]$SkipDependencies
)

# 颜色输出函数
function Write-ColorOutput {
    param(
        [string]$Message,
        [ConsoleColor]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Write-Info {
    param([string]$Message)
    Write-ColorOutput "[INFO] $Message" "Cyan"
}

function Write-Success {
    param([string]$Message)
    Write-ColorOutput "[SUCCESS] $Message" "Green"
}

function Write-Warning {
    param([string]$Message)
    Write-ColorOutput "[WARNING] $Message" "Yellow"
}

function Write-Error {
    param([string]$Message)
    Write-ColorOutput "[ERROR] $Message" "Red"
}

function Write-Header {
    param([string]$Message)
    Write-ColorOutput "[CHECK] $Message" "Magenta"
}

# 全局变量
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$TotalChecks = 0
$PassedChecks = 0
$FailedChecks = 0

# 检查函数
function Test-Command {
    param(
        [string]$Description,
        [scriptblock]$Command
    )

    $script:TotalChecks++
    Write-Header $Description

    try {
        $result = & $Command 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Success "✓ $Description"
            $script:PassedChecks++
            return $true
        } else {
            Write-Error "✗ $Description"
            $script:FailedChecks++
            return $false
        }
    } catch {
        Write-Error "✗ $Description"
        $script:FailedChecks++
        return $false
    }
}

# 显示检查结果
function Show-Results {
    Write-Host ""
    Write-Info "质量检查完成"
    Write-Host "===================="
    Write-Host "总检查数: $TotalChecks"
    Write-Host "通过检查: $PassedChecks" -ForegroundColor Green
    Write-Host "失败检查: $FailedChecks" -ForegroundColor Red

    if ($FailedChecks -eq 0) {
        Write-Host ""
        Write-Success "🎉 所有质量检查都通过了！"
        exit 0
    } else {
        Write-Host ""
        Write-Error "❌ 有 $FailedChecks 项检查失败"
        exit 1
    }
}

# 检查管理员权限
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# 检查系统依赖
function Install-Dependencies {
    Write-Info "检查系统依赖..."

    if (-not (Test-Administrator)) {
        Write-Error "需要管理员权限来安装依赖"
        Write-Info "请以管理员身份运行此脚本"
        exit 1
    }

    # 检查 Chocolatey
    if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
        Write-Info "安装 Chocolatey 包管理器..."
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    } else {
        Write-Success "Chocolatey 已安装"
    }

    # 检查 Docker Desktop
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        Write-Info "安装 Docker Desktop..."
        choco install docker-desktop -y
    } else {
        Write-Success "Docker 已安装"
    }

    # 检查 Node.js
    if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
        Write-Info "安装 Node.js..."
        choco install nodejs -y
    } else {
        Write-Success "Node.js 已安装"
    }

    # 检查 Python
    if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
        Write-Info "安装 Python..."
        choco install python -y
    } else {
        Write-Success "Python 已安装"
    }

    # 检查 Git
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        Write-Info "安装 Git..."
        choco install git -y
    } else {
        Write-Success "Git 已安装"
    }

    Write-Success "所有依赖检查完成"
}

# 设置环境变量
function Set-EnvironmentVariables {
    Write-Info "设置环境变量..."

    $envFile = "$ProjectRoot\.env.prod"

    if (-not (Test-Path $envFile)) {
        Write-Warning ".env.prod 文件不存在，从模板创建..."
        Copy-Item "$ProjectRoot\.env.prod.example" $envFile

        Write-Info "请编辑 $envFile 文件，配置生产环境变量"
        Write-Host "按任意键继续..."
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    }

    # 读取环境变量
    Get-Content $envFile | Where-Object { $_ -notmatch '^#' -and $_ -match '(.+)=' } | ForEach-Object {
        if ($_ -match '^(.+?)=(.*)$') {
            $key = $matches[1]
            $value = $matches[2]
            [Environment]::SetEnvironmentVariable($key, $value, "Process")
        }
    }

    Write-Success "环境变量设置完成"
}

# 生成 SSL 证书
function New-SSLCertificates {
    Write-Info "生成 SSL 证书..."

    $sslDir = "$ProjectRoot\nginx\ssl"

    if (-not (Test-Path $sslDir)) {
        New-Item -ItemType Directory -Path $sslDir -Force
    }

    $certFile = "$sslDir\cert.pem"
    $keyFile = "$sslDir\key.pem"

    if (-not (Test-Path $certFile) -or -not (Test-Path $keyFile)) {
        Write-Info "生成自签名 SSL 证书..."

        $certConfig = @"
[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[req_distinguished_name]
CN = $env:DOMAIN

[v3_req]
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
"@

        $certConfig | Out-File -FilePath "$sslDir\cert.conf" -Encoding UTF8

        # 使用 OpenSSL 生成证书
        if (Get-Command openssl -ErrorAction SilentlyContinue) {
            & openssl req -x509 -nodes -days 365 -newkey rsa:2048 `
                -keyout $keyFile `
                -out $certFile `
                -config "$sslDir\cert.conf"

            Write-Warning "使用自签名证书，浏览器会显示安全警告"
            Write-Info "生产环境请使用 Let's Encrypt 或购买的有效证书"
        } else {
            Write-Error "OpenSSL 未找到，无法生成 SSL 证书"
            Write-Info "请安装 OpenSSL 或手动提供证书文件"
        }
    } else {
        Write-Info "SSL 证书已存在，跳过生成"
    }

    Write-Success "SSL 证书准备完成"
}

# 构建 Docker 镜像
function Build-Images {
    Write-Info "构建 Docker 镜像..."

    Set-Location $ProjectRoot

    # 构建后端镜像
    Write-Info "构建后端镜像..."
    docker-compose -f docker-compose.prod.yml build backend

    # 构建前端镜像
    Write-Info "构建前端镜像..."
    docker-compose -f docker-compose.prod.yml build frontend

    Write-Success "镜像构建完成"
}

# 数据库迁移
function Invoke-Migrations {
    Write-Info "运行数据库迁移..."

    Set-Location $ProjectRoot

    # 启动数据库服务
    docker-compose -f docker-compose.prod.yml up -d postgres redis

    # 等待数据库启动
    Write-Info "等待数据库启动..."
    Start-Sleep -Seconds 10

    # 运行迁移
    docker-compose -f docker-compose.prod.yml run --rm backend alembic upgrade head

    Write-Success "数据库迁移完成"
}

# 启动服务
function Start-Services {
    Write-Info "启动所有服务..."

    Set-Location $ProjectRoot
    docker-compose -f docker-compose.prod.yml up -d

    Write-Info "等待服务启动..."
    Start-Sleep -Seconds 30

    # 检查服务状态
    Get-ServiceStatus

    Write-Success "所有服务启动完成"
}

# 检查服务状态
function Get-ServiceStatus {
    Write-Info "检查服务状态..."

    $services = @("postgres", "redis", "backend", "frontend", "nginx")

    foreach ($service in $services) {
        $status = docker-compose -f docker-compose.prod.yml ps $service --format "table {{.Status}}"
        if ($status -match "Up") {
            Write-Success "$service 运行正常"
        } else {
            Write-Error "$service 运行异常"
            docker-compose -f docker-compose.prod.yml logs $service
        }
    }
}

# 健康检查
function Invoke-HealthCheck {
    Write-Info "执行健康检查..."

    # 检查后端健康状态
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$($env:BACKEND_PORT ?? 8000)/health" -UseBasicParsing -TimeoutSec 10
        if ($response.StatusCode -eq 200) {
            Write-Success "后端健康检查通过"
        } else {
            Write-Error "后端健康检查失败"
        }
    } catch {
        Write-Error "后端健康检查失败"
    }

    # 检查前端健康状态
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$($env:FRONTEND_PORT ?? 3000)" -UseBasicParsing -TimeoutSec 10
        if ($response.StatusCode -eq 200) {
            Write-Success "前端健康检查通过"
        } else {
            Write-Error "前端健康检查失败"
        }
    } catch {
        Write-Error "前端健康检查失败"
    }

    # 检查数据库连接
    try {
        $result = docker-compose -f docker-compose.prod.yml exec -T pg_isready -U $env:POSTGRES_USER
        if ($LASTEXITCODE -eq 0) {
            Write-Success "数据库连接正常"
        } else {
            Write-Error "数据库连接失败"
        }
    } catch {
        Write-Error "数据库连接失败"
    }
}

# 备份数据库
function Backup-Database {
    Write-Info "备份数据库..."

    $backupDir = "$ProjectRoot\backups\$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    New-Item -ItemType Directory -Path $backupDir -Force

    # 导出数据库
    $backupFile = "$backupDir\database.sql"
    $backupCommand = "docker-compose -f docker-compose.prod.yml exec -T postgres pg_dump -U $env:POSTGRES_USER $env:POSTGRES_DB > $backupFile"

    try {
        Invoke-Expression $backupCommand
        Write-Success "数据库备份完成: $backupDir"
    } catch {
        Write-Error "数据库备份失败"
    }
}

# 清理旧镜像
function Clear-OldImages {
    Write-Info "清理旧的 Docker 镜像..."

    # 清理悬空镜像
    docker image prune -f

    # 清理旧的应用镜像（保留最近3个版本）
    $oldImages = docker images --format "table {{.Repository}}`t{{.Tag}}`t{{.ID}}" | Where-Object { $_ -match "cardbattle" } | Select-Object -Skip 3
    if ($oldImages) {
        $oldImages | ForEach-Object {
            if ($_ -match '^(.+?)\t(.+?)\t(.+?)$') {
                $imageId = $matches[3]
                try {
                    docker rmi -f $imageId 2>$null
                } catch {
                    # 忽略删除失败的镜像
                }
            }
        }
    }

    Write-Success "镜像清理完成"
}

# 更新服务
function Update-Services {
    Write-Info "更新服务..."

    # 备份数据库
    Backup-Database

    # 拉取最新代码
    Write-Info "拉取最新代码..."
    Set-Location $ProjectRoot
    git pull origin main

    # 重新构建和部署
    Build-Images
    Invoke-Migrations
    docker-compose -f docker-compose.prod.yml up -d

    # 清理旧镜像
    Clear-OldImages

    Write-Success "服务更新完成"
}

# 回滚服务
function Rollback-Services {
    Write-Info "回滚服务到上一个版本..."

    Set-Location $ProjectRoot

    # 获取上一个版本
    $previousVersion = git describe --tags --abbrev=0 HEAD~1 2>$null
    if (-not $previousVersion) {
        $previousVersion = "HEAD~1"
    }

    Write-Info "回滚到版本: $previousVersion"

    # 切换到上一个版本
    git checkout $previousVersion

    # 重新构建和部署
    Build-Images
    docker-compose -f docker-compose.prod.yml up -d

    Write-Success "服务回滚完成"
}

# 显示日志
function Show-Logs {
    param([string]$ServiceName = "")

    Set-Location $ProjectRoot

    if ($ServiceName) {
        Write-Info "显示 $ServiceName 服务日志..."
        docker-compose -f docker-compose.prod.yml logs -f $ServiceName
    } else {
        Write-Info "显示所有服务日志..."
        docker-compose -f docker-compose.prod.yml logs -f
    }
}

# 停止服务
function Stop-Services {
    Write-Info "停止所有服务..."

    Set-Location $ProjectRoot
    docker-compose -f docker-compose.prod.yml down

    Write-Success "所有服务已停止"
}

# 完全清理
function Clear-All {
    Write-Warning "这将删除所有容器、镜像和数据卷，确定继续吗？(y/N)"
    $response = Read-Host

    if ($response -match '^[yY]') {
        Write-Info "清理所有资源..."

        Set-Location $ProjectRoot
        docker-compose -f docker-compose.prod.yml down -v --rmi all
        docker system prune -af

        Write-Success "清理完成"
    } else {
        Write-Info "取消清理操作"
    }
}

# Windows 服务管理
function Install-WindowsService {
    Write-Info "安装 Windows 服务..."

    if (-not (Test-Administrator)) {
        Write-Error "需要管理员权限来安装 Windows 服务"
        exit 1
    }

    # 创建服务配置文件
    $serviceConfig = @"
{
    "name": "CardBattleArena",
    "displayName": "Card Battle Arena",
    "description": "卡牌对战竞技场后端服务",
    "script": "python $ProjectRoot\backend\main.py",
    "workingDirectory": "$ProjectRoot\backend",
    "user": "NT AUTHORITY\\LocalService",
    "dependencies": [],
    "environment": {
        "PYTHONPATH": "$ProjectRoot\backend",
        "DATABASE_URL": "$env:DATABASE_URL"
    }
}
"@

    $serviceConfig | Out-File -FilePath "$ProjectRoot\service.json" -Encoding UTF8

    # 使用 NSSM 安装服务
    if (Get-Command nssm -ErrorAction SilentlyContinue) {
        nssm install CardBattleArena "python" "$ProjectRoot\backend\main.py"
        nssm set CardBattleArena DisplayName "Card Battle Arena"
        nssm set CardBattleArena Description "卡牌对战竞技场后端服务"
        nssm set CardBattleArena Start SERVICE_AUTO_START
        nssm set CardBattleArena AppDirectory "$ProjectRoot\backend"

        Write-Success "Windows 服务安装完成"
    } else {
        Write-Error "NSSM 未安装，无法安装 Windows 服务"
        Write-Info "请从 https://nssm.cc/download 下载并安装 NSSM"
    }
}

# 质量检查
function Invoke-QualityCheck {
    Write-Info "开始质量检查..."

    Set-Location $ProjectRoot

    # 代码格式检查
    Test-Command "Python 代码格式" {
        python -m black --check backend/
    }

    Test-Command "TypeScript 类型检查" {
        Set-Location frontend; npm run type-check
    }

    Test-Command "JavaScript 代码质量" {
        Set-Location frontend; npm run lint
    }

    # 测试检查
    Test-Command "后端测试" {
        Set-Location backend; python run_tests.py test
    }

    Test-Command "前端测试" {
        Set-Location frontend; npm test -- --watchAll=false
    }

    # 构建检查
    Test-Command "前端构建" {
        Set-Location frontend; npm run build
    }

    # 安全检查
    Test-Command "前端依赖安全" {
        Set-Location frontend; npm audit --audit-level moderate
    }

    Show-Results
}

# 创建快捷方式
function New-Shortcuts {
    Write-Info "创建快捷方式..."

    $desktop = [Environment]::GetFolderPath('Desktop')

    # 创建部署脚本快捷方式
    $deployShortcut = "$desktop\CardBattle Deploy.lnk"
    $shell = New-Object -ComObject WScript.Shell
    $shortcut = $shell.CreateShortcut($deployShortcut)
    $shortcut.TargetPath = "powershell.exe"
    $shortcut.Arguments = "-ExecutionPolicy Bypass -File `"$ScriptDir\deploy-windows.ps1`""
    $shortcut.WorkingDirectory = $ScriptDir
    $shortcut.IconLocation = "powershell.exe, 0"
    $shortcut.Description = "卡牌对战竞技场部署脚本"
    $shortcut.Save()

    # 创建质量检查快捷方式
    $qualityShortcut = "$desktop\CardBattle Quality Check.lnk"
    $shortcut = $shell.CreateShortcut($qualityShortcut)
    $shortcut.TargetPath = "powershell.exe"
    $shortcut.Arguments = "-ExecutionPolicy Bypass -File `"$ScriptDir\quality-check.sh`""
    $shortcut.WorkingDirectory = $ScriptDir
    $shortcut.IconLocation = "powershell.exe, 0"
    $shortcut.Description = "卡牌对战竞技场质量检查"
    $shortcut.Save()

    Write-Success "快捷方式创建完成"
}

# 显示帮助信息
function Show-Help {
    Write-Host "卡牌对战竞技场 Windows 部署脚本" -ForegroundColor Green
    Write-Host ""
    Write-Host "用法: ./deploy-windows.ps1 [命令] [参数]"
    Write-Host ""
    Write-Host "命令:"
    Write-Host "  deploy      完整部署（推荐首次使用）"
    Write-Host "  update      更新服务"
    Write-Host "  rollback    回滚服务"
    Write-Host "  start       启动服务"
    Write-Host "  stop        停止服务"
    Write-Host "  restart     重启服务"
    Write-Host "  status      查看服务状态"
    Write-Host "  logs [服务] 查看日志"
    Write-Host "  health      健康检查"
    Write-Host "  backup      备份数据库"
    Write-Host "  cleanup     清理资源"
    Write-Host "  service     安装 Windows 服务"
    Write-Host "  quality     质量检查"
    Write-Host "  shortcuts   创建桌面快捷方式"
    Write-Host "  help        显示帮助信息"
    Write-Host ""
    Write-Host "参数:"
    Write-Host "  -SkipDependencies  跳过依赖安装"
    Write-Host ""
    Write-Host "示例:"
    Write-Host "  ./deploy-windows.ps1 deploy          # 完整部署"
    Write-Host "  ./deploy-windows.ps1 update          # 更新服务"
    Write-Host "  ./deploy-windows.ps1 logs backend     # 查看后端日志"
    Write-Host "  ./deploy-windows.ps1 quality         # 质量检查"
}

# 主函数
function Main {
    Write-Host "🔍 卡牌对战竞技场 Windows 部署脚本" -ForegroundColor Green
    Write-Host "======================================" -ForegroundColor Green
    Write-Host ""

    # 检查 PowerShell 版本
    if ($PSVersionTable.PSVersion.Major -lt 5) {
        Write-Error "需要 PowerShell 5.0 或更高版本"
        exit 1
    }

    # 切换到项目根目录
    Set-Location $ProjectRoot

    switch ($Action) {
        "deploy" {
            if (-not $SkipDependencies) {
                Install-Dependencies
            }
            Set-EnvironmentVariables
            New-SSLCertificates
            Build-Images
            Invoke-Migrations
            Start-Services
            Invoke-HealthCheck
            New-Shortcuts
        }
        "update" {
            if (-not $SkipDependencies) {
                Install-Dependencies
            }
            Set-EnvironmentVariables
            Update-Services
            Invoke-HealthCheck
        }
        "rollback" {
            if (-not $SkipDependencies) {
                Install-Dependencies
            }
            Set-EnvironmentVariables
            Rollback-Services
            Invoke-HealthCheck
        }
        "start" {
            Start-Services
        }
        "stop" {
            Stop-Services
        }
        "restart" {
            Stop-Services
            Start-Services
        }
        "status" {
            Get-ServiceStatus
        }
        "logs" {
            Show-Logs -ServiceName $Service
        }
        "health" {
            Invoke-HealthCheck
        }
        "backup" {
            Backup-Database
        }
        "cleanup" {
            Clear-All
        }
        "service" {
            Install-WindowsService
        }
        "quality" {
            Invoke-QualityCheck
        }
        "shortcuts" {
            New-Shortcuts
        }
        "help" {
            Show-Help
        }
        default {
            Write-Error "未知命令: $Action"
            Show-Help
            exit 1
        }
    }
}

# 脚本入口
Main