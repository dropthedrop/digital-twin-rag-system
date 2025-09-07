# Frontend Integration Guide

This document explains how to run and develop the integrated Digital Twin RAG System with the Next.js frontend.

## Architecture Overview

```
┌─────────────────┐    HTTP API    ┌──────────────────┐
│   Next.js       │◄──────────────►│   Python         │
│   Frontend      │                │   FastAPI        │
│   (Port 3000)   │                │   (Port 8000)    │
└─────────────────┘                └──────────────────┘
                                           │
                                           ▼
                                   ┌──────────────────┐
                                   │   RAG System     │
                                   │   PostgreSQL +   │
                                   │   Vector DB      │
                                   └──────────────────┘
```

## Quick Start

### Option 1: Automatic Startup (Recommended)
```bash
# On Windows
start.bat

# On Linux/Mac
chmod +x start.sh && ./start.sh
```

### Option 2: Manual Startup

1. **Start Python API Server**:
```bash
pip install -r requirements.txt
python -m uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
```

2. **Start Next.js Frontend** (in a new terminal):
```bash
cd frontend
npm install
npm run dev
```

## Access Points

- **Frontend Application**: http://localhost:3000
- **Python API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000/health

## Features

### Frontend (Next.js + shadcn/ui)
- 🎨 Modern, responsive chat interface
- 💬 Real-time conversation with the RAG system
- 📊 Performance metrics display (latency, confidence, sources)
- 🎯 Source attribution for responses
- 📱 Mobile-friendly design
- 🔐 Admin dashboard (from v0 component)

### Backend (Python FastAPI)
- 🚀 High-performance async API
- 🔍 Integration with existing RAG system
- 📊 Performance monitoring
- 🛡️ CORS enabled for frontend communication
- 📝 Automatic API documentation
- ❤️ Health check endpoints

## Development

### Frontend Development
```bash
cd frontend
npm run dev     # Start development server
npm run build   # Build for production
npm run start   # Start production server
```

### Backend Development
```bash
# Hot reload enabled by default
python -m uvicorn api_server:app --reload

# Or with specific host/port
python -m uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
```

## Environment Setup

### Python Dependencies
```bash
pip install -r requirements.txt
```

### Node.js Dependencies
```bash
cd frontend
npm install
```

## API Integration

The frontend communicates with the Python backend through RESTful API calls:

```typescript
// Example API call from frontend
const response = await fetch('/api/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ message: userInput }),
})
```

The Next.js API route (`/api/chat/route.ts`) then forwards the request to the Python server:

```typescript
// Forward to Python FastAPI
const ragResponse = await fetch('http://localhost:8000/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ query: message }),
})
```

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   - Kill existing processes: `taskkill /f /im python.exe` (Windows) or `pkill python` (Linux/Mac)
   - Or use different ports in the configuration

2. **Frontend Can't Connect to API**
   - Ensure Python API server is running on port 8000
   - Check CORS configuration in `api_server.py`
   - Verify the API URL in `frontend/src/app/api/chat/route.ts`

3. **Missing Dependencies**
   ```bash
   # Python
   pip install -r requirements.txt
   
   # Node.js
   cd frontend && npm install
   ```

### Logs

- **Python API Logs**: Check the terminal running uvicorn
- **Frontend Logs**: Check browser console and Next.js terminal
- **Network Issues**: Use browser dev tools Network tab

## Production Deployment

For production deployment:

1. **Build the frontend**:
```bash
cd frontend
npm run build
npm run start
```

2. **Run Python API with production settings**:
```bash
python -m uvicorn api_server:app --host 0.0.0.0 --port 8000 --workers 4
```

3. **Use environment variables for configuration**:
   - Database connections
   - API URLs
   - Security settings

## Testing

### Test the API
```bash
curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "What is the system architecture?"}'
```

### Test the Frontend
1. Open http://localhost:3000
2. Navigate to the chat interface
3. Send test messages
4. Verify responses and metadata display

## Next Steps

- [ ] Integrate real RAG system with the API server
- [ ] Add authentication and user management
- [ ] Implement conversation history
- [ ] Add file upload capabilities
- [ ] Set up production deployment
- [ ] Add monitoring and analytics