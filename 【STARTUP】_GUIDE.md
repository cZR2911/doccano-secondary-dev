# Doccano 二次开发启动指南

欢迎进行 Doccano 二次开发！由于开发环境需要前后端分离运行，每次开始工作时，你需要启动以下三个服务。

## 核心服务概览

| 服务名称 | 作用 | 端口/地址 | 启动命令简述 |
| :--- | :--- | :--- | :--- |
| **Backend (Django)** | 提供 API 接口、数据库交互 | `http://localhost:8000` | `python manage.py runserver` |
| **Frontend (Nuxt)** | 提供 Web 交互界面 (开发版) | `http://localhost:3000` | `yarn dev` |
| **Celery Worker** | 处理耗时任务 (如导入/导出/训练) | N/A (后台进程) | `celery -A config worker ...` |

---

## 方式一：使用一键启动脚本 (推荐)

我在项目根目录下为您创建了一个 PowerShell 脚本，可以直接双击或在终端运行，它会自动打开三个新窗口分别启动上述服务。

**运行方式：**
1. 在终端中运行：
   ```powershell
   .\dev_start.ps1
   ```
2. 或者在文件管理器中右键点击 `dev_start.ps1` -> "使用 PowerShell 运行"。

---

## 方式二：手动启动 (分步详解)

如果你需要分别查看日志或手动控制，请按照以下步骤开启 **2 个独立的终端窗口**。

### 第 1 个窗口：启动后端 (Backend)
> 确保进入 conda 环境

```powershell
cd C:\Users\mlian\doccano
conda activate doccano
cd backend
python manage.py runserver
```
*成功标志：看到 `Starting development server at http://127.0.0.1:8000/`*

### 第 2 个窗口：启动前端 (Frontend)
> 开发时请访问此端口

```powershell
cd C:\Users\mlian\doccano
cd frontend
yarn dev
```
*成功标志：看到 `Listening on: http://localhost:3000/`*

---

## 开发注意事项

1. **访问地址**：请务必访问 **[http://localhost:3000](http://localhost:3000)** 进行开发和测试。
   * 不要访问 8000 端口，那是纯 API 接口。
2. **代码修改**：
   * 修改 `frontend/` 下的代码，浏览器会自动刷新（热更新）。
   * 修改 `backend/` 下的代码，Django 服务会自动重启。
3. **关闭服务**：
   * 在各自的终端窗口按 `Ctrl + C` 即可停止服务。
