#!/bin/bash

# Digital Twin RAG System Startup Script

echo "🚀 Starting Digital Twin RAG System..."

# Function to check if a port is in use
check_port() {
    netstat -tuln | grep ":$1 " > /dev/null 2>&1
}

# Kill existing processes on our ports
echo "🧹 Cleaning up existing processes..."
if check_port 8000; then
    echo "Stopping existing Python API server on port 8000..."
    pkill -f "uvicorn.*api_server" 2>/dev/null || true
    pkill -f "python.*api_server" 2>/dev/null || true
fi

if check_port 3000; then
    echo "Stopping existing Next.js server on port 3000..."
    pkill -f "next.*dev" 2>/dev/null || true
    pkill -f "node.*next" 2>/dev/null || true
fi

sleep 2

# Start Python API server
echo "🐍 Starting Python FastAPI server..."
cd "$(dirname "$0")"
python -m uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload &
API_PID=$!

# Wait for API to start
echo "⏳ Waiting for API server to start..."
sleep 5

# Check if API is running
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Python API server started successfully on http://localhost:8000"
else
    echo "❌ Failed to start Python API server"
    kill $API_PID 2>/dev/null || true
    exit 1
fi

# Start Next.js frontend
echo "⚛️  Starting Next.js frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!

# Wait for frontend to start
echo "⏳ Waiting for frontend to start..."
sleep 10

# Check if frontend is running
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Next.js frontend started successfully on http://localhost:3000"
else
    echo "❌ Failed to start Next.js frontend"
    kill $API_PID $FRONTEND_PID 2>/dev/null || true
    exit 1
fi

echo ""
echo "🎉 Digital Twin RAG System is now running!"
echo "📊 API Server: http://localhost:8000"
echo "🌐 Frontend: http://localhost:3000"
echo "📖 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down Digital Twin RAG System..."
    kill $API_PID $FRONTEND_PID 2>/dev/null || true
    echo "✅ All services stopped"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup INT TERM

# Wait for user interrupt
wait