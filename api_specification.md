# Markdown to PDF Web API - Technical Specification

## 1. Project Overview

### 1.1 Description
A FastAPI-based web API that converts markdown documents with embedded images to professionally branded PDF files. The API accepts ZIP archives containing markdown files and associated images, processes them with company branding templates, and returns high-quality PDF documents with proper page break handling.

### 1.2 Use Case
This API enables companies to convert project proposals, documentation, and reports written in markdown format into professional PDF documents suitable for client presentation. The solution supports a separate UI application that allows users to upload ZIP files and download the generated PDFs.

### 1.3 Key Requirements
- **Web API**: RESTful API built with FastAPI
- **Package Management**: Poetry for dependency management
- **Input**: ZIP files containing markdown and images
- **Output**: Professionally branded PDF files
- **Page Break Control**: Intelligent page break handling without text fragmentation
- **Company Branding**: Customizable templates with logos, headers, footers
- **Image Support**: Embedded images from ZIP archive
- **Production Ready**: Deployable, scalable, and maintainable

## 2. Technical Stack

### 2.1 Core Technologies
- **Framework**: FastAPI 0.104+
- **Package Manager**: Poetry
- **Server**: Uvicorn (ASGI)
- **Python Version**: 3.11+

### 2.2 Dependencies
```toml
[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.104.1"
uvicorn = {extras = ["standard"], version = "^0.24.0"}
python-multipart = "^0.0.6"
markdown-pdf = "^1.7"
Pillow = "^10.1.0"
python-magic = "^0.4.27"
pydantic = "^2.5.0"
python-dotenv = "^1.0.0"
loguru = "^0.7.2"

[tool.poetry.group.dev.dependencies]
black = "^23.11.0"
isort = "^5.12.0"
flake8 = "^6.1.0"
mypy = "^1.7.1"
```

## 3. Project Structure

```
markdown-pdf-api/
├── pyproject.toml              # Poetry configuration
├── README.md                   # Project documentation
├── .gitignore                  # Git ignore rules
├── .env.example                # Environment variables template
├── Dockerfile                  # Docker configuration
├── app/                        # Main application package
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration management
│   ├── models/                 # Pydantic models
│   │   ├── __init__.py
│   │   ├── requests.py         # Request models
│   │   └── responses.py        # Response models
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   ├── pdf_generator.py    # PDF generation service
│   │   └── zip_processor.py    # ZIP file processing
│   ├── utils/                  # Utility functions
│   │   ├── __init__.py
│   │   ├── file_helpers.py     # File manipulation utilities
│   │   └── validators.py       # Input validation
│   └── templates/              # PDF template (hardcoded)
│       ├── company_template.css # Single company template
│       └── assets/             # Company assets
│           └── logo.png        # Company logo
└── scripts/                   # Development scripts
    ├── setup.sh              # Environment setup
    └── deploy.sh             # Deployment script
```

## 4. API Endpoints Specification

### 4.1 Convert Markdown to PDF
**Endpoint**: `POST /api/v1/convert`

**Description**: Converts a ZIP file containing markdown and images to a branded PDF document.

**Request**:
- **Content-Type**: `multipart/form-data`
- **Parameters**:
  - `file` (required): ZIP file containing markdown and images
  - `title` (required): Document title for cover page (default: "Document")
  - `include_toc` (optional): Include table of contents (default: true)
  - `page_format` (optional): Page format ("A4") (default: "A4")

**Response**:
- **Success (200)**: PDF file as binary stream
- **Headers**:
  - `Content-Type: application/pdf`
  - `Content-Disposition: attachment; filename="document.pdf"`
- **Error Responses**:
  - `400`: Invalid file format or missing markdown
  - `413`: File too large
  - `422`: Validation error
  - `500`: Internal server error

### 4.2 Health Check
**Endpoint**: `GET /health`

**Description**: API health status check.

**Response**:
```json
{
    "status": "healthy",
    "timestamp": "2024-01-15T10:30:00Z",
    "version": "1.0.0"
}
```

### 4.3 API Information
**Endpoint**: `GET /api/v1/info`

**Description**: API capabilities and configuration information.

**Response**:
```json
{
    "name": "Markdown to PDF Converter API",
    "version": "1.0.0",
    "supported_formats": ["zip"],
    "max_file_size": "50MB",
    "supported_images": ["png", "jpg", "jpeg"],
    "page_formats": ["A4"]
}
```

### 4.4 API Status
**Endpoint**: `GET /api/v1/status`

**Description**: API status and configuration information.

**Response**:
```json
{
    "status": "operational",
    "uptime": "2h 30m 15s",
    "version": "1.0.0",
    "environment": "production"
}
```

## 5. Input Requirements

### 5.1 ZIP File Structure
```
project_proposal.zip
├── main.md                 # Main markdown file (required)
├── images/                     # Images directory
│   ├── logo.png
│   ├── chart1.jpg
│   └── screenshot.png
```

