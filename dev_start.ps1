<#
.SYNOPSIS
    Doccano 二次开发环境一键启动脚本 (全自动版)
.DESCRIPTION
    此脚本会自动完成以下工作：
    1. 检查并创建 Conda 环境 (doccano)
    2. 检查并安装 Backend 依赖 (Poetry)
    3. 检查并安装 Frontend 依赖 (Yarn)
    4. 在三个独立窗口中启动 Backend、Celery 和 Frontend
#>

# 获取脚本所在目录作为项目根目录
$ProjectRoot = $PSScriptRoot
if (-not $ProjectRoot) { $ProjectRoot = Get-Location }

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   Doccano 开发环境启动脚本 (Full Auto Mode)    " -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "项目根目录: $ProjectRoot" -ForegroundColor Gray

# 0. 基础工具检查
# -----------------------------------------------------------
function Check-Command ($cmd, $name) {
    if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
        Write-Host "❌ 未检测到 $name ($cmd)。请确保已安装并添加到 PATH。" -ForegroundColor Red
        return $false
    }
    return $true
}

if (-not (Check-Command "conda" "Conda")) { exit }
if (-not (Check-Command "yarn" "Yarn")) { exit }

# 1. 环境自动准备 (Environment Setup)
# -----------------------------------------------------------
Write-Host "`n[1/4] 检查 Conda 环境..." -ForegroundColor Yellow

# 检查 doccano 环境是否存在
$envList = conda env list
if ($envList -match "doccano") {
    Write-Host "✅ Conda 环境 'doccano' 已存在。" -ForegroundColor Green
} else {
    Write-Host "⚠️ 未检测到 'doccano' 环境，正在创建..." -ForegroundColor Yellow
    conda create -n doccano python=3.8 -y
    if ($LASTEXITCODE -ne 0) { Write-Error "Conda 环境创建失败，请检查网络或配置。"; exit }
    Write-Host "✅ Conda 环境创建完成。" -ForegroundColor Green
}

Write-Host "`n[2/4] 检查后端依赖..." -ForegroundColor Yellow
# 检查后端依赖是否安装 (简单判断 pyproject.toml 对应的库是否在环境中)
# 由于 activate 在脚本中比较麻烦，我们使用 conda run
$backendDir = Join-Path $ProjectRoot "backend"
Write-Host "正在安装/更新后端依赖 (使用 poetry)..." -ForegroundColor Gray
# 确保 poetry 已安装
conda run -n doccano pip install poetry
# 安装依赖
conda run -n doccano --cwd "$backendDir" poetry install
if ($LASTEXITCODE -ne 0) { 
    Write-Host "⚠️ Poetry 安装依赖出现警告或错误，尝试继续..." -ForegroundColor Yellow 
} else {
    Write-Host "✅ 后端依赖准备就绪。" -ForegroundColor Green
}

Write-Host "`n[3/4] 检查前端依赖..." -ForegroundColor Yellow
$frontendDir = Join-Path $ProjectRoot "frontend"
if (-not (Test-Path (Join-Path $frontendDir "node_modules"))) {
    Write-Host "⚠️ 未检测到 node_modules，正在执行 yarn install..." -ForegroundColor Yellow
    Push-Location $frontendDir
    yarn install
    Pop-Location
    Write-Host "✅ 前端依赖安装完成。" -ForegroundColor Green
} else {
    Write-Host "✅ 前端依赖已存在 (跳过 yarn install)。" -ForegroundColor Green
}

# 2. 启动服务 (Launch Services)
# -----------------------------------------------------------
Write-Host "`n[4/4] 正在启动服务..." -ForegroundColor Yellow

# 检查端口占用
function Check-Port ($port) {
    $portActive = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($portActive) {
        Write-Host "⚠️ 警告: 端口 $port 已被占用。请先关闭相关程序，否则启动会失败。" -ForegroundColor Red
        return $true
    }
    return $false
}

Check-Port 8000
Check-Port 3000

# Backend
Write-Host "-> 启动 Backend (Port 8000)..." -ForegroundColor Green
# 使用更加稳健的启动方式：先进入目录，激活环境，再启动
$cmdBackend = "cd '$ProjectRoot'; cd backend; Write-Host '正在启动 Backend (8000)...'; conda activate doccano; python manage.py runserver; Read-Host '后端已停止，按回车键退出...'"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "$cmdBackend"

# Celery
Write-Host "-> 启动 Celery Worker (用于导入/导出)..." -ForegroundColor Green
$cmdCelery = "cd '$ProjectRoot'; cd backend; `$Host.UI.RawUI.WindowTitle = 'Doccano - Celery Worker'; Write-Host '正在启动 Celery (处理导入/导出任务)...' -ForegroundColor Cyan; conda activate doccano; celery -A config worker -l info --pool=solo; Read-Host 'Celery 已停止，按回车键退出...'"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "$cmdCelery"

# Frontend
Write-Host "-> 启动 Frontend (Port 3000)..." -ForegroundColor Green
# 前端不需要激活环境，直接运行
$cmdFrontend = "cd '$ProjectRoot'; cd frontend; Write-Host '正在启动 Frontend (3000)...'; yarn dev; if (`$LastExitCode -ne 0) { Write-Host '前端启动失败，请检查报错' -ForegroundColor Red; Read-Host '按回车键退出...' }"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "$cmdFrontend"

Write-Host "`n------------------------------------------------" -ForegroundColor Yellow
Write-Host "✅ 全套服务已启动！" -ForegroundColor Yellow
Write-Host "👉 前端页面: http://localhost:3000" -ForegroundColor Cyan
Write-Host "👉 后端接口: http://localhost:8000" -ForegroundColor Gray
Write-Host "------------------------------------------------" -ForegroundColor Yellow
Write-Host "如果不小心关闭了窗口，请重新运行此脚本。" -ForegroundColor Gray
Read-Host "按回车键退出此引导窗口..."
