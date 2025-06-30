import base64
import json
import logging
import time
import requests
from typing import Optional

from config import Config
from storage.db import DatabaseManager


class OCRService:
    """OCR service using Google Vision API via REST."""

    def __init__(self):
        self.api_key = Config.GOOGLE_VISION_API_KEY
        self.endpoint = Config.GOOGLE_VISION_API_URL
        self.db = DatabaseManager()
        self.logger = logging.getLogger(__name__)

    def process_image(self, image_bytes: bytes, filename: str) -> Optional[str]:
        """ Process image via Google Vision API and save result to DB."""
        try:
            ocr_result = self._extract_text(image_bytes)
            if not ocr_result:
                self.logger.warning(f"No text extracted from {filename}")
                return None

            # Log the OCR result for debugging
            self.logger.info(f"OCR response for {filename}:\n{json.dumps(ocr_result, indent=2)}")

            return ocr_result

        except Exception as e:
            self.logger.error(f"OCR processing failed for {filename}: {e}")
            return None


    def mock_process_image(self) -> dict:
        """Return a static mocked OCR result for local testing."""
        ocr_result = {
            "full_text": (
                "o Clas Ohlson\nClas Ohlson\nTrelleborgsvägen 7\n21432 Malmö\n0247-445 00\n"
                "BUTIK KA. ANV. KVITTO DATUM\n0167 2 OSX\n1129562 20250625 14:09\n"
                "b 40-8808-6\nKOMB.HÄNGLÅS ALUM\n59.90\nb 40-8808-7\nKOMB.HÄNGLAS ALUM\n59.90\n"
                "Komb.hanglås 2 for 99,90\n-19.90\nAntal artiklar: 2\nTOTAL\n100.00\nMasterCard\n99.90\n"
                "MOMS%\nBRUTTO\nMOMS\nNETTO\nb 25.0%\n99.90\n19.98\n79.92\nTotal\n99.90\n19.98 79.92\n"
                "Swedbank\n806 osutuels,alilualo\nlanoxox tobrisottaamable al\nBUTIKSNR: 2544369\n"
                "TERM: 14393803-507091\n2025-06-25 14:09\n"
                "Scanned with CamScanner"
            ),
            "confidence": 0.95,
            "timestamp": time.time()
        }

        return ocr_result

    def _extract_text(self, image_bytes: bytes) -> Optional[dict]:
        """Call Google Vision API to extract text from image."""
        try:
            if not self.api_key:
                raise ValueError("GOOGLE_API_KEY is missing in Config")

            image_base64 = base64.b64encode(image_bytes).decode("utf-8")

            payload = {
                "requests": [
                    {
                        "image": {"content": image_base64},
                        "features": [{"type": "TEXT_DETECTION"}] # Use DOCUMENT_TEXT_DETECTION for confedence scores
                    }
                ]
            }

            response = requests.post(
                f"{self.endpoint}?key={self.api_key}",
                headers={"Content-Type": "application/json"},
                json=payload
            )

            if response.status_code != 200:
                self.logger.error(f"Google Vision API error: {response.text}")
                return None

            result = response.json()
            annotations = result["responses"][0].get("textAnnotations", [])

            if not annotations:
                return None

            full_text = annotations[0]["description"]
            return {
                "full_text": full_text,
                "confidence": 0.95,  # Vision API REST does not return confidence here
                "timestamp": time.time()
            }

        except Exception as e:
            self.logger.error(f"Failed to extract text: {e}")
            return None
