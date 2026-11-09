# Automated test runner for Project J.A.R.V.I.S.
$WorkspaceRoot = "f:\Work\Jarvis- Hero"
Set-Location $WorkspaceRoot
$env:PYTHONPATH = $WorkspaceRoot

Write-Host "Running comprehensive pytest test suite..." -ForegroundColor Cyan
pytest tests/ -v --tb=short
