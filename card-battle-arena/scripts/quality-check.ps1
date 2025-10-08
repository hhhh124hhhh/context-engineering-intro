# 卡牌对战竞技场 - Windows质量检查脚本
# 作者: Card Battle Arena Team
# 版本: 1.0.0

param(
    [switch]$Help,
    [switch]$Fix,
    [switch]$Verbose
)

# 显示帮助信息
if ($Help) {
    Write-Host "卡牌对战竞技场 - Windows质量检查脚本"
    Write-Host ""
    Write-Host "用法: .\quality-check.ps1 [选项]"
    Write-Host ""
    Write-Host "选项:"
    Write-Host "  -Help       显示帮助信息"
    Write-Host "  -Fix        自动修复发现的问题"
    Write-Host "  -Verbose    显示详细信息"
    Write-Host ""
    Write-Host "示例:"
    Write-Host "  .\quality-check.ps1              # 运行质量检查"
    Write-Host "  .\quality-check.ps1 -Fix         # 运行检查并自动修复"
    Write-Host "  .\quality-check.ps1 -Verbose     # 显示详细信息"
    exit 0
}

# 颜色定义
$Colors = @{
    Red = "Red"
    Green = "Green"
    Yellow = "Yellow"
    Blue = "Blue"
    Cyan = "Cyan"
    Magenta = "Magenta"
    White = "White"
}

# 日志函数
function Write-Info {
    param([string]$Message)
    Write-Host $Message -ForegroundColor $Colors.Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host $Message -ForegroundColor $Colors.Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host $Message -ForegroundColor $Colors.Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host $Message -ForegroundColor $Colors.Red
}

function Write-Header {
    param([string]$Message)
    Write-Host $Message -ForegroundColor $Colors.Magenta
}

function Write-Step {
    param([string]$Message)
    Write-Host $Message -ForegroundColor $Colors.Cyan
}

# 验证结果统计
$Script:TotalChecks = 0
$Script:PassedChecks = 0
$Script:FailedChecks = 0

# 检查函数
function Test-Check {
    param(
        [string]$Description,
        [scriptblock]$TestScript,
        [scriptblock]$FixScript = $null
    )

    $Script:TotalChecks++
    Write-Header "检查: $Description"

    try {
        $result = & $TestScript
        if ($result) {
            Write-Success "✓ $Description"
            $Script:PassedChecks++
            return $true
        } else {
            Write-Error "✗ $Description"
            $Script:FailedChecks++

            if ($Fix -and $FixScript) {
                Write-Info "尝试自动修复..."
                try {
                    & $FixScript
                    Write-Success "✓ 修复完成"
                    $Script:PassedChecks++
                    $Script:FailedChecks--
                } catch {
                    Write-Error "✗ 修复失败: $($_.Exception.Message)"
                }
            }
            return $false
        }
    } catch {
        Write-Error "✗ 检查失败: $($_.Exception.Message)"
        $Script:FailedChecks++
        return $false
    }
}

# 显示检查结果
function Show-CheckResults {
    Write-Host ""
    Write-Info "质量检查完成"
    Write-Host "===================="
    Write-Host "总检查数: $Script:TotalChecks"
    Write-Host "通过检查: $Script:PassedChecks" -ForegroundColor $Colors.Green
    Write-Host "失败检查: $Script:FailedChecks" -ForegroundColor $Colors.Red

    if ($Script:FailedChecks -eq 0) {
        Write-Host ""
        Write-Success "🎉 所有质量检查都通过了！"
        return $true
    } else {
        Write-Host ""
        Write-Warning "⚠️  有 $Script:FailedChecks 项检查失败"
        return $false
    }
}

# 项目根目录
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

Write-Info "项目根目录: $ProjectRoot"
Write-Info "开始质量检查..."
Write-Host ""

# 1. 文件结构检查
Write-Step "检查文件结构"

Test-Check "README.md 存在" {
    Test-Path "README.md"
}

Test-Check "LICENSE 文件存在" {
    Test-Path "LICENSE"
}

Test-Check ".gitignore 存在" {
    Test-Path ".gitignore"
}

Test-Check "package.json 存在" {
    Test-Path "frontend\package.json"
}

