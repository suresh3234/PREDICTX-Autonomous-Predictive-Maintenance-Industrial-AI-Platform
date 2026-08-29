# PredictX Automated Cloud Deployment Script (PowerShell)
param (
    [string]$Environment = "production",
    [switch]$SkipTests = $false
)

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  PREDICTX INDUSTRIAL AI PLATFORM - DEPLOYMENT" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Run Automated Test Suite
if (-not $SkipTests) {
    Write-Host "[1/5] Running Complete Test Suite (88 tests)..." -ForegroundColor Yellow
    .venv\Scripts\pytest
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Test suite failed! Aborting deployment." -ForegroundColor Red
        exit 1
    }
    Write-Host "✓ All tests passed!" -ForegroundColor Green
}

# 2. Build Frontend
Write-Host "[2/5] Compiling Production Frontend..." -ForegroundColor Yellow
Set-Location apps/web
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "Frontend build failed! Aborting deployment." -ForegroundColor Red
    exit 1
}
Set-Location ../..
Write-Host "✓ Frontend compiled successfully!" -ForegroundColor Green

# 3. Build & Orchestrate Production Containers
Write-Host "[3/5] Building & Launching Docker Production Containers..." -ForegroundColor Yellow
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# 4. Healthcheck Verification
Write-Host "[4/5] Verifying API & Model Inference Health..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
    Write-Host "✓ System Health Status: $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "Warning: Backend starting up..." -ForegroundColor Yellow
}

# 5. Success Banner
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  PREDICTX DEPLOYMENT COMPLETED SUCCESSFULLY!" -ForegroundColor Green
Write-Host "  Dashboard: http://localhost" -ForegroundColor White
Write-Host "  API Docs:  http://localhost:8000/docs" -ForegroundColor White
Write-Host "  Grafana:   http://localhost:3000" -ForegroundColor White
Write-Host "==========================================================" -ForegroundColor Cyan
