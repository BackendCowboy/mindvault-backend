# app/routes/health_routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, text
from datetime import datetime
import psutil
import os
from app.database import get_session, check_db_connection
from app.config import DATABASE_URL

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "MindVault API",
        "version": "1.0.0",
    }


@router.get("/health/detailed")
async def detailed_health_check(session: Session = Depends(get_session)):
    """Detailed health check with database and system info"""

    # Check database connection
    try:
        # Test database connection
        result = session.exec(text("SELECT 1")).first()
        db_status = "healthy" if result else "unhealthy"
        db_error = None
    except Exception as e:
        db_status = "unhealthy"
        db_error = str(e)

    # System metrics
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    health_data = {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "MindVault API",
        "version": "1.0.0",
        "checks": {
            "database": {
                "status": db_status,
                "error": db_error,
                "type": "postgresql" if "postgresql" in DATABASE_URL else "sqlite",
            },
            "memory": {
                "status": "healthy" if memory.percent < 85 else "warning",
                "usage_percent": memory.percent,
                "available_mb": round(memory.available / 1024 / 1024, 2),
            },
            "disk": {
                "status": "healthy" if disk.percent < 85 else "warning",
                "usage_percent": disk.percent,
                "free_gb": round(disk.free / 1024 / 1024 / 1024, 2),
            },
        },
        "environment": {
            "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
            "platform": os.name,
            "pid": os.getpid(),
        },
    }

    # Return 503 if any critical checks fail
    if db_status == "unhealthy":
        raise HTTPException(status_code=503, detail=health_data)

    return health_data


@router.get("/health/ready")
async def readiness_check(session: Session = Depends(get_session)):
    """Kubernetes readiness probe - checks if app is ready to serve traffic"""
    try:
        # Test database connection
        session.exec(text("SELECT 1"))
        return {"status": "ready", "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        raise HTTPException(
            status_code=503, detail={"status": "not ready", "error": str(e)}
        )


@router.get("/health/live")
async def liveness_check():
    """Kubernetes liveness probe - checks if app is alive"""
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": psutil.Process().create_time(),
    }