Test-Check "requirements.txt 存在" {
    Test-Path "backend\requirements.txt"
}

Test-Check "Docker配置存在" {
    (Test-Path "docker-compose.yml") -and (Test-Path "docker-compose.prod.yml")
}

# 2. 前端质量检查
Write-Step "检查前端代码质量"

Test-Check "TypeScript配置存在" {
    Test-Path "frontend\tsconfig.json"
}

Test-Check "Vite配置存在" {
    Test-Path "frontend\vite.config.ts"
}

Test-Check "ESLint配置存在" {
    (Test-Path "frontend\.eslintrc.js") -or (Test-Path "frontend\.eslintrc.json")
}

Test-Check "Prettier配置存在" {
    Test-Path "frontend\.prettierrc"
}

# 3. 后端质量检查
Write-Step "检查后端代码质量"

Test-Check "Python配置存在" {
    Test-Path "backend\pyproject.toml"
}

Test-Check "main.py 存在" {
    Test-Path "backend\main.py"
}

Test-Check "应用目录存在" {
    Test-Path "backend\app"
}

Test-Check "测试目录存在" {
    Test-Path "backend\tests"
}

# 4. 依赖检查
Write-Step "检查依赖文件"

Test-Check "前端依赖完整" {
    $packageJson = Get-Content "frontend\package.json" -Raw | ConvertFrom-Json
    $packageJson.PSObject.Properties.Name -contains "dependencies" -and $packageJson.PSObject.Properties.Name -contains "devDependencies"
}

Test-Check "后端依赖完整" {
    Test-Path "backend\requirements.txt"
}

# 5. 配置文件检查
Write-Step "检查配置文件"

Test-Check "环境变量模板存在" {
    (Test-Path ".env.example") -and (Test-Path ".env.prod.example")
}

Test-Check "Docker配置完整" {
    (Test-Path "docker\production\Dockerfile.backend") -and
    (Test-Path "docker\production\Dockerfile.frontend") -and
    (Test-Path "docker\development\Dockerfile.backend") -and
    (Test-Path "docker\development\Dockerfile.frontend")
}

Test-Check "Nginx配置存在" {
    Test-Path "nginx\conf.d\default.conf"
}

# 6. 脚本检查
Write-Step "检查脚本文件"

Test-Check "部署脚本存在" {
    (Test-Path "scripts\deploy.sh") -and (Test-Path "scripts\deploy-windows.ps1")
}

Test-Check "质量检查脚本存在" {
    (Test-Path "scripts\quality-check.sh") -and (Test-Path "scripts\quality-check.ps1")
}

Test-Check "设置脚本存在" {
    Test-Path "scripts\setup.sh"
}

# 7. 文档检查
Write-Step "检查文档文件"

Test-Check "API文档存在" {
    Test-Path "API_DOCS.md"
}

Test-Check "部署指南存在" {
    Test-Path "DEPLOYMENT.md"
}

Test-Check "开发指南存在" {
    Test-Path "DEVELOPMENT.md"
}

Test-Check "项目总结存在" {
    Test-Path "PROJECT_SUMMARY.md"
}

# 8. Git配置检查
Write-Step "检查Git配置"

Test-Check "Git仓库存在" {
    Test-Path ".git"
}

Test-Check "Git分支干净" {
    $status = git status --porcelain
    return [string]::IsNullOrEmpty($status)
}

# 9. 安全检查
Write-Step "检查安全配置"

Test-Check "无硬编码密码" {
    $files = @("*.py", "*.ts", "*.js", "*.json", "*.yml", "*.yaml")
    $hasPassword = $false

    foreach ($file in $files) {
        $content = Get-ChildItem -Path . -Recurse -Include $file |
                   Where-Object { $_.FullName -notmatch "node_modules|\.git|\.venv|venv" } |
                   Get-Content |
                   Where-Object { $_ -match "password.*=.*['\"](?!(example|test|mock|dummy))" }

        if ($content) {
            $hasPassword = $true
            break
        }
    }

    return -not $hasPassword
}

