@echo off
REM Quick Setup Script for Railway Deployment
REM Run this to initialize Git and prepare for deployment

echo ============================================
echo Rugby Optimizer - Railway Deployment Setup
echo ============================================
echo.

REM Check if Git is installed
where git >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Git is not installed!
    echo Please install Git from: https://git-scm.com/download/win
    echo.
    pause
    exit /b 1
)

echo [1/5] Initializing Git repository...
git init
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Git already initialized or error occurred
)
echo.

echo [2/5] Adding all files to Git...
git add .
echo.

echo [3/5] Creating initial commit...
git commit -m "Initial commit - Ready for Railway deployment"
echo.

echo [4/5] Checking status...
git status
echo.

echo ============================================
echo Setup Complete!
echo ============================================
echo.
echo NEXT STEPS:
echo.
echo Option 1: Deploy via GitHub
echo   1. Create a new repository on GitHub
echo   2. Copy the remote URL
echo   3. Run: git remote add origin YOUR_GITHUB_URL
echo   4. Run: git push -u origin main
echo   5. Go to railway.app and connect your GitHub repo
echo.
echo Option 2: Deploy via Railway CLI
echo   1. Install Railway CLI: npm install -g @railway/cli
echo   2. Run: railway login
echo   3. Run: railway init
echo   4. Run: railway up
echo.
echo Read RAILWAY_DEPLOYMENT.md for detailed instructions!
echo ============================================
pause
