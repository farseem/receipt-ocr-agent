# OCR Agent - Invoice Processing System

A minimal, automated invoice processing system using Google Cloud Vision API for OCR and OpenRouter LLM API for intelligent field extraction, with real-time file monitoring and structured data extraction.

## 🚀 Features

- **Real-time File Monitoring**: Automatically processes new images uploaded to a watched folder
- **Google Cloud Vision OCR**: High-accuracy text extraction using Google's REST API
- **LLM-Powered Field Extraction**: Uses OpenRouter API to intelligently extract structured invoice fields from OCR text
- **Intelligent Retry Mechanism**: Automatic retry with configurable attempts for failed processing
- **Failed File Management**: Files that fail processing after max retries are moved to failed folder
- **Queue-based Processing**: In-memory queue with background worker thread for efficient processing
- **Pluggable OCR Providers**: Factory pattern supporting mock and Google Vision providers
- **Mock Mode**: Development mode with simulated OCR responses to avoid API costs during testing
- **Lightweight Storage**: Stores extracted data in JSON format using TinyDB
- **Simple Setup**: Minimal dependencies and easy configuration
- **Comprehensive Logging**: Detailed logs for monitoring and debugging

## 📁 Project Structure

```
OCR Agent/
├── src/                       # Main application source
│   ├── __init__.py
│   ├── main.py                # Main entry point with file monitoring
│   ├── config.py              # Configuration management
│   ├── agents/                # Processing agents
│   │   └── receipt_processor.py  # Main processing logic with queue management
│   ├── services/              # Core services
│   │   ├── __init__.py
│   │   ├── extract_service.py # LLM field extraction logic
│   │   └── ocr/               # OCR service providers
│   │       ├── __init__.py
│   │       ├── ocr_service.py     # Abstract OCR service
│   │       ├── ocr_factory.py     # OCR provider factory
│   │       ├── google_vision_ocr_service.py  # Google Vision implementation
│   │       └── mock_ocr_service.py # Mock implementation for testing
│   ├── storage/               # Data storage
│   │   ├── __init__.py
│   │   └── db.py              # TinyDB JSON storage
│   └── utils/                 # Utility functions
│       ├── __init__.py
│       └── helpers.py         # Helper functions
├── tests/                     # Test suite
├── data/                      # Data directories
│   ├── input/                 # Watch folder for new images
│   ├── processed/             # Successfully processed images
│   ├── failed/                # Images that failed processing after retries
│   └── storage/               # Database files
├── logs/                      # Log files (auto-generated)
├── credentials/               # Google Cloud credentials
├── run.py                     # Alternative CLI runner
├── requirements.txt           # Minimal production dependencies
├── requirements-dev.txt       # Development dependencies
├── .env.example              # Environment variables template
└── README.md                 # This file
```

## 🔧 Setup Instructions

### 1. Prerequisites

- Python 3.8 or higher
- Google Cloud Platform account with Vision API enabled
- OpenRouter API account for LLM-powered field extraction

### 2. Google Cloud Setup

**Option 1: API Key (Recommended for simplicity)**
1. Create a Google Cloud Project
2. Enable the Cloud Vision API
3. Create an API Key in the Credentials section
4. Restrict the API key to Cloud Vision API only (for security)

**Option 2: Service Account (More secure)**
1. Create a Google Cloud Project
2. Enable the Cloud Vision API
3. Create a service account and download the JSON key file
4. Set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable

### 3. OpenRouter Setup

