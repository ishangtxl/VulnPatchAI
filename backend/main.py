"""
VulnPatch AI - Main FastAPI Application
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from app.core.config import settings
from app.api.v1.api import api_router
from app.core.database import engine, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("Starting VulnPatch AI...")
    
    # Initialize AI learning service with feedback integration
    try:
        from app.services.ai_learning_service import ai_learning_service
        from app.core.database import SessionLocal
        
        # Initialize with a database session
        db = SessionLocal()
        try:
            ai_learning_service.initialize_with_db(db)
            # Load initial learning improvements
            await ai_learning_service.load_learning_improvements()
            print("✓ AI Learning Service initialized with feedback integration")
        except Exception as e:
            print(f"⚠ AI Learning Service initialization failed: {e}")
        finally:
            db.close()
            
    except Exception as e:
        print(f"⚠ AI Learning Service setup error: {e}")
    
    yield
    
    # Shutdown
    print("Shutting down VulnPatch AI...")
    
    # Cleanup AI services
    try:
        from app.services.gemini_llm_service import gemini_llm_service
        await gemini_llm_service.close()
        print("✓ AI Services cleaned up")
    except Exception as e:
        print(f"⚠ AI Services cleanup error: {e}")


app = FastAPI(
    title="VulnPatch AI",
    description="Intelligent Vulnerability Patch Management System",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "VulnPatch AI - Intelligent Vulnerability Patch Management System",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )