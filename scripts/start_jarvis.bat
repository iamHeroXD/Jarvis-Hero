@echo off
title PROJECT J.A.R.V.I.S. Command Centre
echo ==========================================================
echo           PROJECT J.A.R.V.I.S. MASTER COMMAND CENTRE      
echo ==========================================================
cd /d "f:\Work\Jarvis- Hero"
set PYTHONPATH=f:\Work\Jarvis- Hero

echo [1/3] Starting backend engine on 127.0.0.1:8765...
start "JARVIS Backend Engine" /min python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8765 --log-level info

timeout /t 3 /nobreak >nul

echo [2/3] Launching JARVIS Desktop Interface...
cd /d "f:\Work\Jarvis- Hero\apps\desktop"
call npm run tauri dev

echo System stood down.
pause
