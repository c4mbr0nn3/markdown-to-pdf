from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger

from app.config import settings, setup_logging
from app.services.pdf_generator import PDFGenerator
from app.routes import convert, health


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

# Include routers
app.include_router(convert.router)
app.include_router(health.router)


# @app.middleware("http")
# async def logging_middleware(request: Request, call_next):
#     """Middleware for request/response logging."""
#     request_id = str(uuid.uuid4())
#     start_time = time.time()

#     # Log request
#     logger.info(
#         "Request received",
#         extra={
#             "request_id": request_id,
#             "method": request.method,
#             "url": str(request.url),
#             "client_ip": request.client.host if request.client else None
#         }
#     )

#     # Process request
#     try:
#         response = await call_next(request)

#         # Log response
#         process_time = time.time() - start_time
#         logger.info(
#             "Request completed",
#             extra={
#                 "request_id": request_id,
#                 "status_code": response.status_code,
#                 "process_time": round(process_time, 3)
#             }
#         )

#         # Add request ID to response headers
#         response.headers["X-Request-ID"] = request_id
#         return response

#     except Exception as e:
#         process_time = time.time() - start_time
#         logger.error(
#             "Request failed",
#             extra={
#                 "request_id": request_id,
#                 "error": str(e),
#                 "process_time": round(process_time, 3)
#             }
#         )
#         raise


# @app.exception_handler(ValidationError)
# async def validation_exception_handler(request: Request, exc: ValidationError):
#     """Handle validation errors."""
#     request_id = request.headers.get("X-Request-ID")
#     error_response = create_error_response(exc, request_id)

#     logger.warning(
#         "Validation error",
#         extra={
#             "request_id": request_id,
#             "error_code": exc.error_code,
#             "error_message": exc.message
#         }
#     )

#     return HTTPException(status_code=400, detail=error_response)


# @app.exception_handler(Exception)
# async def general_exception_handler(request: Request, exc: Exception):
#     """Handle general exceptions."""
#     request_id = request.headers.get("X-Request-ID")

#     logger.error(
#         "Unhandled exception",
#         extra={
#             "request_id": request_id,
#             "error": str(exc),
#             "error_type": type(exc).__name__
#         }
#     )

#     error_response = {
#         "error": {
#             "code": "INTERNAL_SERVER_ERROR",
#             "message": "An internal server error occurred",
#             "details": {},
#             "timestamp": None,
#             "request_id": request_id
#         }
#     }

#     raise HTTPException(status_code=500, detail=error_response)




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