1. Sign up at [OpenRouter.ai](https://openrouter.ai/)
2. Get your API key from the dashboard
3. Choose a model (e.g., `meta-llama/llama-3.1-8b-instruct:free` for free tier)

### 4. Environment Setup

```powershell
# Navigate to the project directory
cd "d:\Workspace\OCR Agent"

# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows PowerShell)
venv\Scripts\Activate.ps1

# Install minimal dependencies
pip install -r requirements.txt

# For development work:
pip install -r requirements-dev.txt
```

### 5. Configuration

```powershell
# Copy environment template
copy .env.example .env

# Edit .env file with your API keys:
# Google Cloud:
GOOGLE_VISION_API_KEY=your-google-vision-api-key
GOOGLE_VISION_API_URL=https://vision.googleapis.com/v1/images:annotate
# OR GOOGLE_APPLICATION_CREDENTIALS=path\to\service-account.json

# OpenRouter:
OPENROUTER_API_KEY=your-openrouter-api-key
OPENROUTER_ENDPOINT=https://openrouter.ai/api/v1/chat/completions
OPENROUTER_MODEL=mistralai/mistral-7b-instruct

# Processing Configuration:
OCR_CONFIDENCE_THRESHOLD=0.9
FAILED_FOLDER=./data/failed
```

### 6. Directory Setup

The application will automatically create necessary directories when you first run it.

## 🚀 Usage

### Start the OCR Agent

**Primary method - Direct execution:**
```powershell
# Navigate to src directory and run main.py
cd src
python main.py
```

**Alternative - Using the CLI runner:**
```powershell
# From project root
python run.py
```

### Mock vs Production Mode

The system supports two operating modes:

**🧪 Mock Mode (Development)**
- Uses simulated OCR responses without API calls
- Perfect for development and testing
- No API costs incurred
- Controlled, predictable results
- Set `use_mock=True` in ReceiptProcessor initialization

**🚀 Production Mode (Live API)**
- Uses real Google Cloud Vision API
- Requires valid API keys and credits
- Real OCR processing of uploaded images
- Set `use_mock=False` in ReceiptProcessor initialization

**Why use Mock Mode?**
- Develop and test without API costs
- Predictable responses for testing logic
- No dependency on internet connectivity
- Faster development iteration
python main.py
```

The system will:
1. Monitor the `data/input/` folder for new images
2. Add detected files to an in-memory processing queue
3. Process files using background worker thread with retry mechanism
4. Extract text using Google Cloud Vision OCR (or mock responses in development)
5. Use OpenRouter LLM to intelligently extract structured invoice fields
6. Store results in the JSON database (`data/storage/`)
7. Move successfully processed files to `data/processed/` folder
8. Move failed files (after max retries) to `data/failed/` folder

### Adding Images for Processing

Simply copy image files to the `data/input/` folder and the system will automatically detect and process them.

### Viewing Results

- **Database file**: Check `data/storage/invoice_data.json` for extracted data
- **Logs**: Monitor `logs/ocr_agent.log` for processing details
- **Console**: Watch real-time processing output

## 📊 Extracted Data Fields

The system uses LLM-powered extraction via OpenRouter to intelligently identify and structure the following fields from invoices:

- **Vendor**: Company/vendor name
- **Date**: Transaction date (in YYYY-MM-DD format)
- **Total Amount**: Total amount in SEK
- **Items**: List of items with names and prices
- **Payment Method**: Card, cash, Swish, etc.
- **Discounts**: Any discounts or adjustments

The LLM can handle complex invoice layouts and extract itemized details with individual prices, making it much more accurate than simple pattern matching.

Results are stored in JSON format with OCR confidence scores and processing timestamps.

## 🧪 Testing

Run the test suite:

```powershell
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_main.py -v
```

## 🔧 Development

### Code Quality

```powershell
# Format code with Black
black src/ tests/

# Type checking with MyPy
mypy src/

# Lint with Flake8
flake8 src/ tests/
```

## 🔍 How It Works

1. **File Detection**: Watchdog monitors the `data/input/` folder for new files
2. **Queue Management**: Files are added to an in-memory processing queue with status tracking
3. **Background Processing**: Dedicated worker thread processes queued files continuously
4. **OCR Processing**: Google Cloud Vision REST API extracts raw text from images (or mock service in development)
5. **LLM Field Extraction**: OpenRouter API uses AI to intelligently parse the OCR text and extract structured invoice fields
6. **Retry Logic**: Failed processing attempts are automatically retried up to configurable maximum attempts
7. **Data Storage**: Successfully processed results stored in TinyDB JSON database
8. **File Management**: 
   - Successfully processed files moved to `data/processed/` folder
   - Failed files (after max retries) moved to `data/failed/` folder

## 📝 Configuration Options

Key environment variables in `.env`:

```bash
# Google Cloud API Key (preferred method)
GOOGLE_VISION_API_KEY=your-google-vision-api-key
GOOGLE_VISION_API_URL=https://vision.googleapis.com/v1/images:annotate

# OR Google Cloud Service Account (alternative)
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json

# OpenRouter API for LLM field extraction
OPENROUTER_API_KEY=your-openrouter-api-key
OPENROUTER_ENDPOINT=https://openrouter.ai/api/v1/chat/completions
OPENROUTER_MODEL=mistralai/mistral-7b-instruct

# Directories (relative to project root)
WATCH_FOLDER=./data/input
PROCESSED_FOLDER=./data/processed
FAILED_FOLDER=./data/failed

# Processing
MAX_FILE_SIZE_MB=10
OCR_CONFIDENCE_THRESHOLD=0.9

# Storage
DATABASE_PATH=./data/storage/invoice_data.json

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/ocr_agent.log
```

## 🚨 Troubleshooting

### Common Issues

**Google Cloud Authentication Error**
```powershell
# Check API key is set correctly
python -c "import os; print('API Key:', 'Set' if os.getenv('GOOGLE_API_KEY') else 'Not Set')"

# OR check service account credentials
python -c "import os; print('Credentials:', os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 'Not Set'))"
```

**OpenRouter API Error**
```powershell
# Check OpenRouter API key is set
python -c "import os; print('OpenRouter Key:', 'Set' if os.getenv('OPENROUTER_API_KEY') else 'Not Set')"
```

**LLM Field Extraction Failed**
- Check OpenRouter API key is valid
- Verify you have sufficient credits/quota
- Check the model name is correct
- Review logs for specific error messages

**No Text Extracted**
- Check image quality and resolution
- Ensure text is clearly visible
- Try different image formats (JPG, PNG work best)

**File Not Processing**
- Check that files are being placed in `data/input/` folder
- Verify file format is supported
- Check file size limits in configuration

**Database Errors**
- Ensure write permissions to `data/storage/` folder
- Check available disk space

## 📈 Performance Tips

- Use high-quality, high-resolution images
- Ensure good contrast between text and background
- Use supported formats (JPG, PNG work best)
- Keep images under the configured size limit

## 🔐 Security Considerations

- Keep Google Cloud API keys secure (never commit to version control)
- Keep OpenRouter API keys secure and monitor usage
- Restrict API key permissions to Cloud Vision API only
- Regularly backup the database
- Monitor log files for unusual activity

## 💰 Cost Management

**Google Cloud Vision API**:
- Charges per image processed
- Monitor usage in Google Cloud Console
- Consider setting billing alerts

**OpenRouter API**:
- Charges per token processed by the LLM
- Monitor usage in OpenRouter dashboard
- Consider using free tier models for testing
- Optimize prompts to reduce token usage

Test with small batches first to understand costs.

## 📦 Dependencies

**Production dependencies** (`requirements.txt`):
- `watchdog>=2.1.9` - File system monitoring
- `python-dotenv>=0.19.0` - Environment variable management
- `tinydb>=4.7.0` - Lightweight JSON database
- `requests>=2.25.0` - HTTP client for Google Vision API and OpenRouter API

**Development dependencies** (`requirements-dev.txt`):
- `pytest>=6.2.0` - Testing framework
- `pytest-cov>=2.12.0` - Test coverage
- `black>=21.0.0` - Code formatting
- `flake8>=3.9.0` - Code linting
- `mypy>=0.910` - Type checking

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Ensure all tests pass
5. Format code with Black
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

---

**Note**: This project follows YAGNI (You Aren't Gonna Need It) principles - keeping dependencies minimal and adding features only when actually needed. The current implementation provides a solid foundation for invoice OCR processing that can be extended as requirements evolve.
