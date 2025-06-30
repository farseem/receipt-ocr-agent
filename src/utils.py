import os
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


def validate_file_path(file_path: str) -> bool:
    try:
        return os.path.isfile(file_path) and os.access(file_path, os.R_OK)
    except Exception as e:
        logger.error(f"Error validating file path {file_path}: {e}")
        return False


def get_supported_formats() -> List[str]:
    return ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.pdf', '.docx']


def sanitize_filename(filename: str) -> str:
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename