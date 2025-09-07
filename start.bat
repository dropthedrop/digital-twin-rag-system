@echo off
echo 🚀 Starting Digital Twin RAG System...

REM Change to project directory
cd /d "%~dp0"

REM Kill existing processes
echo 🧹 Cleaning up existing processes...
taskkill /f /im uvicorn.exe >nul 2>&1
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1

timeout /t 2 >nul

REM Start Python API server
echo 🐍 Starting Python FastAPI server...
start "Python API Server" cmd /k "python -m uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload"

REM Wait for API to start
echo ⏳ Waiting for API server to start...
timeout /t 8 >nul

REM Check if API is running
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Python API server started successfully on http://localhost:8000
) else (
    echo ❌ API server may still be starting, check the Python window...
)

REM Start Next.js frontend
echo ⚛️  Starting Next.js frontend...
cd frontend
start "Next.js Frontend" cmd /k "npm run dev"

REM Wait for frontend to start
echo ⏳ Waiting for frontend to start...
timeout /t 10 >nul

echo.
echo 🎉 Digital Twin RAG System is now running!
echo 📊 API Server: http://localhost:8000
echo 🌐 Frontend: http://localhost:3000
echo 📖 API Docs: http://localhost:8000/docs
echo.
echo Check the opened terminal windows for logs
echo Press any key to open the frontend in your browser...
pause >nul

start http://localhost:3000