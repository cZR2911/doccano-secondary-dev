@echo off
setlocal

:: Configuration
set "CONDA_PATH=C:\Users\mlian\miniconda3"
set "ENV_NAME=doccano"
set "PROJECT_ROOT=C:\Users\mlian\doccano"

:: Activate Conda
echo Activating Conda environment '%ENV_NAME%'...
call "%CONDA_PATH%\Scripts\activate.bat" "%CONDA_PATH%"
call conda activate %ENV_NAME%
if errorlevel 1 (
    echo Failed to activate Conda environment.
    pause
    exit /b 1
)

:: Start Backend
echo Starting Backend (Django)...
start "Doccano Backend" cmd /k "cd /d %PROJECT_ROOT%\backend && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"

:: Start Celery
echo Starting Celery Worker...
start "Doccano Celery" cmd /k "cd /d %PROJECT_ROOT%\backend && celery -A config worker -l info --pool=solo"

:: Start Frontend
echo Starting Frontend (Nuxt)...
start "Doccano Frontend" cmd /k "cd /d %PROJECT_ROOT%\frontend && yarn dev"

echo.
echo All services started in separate windows.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
pause
