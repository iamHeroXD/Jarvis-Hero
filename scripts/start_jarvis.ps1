# PROJECT J.A.R.V.I.S. Desktop Launcher (PowerShell)
# Boots the FastAPI Python backend and launches the dedicated Command Centre.

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "          PROJECT J.A.R.V.I.S. MASTER COMMAND CENTRE      " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$WorkspaceRoot = "f:\Work\Jarvis- Hero"
Set-Location $WorkspaceRoot
$env:PYTHONPATH = $WorkspaceRoot

# Check if backend is alive
$BackendUp = $false
try {
    $res = Invoke-WebRequest -Uri "http://127.0.0.1:8765/health" -TimeoutSec 1 -UseBasicParsing -ErrorAction SilentlyContinue
    if ($res.StatusCode -eq 200) { $BackendUp = $true }
} catch {}

if (-not $BackendUp) {
    Write-Host "[1/2] Starting JARVIS backend daemon on http://127.0.0.1:8765..." -ForegroundColor Green
    Start-Process python -ArgumentList "-m uvicorn backend.app.main:app --host 127.0.0.1 --port 8765 --log-level warning" -WindowStyle Hidden
    Start-Sleep -Seconds 1
}

Write-Host "[2/2] Launching JARVIS Iron Man Command Centre..." -ForegroundColor Cyan
$ChromePath = "C:\Program Files\Google\Chrome\Application\chrome.exe"
$EdgePath = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

if (Test-Path $ChromePath) {
    Start-Process $ChromePath -ArgumentList "--app=http://127.0.0.1:8765 --window-size=1360,900"
} elseif (Test-Path $EdgePath) {
    Start-Process $EdgePath -ArgumentList "--app=http://127.0.0.1:8765 --window-size=1360,900"
} else {
    Start-Process "http://127.0.0.1:8765"
}

Write-Host "J.A.R.V.I.S. Command Centre online and ready." -ForegroundColor Green
