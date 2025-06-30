import json
import logging
import os
import time
from datetime import datetime

from typing import Optional
from watchdog.events import FileSystemEventHandler

from config import Config
from services.extract_service import ExtractService
from services.ocr_service import OCRService
from storage.db import DatabaseManager
from utils.helpers import is_supported_file


class ReceiptProcessor(FileSystemEventHandler):
    """Watches for new receipt images and processes them."""

    # TODO: Must change the use_mock flag to False in production
    def __init__(self, use_mock=True):
        self.logger = logging.getLogger(__name__)
        self.ocr_service = OCRService()
        self.extract_service = ExtractService()
        self.db = DatabaseManager()
        self.use_mock = use_mock

    def on_created(self, event):
        """Called when a new file is added."""
        if not event.is_directory and is_supported_file(event.src_path):
            self.logger.info(f"\U0001F4E5 New file detected: {event.src_path}")
            self.process_image(event.src_path)

    def process_image(self, image_path: str):
        """Handles image processing, real or mock."""
        try:
            result = (
                self.mock_process_image()
                if self.use_mock
                else self._process_image_from_path(image_path)
            )

            if not result:
                return

            self._handle_result(result, image_path)

        except Exception as e:
            self.logger.error(f"Error processing {image_path}: {str(e)}")

    def _process_image_from_path(self, image_path: str):
        with open(image_path, 'rb') as f:
            image_bytes = f.read()
        return self.ocr_service.process_image(image_bytes, os.path.basename(image_path))

    def mock_process_image(self):
        """Simulate OCR processing for development without API calls."""
        result = self.ocr_service.mock_process_image()
        self.logger.info(f"\U0001F50D Mock OCR Result: {result}")
        return result

    def _handle_result(self, result, image_path: str):
        if not self._is_confidence_valid(result):
            return

        full_text = result.get("full_text", "")
        self.logger.info(f"Extracted text:\n{full_text}")

        fields = self._parse_fields(full_text)
        if not fields:
            return

        finalized = self._finalize_invoice_data(fields, result)
        self._save_and_confirm(finalized, image_path)

    def _is_confidence_valid(self, result: dict) -> bool:
        confidence = result.get("confidence", 0.0)
        if confidence <= Config.OCR_CONFIDENCE_THRESHOLD:
            self.logger.error(f"OCR confidence too low: {confidence:.2%}. Skipping.")
            return False
        return True

    def _parse_fields(self, full_text: str) -> Optional[dict]:
        fields = self.extract_service.extract_invoice_fields(full_text)
        if isinstance(fields, str):
            try:
                fields = json.loads(fields)
            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to decode extracted fields: {e}")
                return None

        if not isinstance(fields, dict) or not fields:
            self.logger.error("Extracted fields are empty or invalid. Skipping save.")
            return None

        return fields

    def _finalize_invoice_data(self, fields: dict, result: dict) -> dict:
        fields["confidence"] = result.get("confidence", 0.0)
        fields["extracted_at"] = datetime.now().strftime("%Y-%m-%d")
        return fields

    def _save_and_confirm(self, fields: dict, image_path: str):
        try:
            doc_id = self.db.save_invoice_data(fields)
            self.logger.info(f"Invoice saved successfully with ID: {doc_id}")
            self.logger.info(f"Verifying saved invoice with ID: {doc_id}")
            all_records = self.db.get_all_invoices()
            print(json.dumps(all_records, indent=2))
            self._move_processed_file(image_path)
            return doc_id
        except Exception as e:
            self.logger.error(f"Failed to save invoice data: {e}")
            return None

    def _move_processed_file(self, image_path: str):
        try:
            os.makedirs(Config.PROCESSED_FOLDER, exist_ok=True)
            filename = os.path.basename(image_path)
            target_path = os.path.join(Config.PROCESSED_FOLDER, filename)

            if os.path.exists(target_path):
                name, ext = os.path.splitext(filename)
                timestamp = int(time.time())
                target_path = os.path.join(Config.PROCESSED_FOLDER, f"{name}_{timestamp}{ext}")

            os.rename(image_path, target_path)
            self.logger.info(f"Moved processed file to: {target_path}")

        except Exception as e:
            self.logger.error(f"Failed to move file: {str(e)}")
