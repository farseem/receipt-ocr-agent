
import os
import logging
from typing import Dict, Any, List, Optional
from tinydb import TinyDB, Query
from datetime import datetime
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware

from config import Config


class DatabaseManager:
    """TinyDB database manager for saving and searching invoices."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or Config.DATABASE_PATH
        self.logger = logging.getLogger(__name__)
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        self.db = TinyDB(
            self.db_path,
            storage=CachingMiddleware(JSONStorage),
            indent=2
        )
        self.invoices = self.db.table("invoices")
        self.logger.info(f"TinyDB initialized at: {self.db_path}")

    def save_invoice_data(self, invoice_data: Dict[str, Any]) -> int:
        """Save invoice data to the TinyDB 'invoices' table."""
        try:
            invoice_data.setdefault("created_at", datetime.now().strftime("%Y-%m-%d"))
            invoice_data.setdefault("updated_at", datetime.now().strftime("%Y-%m-%d"))
            doc_id = self.invoices.insert(invoice_data)
            self.logger.info(f"Invoice saved with ID: {doc_id}")
            
            self.db.storage.flush()
            return doc_id
        except Exception as e:
            self.logger.error(f"Failed to save invoice: {e}")
            return -1

    def get_all_invoices(self) -> List[Dict[str, Any]]:
        """Return all saved invoices."""
        try:
            return self.invoices.all()
        except Exception as e:
            self.logger.error(f"Failed to fetch all invoices: {e}")
            return []

    def search_invoices(self, **criteria) -> List[Dict[str, Any]]:
        """
        Search for invoices using simple field=value filters.
        Example: search_invoices(vendor="Clas Ohlson")
        """
        try:
            Invoice = Query()
            filters = [Invoice[k] == v for k, v in criteria.items() if v is not None]
            if not filters:
                return self.get_all_invoices()

            query = filters[0]
            for f in filters[1:]:
                query &= f

            results = self.invoices.search(query)
            self.logger.info(f"Found {len(results)} invoices matching: {criteria}")
            return results
        except Exception as e:
            self.logger.error(f"Search failed: {e}")
            return []

    def close(self):
        """Close TinyDB (flushes cache)."""
        try:
            self.db.close()
            self.logger.info("TinyDB connection closed.")
        except Exception as e:
            self.logger.error(f"Error closing DB: {e}")
