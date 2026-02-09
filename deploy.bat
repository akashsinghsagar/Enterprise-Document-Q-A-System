@echo off
REM Quick Deploy Script for Windows
REM Usage: deploy.bat [docker|render|railway|streamlit|local]

setlocal enabledelayedexpansion

set DEPLOY_METHOD=%1
if "%DEPLOY_METHOD%"=="" set DEPLOY_METHOD=docker

echo 🚀 Enterprise Document Q&A - Quick Deploy
echo ==========================================
echo.

REM Check for NVIDIA API Key
if "%NVIDIA_API_KEY%"=="" (
    echo ⚠️  NVIDIA_API_KEY not found in environment
    set /p NVIDIA_API_KEY="Enter your NVIDIA API Key: "
)

if "%DEPLOY_METHOD%"=="docker" (
    echo 🐳 Deploying with Docker...
    echo.
    
    echo 📦 Building Docker image...
    docker build -t docqa-system:latest .
    
    echo 🏃 Starting container...
    docker stop docqa 2>nul
    docker rm docqa 2>nul
    
    docker run -d ^
        -p 8000:8000 ^
        -p 8501:8501 ^
        -e NVIDIA_API_KEY=%NVIDIA_API_KEY% ^
        -v "%cd%\data:/app/data" ^
        -v "%cd%\logs:/app/logs" ^
        --name docqa ^
        --restart unless-stopped ^
        docqa-system:latest
    
    echo.
    echo ✅ Deployment complete!
    echo.
    echo 🌐 Access your application:
    echo    Frontend: http://localhost:8501
    echo    Backend:  http://localhost:8000
    echo    API Docs: http://localhost:8000/docs
    echo.
    echo 📝 View logs: docker logs -f docqa
    
) else if "%DEPLOY_METHOD%"=="docker-compose" (
    echo 🐳 Deploying with Docker Compose...
    echo.
    
    echo NVIDIA_API_KEY=%NVIDIA_API_KEY% > .env
    
    docker-compose down 2>nul
    docker-compose up -d --build
    
    echo.
    echo ✅ Deployment complete!
    echo.
    echo 🌐 Access your application:
    echo    Frontend: http://localhost:8501
    echo    Backend:  http://localhost:8000
    
) else if "%DEPLOY_METHOD%"=="local" (
    echo 💻 Starting local development servers...
    echo.
    
    echo 📦 Installing dependencies...
    pip install -r requirements.txt
    
    echo 🔧 Starting backend...
    start /B python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    
    timeout /t 3 /nobreak >nul
    
    echo 🎨 Starting frontend...
    start /B streamlit run frontend/ui.py --server.port 8501
    
    echo.
    echo ✅ Local servers started!
    echo.
    echo 🌐 Access your application:
    echo    Frontend: http://localhost:8501
    echo    Backend:  http://localhost:8000
    echo.
    echo Press any key to stop servers...
    pause >nul
    
    taskkill /F /FI "WINDOWTITLE eq uvicorn*" 2>nul
    taskkill /F /FI "WINDOWTITLE eq streamlit*" 2>nul
    
) else if "%DEPLOY_METHOD%"=="render" (
    echo ☁️  Deploying to Render.com...
    echo.
    echo 📋 Next steps:
    echo 1. Push code to GitHub/GitLab
    echo 2. Go to https://render.com
    echo 3. Click 'New +' → 'Blueprint'
    echo 4. Connect your repository
    echo 5. Add NVIDIA_API_KEY environment variable
    echo 6. Click 'Apply'
    
) else if "%DEPLOY_METHOD%"=="railway" (
    echo 🚂 Deploying to Railway...
    echo.
    
    where railway >nul 2>nul
    if errorlevel 1 (
        echo Installing Railway CLI...
        npm install -g @railway/cli
    )
    
    echo 🔐 Login to Railway...
    railway login
    
    echo 🚀 Deploying...
    railway init
    railway variables set NVIDIA_API_KEY=%NVIDIA_API_KEY%
    railway up
    
    echo.
    echo ✅ Deployment complete!
    echo 🌐 Generate domain with: railway domain
    
) else if "%DEPLOY_METHOD%"=="streamlit" (
    echo 🎈 Preparing for Streamlit Community Cloud...
    echo.
    echo 📋 Next steps:
    echo 1. Push code to GitHub
    echo 2. Go to https://share.streamlit.io
    echo 3. Click 'New app'
    echo 4. Select repo and set: frontend/ui.py
    echo 5. Add secrets: API_BASE_URL, NVIDIA_API_KEY
    
) else (
    echo ❌ Unknown deployment method: %DEPLOY_METHOD%
    echo.
    echo Usage: deploy.bat [METHOD]
    echo.
    echo Available methods:
    echo   docker          - Deploy with Docker
    echo   docker-compose  - Deploy with Docker Compose
    echo   render          - Deploy to Render.com
    echo   railway         - Deploy to Railway.app
    echo   streamlit       - Deploy to Streamlit Cloud
    echo   local           - Run local development servers
)

endlocal
