@echo off
title PROJECT J.A.R.V.I.S.
cd /d "f:\Work\Jarvis- Hero"
set PYTHONPATH=f:\Work\Jarvis- Hero

:: 1. Zero-delay check if backend daemon is running on port 8765 (<10ms via native curl)
curl.exe -s -m 1 http://127.0.0.1:8765/health >nul 2>&1
if %errorlevel% neq 0 (
    echo [JARVIS] Initialising neural backend...
    start "" /b python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8765 --log-level warning
    timeout /t 1 /nobreak >nul
)

:: 2. Launch dedicated cinematic desktop command window (<0.3 seconds)
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --app="http://127.0.0.1:8765" --window-size=1360,900
) else if exist "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" (
    start "" "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --app="http://127.0.0.1:8765" --window-size=1360,900
) else (
    start "" "http://127.0.0.1:8765"
)

exit
