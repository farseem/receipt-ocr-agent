import time
from services.ocr.ocr_service import OCRService

class MockOCRService(OCRService):
    def process_image(self, image_bytes: bytes, filename: str) -> dict:
        
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