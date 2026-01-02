"""
FastAPI application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from core.config import settings
from core.database import init_db, close_db
from api.v1.auth import router as auth_router
from api.v1.campaigns import router as campaigns_router
from api.v1.ai_generation import router as ai_generation_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan events for startup and shutdown
    """
    # Startup
    print("Starting up...")
    # Optionally initialize database here
    # await init_db()
    
    yield
    
    # Shutdown
    print("Shutting down...")
    await close_db()


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered B2B email marketing platform",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(campaigns_router, prefix="/api/v1")
app.include_router(ai_generation_router, prefix="/api/v1")

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "anthropic_configured": bool(settings.ANTHROPIC_API_KEY)
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Email Campaign Manager API",
        "docs": "/docs",
        "health": "/health",
        "features": [
            "AI-powered email generation",
            "Campaign management",
            "Multi-tenant architecture",
            "Role-based access control"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )