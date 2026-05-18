@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0"
set PYTHON="%~dp0.venv\Scripts\python.exe"
echo ==============================================
echo    RAG-Philosophy System Launcher
echo ==============================================
echo.

:: Step 1: Start Docker infrastructure
echo [1/4] Starting Docker infrastructure (Redis, Qdrant, Postgres)...
docker-compose up -d redis postgres qdrant minio
if errorlevel 1 (
    echo.
    echo [WARNING] Docker failed. Make sure Docker Desktop is running!
    echo Press any key to continue anyway...
    pause > nul
)
echo      [OK] Infrastructure containers started.
echo.

:: Wait for services to be ready
echo      Waiting 5s for services to initialize...
timeout /t 5 /nobreak > nul

:: Step 2: Start Backend (FastAPI)
echo [2/4] Starting Backend (FastAPI on port 8000)...
start "RAG Backend" cmd /k "cd /d "%~dp0" && %PYTHON% -m uvicorn backend.app.main:app --reload"
echo      [OK] Backend starting...
echo.

:: Step 3: Start Celery Worker
echo [3/4] Starting Celery Worker (for PDF ingestion)...
start "RAG Worker" cmd /k "cd /d "%~dp0" && %PYTHON% -m celery -A backend.app.worker.celery_app worker -Q ingest -l info -P solo"
echo      [OK] Celery worker starting...
echo.

:: Step 4: Start Frontend
echo [4/4] Starting Frontend (on port 5500)...
start "RAG Frontend" cmd /k "cd /d "%~dp0frontend" && %PYTHON% -m http.server 5500 --bind 127.0.0.1"
echo      [OK] Frontend starting...
echo.

:: Open browser
echo Waiting 4 seconds for all servers...
timeout /t 4 /nobreak > nul

echo.
echo ==============================================
echo    All services started!
echo    Frontend:  http://127.0.0.1:5500
echo    Backend:   http://127.0.0.1:8000
echo    API Docs:  http://127.0.0.1:8000/docs
echo ==============================================
echo.

echo Opening browser...
start "" "http://127.0.0.1:5500"
