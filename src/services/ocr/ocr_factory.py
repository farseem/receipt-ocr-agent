from .mock_ocr_service import MockOCRService
from .google_vision_ocr_service import GoogleVisionOCRService

class OCRServiceFactory:
    @staticmethod
    def get_ocr_service(provider: str):
        if provider == "mock":
            return MockOCRService()
        elif provider == "google":
            return GoogleVisionOCRService()
        else:
            raise ValueError(f"OCR provider '{provider}' not supported")