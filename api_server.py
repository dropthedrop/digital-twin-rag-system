from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager
import asyncio
import time
import json
import os
from typing import List, Optional, Dict, Any
import logging

# Import our existing RAG functionality
import sys
sys.path.append('.')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global RAG system instance (we'll initialize this)
rag_system = None

async def initialize_rag_system():
    """Initialize the RAG system on startup"""
    global rag_system
    try:
        # Here we would initialize our RAG system
        # For now, we'll create a mock system
        logger.info("Initializing RAG system...")
        
        # In a real implementation, you would:
        # 1. Load environment variables
        # 2. Connect to PostgreSQL
        # 3. Connect to Upstash Vector
        # 4. Initialize embedding models
        
        rag_system = {
            "initialized": True,
            "postgres_connected": True,
            "vector_db_connected": True,
            "embedding_model": "mixbread-large-1024"
        }
        
        logger.info("RAG system initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize RAG system: {str(e)}")
        rag_system = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await initialize_rag_system()
    yield
    # Shutdown
    logger.info("Shutting down RAG system...")

app = FastAPI(
    title="Digital Twin RAG API",
    description="Advanced RAG system with PostgreSQL and Vector Database",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str
    max_results: Optional[int] = 5
    similarity_threshold: Optional[float] = 0.7

class QueryResponse(BaseModel):
    content: str
    sources: List[str]
    confidence: float
    latency: float
    timestamp: str
    metadata: Optional[Dict[str, Any]] = None

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    database_status: str

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    database_status = "connected" if rag_system and rag_system.get("postgres_connected") else "disconnected"
    
    return HealthResponse(
        status="healthy" if rag_system else "unhealthy",
        timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
        version="1.0.0",
        database_status=database_status
    )

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process a query through the RAG system"""
    if not rag_system:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    start_time = time.time()
    
    try:
        # Simulate RAG processing
        # In a real implementation, this would:
        # 1. Generate embeddings for the query
        # 2. Search vector database for similar content
        # 3. Retrieve relevant documents from PostgreSQL
        # 4. Generate response using LLM
        
        await asyncio.sleep(0.1 + (len(request.query) / 1000))  # Simulate processing time
        
        # Mock response based on query content
        response_content = generate_mock_response(request.query)
        sources = get_mock_sources(request.query)
        confidence = calculate_mock_confidence(request.query)
        
        latency = time.time() - start_time
        
        return QueryResponse(
            content=response_content,
            sources=sources,
            confidence=confidence,
            latency=latency,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            metadata={
                "query_length": len(request.query),
                "processing_method": "mock_rag",
                "vector_results": len(sources)
            }
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")

def generate_mock_response(query: str) -> str:
    """Generate a mock response based on the query"""
    query_lower = query.lower()
    
    if any(word in query_lower for word in ["system", "architecture", "database"]):
        return f"""The Digital Twin RAG system uses a hybrid architecture combining PostgreSQL and Upstash Vector databases. 
        The system maintains an 8-table PostgreSQL schema with 61 optimized indexes and leverages 19 vector embeddings 
        using the 1024-dimensional mixbread-large model. Current performance metrics show 86.7% accuracy with 
        0.265s average latency and 3.8 queries per second throughput."""
    
    elif any(word in query_lower for word in ["performance", "speed", "latency"]):
        return f"""Current system performance metrics: Average latency of 0.265 seconds, throughput of 3.8 queries 
        per second, and 86.7% test success rate (13/15 tests passing). The vector search typically completes in 
        under 100ms, while PostgreSQL queries average 165ms response time."""
    
    elif any(word in query_lower for word in ["test", "testing", "results"]):
        return f"""The RAG system has been thoroughly tested with a success rate of 86.7% (13 out of 15 tests passing). 
        Testing covers vector similarity search, content retrieval, chunk ID mapping, and end-to-end query processing. 
        Recent improvements fixed critical chunk ID mapping issues between the vector database and PostgreSQL."""
    
    else:
        return f"""Based on your query about "{query}", I can provide information from the knowledge base. 
        The Digital Twin RAG system combines advanced vector search with relational database querying to deliver 
        accurate, contextual responses. The system processes your request through semantic similarity matching 
        and retrieves the most relevant information from our comprehensive knowledge repository."""

def get_mock_sources(query: str) -> List[str]:
    """Get mock sources based on query content"""
    query_lower = query.lower()
    
    base_sources = ["schema/complete_schema.sql", "test_rag_functionality.py"]
    
    if "system" in query_lower or "architecture" in query_lower:
        return base_sources + ["docs/current_system_overview.md", "IMPLEMENTATION_SUMMARY.md"]
    elif "performance" in query_lower:
        return base_sources + ["rag_test_results.json", "upstash_vector_test_results.json"]
    elif "test" in query_lower:
        return base_sources + ["test_rag_functionality.py", "debug_rag.py"]
    else:
        return base_sources + ["README.md"]

def calculate_mock_confidence(query: str) -> float:
    """Calculate mock confidence based on query characteristics"""
    base_confidence = 0.85
    
    # Adjust confidence based on query length and specificity
    if len(query) < 10:
        return max(0.6, base_confidence - 0.2)
    elif len(query) > 50:
        return min(0.95, base_confidence + 0.1)
    
    # Higher confidence for technical queries
    technical_terms = ["database", "vector", "embedding", "sql", "performance", "latency"]
    if any(term in query.lower() for term in technical_terms):
        return min(0.92, base_confidence + 0.07)
    
    return base_confidence

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Digital Twin RAG API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "query": "/query",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)