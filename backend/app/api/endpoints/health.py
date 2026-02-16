"""
Health check endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime

from app.core.database import get_db
from app.core.query_executor import query_executor

router = APIRouter()


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Health check endpoint
    """
    try:
        # Test database connection
        await db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    return {
        "status": "healthy" if db_status == "healthy" else "unhealthy",
        "timestamp": datetime.now().isoformat(),
        "database": db_status,
        "queries_loaded": len(query_executor.list_queries())
    }


@router.get("/health/ready")
async def readiness_check():
    """
    Readiness check for Kubernetes/orchestration
    """
    return {"ready": True}


@router.get("/health/live")
async def liveness_check():
    """
    Liveness check for Kubernetes/orchestration
    """
    return {"alive": True}
