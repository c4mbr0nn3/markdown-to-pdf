import zipfile
import tempfile
import os
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from loguru import logger
import magic

from app.config import settings


class ZipProcessor:
    """Service for processing ZIP files containing markdown and images."""
    
    SUPPORTED_IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg'}
    MARKDOWN_EXTENSIONS = {'.md', '.markdown'}
    
    def __init__(self) -> None:
        self.temp_dir: Optional[str] = None
        self.markdown_files: List[Path] = []
        self.image_files: Dict[str, Path] = {}
        self.main_markdown: Optional[Path] = None
    
    async def process_zip(self, zip_content: bytes) -> Tuple[str, Dict[str, str]]:
        """
        Process ZIP file and extract markdown and images.
        
        Args:
            zip_content: Raw ZIP file content
            
        Returns:
            Tuple of (main_markdown_content, image_mapping)
            
        Raises:
            ValueError: If ZIP is invalid or no markdown found
        """
        logger.info("Starting ZIP file processing", extra={"zip_size": len(zip_content)})
        
        try:
            # Create temporary directory
            self.temp_dir = tempfile.mkdtemp()
            logger.debug("Created temporary directory", extra={"temp_dir": self.temp_dir})
            
            # Extract ZIP file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_zip:
                temp_zip.write(zip_content)
                temp_zip_path = temp_zip.name
            
            # Validate and extract ZIP
            await self._extract_zip(temp_zip_path)
            
            # Find and validate files
            await self._find_files()
            
            # Read main markdown content
            markdown_content = await self._read_main_markdown()
            
            # Create image mapping
            image_mapping = await self._create_image_mapping()
            
            logger.info(
                "ZIP processing completed successfully",
                extra={
                    "markdown_files_count": len(self.markdown_files),
                    "image_files_count": len(self.image_files),
                    "main_markdown_size": len(markdown_content)
                }
            )
            
            return markdown_content, image_mapping
            
        except Exception as e:
            logger.error("ZIP processing failed", extra={"error": str(e)})
            raise
        finally:
            # Clean up temporary ZIP file
            if 'temp_zip_path' in locals():
                try:
                    os.unlink(temp_zip_path)
                except OSError:
                    pass
    
    async def _extract_zip(self, zip_path: str) -> None:
        """Extract ZIP file to temporary directory."""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Check for zip bomb protection
                total_size = sum(info.file_size for info in zip_ref.infolist())
                if total_size > settings.max_extracted_size:
                    raise ValueError(f"Extracted size {total_size} exceeds limit {settings.max_extracted_size}")
                
                # Extract all files
                zip_ref.extractall(self.temp_dir)
                logger.debug("ZIP file extracted successfully", extra={"extracted_size": total_size})
                
        except zipfile.BadZipFile:
            raise ValueError("Invalid ZIP file format")
        except Exception as e:
            raise ValueError(f"Failed to extract ZIP file: {str(e)}")
    
    async def _find_files(self) -> None:
        """Find markdown and image files in extracted directory."""
        if not self.temp_dir:
            raise ValueError("No temporary directory available")
        
        temp_path = Path(self.temp_dir)
        
        # Find all files recursively
        for file_path in temp_path.rglob('*'):
            if file_path.is_file():
                file_ext = file_path.suffix.lower()
                
                if file_ext in self.MARKDOWN_EXTENSIONS:
                    self.markdown_files.append(file_path)
                    # Prioritize main.md or README.md
                    if file_path.name.lower() in ['main.md', 'readme.md']:
                        self.main_markdown = file_path
                elif file_ext in self.SUPPORTED_IMAGE_EXTENSIONS:
                    # Use relative path as key for image mapping
                    relative_path = file_path.relative_to(temp_path)
                    self.image_files[str(relative_path)] = file_path
        
        # Validate we found at least one markdown file
        if not self.markdown_files:
            raise ValueError("No markdown files found in ZIP archive")
        
        # Set main markdown if not already set
        if not self.main_markdown:
            self.main_markdown = self.markdown_files[0]
        
        logger.debug(
            "Files discovered",
            extra={
                "markdown_files": [str(f) for f in self.markdown_files],
                "image_files": list(self.image_files.keys()),
                "main_markdown": str(self.main_markdown)
            }
        )
    
    async def _read_main_markdown(self) -> str:
        """Read the main markdown file content."""
        if not self.main_markdown:
            raise ValueError("No main markdown file identified")
        
        try:
            with open(self.main_markdown, 'r', encoding='utf-8') as f:
                content = f.read()
            
            logger.debug("Main markdown content read", extra={"content_length": len(content)})
            return content
            
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(self.main_markdown, 'r', encoding='latin-1') as f:
                    content = f.read()
                logger.warning("Used latin-1 encoding for markdown file")
                return content
            except Exception as e:
                raise ValueError(f"Failed to read markdown file: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to read markdown file: {str(e)}")
    
    async def _create_image_mapping(self) -> Dict[str, str]:
        """Create mapping of image paths to base64 encoded data."""
        image_mapping = {}
        
        for relative_path, file_path in self.image_files.items():
            try:
                # Validate image file
                mime_type = magic.from_file(str(file_path), mime=True)
                if not mime_type.startswith('image/'):
                    logger.warning(
                        "Skipping non-image file",
                        extra={"file": relative_path, "mime_type": mime_type}
                    )
                    continue
                
                # Read image file
                with open(file_path, 'rb') as f:
                    image_data = f.read()
                
                # Store file path for later use by PDF generator
                image_mapping[relative_path] = str(file_path)
                
                logger.debug(
                    "Image processed",
                    extra={
                        "file": relative_path,
                        "size": len(image_data),
                        "mime_type": mime_type
                    }
                )
                
            except Exception as e:
                logger.warning(
                    "Failed to process image",
                    extra={"file": relative_path, "error": str(e)}
                )
                continue
        
        return image_mapping
    
    def cleanup(self) -> None:
        """Clean up temporary files and directories."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                logger.debug("Temporary directory cleaned up", extra={"temp_dir": self.temp_dir})
            except Exception as e:
                logger.warning(
                    "Failed to clean up temporary directory",
                    extra={"temp_dir": self.temp_dir, "error": str(e)}
                )
        
        # Reset instance variables
        self.temp_dir = None
        self.markdown_files = []
        self.image_files = {}
        self.main_markdown = None
    
    def __enter__(self) -> 'ZipProcessor':
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.cleanup()