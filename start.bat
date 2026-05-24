@echo off
setlocal EnableExtensions
chcp 65001 >nul 2>&1
cd /d "%~dp0"

echo ==============================================
echo    RAG-Philosophy Local Dev Launcher
echo ==============================================
echo.

if not exist ".env" (
    echo [ERROR] .env was not found.
    echo Create .env from .env.example and fill required API keys before starting.
    echo.
    pause
    exit /b 1
)

where docker >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker was not found in PATH.
    echo Docker is needed for Redis, Postgres, Qdrant, and MinIO.
    echo.
    pause
    exit /b 1
)

docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Desktop is not running.
    echo Start Docker Desktop, wait until it is ready, then run this file again.
    echo.
    pause
    exit /b 1
)

docker compose version >nul 2>&1
if errorlevel 1 (
    where docker-compose >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Docker Compose was not found.
        echo Install Docker Desktop with Compose support, then run this file again.
        echo.
        pause
        exit /b 1
    )
    set "COMPOSE_CMD=docker-compose"
) else (
    set "COMPOSE_CMD=docker compose"
)

echo [1/5] Starting infrastructure containers only...
%COMPOSE_CMD% stop nginx backend worker >nul 2>&1
%COMPOSE_CMD% up -d redis postgres qdrant minio
if errorlevel 1 (
    echo.
    echo [ERROR] Could not start infrastructure containers.
    echo Run "%COMPOSE_CMD% logs --tail=100" to inspect the error.
    echo.
    pause
    exit /b 1
)

echo.
echo [2/5] Preparing Python virtual environment...
if not exist ".venv\Scripts\python.exe" (
    where py >nul 2>&1
    if errorlevel 1 (
        python -m venv .venv
    ) else (
        py -3 -m venv .venv
    )
    if errorlevel 1 (
        echo [ERROR] Failed to create .venv.
        echo.
        pause
        exit /b 1
    )
)

set "PYTHON=%~dp0.venv\Scripts\python.exe"
set "PIP=%~dp0.venv\Scripts\pip.exe"

echo.
echo [3/5] Installing/updating Python requirements...
"%PYTHON%" -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo [ERROR] pip install failed.
    echo.
    pause
    exit /b 1
)

echo.
echo [4/5] Applying local runtime overrides...
set "PYTHONPATH=%~dp0"
set "DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/rag_db"
set "REDIS_BROKER_URL=redis://localhost:6379/0"
set "REDIS_RESULT_BACKEND=redis://localhost:6379/1"
set "QDRANT_URL=http://localhost:6333"
set "QDRANT_HOST=localhost"
set "QDRANT_PORT=6333"
set "OBJECT_STORAGE_BACKEND=minio"
set "MINIO_ENDPOINT=localhost:9000"
set "MINIO_ACCESS_KEY=minioadmin"
set "MINIO_SECRET_KEY=minioadmin"
set "MINIO_BUCKET=rag-documents"
set "MINIO_SECURE=false"
set "OLLAMA_BASE_URL=http://localhost:11434"
set "LOCAL_LLM_BASE_URL=http://localhost:11434"

echo.
echo [5/5] Starting local services...
start "RAG Backend" cmd /k "cd /d "%~dp0" && set PYTHONPATH=%PYTHONPATH%&& set DATABASE_URL=%DATABASE_URL%&& set REDIS_BROKER_URL=%REDIS_BROKER_URL%&& set REDIS_RESULT_BACKEND=%REDIS_RESULT_BACKEND%&& set QDRANT_URL=%QDRANT_URL%&& set QDRANT_HOST=%QDRANT_HOST%&& set QDRANT_PORT=%QDRANT_PORT%&& set OBJECT_STORAGE_BACKEND=%OBJECT_STORAGE_BACKEND%&& set MINIO_ENDPOINT=%MINIO_ENDPOINT%&& set MINIO_ACCESS_KEY=%MINIO_ACCESS_KEY%&& set MINIO_SECRET_KEY=%MINIO_SECRET_KEY%&& set MINIO_BUCKET=%MINIO_BUCKET%&& set MINIO_SECURE=%MINIO_SECURE%&& set OLLAMA_BASE_URL=%OLLAMA_BASE_URL%&& set LOCAL_LLM_BASE_URL=%LOCAL_LLM_BASE_URL%&& "%PYTHON%" -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000"
start "RAG Worker" cmd /k "cd /d "%~dp0" && set PYTHONPATH=%PYTHONPATH%&& set DATABASE_URL=%DATABASE_URL%&& set REDIS_BROKER_URL=%REDIS_BROKER_URL%&& set REDIS_RESULT_BACKEND=%REDIS_RESULT_BACKEND%&& set QDRANT_URL=%QDRANT_URL%&& set QDRANT_HOST=%QDRANT_HOST%&& set QDRANT_PORT=%QDRANT_PORT%&& set OBJECT_STORAGE_BACKEND=%OBJECT_STORAGE_BACKEND%&& set MINIO_ENDPOINT=%MINIO_ENDPOINT%&& set MINIO_ACCESS_KEY=%MINIO_ACCESS_KEY%&& set MINIO_SECRET_KEY=%MINIO_SECRET_KEY%&& set MINIO_BUCKET=%MINIO_BUCKET%&& set MINIO_SECURE=%MINIO_SECURE%&& set OLLAMA_BASE_URL=%OLLAMA_BASE_URL%&& set LOCAL_LLM_BASE_URL=%LOCAL_LLM_BASE_URL%&& "%PYTHON%" -m celery -A backend.app.worker.celery_app.celery_app worker -Q ingest -l info -P solo"
start "RAG Frontend" cmd /k "cd /d "%~dp0frontend" && "%PYTHON%" -m http.server 5500 --bind 127.0.0.1"

echo.
echo Waiting 4 seconds for local servers...
timeout /t 4 /nobreak >nul

echo.
echo ==============================================
echo    Local dev services started
echo    Frontend: http://127.0.0.1:5500
echo    Backend:  http://127.0.0.1:8000
echo    API Docs: http://127.0.0.1:8000/docs
echo.
echo    Docker infrastructure:
echo    %COMPOSE_CMD% ps redis postgres qdrant minio
echo ==============================================
echo.

start "" "http://127.0.0.1:5500"

endlocal
