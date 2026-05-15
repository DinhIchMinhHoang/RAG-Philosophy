@echo off
cd /d "%~dp0"
set PYTHON="%~dp0.venv\Scripts\python.exe"
echo ==============================================
echo Starting RAG-Philosophy System
echo ==============================================

echo [1/2] Starting Backend (FastAPI)...
start "RAG Backend" cmd /k "cd /d "%~dp0" && %PYTHON% -m uvicorn backend.app.main:app --reload"

echo [2/2] Starting Frontend (Web)...
start "RAG Frontend" cmd /k "cd /d "%~dp0frontend" && %PYTHON% -m http.server 5500 --bind 127.0.0.1"

echo.
echo Waiting 3 seconds for servers to start...
timeout /t 3 /nobreak > nul

echo Opening browser...
start "" "http://127.0.0.1:5500"
