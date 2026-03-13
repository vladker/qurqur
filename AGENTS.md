# AGENTS.md

## Project Overview
This is a QR Code File Encoder CLI application (v2.0) that generates QR codes from text/binary files with customizable parameters and supports decoding files from QR codes.

## Project Structure
```
qurqur/
├── qr_encoder.py          # Main CLI for generating QR codes
├── qr_decoder.py          # Main CLI for decoding QR codes
├── config.py              # Configuration constants
├── services/
│   ├── __init__.py
│   ├── text_processor.py  # Text splitting and metadata handling
│   ├── qr_generator.py    # QR code generation
│   ├── file_manager.py    # File I/O operations
│   ├── qr_collector.py    # QR code collection/decoding
│   └── compression.py     # Data compression (ZIP, GZIP, BZ2, LZMA)
├── utils/
│   └── __init__.py
└── requirements.txt       # Dependencies
```

## Build Commands
```bash
# Install dependencies
pip install -r requirements.txt

# Run the main encoder application
python qr_encoder.py

# Run the decoder application
python qr_decoder.py

# Activate virtual environment (if using .venv)
# On Windows:
.venv\Scripts\activate
# On Unix/Mac:
source .venv/bin/activate
```

## Lint Commands
```bash
# Using pylint for Python linting
pylint *.py services/*.py

# Using flake8 for Python linting
flake8 .

# Using autopep8 to auto-format code
autopep8 --in-place --aggressive --aggressive *.py services/*.py
```

## Test Commands
```bash
# Run all tests
pytest

# Run a single test file
pytest test_file.py

# Run specific test function
pytest test_file.py::test_function_name

# Run with coverage
pytest --cov=. --cov-report=html
```

## Code Style Guidelines

### Imports
- Import standard library modules first, then third-party libraries, then local modules
- Sort imports alphabetically within each group
- Example:
```python
import base64
import os
import re
from typing import List, Tuple

import qrcode
from PIL import Image

from config import VERSION
from services.text_processor import TextProcessor
```

### Formatting
- Follow PEP 8 style guide
- Use 4 spaces for indentation (no tabs)
- Limit lines to 79 characters (100 for comments)
- Use blank lines to separate functions and classes (2 blank lines between top-level definitions)
- Add a space after commas, colons, and semicolons
- Use trailing commas for multi-line collections

### Types
- Use type hints for all function parameters and return values
- Use `Optional[T]` instead of `T | None` for Python 3.9 compatibility
- Example:
```python
def process_text(self, text: str) -> List[Tuple[str, str, int]]:
    ...
```

### Naming Conventions
- Class names: PascalCase (e.g., `TextProcessor`, `QRGenerator`)
- Function and variable names: snake_case (e.g., `generate_qr`, `file_content`)
- Constants: UPPER_CASE (e.g., `MAX_QR_CHARS`, `BLOCK_START_TAG`)
- Private methods: underscore_prefix (e.g., `_calculate_checksum`)
- Module names: snake_case (e.g., `text_processor`, `qr_generator`)

### Error Handling
- Use try/except blocks for operations that might fail
- Include specific exception types where possible (e.g., `FileNotFoundError`, `ValueError`)
- Provide informative error messages to users
- Validate input parameters early in functions
- Example:
```python
if not os.path.exists(input_file):
    print(f"Ошибка: файл '{input_file}' не найден")
    return
```

### Documentation
- All public functions should have docstrings using Google or NumPy style
- Class docstrings should explain purpose, attributes, and methods
- Use Russian language for user-facing messages (as per project convention)
- Use inline comments sparingly but descriptively for complex logic
- Document any non-obvious logic or complex operations

### File Structure Standards
- Each module should be in its own file
- Related classes/functions should be grouped together in the same file
- Main application files (`qr_encoder.py`, `qr_decoder.py`) are entry points
- Service modules should be organized under `/services/`
- Configuration constants go in `config.py`

## Dependencies
- `qrcode>=7.4.0` - QR code generation
- `Pillow>=10.0.0` - Image handling
- `reportlab>=4.0.0` - PDF generation
- `svgwrite>=1.4.3` - SVG support
- `pyzbar>=0.1.9` - QR code decoding
- `python-dateutil>=2.8.0` - Date/time utilities

## Notes for Agents Working on This Project
- This is a CLI tool with interactive input/output
- The project uses Russian for all user-facing messages and comments
- Main entry points: `qr_encoder.py` (encoding) and `qr_decoder.py` (decoding)
- Output directory defaults to `qr_output/`
- Supports text files (UTF-8) and binary files (Base64 encoded)
- Compression methods: auto, ZIP, GZIP, BZ2, LZMA, or none
- QR codes include metadata in two formats:
  - Inside QR: compact format like `BN:1 TOT:25 M:B C:zip #QRS#...data...#QRE#`
  - Above QR: human-readable like `filename.ext | Блок 1/25 | 1234567890`
- When adding new features, test with both text and binary files
- The decoder scans for images in PNG, JPG, JPEG, BMP, GIF, TIFF, WEBP formats
