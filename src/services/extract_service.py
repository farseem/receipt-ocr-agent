import json
import logging
import requests
from config import Config

class ExtractService:
    """LLM-powered field extractor using OpenRouter API."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.api_key = Config.OPENROUTER_API_KEY
        self.endpoint = Config.OPENROUTER_ENDPOINT
        self.model = Config.OPENROUTER_MODEL

    def extract_invoice_fields(self, full_text: str) -> dict:
        """Extract structured invoice data using LLM via OpenRouter."""
        try:
            if not self.api_key:
                raise ValueError("LLM API key missing")

            prompt = (
                "You are a receipt parser. "
                "From the following OCR receipt text, extract the following fields:\n"
                "- Vendor name\n"
                "- Date of transaction (in YYYY-MM-DD format)\n"
                "- Total amount in SEK\n"
                "- List of items (as name and price)\n\n"
                "- Payment method (e.g., card, cash, swish)\n"
                "- Consider any discounts or adjustments. "
                "If possible, include itemized details with their individual prices. "
                "If the discount cannot be matched to a specific item, include a separate "
                "field called \"discount\" as a total adjustment.\n"
                f"OCR Text:\n{full_text}\n\n"
                "Respond in JSON format with keys: vendor, date, total_amount, items "
                "(list of {name, price})."
            )

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.2,
            }

            response = requests.post(self.endpoint, headers=headers, json=payload)
            response.raise_for_status()

            reply_text = response.json()["choices"][0]["message"]["content"]
            extracted = json.loads(reply_text)
            if not isinstance(extracted, dict):
                raise ValueError("LLM response is not a valid JSON object")
            # Ensure all required fields are present
            required_fields = ["vendor", "date", "total_amount", "items"]
            missing_fields = [field for field in required_fields if field not in extracted]
            if missing_fields:
                raise ValueError(f"Missing fields in LLM response: {missing_fields}")
            
            self.logger.info(f"Extracted fields: {extracted}")
            return extracted

        except Exception as e:
            self.logger.error(f"LLM extraction failed: {e}")
            return {}