@echo off
setlocal EnableDelayedExpansion
title Fin-Sight Startup

echo.
echo  =======================================
echo   Fin-Sight AI Credit Appraisal Engine
echo  =======================================
echo.

:: ── 1. Check Python ──────────────────────────────────────────────────────────
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python not found. Install Python 3.10+ and add it to PATH.
    pause
    exit /b 1
)

for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set PY_VER=%%v
echo [OK] Python %PY_VER% found.

:: ── 2. Create / activate virtual environment ─────────────────────────────────
if not exist ".venv\Scripts\activate.bat" (
    echo [INFO] Creating virtual environment...
    python -m venv .venv
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created.
) else (
    echo [OK] Virtual environment found.
)

call .venv\Scripts\activate.bat

:: ── 3. Install / upgrade dependencies ────────────────────────────────────────
echo.
echo [INFO] Installing dependencies (requirements.txt)...
pip install -q --upgrade pip
pip install -q -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Dependency installation failed. Check requirements.txt.
    pause
    exit /b 1
)
echo [OK] Dependencies installed.

:: ── 4. Copy .env.example → .env if .env is missing ──────────────────────────
if not exist ".env" (
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
        echo [INFO] .env created from .env.example — add your API keys before continuing.
    )
) else (
    echo [OK] .env found.
)

:: ── 5. Open browser with a short delay, then start server ────────────────────
echo.
echo [INFO] Starting server at http://127.0.0.1:8140
echo [INFO] Press Ctrl+C to stop.
echo.

:: Open browser after 3 seconds
start "" cmd /c "timeout /t 3 /nobreak >nul && start http://127.0.0.1:8140"

python api.py

echo.
echo [INFO] Server stopped.
pause
