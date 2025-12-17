# FastAPI main application entry point

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Import database and services
from .database import init_db, check_db_health
from .vector_db import vector_db
from .ai_client import ai_client

# Import routers
from .routers import auth, rag, translation, personalization, content

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    print("Starting AI-Native Textbook API...")
    
    try:
        # Initialize database
        print("Initializing database...")
        init_db()
        
        # Initialize vector database
        print("Initializing vector database...")
        await vector_db.initialize_collection()
        
        # Check service health
        print("Checking service health...")
        db_healthy = check_db_health()
        vector_db_healthy = await vector_db.health_check()
        ai_healthy = await ai_client.health_check()
        
        print(f"Database: {'✓' if db_healthy else '✗'}")
        print(f"Vector DB: {'✓' if vector_db_healthy else '✗'}")
        print(f"AI Services: {ai_healthy}")
        
        print("API startup complete!")
        
    except Exception as e:
        print(f"Startup error: {e}")
        raise
    
    yield
    
    # Shutdown
    print("Shutting down AI-Native Textbook API...")
    print("API shutdown complete!")

# Create FastAPI application
app = FastAPI(
    title="AI-Native Textbook API",
    description="Backend API for Physical AI & Humanoid Robotics textbook with RAG, translation, and personalization",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
origins = [
    "http://localhost:3000",  # Docusaurus dev server
    "http://127.0.0.1:3000",
    "https://localhost:3000",
]

# Add environment-specific origins
if os.getenv("CORS_ORIGINS"):
    origins.extend(os.getenv("CORS_ORIGINS").split(","))

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Add trusted host middleware for security
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.vercel.app", "*.github.io"]
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint."""
    db_healthy = check_db_health()
    vector_db_healthy = await vector_db.health_check()
    ai_healthy = await ai_client.health_check()
    
    overall_healthy = db_healthy and vector_db_healthy and any(ai_healthy.values())
    
    return {
        "status": "healthy" if overall_healthy else "unhealthy",
        "service": "ai-native-textbook-api",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "services": {
            "database": "healthy" if db_healthy else "unhealthy",
            "vector_db": "healthy" if vector_db_healthy else "unhealthy",
            "ai_services": ai_healthy
        }
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "AI-Native Textbook API",
        "description": "Backend for Physical AI & Humanoid Robotics textbook",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

# API version prefix
API_V1_PREFIX = "/api/v1"

# Service status endpoints
@app.get(f"{API_V1_PREFIX}/status/database")
async def database_status():
    """Database status endpoint."""
    healthy = check_db_health()
    return {
        "service": "database",
        "status": "healthy" if healthy else "unhealthy",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

@app.get(f"{API_V1_PREFIX}/status/vector-db")
async def vector_db_status():
    """Vector database status endpoint."""
    healthy = await vector_db.health_check()
    info = await vector_db.get_collection_info()
    
    return {
        "service": "vector_database",
        "status": "healthy" if healthy else "unhealthy",
        "collection_info": info,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

@app.get(f"{API_V1_PREFIX}/status/ai-services")
async def ai_services_status():
    """AI services status endpoint."""
    health_status = await ai_client.health_check()
    
    return {
        "service": "ai_services",
        "status": health_status,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

# Include routers
app.include_router(auth.router, prefix=f"{API_V1_PREFIX}/auth", tags=["authentication"])
app.include_router(rag.router, prefix=f"{API_V1_PREFIX}/rag", tags=["rag-chatbot"])
app.include_router(translation.router, prefix=f"{API_V1_PREFIX}/translation", tags=["translation"])
app.include_router(personalization.router, prefix=f"{API_V1_PREFIX}/personalization", tags=["personalization"])
app.include_router(content.router, prefix=f"{API_V1_PREFIX}/content", tags=["content"])

# Global exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Global HTTP exception handler."""
    return {
        "error": True,
        "message": exc.detail,
        "status_code": exc.status_code,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

# Global exception handler for all exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unexpected errors."""
    print(f"Unexpected error: {exc}")
    return {
        "error": True,
        "message": "Internal server error",
        "status_code": 500,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

# Development server runner
if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True if os.getenv("DEBUG") == "true" else False,
        log_level="info"
    )