### 5.2 Supported File Types
- **Markdown**: `.md`
- **Images**: `.png`, `.jpg`, `.jpeg`
- **Maximum file size**: 50MB
- **Maximum extracted size**: 200MB

### 5.3 Markdown Requirements
- Standard CommonMark syntax
- GitHub Flavored Markdown extensions
- Image references using relative paths
- Support for HTML tags for advanced formatting
- Custom CSS classes for page breaks

## 6. PDF Generation Features

### 6.1 Company Branding
- **Cover Page**: Always included with company logo and branding
- **Headers/Footers**: always included with company name, page numbers
- **Color Scheme**: Hardcoded brand colors
- **Fonts**: Hardcoded company font

### 6.2 Page Break Control
- **Automatic**: Intelligent page breaks between sections
- **Manual**: Support for explicit page break markers
- **Avoid Breaks**: Keep tables, code blocks, and images together
- **CSS Control**: Custom CSS classes for precise control

**Page Break Syntax**:
```markdown
<!-- Page break using HTML comment -->
<div class="page-break"></div>

<!-- Keep together -->
<div class="keep-together">
Content that should not be split across pages
</div>
```

### 6.3 Advanced Features
- **Table of Contents**: Auto-generated from markdown headers
- **Bookmarks**: PDF navigation bookmarks
- **Hyperlinks**: Clickable internal and external links
- **Image Optimization**: Automatic compression. Image resize is a nice to have requirement if not too complex to implement e maintain
- **Code Highlighting**: Syntax highlighting for code blocks

## 7. Company Template

### 7.1 Template Structure
The application uses a single hardcoded company template that includes:
- **CSS Stylesheet**: Layout, fonts, colors, page formatting
- **Cover Page Template**: HTML template for cover page generation
- **Company Assets**: Logo and branding elements

### 7.2 Company Template CSS
```css
/* Company branding colors */
:root {
    --primary-color: #2c3e50;
    --secondary-color: #3498db;
    --accent-color: #e74c3c;
    --text-color: #333333;
    --background-color: #ffffff;
}

/* Page setup */
@page {
    size: A4;
    margin: 2cm;
    @top-center {
        content: "Company Name - " attr(data-title);
    }
    @bottom-center {
        content: "Page " counter(page) " of " counter(pages);
    }
}

/* Page break control */
h1 { page-break-before: always; }
h1:first-child { page-break-before: avoid; }
h2, h3 { page-break-after: avoid; }
table, img, pre { page-break-inside: avoid; }
```

### 7.3 Cover Page Template
```html
<div class="cover-page">
    <div class="company-logo">
        <img src="{{logo_url}}" alt="Company Logo">
    </div>
    <h1 class="document-title">{{title}}</h1>
</div>
```

## 8. Configuration Management

### 8.1 Environment Variables
```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_ENV=development
DEBUG=true

# File Upload Limits
MAX_FILE_SIZE=52428800  # 50MB
MAX_EXTRACTED_SIZE=209715200  # 200MB
UPLOAD_TIMEOUT=300  # 5 minutes

# PDF Generation
DEFAULT_TEMPLATE=default
DEFAULT_PAGE_FORMAT=A4
COMPANY_NAME="Your Company Name"
COMPANY_LOGO_URL="/templates/assets/logo.png"

# Logging
LOG_LEVEL=INFO

# Security
ALLOWED_ORIGINS=["http://localhost:3000", "https://yourdomain.com"]
```

### 8.2 Application Configuration
```python
# app/config.py
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_env: str = "development"
    debug: bool = False
    
    # File Upload Settings
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    max_extracted_size: int = 200 * 1024 * 1024  # 200MB
    upload_timeout: int = 300
    
    # PDF Generation Settings
    default_page_format: str = "A4"
    company_name: str = "Your Company Name"
    
    # Security Settings
    allowed_origins: List[str] = ["*"]
    
    class Config:
        env_file = ".env"
```

## 9. Error Handling

### 9.1 Error Response Format
```json
{
    "error": {
        "code": "INVALID_FILE_FORMAT",
        "message": "The uploaded file must be a ZIP archive",
        "details": {
            "received_type": "text/plain",
            "expected_types": ["application/zip"]
        },
        "timestamp": "2024-01-15T10:30:00Z",
        "request_id": "req_123456789"
    }
}
```

### 9.2 Error Codes
- `INVALID_FILE_FORMAT`: File is not a ZIP archive
- `FILE_TOO_LARGE`: File exceeds size limit
- `NO_MARKDOWN_FOUND`: No markdown files in ZIP
- `INVALID_MARKDOWN`: Markdown parsing error
- `IMAGE_NOT_FOUND`: Referenced image missing
- `TEMPLATE_ERROR`: PDF template processing error
- `PDF_GENERATION_FAILED`: PDF creation error
- `INTERNAL_SERVER_ERROR`: Unexpected server error

