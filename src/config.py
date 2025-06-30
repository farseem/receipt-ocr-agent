import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for OCR Agent."""
    
    # Google Cloud Vision API - Support both authentication methods
    GOOGLE_VISION_API_KEY: Optional[str] = os.getenv("GOOGLE_VISION_API_KEY")
    GOOGLE_VISION_API_URL: Optional[str] = os.getenv("GOOGLE_VISION_API_URL")
    
    # LLM configuration
    # OPENROUTER 
    OPENROUTER_API_KEY: Optional[str] = os.getenv("OPENROUTE_API_KEY")
    OPENROUTER_ENDPOINT: Optional[str] = os.getenv("OPENROUTER_ENDPOINT")
    OPENROUTER_MODEL: Optional[str] = os.getenv("OPENROUTER_MODEL", "mistralai/mistral-7b-instruct")


    # File monitoring
    WATCH_FOLDER: str = os.getenv("WATCH_FOLDER", "./input_images")
    PROCESSED_FOLDER: str = os.getenv("PROCESSED_FOLDER", "./processed_images")
    FAILED_FOLDER = os.getenv("FAILED_FOLDER", "./failed_images")
    
    # Storage configuration
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "./storage/invoice_data.json")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "./logs/ocr_agent.log")
    
    # Processing settings
    SUPPORTED_FORMATS: list = [".jpg", ".jpeg", ".png", ".pdf", ".tiff", ".bmp"]
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
    
    # OCR confidence threshold
    OCR_CONFIDENCE_THRESHOLD: float = float(os.getenv("OCR_CONFIDENCE_THRESHOLD", "0.9"))
    
    @classmethod
    def validate(cls) -> bool:
        """
        Validate essential configuration settings.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        if not cls.GOOGLE_VISION_API_KEY:
            print("Warning: GOOGLE_VISION_API_KEY not set")
            return False
        if not cls.GOOGLE_VISION_API_URL:
            print("Warning: GOOGLE_VISION_API_URL not set")
            return False
        if not cls.OPENROUTER_API_KEY:
            print("Warning: OPENROUTER_API_KEY not set")
            return False
        if not cls.OPENROUTER_ENDPOINT:
            print("Warning: OPENROUTER_ENDPOINT not set")
            return False
        if not cls.OPENROUTER_MODEL:
            print("Warning: OPENROUTER_MODEL not set, using default 'mistralai/mistral-7b-instruct'")
            cls.OPENROUTER_MODEL = "mistralai/mistral-7b-instruct"
        if not cls.WATCH_FOLDER:
            print("Warning: WATCH_FOLDER not set")
            return False        
        if not cls.PROCESSED_FOLDER:
            print("Warning: PROCESSED_FOLDER not set")
            return False
        if not cls.DATABASE_PATH:
            print("Warning: DATABASE_PATH not set")
            return False
        if not cls.LOG_FILE:
            print("Warning: LOG_FILE not set")
            return False
        return True
    
    @classmethod
    def create_directories(cls) -> None:
        """Create necessary directories if they don't exist."""
        directories = [
            cls.WATCH_FOLDER,
            cls.PROCESSED_FOLDER,
            cls.FAILED_FOLDER,
            os.path.dirname(cls.DATABASE_PATH),
            os.path.dirname(cls.LOG_FILE),
        ]
        
        for directory in directories:
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                print(f"Created directory: {directory}")
