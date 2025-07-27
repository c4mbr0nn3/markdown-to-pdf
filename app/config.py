from pydantic_settings import BaseSettings
from typing import List
from loguru import logger
import sys
import os


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
    company_logo_url: str = "/templates/assets/logo.png"
    
    # Security Settings
    allowed_origins: List[str] = ["*"]
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"


def setup_logging(log_level: str = "INFO", environment: str = "development") -> None:
    """Configure Loguru logging."""
    
    # Remove default handler
    logger.remove()
    
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
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


# Global settings instance
settings = Settings()