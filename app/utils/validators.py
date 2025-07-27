import re
from typing import Optional, List, Dict, Any
from fastapi import UploadFile, HTTPException
from loguru import logger

from app.config import settings
from app.utils.file_helpers import validate_file_size, validate_file_type


class ValidationError(Exception):
    """Custom exception for validation errors."""
    def __init__(self, message: str, error_code: str = "VALIDATION_ERROR", details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


async def validate_upload_file(file: UploadFile) -> bytes:
    """
    Validate uploaded file and return content.
    
    Args:
        file: FastAPI UploadFile object
        
    Returns:
        File content as bytes
        
    Raises:
        ValidationError: If validation fails
    """
    if not file:
        raise ValidationError("No file provided", "NO_FILE_PROVIDED")
    
    if not file.filename:
        raise ValidationError("Filename is required", "NO_FILENAME")
    
    # Read file content
    try:
        content = await file.read()
    except Exception as e:
        logger.error(f"Failed to read uploaded file: {str(e)}")
        raise ValidationError("Failed to read file", "FILE_READ_ERROR")
    
    # Validate file size
    if not validate_file_size(len(content)):
        raise ValidationError(
            f"File size {len(content)} exceeds maximum allowed size {settings.max_file_size}",
            "FILE_TOO_LARGE",
            {
                "file_size": len(content),
                "max_size": settings.max_file_size,
                "filename": file.filename
            }
        )
    
    # Validate file type
    if not validate_file_type(content, "application/zip"):
        raise ValidationError(
            "File must be a ZIP archive",
            "INVALID_FILE_FORMAT",
            {
                "filename": file.filename,
                "expected_type": "application/zip"
            }
        )
    
    logger.info(
        "File validation successful",
        extra={
            "filename": file.filename,
            "size": len(content),
            "content_type": file.content_type
        }
    )
    
    return content


def validate_title(title: str) -> str:
    """
    Validate and sanitize document title.
    
    Args:
        title: Document title
        
    Returns:
        Sanitized title
        
    Raises:
        ValidationError: If title is invalid
    """
    if not title or not title.strip():
        raise ValidationError("Title cannot be empty", "EMPTY_TITLE")
    
    # Remove potentially dangerous characters
    sanitized_title = re.sub(r'[<>:"/\\|?*]', '', title.strip())
    
    # Limit length
    if len(sanitized_title) > 200:
        sanitized_title = sanitized_title[:200].strip()
    
    if not sanitized_title:
        raise ValidationError("Title contains only invalid characters", "INVALID_TITLE")
    
    return sanitized_title


def validate_page_format(page_format: str) -> str:
    """
    Validate page format.
    
    Args:
        page_format: Page format string
        
    Returns:
        Validated page format
        
    Raises:
        ValidationError: If page format is invalid
    """
    supported_formats = ["A4", "Letter", "Legal", "A3", "A5"]
    
    if page_format not in supported_formats:
        raise ValidationError(
            f"Unsupported page format: {page_format}",
            "INVALID_PAGE_FORMAT",
            {
                "provided_format": page_format,
                "supported_formats": supported_formats
            }
        )
    
    return page_format


def validate_boolean_parameter(value: Any, param_name: str) -> bool:
    """
    Validate and convert boolean parameter.
    
    Args:
        value: Parameter value
        param_name: Parameter name for error messages
        
    Returns:
        Boolean value
        
    Raises:
        ValidationError: If value cannot be converted to boolean
    """
    if isinstance(value, bool):
        return value
    
    if isinstance(value, str):
        lower_value = value.lower()
        if lower_value in ("true", "1", "yes", "on"):
            return True
        elif lower_value in ("false", "0", "no", "off"):
            return False
    
    raise ValidationError(
        f"Invalid boolean value for {param_name}: {value}",
        "INVALID_BOOLEAN",
        {"parameter": param_name, "value": value}
    )


def validate_markdown_content(content: str) -> None:
    """
    Validate markdown content.
    
    Args:
        content: Markdown content
        
    Raises:
        ValidationError: If content is invalid
    """
    if not content or not content.strip():
        raise ValidationError("Markdown content cannot be empty", "EMPTY_CONTENT")
    
    # Check for reasonable content length
    if len(content) > 10 * 1024 * 1024:  # 10MB text limit
        raise ValidationError(
            "Markdown content too large",
            "CONTENT_TOO_LARGE",
            {"content_size": len(content)}
        )
    
    # Check for basic markdown structure
    if not re.search(r'[#\*\-\[\]`]', content):
        logger.warning("Content appears to be plain text without markdown formatting")


def validate_image_references(markdown_content: str, available_images: List[str]) -> List[str]:
    """
    Validate image references in markdown content.
    
    Args:
        markdown_content: Markdown content
        available_images: List of available image paths
        
    Returns:
        List of missing image references
        
    Raises:
        ValidationError: If critical images are missing
    """
    # Find all image references in markdown
    image_patterns = [
        r'!\[([^\]]*)\]\(([^)]+)\)',  # ![alt](path)
        r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>',  # <img src="path">
    ]
    
    referenced_images = set()
    for pattern in image_patterns:
        matches = re.findall(pattern, markdown_content, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                # Extract path from tuple (alt, path) or just path
                image_path = match[-1] if len(match) > 1 else match[0]
            else:
                image_path = match
            
            # Normalize path (remove ./ prefix)
            image_path = image_path.lstrip('./')
            referenced_images.add(image_path)
    
    # Check for missing images
    available_set = set(available_images)
    missing_images = referenced_images - available_set
    
    if missing_images:
        logger.warning(
            "Missing image references found",
            extra={
                "missing_images": list(missing_images),
                "available_images": available_images
            }
        )
    
    return list(missing_images)


def create_error_response(
    error: ValidationError,
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create standardized error response.
    
    Args:
        error: ValidationError instance
        request_id: Optional request ID
        
    Returns:
        Error response dictionary
    """
    return {
        "error": {
            "code": error.error_code,
            "message": error.message,
            "details": error.details,
            "timestamp": None,  # Will be set by response model
            "request_id": request_id
        }
    }


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe use.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove path separators and dangerous characters
    safe_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_."
    sanitized = "".join(c if c in safe_chars else "_" for c in filename)
    
    # Ensure it doesn't start with a dot or hyphen
    if sanitized.startswith(('.', '-')):
        sanitized = 'file_' + sanitized
    
    # Ensure it's not empty
    if not sanitized:
        sanitized = 'document.pdf'
    
    # Limit length
    if len(sanitized) > 100:
        name, ext = sanitized.rsplit('.', 1) if '.' in sanitized else (sanitized, '')
        sanitized = name[:100-len(ext)-1] + ('.' + ext if ext else '')
    
    return sanitized