Test-Check "无硬编码密钥" {
    $files = @("*.py", "*.ts", "*.js", "*.json", "*.yml", "*.yaml")
    $hasSecret = $false

    foreach ($file in $files) {
        $content = Get-ChildItem -Path . -Recurse -Include $file |
                   Where-Object { $_.FullName -notmatch "node_modules|\.git|\.venv|venv" } |
                   Get-Content |
                   Where-Object { $_ -match "secret.*=.*['\"](?!(example|test|mock|dummy))" }

        if ($content) {
            $hasSecret = $true
            break
        }
    }

    return -not $hasSecret
}

# 10. 性能检查
Write-Step "检查性能配置"

Test-Check "缓存配置存在" {
    (Get-Content ".env.example" | Select-String "REDIS_URL") -ne $null
}

Test-Check "压缩配置存在" {
    if (Test-Path "nginx\conf.d\default.conf") {
        $nginxConfig = Get-Content "nginx\conf.d\default.conf"
        return $nginxConfig -match "gzip"
    }
    return $false
}

# 如果安装了Node.js，运行前端检查
if (Get-Command node -ErrorAction SilentlyContinue) {
    Write-Step "运行前端质量检查"

    Set-Location "frontend"

    Test-Check "前端依赖安装完整" {
        Test-Path "node_modules"
    } {
        if ($Fix) {
            npm install
        }
    }

    if (Test-Path "package.json") {
        $packageJson = Get-Content "package.json" -Raw | ConvertFrom-Json

        if ($packageJson.scripts.PSObject.Properties.Name -contains "lint") {
            Test-Check "ESLint检查通过" {
                npm run lint 2>&1 | Out-Null
                $LASTEXITCODE -eq 0
            }
        }

        if ($packageJson.scripts.PSObject.Properties.Name -contains "type-check") {
            Test-Check "TypeScript类型检查通过" {
                npm run type-check 2>&1 | Out-Null
                $LASTEXITCODE -eq 0
            }
        }

        if ($packageJson.scripts.PSObject.Properties.Name -contains "build") {
            Test-Check "前端构建成功" {
                npm run build 2>&1 | Out-Null
                $LASTEXITCODE -eq 0 -and (Test-Path "dist")
            }
        }
    }

    Set-Location $ProjectRoot
}

# 如果安装了Python，运行后端检查
if (Get-Command python -ErrorAction SilentlyContinue) {
    Write-Step "运行后端质量检查"

    Set-Location "backend"

    Test-Check "Python虚拟环境存在" {
        Test-Path "venv" -or Test-Path ".venv"
    }

    # 尝试激活虚拟环境并运行检查
    if (Test-Path "venv") {
        & .\venv\Scripts\Activate.ps1

        Test-Check "Python依赖安装完整" {
            try {
                pip list | Out-Null
                $true
            } catch {
                $false
            }
        } {
            if ($Fix) {
                pip install -r requirements.txt
            }
        }

        # 检查代码质量工具是否可用
        if (Get-Command black -ErrorAction SilentlyContinue) {
            Test-Check "Black代码格式检查通过" {
                black --check . 2>&1 | Out-Null
                $LASTEXITCODE -eq 0
            } {
                if ($Fix) {
                    black .
                }
            }
        }

        if (Get-Command pytest -ErrorAction SilentlyContinue) {
            Test-Check "Pytest测试通过" {
                pytest tests/ -v 2>&1 | Out-Null
                $LASTEXITCODE -eq 0
            }
        }

        deactivate
    }

    Set-Location $ProjectRoot
}

# 显示最终结果
Write-Host ""
$success = Show-CheckResults

Write-Host ""
Write-Info "质量检查报告生成完成"

if ($Verbose) {
    Write-Host ""
    Write-Info "详细统计信息:"
    Write-Host "- 检查项目: $Script:TotalChecks"
    Write-Host "- 通过项目: $Script:PassedChecks"
    Write-Host "- 失败项目: $Script:FailedChecks"
    Write-Host "- 成功率: $([math]::Round($Script:PassedChecks / $Script:TotalChecks * 100, 2))%"
}

# 退出脚本
if ($success) {
    Write-Host ""
    Write-Success "项目质量检查通过！可以继续部署。"
    exit 0
} else {
    Write-Host ""
    Write-Warning "项目质量检查失败，请修复问题后重试。"
    exit 1
}