## 9. Testing Requirements

*Note: Testing implementation is not required at this time and will be added in future iterations.*

## 10. Performance Requirements

### 11.1 Response Times
- Small files (<1MB): < 5 seconds
- Medium files (1-10MB): < 15 seconds
- Large files (10-50MB): < 60 seconds
- Health check: < 100ms

### 11.2 Throughput
- Concurrent requests: 10+ simultaneous conversions
- Memory usage: < 1GB per conversion
- Disk usage: Temporary files cleaned automatically
- CPU usage: Optimized for multi-core processing

### 11.3 Scalability
- Horizontal scaling support
- Stateless design
- Docker containerization
- Load balancer compatibility

## 11. Security Requirements

### 11.1 Input Validation
- File type verification (magic bytes)
- File size limits enforcement

### 11.2 Security Headers
- CORS configuration
- Content Security Policy
- X-Frame-Options
- X-Content-Type-Options
- Security response headers

## 12. Deployment Specifications

### 12.1 Docker Configuration
```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Set work directory
WORKDIR /app

# Copy Poetry files
COPY pyproject.toml poetry.lock ./

# Configure Poetry and install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --only=main

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 12.2 Production Requirements
- **Process Manager**: docker ce in debian server
- **Health**: Health checks
- **Logging**: Structured logging with Loguru
- **Configuration**: Environment-based configuration management

## 13. Documentation Requirements

### 13.1 API Documentation
- OpenAPI/Swagger specification
- Interactive API documentation (FastAPI automatic docs)

### 13.2 Development Documentation
- Setup and installation guide
- Architecture documentation
- Code style guide
- Troubleshooting guide

### 13.3 User Documentation
- API usage examples
- Supported markdown syntax
- Best practices for ZIP file structure

## 14. Logging with Loguru

### 14.1 Logging Configuration
```python
# app/config.py
from loguru import logger
import sys

def setup_logging(log_level: str = "INFO", environment: str = "development"):
    """Configure Loguru logging."""
    
    # Remove default handler
    logger.remove()
    
    # Console logging for development
    if environment == "development":
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level=log_level,
            colorize=True
        )
    
    # File logging for production with JSON format
    logger.add(
        "logs/app.log",
        format="{time} | {level} | {name}:{function}:{line} | {message}",
        level=log_level,
        rotation="10 MB",
        retention="30 days",
        compression="gz",
        serialize=True  # JSON format
    )
    
    # Error-specific logging
    logger.add(
        "logs/errors.log",
        format="{time} | {level} | {name}:{function}:{line} | {message}",
        level="ERROR",
        rotation="10 MB",
        retention="90 days",
        compression="gz",
        serialize=True
    )
```

### 14.2 Logging Usage Examples
```python
from loguru import logger

# Request logging
logger.info("Processing PDF conversion request", 
           extra={"request_id": "req_123", "file_size": 1024})

# Error logging with context
logger.error("PDF generation failed", 
            extra={"error": str(e), "request_id": "req_123", "file_name": "document.md"})

# Performance logging
logger.info("PDF conversion completed", 
           extra={"request_id": "req_123", "processing_time": 5.2, "output_size": 2048})
```

### 14.3 Log Structure
```json
{
    "text": "Processing PDF conversion request",
    "record": {
        "elapsed": {"repr": "0:00:00.123456", "total_seconds": 0.123456},
        "exception": null,
        "extra": {
            "request_id": "req_123",
            "file_size": 1024
        },
        "file": {"name": "main.py", "path": "/app/main.py"},
        "function": "convert_markdown_to_pdf",
        "level": {"icon": "ℹ️", "name": "INFO", "no": 20},
        "line": 45,
        "message": "Processing PDF conversion request",
        "module": "main",
        "name": "app.main",
        "process": {"id": 1234, "name": "MainProcess"},
        "thread": {"id": 140285, "name": "MainThread"},
        "time": {"repr": "2024-01-15 10:30:00.123456+00:00", "timestamp": 1705314600.123456}
    }
}
```

## 15. Implementation Notes

### 15.1 Development Workflow
1. Set up Poetry environment
2. Implement core services (ZIP processing, PDF generation)
3. Create FastAPI application with endpoints
4. Implement the hardcoded company template
5. Add error handling and validation
6. Configure Loguru logging
7. Configure deployment

### 15.2 Quality Assurance
- Code formatting with Black
- Import sorting with isort
- Linting with flake8
- Type checking with mypy
- Security scanning with bandit

### 15.3 Maintenance Considerations
- Regular dependency updates
- Configuration management
- Performance optimization
- Security patch management

This specification provides a complete blueprint for implementing a production-ready markdown-to-PDF conversion API using FastAPI and Poetry, with a single hardcoded company template, proper logging with Loguru, and simplified architecture suitable for existing company infrastructure.
