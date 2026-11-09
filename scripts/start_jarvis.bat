@echo off
title PROJECT J.A.R.V.I.S.
cd /d "f:\Work\Jarvis- Hero"
set PYTHONPATH=f:\Work\Jarvis- Hero

:: 1. Ultra-fast check if backend is already online on 8765
powershell -NoProfile -Command "try { (Invoke-WebRequest -Uri 'http://127.0.0.1:8765/health' -TimeoutSec 1 -UseBasicParsing).StatusCode -eq 200 } catch { exit 1 }" >nul 2>&1
if %errorlevel% neq 0 (
    start "" /b python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8765 --log-level warning
    timeout /t 1 /nobreak >nul
)

:: 2. Open dedicated desktop window with zero lag (<0.5 seconds)
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --app="http://127.0.0.1:8765" --window-size=1300,860
) else if exist "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" (
    start "" "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --app="http://127.0.0.1:8765" --window-size=1300,860
) else (
    start "" "http://127.0.0.1:8765"
)

exit
