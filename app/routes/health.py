import time
from fastapi import APIRouter

from app.config import settings
from app.models.responses import HealthResponse, ApiInfoResponse, ApiStatusResponse

router = APIRouter(tags=["health"])

# Application startup time for uptime calculation
startup_time = time.time()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    API health status check.

    Returns the current health status of the API.
    """
    return HealthResponse(status="healthy")


@router.get("/api/v1/info", response_model=ApiInfoResponse)
async def get_api_info():
    """
    Get API capabilities and configuration information.

    Returns information about supported formats, file size limits, and other capabilities.
    """
    return ApiInfoResponse(
        max_file_size=f"{settings.max_file_size // (1024*1024)}MB"
    )


@router.get("/api/v1/status", response_model=ApiStatusResponse)
async def get_api_status():
    """
    Get API status and runtime information.

    Returns operational status, uptime, and environment information.
    """
    uptime_seconds = int(time.time() - startup_time)
    hours = uptime_seconds // 3600
    minutes = (uptime_seconds % 3600) // 60
    seconds = uptime_seconds % 60

    uptime_str = f"{hours}h {minutes}m {seconds}s"

    return ApiStatusResponse(
        status="operational",
        uptime=uptime_str,
        environment=settings.api_env
    )


@router.get("/")
async def root():
    """
    Root endpoint with basic API information.
    """
    return {
        "name": "Markdown to PDF Converter API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
        "health": "/health"
    }