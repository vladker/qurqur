# AGENTS.md

## Project Overview
This is a QR Code File Encoder CLI application that generates QR codes from text files with customizable parameters.

## Build Commands
```bash
# Install dependencies
pip install -r requirements.txt

# Run the main application
python qr_encoder.py

# Run tests (if any exist)
pytest
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
# Run all tests (if applicable)
pytest

# Run a single test file
pytest test_file.py

# Run specific test function
pytest test_file.py::test_function_name

# Run with coverage
pytest --cov=.
```

## Code Style Guidelines

### Imports
- Import standard library modules first, then third-party libraries, then local modules
- Example:
```python
import os
import sys
from typing import List, Dict

import qrcode
from PIL import Image

from services.text_processor import TextProcessor
```

### Formatting
- Follow PEP 8 style guide
- Use 4 spaces for indentation (no tabs)
- Limit lines to 79 characters
- Use blank lines to separate functions and classes
- Add a space after commas, colons, and semicolons

### Types
- Use type hints for all function parameters and return values
- Example:
```python
def process_text(self, text: str) -> List[Tuple[str, str, int]]:
    ...
```

### Naming Conventions
- Class names: PascalCase (e.g., `TextProcessor`)
- Function and variable names: snake_case (e.g., `generate_qr`)
- Constants: UPPER_CASE (e.g., `MAX_QR_CHARS`)
- Private methods: underscore_prefix (e.g., `_calculate_checksum`)

### Error Handling
- Use try/except blocks for operations that might fail
- Include specific exception types where possible
- Log errors appropriately and provide informative messages to users
- Validate input parameters early in functions

### Documentation
- All public functions should have docstrings using Google or NumPy style
- Class docstrings should explain purpose, attributes, and methods
- Use inline comments sparingly but descriptively
- Document any non-obvious logic or complex operations

### File Structure Standards
- Each module should be in its own file
- Related classes/functions should be grouped together in the same file
- Main application files (like `qr_encoder.py`) are the entry point
- Service modules should be organized under `/services/`

## Notes for Agents Working on This Project
This project is a Python CLI tool with no tests currently, so testing will need to be implemented.
The code uses:
- qrcode library for generating QR codes
- Pillow (PIL) for image handling  
- reportlab for PDF generation
- svgwrite for SVG support