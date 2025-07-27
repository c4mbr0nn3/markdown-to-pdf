# Markdown to PDF Converter API

A FastAPI-based web API that converts markdown documents with embedded images to professionally branded PDF files. The API accepts ZIP archives containing markdown files and associated images, processes them with company branding templates, and returns high-quality PDF documents with proper page break handling.

## Features

- **RESTful API**: Built with FastAPI for high performance and automatic documentation
- **ZIP File Processing**: Accepts ZIP archives containing markdown and image files
- **Professional PDF Generation**: Creates branded PDFs with company logos, headers, and footers
- **Image Support**: Embeds images from ZIP archives into generated PDFs
- **Page Break Control**: Intelligent page breaks with customizable CSS classes
- **Table of Contents**: Auto-generated TOC from markdown headers
- **Input Validation**: Comprehensive file type and size validation
- **Error Handling**: Detailed error responses with proper HTTP status codes
- **Logging**: Structured logging with Loguru
- **Docker Support**: Containerized deployment with Docker

## Technology Stack

- **Framework**: FastAPI 0.104+
- **Package Manager**: Poetry
- **Server**: Uvicorn (ASGI)
- **Python Version**: 3.11+
- **PDF Generation**: WeasyPrint
- **Markdown Processing**: Python-Markdown with extensions
- **Logging**: Loguru
- **Containerization**: Docker

## Quick Start

### Using Docker (Recommended)

1. Clone the repository:

```bash
git clone <repository-url>
cd markdown-pdf-api
```

2. Build and run the Docker container:

```bash
docker build -t markdown-pdf-api .
docker run -p 8000:8000 markdown-pdf-api
```

3. Access the API:

- API Documentation: <http://localhost:8000/docs>
- Health Check: <http://localhost:8000/health>
- API Info: <http://localhost:8000/api/v1/info>

### Local Development

1. Install Poetry:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. Set up the environment:

```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

3. Start the development server:

```bash
poetry run uvicorn app.main:app --reload
```

## API Endpoints

### Convert Markdown to PDF

```text
POST /api/v1/convert
```

**Parameters:**

- `file` (required): ZIP file containing markdown and images
- `title` (required): Document title for cover page
- `include_toc` (optional): Include table of contents (default: true)

**Response:** PDF file as binary stream

### Health Check

```text
GET /health
```

**Response:**

```json
{
    "status": "healthy",
    "timestamp": "2024-01-15T10:30:00Z",
    "version": "1.0.0"
}
```

### API Information

```text
GET /api/v1/info
```

**Response:**

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

### API Status

```text
GET /api/v1/status
```

**Response:**

```json
{
    "status": "operational",
    "uptime": "2h 30m 15s",
    "version": "1.0.0",
    "environment": "production"
}
```

## ZIP File Structure

Your ZIP file should contain markdown files and images:

```text
project_proposal.zip
├── main.md                 # Main markdown file (required)
├── images/                 # Images directory
│   ├── logo.png
│   ├── chart1.jpg
│   └── screenshot.png
```

## Supported File Types

- **Markdown**: `.md`, `.markdown`
- **Images**: `.png`, `.jpg`, `.jpeg`
- **Maximum file size**: 50MB
- **Maximum extracted size**: 200MB

## Markdown Features

### Standard Markdown

- Headers (H1-H6)
- Paragraphs and line breaks
- Bold and italic text
- Lists (ordered and unordered)
- Links
- Code blocks and inline code
- Tables
- Blockquotes

### Page Break Control

```markdown
<!-- Force page break -->
<div class="page-break"></div>

<!-- Keep content together -->
<div class="keep-together">
Content that should not be split across pages
</div>

