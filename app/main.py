import time
import uuid
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger

from app.config import settings, setup_logging
from app.models.responses import HealthResponse, ApiInfoResponse, ApiStatusResponse, ErrorDetail
from app.services.zip_processor import ZipProcessor
from app.services.pdf_generator import PDFGenerator
from app.utils.validators import (
    validate_upload_file, 
    validate_title, 
    validate_boolean_parameter,
    ValidationError,
    create_error_response,
    sanitize_filename
)


# Application startup time for uptime calculation
startup_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    setup_logging(settings.log_level, settings.api_env)
    logger.info("Starting Markdown to PDF API", extra={"version": "1.0.0", "environment": settings.api_env})
    
    # Validate PDF generator requirements
    pdf_generator = PDFGenerator()
    if not pdf_generator.validate_requirements():
        logger.error("PDF generator validation failed - missing required template files")
        raise RuntimeError("PDF generator validation failed")
    
    logger.info("API startup completed successfully")
    
    yield
    
    # Shutdown
    logger.info("API shutdown completed")


# Create FastAPI app
app = FastAPI(
    title="Markdown to PDF Converter API",
    description="A FastAPI-based web API that converts markdown documents with embedded images to professionally branded PDF files",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Middleware for request/response logging."""
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    # Log request
    logger.info(
        "Request received",
        extra={
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "client_ip": request.client.host if request.client else None
        }
    )
    
    # Process request
    try:
        response = await call_next(request)
        
        # Log response
        process_time = time.time() - start_time
        logger.info(
            "Request completed",
            extra={
                "request_id": request_id,
                "status_code": response.status_code,
                "process_time": round(process_time, 3)
            }
        )
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        return response
        
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            "Request failed",
            extra={
                "request_id": request_id,
                "error": str(e),
                "process_time": round(process_time, 3)
            }
        )
        raise


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    """Handle validation errors."""
    request_id = request.headers.get("X-Request-ID")
    error_response = create_error_response(exc, request_id)
    
    logger.warning(
        "Validation error",
        extra={
            "request_id": request_id,
            "error_code": exc.error_code,
            "error_message": exc.message
        }
    )
    
    return HTTPException(status_code=400, detail=error_response)


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    request_id = request.headers.get("X-Request-ID")
    
    logger.error(
        "Unhandled exception",
        extra={
            "request_id": request_id,
            "error": str(exc),
            "error_type": type(exc).__name__
        }
    )
    
    error_response = {
        "error": {
            "code": "INTERNAL_SERVER_ERROR",
            "message": "An internal server error occurred",
            "details": {},
            "timestamp": None,
            "request_id": request_id
        }
    }
    
    raise HTTPException(status_code=500, detail=error_response)


@app.post("/api/v1/convert")
async def convert_markdown_to_pdf(
    file: UploadFile = File(..., description="ZIP file containing markdown and images"),
    title: str = Form(..., description="Document title for cover page"),
    include_toc: str = Form(default="true", description="Include table of contents")
):
    """
    Convert a ZIP file containing markdown and images to a branded PDF document.
    
    - **file**: ZIP file containing markdown files and images
    - **title**: Document title for the cover page (required)
    - **include_toc**: Include table of contents (default: true)
    
    Returns a PDF file as binary stream.
    """
    logger.info(
        "PDF conversion request received",
        extra={
            "filename": file.filename,
            "title": title,
            "include_toc": include_toc
        }
    )
    
    try:
        # Validate inputs
        file_content = await validate_upload_file(file)
        validated_title = validate_title(title)
        validated_include_toc = validate_boolean_parameter(include_toc, "include_toc")
        
        # Process ZIP file
        zip_processor = ZipProcessor()
        try:
            markdown_content, image_mapping = await zip_processor.process_zip(file_content)
            
            # Generate PDF
            pdf_generator = PDFGenerator()
            pdf_bytes = await pdf_generator.generate_pdf(
                markdown_content=markdown_content,
                image_mapping=image_mapping,
                title=validated_title,
                include_toc=validated_include_toc,
                page_format="A4"
            )
            
            # Create safe filename for download
            safe_filename = sanitize_filename(f"{validated_title}.pdf")
            
            logger.info(
                "PDF conversion completed successfully",
                extra={
                    "title": validated_title,
                    "pdf_size": len(pdf_bytes),
                    "output_filename": safe_filename
                }
            )
            
            # Return PDF as response
            return Response(
                content=pdf_bytes,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename=\"{safe_filename}\"",
                    "Content-Length": str(len(pdf_bytes))
                }
            )
            
        finally:
            zip_processor.cleanup()
            
    except ValidationError:
        raise  # Re-raise validation errors to be handled by exception handler
    except Exception as e:
        logger.error(f"PDF conversion failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "PDF_GENERATION_FAILED",
                    "message": "PDF generation failed",
                    "details": {"error": str(e)},
                    "timestamp": None,
                    "request_id": None
                }
            }
        )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    API health status check.
    
    Returns the current health status of the API.
    """
    return HealthResponse(status="healthy")


@app.get("/api/v1/info", response_model=ApiInfoResponse)
async def get_api_info():
    """
    Get API capabilities and configuration information.
    
    Returns information about supported formats, file size limits, and other capabilities.
    """
    return ApiInfoResponse(
        max_file_size=f"{settings.max_file_size // (1024*1024)}MB"
    )


@app.get("/api/v1/status", response_model=ApiStatusResponse)
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


@app.get("/")
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


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
        access_log=True
    )