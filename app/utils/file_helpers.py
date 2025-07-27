import os
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Union
import magic
from loguru import logger

from app.config import settings


def validate_file_size(file_size: int) -> bool:
    """
    Validate if file size is within allowed limits.
    
    Args:
        file_size: Size of the file in bytes
        
    Returns:
        True if file size is valid, False otherwise
    """
    return file_size <= settings.max_file_size


def validate_file_type(file_content: bytes, expected_mime_type: str = "application/zip") -> bool:
    """
    Validate file type using magic bytes.
    
    Args:
        file_content: Raw file content
        expected_mime_type: Expected MIME type
        
    Returns:
        True if file type matches expected type, False otherwise
    """
    try:
        detected_mime_type = magic.from_buffer(file_content, mime=True)
        return detected_mime_type == expected_mime_type
    except Exception as e:
        logger.warning(f"Failed to detect file type: {str(e)}")
        return False


def create_temp_directory() -> str:
    """
    Create a temporary directory for processing files.
    
    Returns:
        Path to the temporary directory
    """
    temp_dir = tempfile.mkdtemp()
    logger.debug(f"Created temporary directory: {temp_dir}")
    return temp_dir


def cleanup_temp_directory(temp_dir: str) -> None:
    """
    Clean up a temporary directory and all its contents.
    
    Args:
        temp_dir: Path to the temporary directory to clean up
    """
    if temp_dir and os.path.exists(temp_dir):
        try:
            shutil.rmtree(temp_dir)
            logger.debug(f"Cleaned up temporary directory: {temp_dir}")
        except Exception as e:
            logger.warning(f"Failed to clean up temporary directory {temp_dir}: {str(e)}")


def safe_filename(filename: str) -> str:
    """
    Create a safe filename by removing/replacing dangerous characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Safe filename
    """
    # Remove path separators and other dangerous characters
    safe_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_."
    safe_name = "".join(c if c in safe_chars else "_" for c in filename)
    
    # Ensure filename is not empty and doesn't start with a dot
    if not safe_name or safe_name.startswith("."):
        safe_name = "document" + safe_name
    
    # Limit length
    if len(safe_name) > 255:
        name, ext = os.path.splitext(safe_name)
        safe_name = name[:255-len(ext)] + ext
    
    return safe_name


def get_file_extension(filename: str) -> str:
    """
    Get file extension from filename.
    
    Args:
        filename: The filename
        
    Returns:
        File extension (lowercase, including the dot)
    """
    return Path(filename).suffix.lower()


def ensure_directory_exists(directory_path: Union[str, Path]) -> None:
    """
    Ensure that a directory exists, creating it if necessary.
    
    Args:
        directory_path: Path to the directory
    """
    path = Path(directory_path)
    path.mkdir(parents=True, exist_ok=True)


def get_file_size_human(size_bytes: int) -> str:
    """
    Convert file size in bytes to human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Human-readable size string
    """
    if size_bytes == 0:
        return "0 B"
    
    units = ["B", "KB", "MB", "GB", "TB"]
    unit_index = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and unit_index < len(units) - 1:
        size /= 1024.0
        unit_index += 1
    
    return f"{size:.1f} {units[unit_index]}"


def write_temp_file(content: bytes, suffix: str = None) -> str:
    """
    Write content to a temporary file.
    
    Args:
        content: File content as bytes
        suffix: Optional file suffix
        
    Returns:
        Path to the temporary file
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_file.write(content)
        temp_file_path = temp_file.name
    
    logger.debug(f"Created temporary file: {temp_file_path}")
    return temp_file_path


def read_file_safely(file_path: Union[str, Path], encoding: str = "utf-8") -> Optional[str]:
    """
    Safely read a text file with error handling.
    
    Args:
        file_path: Path to the file
        encoding: Text encoding
        
    Returns:
        File content as string, or None if failed
    """
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()
    except UnicodeDecodeError:
        # Try with different encoding
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()
                logger.warning(f"Used latin-1 encoding for file: {file_path}")
                return content
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {str(e)}")
            return None
    except Exception as e:
        logger.error(f"Failed to read file {file_path}: {str(e)}")
        return None


def copy_file_safely(src: Union[str, Path], dst: Union[str, Path]) -> bool:
    """
    Safely copy a file with error handling.
    
    Args:
        src: Source file path
        dst: Destination file path
        
    Returns:
        True if successful, False otherwise
    """
    try:
        shutil.copy2(src, dst)
        logger.debug(f"Copied file from {src} to {dst}")
        return True
    except Exception as e:
        logger.error(f"Failed to copy file from {src} to {dst}: {str(e)}")
        return False