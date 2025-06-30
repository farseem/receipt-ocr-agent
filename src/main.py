import sys
import time
from watchdog.observers import Observer

from config import Config
from utils.helpers import setup_logging
from agents.receipt_processor import ReceiptProcessor


def main():
    """Start the OCR agent and begin watching for files."""
    print("OCR Agent - Invoice Processing System")
    print("=" * 40)

    setup_logging()

    if not Config.validate():
        print("Invalid configuration. Please fix and retry.")
        return 1

    Config.create_directories()

    event_handler = ReceiptProcessor()
    observer = Observer()
    observer.schedule(event_handler, Config.WATCH_FOLDER, recursive=False)

    print(f"Watching: {Config.WATCH_FOLDER}")
    print(f"Using database: {Config.DATABASE_PATH}")
    print("Running OCR Agent... Press Ctrl+C to exit.")

    try:
        observer.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping OCR Agent...")
        observer.stop()
    finally:
        observer.join()
        print("OCR Agent stopped.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
