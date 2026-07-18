@echo off
title Detective Game Core Launcher
echo ===================================================
echo   LAUNCHING CRIME SCENE DETECTIVE GAME CONSOLE
echo ===================================================
echo.

:: Lock the running context directory to where this bat file lives
cd /d "%~dp0"

:: Verify structure before firing python compiler loops
if not exist "backend\game.py" (
    echo [ERROR] Critical framework configuration error: backend\game.py not found!
    pause
    exit /b
)

echo [*] Initializing engine workspace context...
python backend/game.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [CRITICAL] Runtime closed unexpectedly with system error code %ERRORLEVEL%.
    echo Trace details have been dumped to logs/game_errors.txt
    pause
)