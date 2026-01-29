# Quick Setup Script for Railway Deployment
# Run this to initialize Git and prepare for deployment

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Rugby Optimizer - Railway Deployment Setup" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check if Git is installed
try {
    $gitVersion = git --version
    Write-Host "[✓] Git is installed: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "[✗] Git is not installed!" -ForegroundColor Red
    Write-Host "Please install Git from: https://git-scm.com/download/win" -ForegroundColor Yellow
    Write-Host ""
    pause
    exit 1
}

Write-Host ""
Write-Host "[1/5] Initializing Git repository..." -ForegroundColor Yellow
git init
if ($LASTEXITCODE -eq 0) {
    Write-Host "[✓] Git repository initialized" -ForegroundColor Green
} else {
    Write-Host "[!] Git already initialized or error occurred" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[2/5] Adding all files to Git..." -ForegroundColor Yellow
git add .
Write-Host "[✓] Files staged" -ForegroundColor Green

Write-Host ""
Write-Host "[3/5] Creating initial commit..." -ForegroundColor Yellow
git commit -m "Initial commit - Ready for Railway deployment"
if ($LASTEXITCODE -eq 0) {
    Write-Host "[✓] Initial commit created" -ForegroundColor Green
} else {
    Write-Host "[!] Commit skipped (no changes or error)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[4/5] Checking status..." -ForegroundColor Yellow
git status

Write-Host ""
Write-Host "[5/5] Checking files..." -ForegroundColor Yellow
if (Test-Path "requirements.txt") {
    Write-Host "[✓] requirements.txt exists" -ForegroundColor Green
} else {
    Write-Host "[✗] requirements.txt missing!" -ForegroundColor Red
}

if (Test-Path "Procfile") {
    Write-Host "[✓] Procfile exists" -ForegroundColor Green
} else {
    Write-Host "[✗] Procfile missing!" -ForegroundColor Red
}

if (Test-Path "railway.toml") {
    Write-Host "[✓] railway.toml exists" -ForegroundColor Green
} else {
    Write-Host "[✗] railway.toml missing!" -ForegroundColor Red
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "NEXT STEPS:" -ForegroundColor Yellow
Write-Host ""
Write-Host "Option 1: Deploy via GitHub (Recommended)" -ForegroundColor White
Write-Host "  1. Create a new repository on GitHub" -ForegroundColor Gray
Write-Host "  2. Copy the remote URL" -ForegroundColor Gray
Write-Host "  3. Run: git remote add origin YOUR_GITHUB_URL" -ForegroundColor Cyan
Write-Host "  4. Run: git push -u origin main" -ForegroundColor Cyan
Write-Host "  5. Go to railway.app and connect your GitHub repo" -ForegroundColor Gray
Write-Host ""
Write-Host "Option 2: Deploy via Railway CLI" -ForegroundColor White
Write-Host "  1. Install: npm install -g @railway/cli" -ForegroundColor Cyan
Write-Host "  2. Login: railway login" -ForegroundColor Cyan
Write-Host "  3. Initialize: railway init" -ForegroundColor Cyan
Write-Host "  4. Deploy: railway up" -ForegroundColor Cyan
Write-Host ""
Write-Host "Read RAILWAY_DEPLOYMENT.md for detailed instructions!" -ForegroundColor Yellow
Write-Host "============================================" -ForegroundColor Cyan

pause
