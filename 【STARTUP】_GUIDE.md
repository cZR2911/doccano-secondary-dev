# 📖 Doccano 二次开发环境启动指南

## 🔗 快速访问地址
*   **前端开发界面 (标注人员/用户入口)**: [http://localhost:3000](http://localhost:3000)
    *   *默认账号/密码: admin / password*
*   **后端管理后台 (开发/管理人员入口)**: [http://localhost:8000/admin/](http://localhost:8000/admin/)

> 🚨 **特别重要提示 (CRITICAL)**：
> **必须确保 Celery 窗口正在运行！**
> Celery 负责后台任务（如导入文件、导出数据）。
> **如果您发现上传文件一直“转圈圈”不结束，99% 是因为 Celery 没有启动或报错退出了。**

---

本指南旨在帮助您在本地搭建并运行 Doccano 的开发环境。

---

## 🛠️ 首次运行准备 (仅需执行一次)

如果您是第一次运行，请按照以下步骤配置环境：

### 1. 后端环境 (Conda + Poetry)
打开 PowerShell，执行：
```powershell
# 1. 创建虚拟环境
conda create -n doccano python=3.8 -y

# 2. 激活环境并安装依赖
conda activate doccano
cd backend
pip install poetry
poetry install
```

### 2. 前端环境 (Node.js + Yarn)
确保已安装 [Node.js LTS](https://nodejs.org/)。
```powershell
cd frontend
yarn install
```

### 3. 设置 PowerShell 执行策略 (解决脚本无法运行)
以管理员身份运行 PowerShell，执行：
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 🚀 日常一键启动 (唯一推荐)

项目根目录下提供了一个全自动启动脚本 `start_doccano.bat` (Windows 批处理文件)。**请使用此脚本，不要使用旧版 ps1 脚本。**

**启动步骤：**
1.  在项目文件夹中找到 `start_doccano.bat`。
2.  **直接双击**该文件即可运行 (无需右键)。
3.  脚本会自动打开三个新窗口：
    *   **Backend**: 运行在 `http://127.0.0.1:8000` (提供 API 和后台管理)
    *   **Celery**: **必须运行！** 负责处理文件导入、导出等耗时任务。如果不启动，上传文件会一直转圈。
    *   **Frontend**: 运行在 `http://127.0.0.1:3000` (提供标注界面)
4.  **等待约 30-60 秒**，直到前端窗口显示 `Nuxt @ v2.x.x Listening on...`。
5.  系统通常会自动打开浏览器；如果没有，请手动访问：**[http://localhost:3000](http://localhost:3000)**

---

## ⚠️ 旧版启动方式 (已废弃)

请**不要**使用 `dev_start.ps1`，该脚本在部分系统上可能导致闪退或权限问题。请统一使用上面的 `start_doccano.bat`。

---

## �️ 手动分步启动 (若脚本失效时使用)

如果一键脚本运行异常，请手动开启三个 PowerShell 终端：

### 终端 1: 后端服务 (API)
```powershell
conda activate doccano
cd backend
python manage.py runserver
```

### 终端 2: 任务队列 (Celery)
> **注意**：必须启动此项，否则文件导入/导出功能将无法工作（一直转圈）。
```powershell
conda activate doccano
cd backend
celery -A config worker -l info --pool=solo
```

### 终端 3: 前端界面 (UI)
```powershell
cd frontend
yarn dev
```

---

## ❓ 常见问题排查 (Troubleshooting)

### 1. 访问 3000 端口显示“拒绝连接”
*   **原因**：前端 Nuxt 还在编译中，或者启动失败。
*   **解决**：检查前端窗口，确保没有红色报错。看到 `Listening on: http://localhost:3000/` 才算启动成功。

### 2. 登录时提示“404”或“Proxy Error”
*   **原因**：后端服务（8000 端口）没启动。
*   **解决**：确保后端窗口显示 `Starting development server at http://127.0.0.1:8000/`。

### 3. 端口被占用
*   **解决**：如果提示端口 8000 或 3000 已被占用，请关闭其他正在运行的 Doccano 实例或重启电脑。

---

## 📊 数据导入说明 (新功能)

### 1. Excel 多列导入与一键全选
在导入 Excel/CSV 文件时，如果希望导入所有列（合并显示）：
*   在导入界面，点击输入框右侧的 **“全选按钮”** (图标为方框内带勾)。
*   系统会自动选中所有识别到的列名。
*   再次点击可清空选择。

### 2. 批注与纠错导入
如果您希望直接导入已有的批注或纠错信息，请在 Excel 中准备名为 **`comment`** 或 **`correction`** 的列，系统会自动将其识别为“批注与纠错”内容。
