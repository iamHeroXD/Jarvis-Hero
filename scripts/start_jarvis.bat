@echo off
title PROJECT J.A.R.V.I.S.
cd /d "f:\Work\Jarvis- Hero"
set PYTHONPATH=f:\Work\Jarvis- Hero

:: 1. Fast check if backend daemon is already active on port 8765
curl.exe -s -m 1 http://127.0.0.1:8765/health >nul 2>&1
if %errorlevel% neq 0 (
    echo [JARVIS] Initialising neural backend daemon...
    start "" /b python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8765 --log-level warning
)

:: 2. Robust Polling Loop: wait until port 8765 is actively responding before opening browser
echo [JARVIS] Synchronizing neural core...
set /a retries=0
:wait_loop
curl.exe -s -m 1 http://127.0.0.1:8765/health >nul 2>&1
if %errorlevel% equ 0 goto ready
set /a retries+=1
if %retries% geq 25 (
    echo [JARVIS WARNING] Backend initialization taking longer than usual. Launching interface...
    goto ready
)
timeout /t 1 /nobreak >nul
goto wait_loop

:ready
echo [JARVIS] Core online. Launching Command Centre...
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --app="http://127.0.0.1:8765" --window-size=1360,900
) else if exist "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" (
    start "" "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --app="http://127.0.0.1:8765" --window-size=1360,900
) else (
    start "" "http://127.0.0.1:8765"
)

exit
