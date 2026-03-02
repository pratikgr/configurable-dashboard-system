"""
FastAPI main application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine, Base
from app.api.endpoints import query, dashboards, health, ai, admin  # ← ai added


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 Starting dashboard application...")
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database initialized")
    
    # Check AI configuration
    if settings.AZURE_OPENAI_ENDPOINT and settings.AZURE_OPENAI_DEPLOYMENT:
        auth_method = "API Key" if settings.AZURE_OPENAI_API_KEY else "Managed Identity"
        print(f"✅ AI service configured ({auth_method})")
        print(f"   Endpoint: {settings.AZURE_OPENAI_ENDPOINT}")
        print(f"   Deployment: {settings.AZURE_OPENAI_DEPLOYMENT}")
    else:
        print("⚠️  AI service not configured - set AZURE_OPENAI_* environment variables")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down dashboard application...")
    await engine.dispose()


# Create FastAPI app
app = FastAPI(
    title="Configurable Dashboard API",
    description="Universal dashboard system with AI-powered natural language interface",
    version="2.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(query.router, prefix="/api", tags=["queries"])
app.include_router(dashboards.router, prefix="/api", tags=["dashboards"])
app.include_router(ai.router, prefix="/api", tags=["ai"])  # ← NEW: AI router
app.include_router(admin.router, prefix="/api", tags=["admin"])  # ← NEW: Admin router

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Configurable Dashboard API",
        "version": "2.0.0",
        "features": [
            "Configuration-driven dashboards",
            "5 widget types (line, bar, pie, table, metric)",
            "AI-powered natural language interface",
            "Dual-mode: Dashboard builder + Data analyst"
        ],
        "docs": "/docs",
        "ai_status": "/api/ai/status"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
