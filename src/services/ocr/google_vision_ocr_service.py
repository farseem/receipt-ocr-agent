import base64, json, time, logging, requests
from typing import Optional
from config import Config
from services.ocr.ocr_service import OCRService

class GoogleVisionOCRService(OCRService):
    def __init__(self):
        self.api_key = Config.GOOGLE_VISION_API_KEY
        self.endpoint = Config.GOOGLE_VISION_API_URL
        self.logger = logging.getLogger(__name__)

    def process_image(self, image_bytes: bytes, filename: str) -> Optional[dict]:
        try:
            self._validate_api_key()
            payload = self._build_payload(image_bytes)
            response = self._send_request(payload)

            if response.status_code != 200:
                self.logger.error(f"Google Vision API error: {response.text}")
                return None

            return self._parse_response(response.json())

        except Exception as e:
            self.logger.error(f"OCR failed for {filename}: {e}")
            return None

    def _validate_api_key(self):
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY is missing")

    def _build_payload(self, image_bytes: bytes) -> dict:
        encoded = base64.b64encode(image_bytes).decode("utf-8")
        return {
            "requests": [
                {
                    "image": {"content": encoded},
                    "features": [{"type": "TEXT_DETECTION"}]
                }
            ]
        }

    def _send_request(self, payload: dict) -> requests.Response:
        return requests.post(
            f"{self.endpoint}?key={self.api_key}",
            headers={"Content-Type": "application/json"},
            json=payload
        )

    def _parse_response(self, result: dict) -> Optional[dict]:
        annotations = result["responses"][0].get("textAnnotations", [])
        if not annotations:
            return None
        return {
            "full_text": annotations[0]["description"],
            "confidence": 0.95,
            "timestamp": time.time()
        }