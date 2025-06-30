import os
import logging

from pathlib import Path
from config import Config


def setup_logging() -> None:
    """Setup logging configuration for the application."""
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(Config.LOG_FILE)
    os.makedirs(log_dir, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(Config.LOG_FILE),
            logging.StreamHandler()  # Also log to console
        ]
    )
    
    # Set specific logger levels
    logging.getLogger('google.cloud').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.info("Logging system initialized")


def is_supported_file(file_path: str) -> bool:
    if not os.path.isfile(file_path):
        return False
    
    file_extension = Path(file_path).suffix.lower()
    return file_extension in Config.SUPPORTED_FORMATS