<!-- Avoid page break before element -->
<div class="avoid-break-before">
Content
</div>
```

### Image References

```markdown
![Alt text](images/chart.png)
![Alt text](./images/chart.png)
<img src="images/chart.png" alt="Alt text">
```

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_ENV=development
DEBUG=true

# File Upload Limits
MAX_FILE_SIZE=52428800      # 50MB
MAX_EXTRACTED_SIZE=209715200 # 200MB
UPLOAD_TIMEOUT=300          # 5 minutes

# PDF Generation
COMPANY_NAME="Your Company Name"
DEFAULT_PAGE_FORMAT=A4

# Logging
LOG_LEVEL=INFO

# Security
ALLOWED_ORIGINS=["http://localhost:3000"]
```

## Company Branding

The API uses a hardcoded company template that includes:

- **Cover Page**: Company logo and branding
- **Headers/Footers**: Company name and page numbers
- **Color Scheme**: Professional brand colors
- **Typography**: Company fonts and styling

To customize the branding, modify:

- `app/templates/company_template.css`
- `app/templates/cover_page.html`
- `app/templates/assets/logo.svg`

## Development

### Code Quality

The project includes tools for maintaining code quality:

```bash
# Format code
poetry run black app/

# Sort imports
poetry run isort app/

# Lint code
poetry run flake8 app/

# Type checking
poetry run mypy app/
```

### Project Structure

```text
markdown-pdf-api/
├── app/                        # Main application package
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration management
│   ├── models/                 # Pydantic models
│   │   ├── requests.py         # Request models
│   │   └── responses.py        # Response models
│   ├── services/               # Business logic
│   │   ├── pdf_generator.py    # PDF generation service
│   │   └── zip_processor.py    # ZIP file processing
│   ├── utils/                  # Utility functions
│   │   ├── file_helpers.py     # File manipulation utilities
│   │   └── validators.py       # Input validation
│   └── templates/              # PDF templates
│       ├── company_template.css # Company template styles
│       ├── cover_page.html     # Cover page template
│       └── assets/             # Company assets
├── scripts/                    # Development scripts
├── logs/                       # Log files
├── pyproject.toml              # Poetry configuration
├── Dockerfile                  # Docker configuration
└── README.md                   # Project documentation
```

## Deployment

### Production Deployment

1. Update environment variables for production
2. Use the deployment script:

```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

### Docker Production Deployment

For production deployment with Docker:

```bash
# Build the image
docker build -t markdown-pdf-api .

# Run with production settings
docker run -d \
  --name markdown-pdf-api \
  --restart unless-stopped \
  -p 8000:8000 \
  -v $(pwd)/logs:/app/logs \
  -e API_ENV=production \
  -e DEBUG=false \
  -e LOG_LEVEL=INFO \
  markdown-pdf-api
```

## Error Handling

The API returns standardized error responses:

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

### Common Error Codes

- `INVALID_FILE_FORMAT`: File is not a ZIP archive
- `FILE_TOO_LARGE`: File exceeds size limit
- `NO_MARKDOWN_FOUND`: No markdown files in ZIP
- `INVALID_MARKDOWN`: Markdown parsing error
- `IMAGE_NOT_FOUND`: Referenced image missing
- `PDF_GENERATION_FAILED`: PDF creation error

## Performance

### Response Times

- Small files (<1MB): < 5 seconds
- Medium files (1-10MB): < 15 seconds
- Large files (10-50MB): < 60 seconds
- Health check: < 100ms

### Scalability

- Concurrent requests: 10+ simultaneous conversions
- Memory usage: < 1GB per conversion
- Horizontal scaling support
- Stateless design

## Security

- File type validation using magic bytes
- File size limits enforcement
- Input sanitization and validation
- CORS configuration
- Security headers
- Non-root container user

## Monitoring

The application provides structured logging and metrics:

- Request/response logging
- Performance metrics
- Error tracking
- Health monitoring

Log files are stored in the `logs/` directory:

- `app.log`: General application logs
- `errors.log`: Error-specific logs

## Support

For issues and questions:

1. Check the API documentation at `/docs`
2. Review the logs in the `logs/` directory
3. Verify your ZIP file structure and content
4. Ensure all required dependencies are installed

## License

This project is licensed under the MIT License.
