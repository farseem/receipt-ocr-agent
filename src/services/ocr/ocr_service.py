from abc import ABC, abstractmethod
from typing import Optional

class OCRService(ABC):
    @abstractmethod
    def process_image(self, image_bytes: bytes, filename: str) -> Optional[dict]:
        pass
