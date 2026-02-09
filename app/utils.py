"""
Utility Module for Enterprise Document Q&A System

Provides logging, configuration, and helper utilities.
"""

import logging
import os
import sys
import re
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from app.config import config

# Load environment variables from .env file
load_dotenv()


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """
    Configure application-wide logging.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    logging.basicConfig(
        level=numeric_level,
        format=log_format,
        datefmt=date_format,
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    
    logger = logging.getLogger("enterprise_doc_qa")
    logger.setLevel(numeric_level)
    return logger


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to remove potentially harmful characters.
    
    Args:
        filename: Original filename
        
    Returns:
        str: Sanitized filename safe for filesystem operations
    """
    invalid_chars = '<>:"/\\|?*'
    sanitized = filename
    
    for char in invalid_chars:
        sanitized = sanitized.replace(char, '_')
    
    sanitized = sanitized.strip('. ')
    
    if not sanitized:
        sanitized = "unnamed_document"
    
    return sanitized


def get_file_metadata(file_path: str) -> dict:
    """
    Extract metadata from a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        dict: File metadata including name and size
    """
    file_path_obj = Path(file_path)
    
    return {
        "filename": file_path_obj.name,
        "size_bytes": file_path_obj.stat().st_size,
        "absolute_path": str(file_path_obj.absolute())
    }


def validate_pdf_file(file_path: str) -> bool:
    """
    Validate if a file is a valid PDF.
    
    Args:
        file_path: Path to the file to validate
        
    Returns:
        bool: True if file is a valid PDF
    """
    if not os.path.exists(file_path):
        return False
    
    if not file_path.lower().endswith('.pdf'):
        return False
    
    try:
        file_size = os.path.getsize(file_path)
        return file_size > 0
    except Exception:
        return False


# ============================================================================
# Global Initialization
# ============================================================================

logger = setup_logging(config.log_level)
logger.info("Application utilities initialized successfully")

