# PROJECT J.A.R.V.I.S. Desktop Launcher (PowerShell)
# Boots the FastAPI Python backend and launches the Tauri desktop application.

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "          PROJECT J.A.R.V.I.S. MASTER COMMAND CENTRE      " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$WorkspaceRoot = "f:\Work\Jarvis- Hero"
Set-Location $WorkspaceRoot
$env:PYTHONPATH = $WorkspaceRoot

Write-Host "[1/3] Validating system health and local database..." -ForegroundColor Yellow
python -c "from backend.app.core.config import settings; print(f'Config verified. Database at {settings.database_url}')"
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Python environment validation failed." -ForegroundColor Red
    exit 1
}

Write-Host "[2/3] Starting JARVIS backend daemon on http://127.0.0.1:8765..." -ForegroundColor Green
$BackendJob = Start-Job -ScriptBlock {
    param($root)
    Set-Location $root
    $env:PYTHONPATH = $root
    python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8765 --log-level info
} -ArgumentList $WorkspaceRoot

Start-Sleep -Seconds 3

Write-Host "[3/3] Launching JARVIS Desktop Command Centre UI..." -ForegroundColor Cyan
Set-Location "$WorkspaceRoot\apps\desktop"
npm run tauri dev

# Clean up backend job when frontend closes
Stop-Job $BackendJob
Remove-Job $BackendJob
Write-Host "Systems stood down. Good day, sir." -ForegroundColor Cyan
