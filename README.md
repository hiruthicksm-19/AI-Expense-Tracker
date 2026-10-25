# Invoice Extractor - AI Expense Tracker

A modern, modular Python application for extracting invoice data using AI (Groq LLM) and storing it in MongoDB.

![Architecture](kiro-artifact://26004e77-b3de-4ec1-9d15-d5fc125d3a92)

## Features

- **Modular Architecture** - Clean separation of concerns  
- **Dual Interface** - CLI for batch processing + Web UI for interactive use  
- **AI-Powered Extraction** - Uses Groq LLM for intelligent data extraction  
- **MongoDB Integration** - Persistent storage with duplicate detection  
- **Batch Processing** - Process multiple PDFs automatically  
- **Real-time Progress** - Visual feedback during extraction  
- **JSON Export** - Download extracted data  
- **Database Viewer** - View all stored invoices  
- **Voice Queries** - Record questions and transcribe them locally with Whisper

## Quick Start

### 1. Setup

```bash
# Navigate to project directory
cd "d:\Hiruthick\Project\AI Expense Tracker"

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure

Create `.env` file:
```env
GROQ_API_KEY=your_api_key_here
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=invoice_tracker
MONGODB_COLLECTION=invoices
WHISPER_MODEL=base.en
```

### 3. Run

**Option A: CLI (Batch Processing)**
```bash
python pdf_extractor.py
```

**Option B: Web UI (Interactive)**
```bash
streamlit run app.py
# Opens at http://localhost:8501
```

## Project Structure

```
AI Expense Tracker/
├── config.py                    # Central configuration
├── mongodb_handler.py           # Database operations
├── pdf_extractor.py            # CLI entry point
├── app.py                      # Streamlit web UI
├── modules/                    # Core modules
│   ├── pdf_extractor_module.py # PDF text extraction
│   ├── llm_module.py           # Groq LLM integration
│   ├── stt_module.py           # Local Whisper speech-to-text
│   ├── llm_query_generator.py  # Natural-language MongoDB queries
│   ├── invoice_validator.py    # Data validation
│   └── file_handler.py         # File I/O
├── invoices/                   # Input PDFs
├── output/                     # Output JSON
└── venv/                       # Python environment
```

## Modules Overview

### Core Modules

| Module | Purpose |
|--------|---------|
| `pdf_extractor_module.py` | Extract text from PDF files |
| `llm_module.py` | Groq LLM integration for data extraction |
| `stt_module.py` | Local Whisper transcription for voice queries |
| `llm_query_generator.py` | Generate MongoDB pipelines and natural-language answers |
| `invoice_validator.py` | Validate and normalize extracted data |
| `file_handler.py` | JSON save/load operations |

### Main Components

| File | Purpose |
|------|---------|
| `config.py` | Centralized configuration & constants |
| `mongodb_handler.py` | Database operations & duplicate detection |
| `pdf_extractor.py` | CLI batch processing script |
| `app.py` | Streamlit web interface |

## Usage

### CLI Mode - Batch Processing

```bash
python pdf_extractor.py
```

**Workflow:**
1. Place PDF files in `invoices/` folder
2. Script automatically processes all PDFs
3. Saves extracted data to `output/invoices.json`
4. Inserts into MongoDB (duplicates are skipped)
5. Shows progress and results in terminal

**Example Output:**
```
Found 2 PDF file(s) to process.

[1/2] Processing: invoice-1.pdf
Successfully extracted invoice #INV-2024-001

[2/2] Processing: invoice-2.pdf
Successfully extracted invoice #INV-2024-002

Saving 2 invoice(s) to JSON...
Saved to output/invoices.json

Inserting into MongoDB with duplicate detection...
Successfully inserted 2 new invoice(s)
```

### Web UI Mode - Interactive

```bash
streamlit run app.py
```

**Features:**
- Drag & drop PDF upload (single or multiple)
- Real-time extraction progress
- Data display with expandable cards
- One-click MongoDB save with duplicate detection
- JSON export with download button
- Database viewer showing all stored invoices
- MongoDB connection status indicator
- Voice query input using local Whisper transcription

### Voice Query Workflow

1. Record a question using the microphone in the Query Assistant section.
2. The local Whisper model transcribes the recording.
3. The transcription is placed into the text input field.
4. Review or edit the text if needed.
5. Press **Search** to send the text to the LLM query pipeline.

The recorded audio is processed locally and removed after transcription. The
default model is `base.en`; set `WHISPER_MODEL` in `.env` to use another
installed Whisper model, such as `small.en`.

## Extracted Invoice Fields

Each invoice extracts the following information:

```json
{
  "invoice_number": "INV-2024-001",
  "invoice_date": "2024-10-14",
  "seller_name": "Company ABC",
  "seller_address": "123 Main St, City, State",
  "description": "Product/Service Description",
  "quantity": 10,
  "total_amount": 1000.00,
  "payment_details": "Bank Transfer"
}
```

## Duplicate Detection

The system automatically prevents duplicate entries:

- **CLI Mode**: Shows warning and skips duplicates
- **Web UI Mode**: Displays warning and prevents insertion
- **Check**: Compares invoice numbers with existing records

## Configuration

All configuration is in `config.py` and `.env`:

### Environment Variables (`.env`)
- `GROQ_API_KEY` - Your Groq API key (required)
- `MONGODB_URI` - MongoDB connection string
- `MONGODB_DATABASE` - Database name
- `MONGODB_COLLECTION` - Collection name
- `WHISPER_MODEL` - Local Whisper model name (default: `base.en`)

### config.py
- Directory paths
- Invoice schema
- LLM system prompt
- Model configuration

## Data Flow

### CLI Processing
```
PDF Files 
  ↓
PDF Extractor (extract_pdf_text)
  ↓
Groq LLM (extract_with_llm)
  ↓
Invoice Validator (validate)
  ↓
File Handler (save to JSON)
  ↓
MongoDB Handler (insert to DB)
```

### Web UI Processing
```
File Upload
  ↓
PDF Extractor (extract_pdf_text_from_upload)
  ↓
Groq LLM (extract_with_llm)
  ↓
Invoice Validator (validate)
  ↓
Display on UI
  ↓
MongoDB Handler (insert when user clicks Save)
```

### Voice Query Processing
```
Microphone Recording
  ↓
Local Whisper Transcription
  ↓
Query Textbox
  ↓
User clicks Search
  ↓
LLM Query Generator
  ↓
MongoDB Aggregation Pipeline
  ↓
Natural-language Answer
```

## Dependencies

All dependencies are listed in `requirements.txt`:

```
pymupdf              # PDF text extraction
groq                 # Groq LLM API
pydantic             # Data validation
python-dotenv        # Environment variables
pymongo              # MongoDB driver
streamlit            # Web UI framework
certifi              # TLS certificates
openai-whisper       # Local speech-to-text
```

## Documentation

**This README** - Quick reference and overview  

## Troubleshooting

### Groq API Issues
```python
# Error: GROQ_API_KEY missing
# Solution: Add to .env file
GROQ_API_KEY=your_key_here

# Error: Model decommissioned
# Solution: Update MODEL_NAME in config.py with valid model
```

### MongoDB Issues
```python
# Error: Connection refused
# Solution: Ensure MongoDB is running
# Default: mongodb://localhost:27017

# Error: Authentication failed
# Solution: Update MONGODB_URI with credentials
# Example: mongodb://user:password@host:27017
```

### PDF Extraction Issues
```python
# Error: No extractable text
# Solution: Ensure PDF has selectable text (not scanned image)
# Workaround: Consider using OCR for scanned PDFs
```

## Module Dependencies Graph

```
config.py (Configuration)
    ↓
    ├─→ pdf_extractor_module.py
    ├─→ llm_module.py
    ├─→ invoice_validator.py
    ├─→ file_handler.py
    └─→ mongodb_handler.py
         ↓
    pdf_extractor.py (CLI)
    app.py (Web UI)
```

## Best Practices

- Always keep `.env` file with credentials  
- Test new features with sample PDFs first  
- Monitor MongoDB for storage usage  
- Review extracted data for accuracy  
- Keep backups of `output/invoices.json`  
- Update Groq model when deprecated  

## Performance Tips

- **Batch Processing**: Use CLI mode for large numbers of files
- **Web UI**: Better for interactive, small-batch uploads
- **Database**: Index `invoice_number` for faster duplicate checks
- **Memory**: Process files sequentially to avoid memory issues

## Security Notes

- Never commit `.env` file to version control  
- Keep Groq API key confidential  
- Use MongoDB authentication in production  
- Validate all PDF inputs  
- Sanitize extracted data before display  

## Contributing

To extend the project:

1. **Add new extraction logic** → Modify `modules/pdf_extractor_module.py`
2. **Change LLM behavior** → Modify `modules/llm_module.py`
3. **Update validation rules** → Modify `modules/invoice_validator.py`
4. **Add new file formats** → Modify `modules/file_handler.py`
5. **Update configuration** → Modify `config.py`

Each module is self-contained and can be updated independently.

## License

[Add your license here]

## Support

For issues, questions, or suggestions:
1. Review the documentation files
2. Check `.env` configuration
3. Verify MongoDB is running
4. Ensure all dependencies are installed
5. Check Groq API quota and status

## Future Enhancements

- OCR support for scanned PDFs
- Email notification on completion
- Webhook integration
- Mobile app interface
- User authentication
- Advanced analytics dashboard
- Multi-language support
- Cloud deployment ready

---

**Built with:** Python • Groq API • MongoDB • Streamlit  
**Architecture:** Modular, Scalable, Production-Ready
