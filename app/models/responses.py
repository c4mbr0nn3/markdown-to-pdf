from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime


class ErrorDetail(BaseModel):
    """Error detail model."""
    code: str = Field(description="Error code")
    message: str = Field(description="Error message")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    request_id: Optional[str] = Field(default=None, description="Request ID for tracking")


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = Field(description="Health status")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    version: str = Field(default="1.0.0", description="API version")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2024-01-15T10:30:00Z",
                "version": "1.0.0"
            }
        }


class ApiInfoResponse(BaseModel):
    """API information response model."""
    name: str = Field(default="Markdown to PDF Converter API", description="API name")
    version: str = Field(default="1.0.0", description="API version")
    supported_formats: List[str] = Field(default=["zip"], description="Supported file formats")
    max_file_size: str = Field(default="50MB", description="Maximum file size")
    supported_images: List[str] = Field(default=["png", "jpg", "jpeg"], description="Supported image formats")
    page_formats: List[str] = Field(default=["A4"], description="Supported page formats")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Markdown to PDF Converter API",
                "version": "1.0.0",
                "supported_formats": ["zip"],
                "max_file_size": "50MB",
                "supported_images": ["png", "jpg", "jpeg"],
                "page_formats": ["A4"]
            }
        }


class ApiStatusResponse(BaseModel):
    """API status response model."""
    status: str = Field(description="Operational status")
    uptime: str = Field(description="System uptime")
    version: str = Field(default="1.0.0", description="API version")
    environment: str = Field(description="Environment")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "operational",
                "uptime": "2h 30m 15s",
                "version": "1.0.0",
                "environment": "production"
            }
        }