<#
.SYNOPSIS
    Doccano 二次开发环境一键启动脚本
.DESCRIPTION
    此脚本会自动打开三个 PowerShell 窗口，分别启动 Backend、Celery 和 Frontend。
#>

Write-Host "正在启动 Doccano 开发环境..." -ForegroundColor Cyan

# 定义项目根目录
$ProjectRoot = "C:\Users\mlian\doccano"

# 1. 启动 Backend (Django)
Write-Host "1. 启动 Backend (Port 8000)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$ProjectRoot'; conda activate doccano; cd backend; python manage.py runserver"

# 2. 启动 Celery Worker (开发模式下已启用同步处理，无需启动 Celery)
# Write-Host "2. 启动 Celery Worker..." -ForegroundColor Green
# Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$ProjectRoot'; conda activate doccano; cd backend; celery -A config worker -l info --pool=solo"

# 2. 启动 Frontend (Nuxt)
Write-Host "2. 启动 Frontend (Port 3000)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$ProjectRoot'; cd frontend; yarn dev"

Write-Host "------------------------------------------------" -ForegroundColor Yellow
Write-Host "所有服务已在独立窗口中启动！" -ForegroundColor Yellow
Write-Host "请访问前端开发页面: http://localhost:3000" -ForegroundColor Cyan
Write-Host "------------------------------------------------" -ForegroundColor Yellow
