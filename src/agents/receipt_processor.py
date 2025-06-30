import json
import logging
import os
import time
import threading
from datetime import datetime

from typing import Optional
from watchdog.events import FileSystemEventHandler

from config import Config
from services.extract_service import ExtractService
from services.ocr.ocr_service import OCRService
from storage.db import DatabaseManager
from utils.helpers import is_supported_file
from services.ocr.ocr_factory import OCRServiceFactory


class ReceiptProcessor(FileSystemEventHandler):
    """Watches for new receipt images and processes them."""

    # TODO: Must change the use_mock flag to False in production
    def __init__(self, use_mock=False):
        self.logger = logging.getLogger(__name__)
        self.extract_service = ExtractService()
        self.db = DatabaseManager()
        self.use_mock = use_mock
        self.processing_queue = {}  # filename -> {retries, status}
        self.max_retries = 3 # TODO: Make this configurable
        
        provider = "mock" if self.use_mock else "google"
        self.ocr_service = OCRServiceFactory.get_ocr_service(provider)
        
        # Start background worker
        threading.Thread(target=self._queue_worker, daemon=True).start()
            
    def on_created(self, event):
        """Called when a new file is added."""
        if not event.is_directory and is_supported_file(event.src_path):
            self.logger.info(f"New file detected: {event.src_path}")
            self._enqueue(event.src_path)

    def _enqueue(self, image_path: str):
        if image_path in self.processing_queue:
            self.logger.debug(f"Already in queue: {image_path}")
            return

        self.processing_queue[image_path] = {"retries": 0, "status": "pending"}
        self.logger.info(f"Enqueued for processing: {image_path}")
        
    def _queue_worker(self):
        while True:
            for path, meta in list(self.processing_queue.items()):
                if meta["status"] != "pending":
                    continue
                meta["status"] = "processing"
                self._process_image(path)
            time.sleep(2)  # Polling delay
            
    def _process_image(self, image_path: str):
        self.logger.info(f"Processing: {image_path}")
        try:
            result = (
                self.mock_process_image(image_path)
                if self.use_mock
                else self._process_image_from_path(image_path)
            )

            if not result:
                raise ValueError("Processing returned no result.")

            self._handle_result(result, image_path)
            del self.processing_queue[image_path]

        except Exception as e:
            self._handle_processing_failure(image_path, e)

    def _handle_processing_failure(self, image_path: str, error: Exception):
        meta = self.processing_queue.get(image_path, {})
        retries = meta.get("retries", 0) + 1
        meta["retries"] = retries

        if retries >= self.max_retries:
            self.logger.error(f"Max retries reached for {image_path}. Moving to failed folder. Error: {error}")
            meta["status"] = "failed"
            self._move_to_failed_folder(image_path)
            del self.processing_queue[image_path]
        else:
            self.logger.warning(f"Retrying {image_path} (attempt {retries}) due to error: {error}")
            meta["status"] = "pending"
            self.processing_queue[image_path] = meta


    def _process_image_from_path(self, image_path: str):
        with open(image_path, 'rb') as f:
            image_bytes = f.read()
        return self.ocr_service.process_image(image_bytes, os.path.basename(image_path))

    def mock_process_image(self, image_path: str):
        """Simulate OCR processing for development without API calls."""
        with open(image_path, 'rb') as f:
            image_bytes = f.read()
        result = self.ocr_service.process_image(image_bytes, os.path.basename(image_path))
        self.logger.info(f"Mock OCR Result: {result}")
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
            
            record = self.db.get_invoice_by_id(doc_id)
            if record:
                print(json.dumps(record, indent=2))
                
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
            
    def _move_to_failed_folder(self, image_path: str):
        try:
            os.makedirs(Config.FAILED_FOLDER, exist_ok=True)
            filename = os.path.basename(image_path)
            target_path = os.path.join(Config.FAILED_FOLDER, filename)

            if os.path.exists(target_path):
                name, ext = os.path.splitext(filename)
                timestamp = int(time.time())
                target_path = os.path.join(Config.FAILED_FOLDER, f"{name}_{timestamp}{ext}")

            os.rename(image_path, target_path)
            self.logger.info(f"Moved failed file to: {target_path}")

        except Exception as e:
            self.logger.error(f"Failed to move file to failed folder: {str(e)}")
