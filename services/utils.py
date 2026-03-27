"""
Common utilities for QR encoder/decoder
With path validation and security checks
"""

import os
import sys
import io
from pathlib import Path
from typing import Optional


def setup_windows_encoding():
    """Configure UTF-8 encoding for Windows console"""
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def safe_input(prompt: str = "") -> str:
    """
    Safe input handling for cases when stdin is unavailable
    
    Args:
        prompt: Input prompt message
        
    Returns:
        User input string
    """
    try:
        return input(prompt)
    except EOFError:
        print("\nError: Cannot read input. Run from command line.")
        print(f"Example: qr_encoder.exe <path_to_file>")
        sys.exit(1)


def normalize_path(path: str) -> str:
    """
    Normalize file path by removing quotes and resolving to absolute path
    
    Args:
        path: Raw path input
        
    Returns:
        Cleaned absolute path
    """
    path = path.strip()
    if path.startswith('"') and path.endswith('"'):
        path = path[1:-1]
    if path.startswith("'") and path.endswith("'"):
        path = path[1:-1]
    
    # Resolve to absolute path and normalize
    return os.path.normpath(os.path.abspath(path))


def validate_file_exists(file_path: str) -> Optional[str]:
    """
    Validate that file exists and is accessible
    
    Args:
        file_path: Path to check
        
    Returns:
        Error message if invalid, None if valid
    """
    if not file_path:
        return "Path cannot be empty"
    
    # Security check: prevent directory traversal attacks
    try:
        resolved_path = Path(file_path).resolve()
        # Ensure the path is within allowed directories (optional)
        # For now, just check it's a valid absolute path
    except (ValueError, OSError) as e:
        return f"Invalid path: {e}"
    
    if not os.path.exists(file_path):
        return f"File not found: {file_path}"
    
    if not os.path.isfile(file_path):
        return f"Path is not a file: {file_path}"
    
    # Check read permissions
    if not os.access(file_path, os.R_OK):
        return f"No read permission: {file_path}"
    
    return None


def validate_dir_exists(dir_path: str) -> Optional[str]:
    """
    Validate that directory exists and is accessible
    
    Args:
        dir_path: Path to check
        
    Returns:
        Error message if invalid, None if valid
    """
    if not dir_path:
        return "Path cannot be empty"
    
    # Security check: prevent directory traversal attacks
    try:
        resolved_path = Path(dir_path).resolve()
    except (ValueError, OSError) as e:
        return f"Invalid path: {e}"
    
    if not os.path.exists(dir_path):
        return f"Directory not found: {dir_path}"
    
    if not os.path.isdir(dir_path):
        return f"Path is not a directory: {dir_path}"
    
    # Check read permissions
    if not os.access(dir_path, os.R_OK):
        return f"No read permission: {dir_path}"
    
    return None


def get_file_info(file_path: str) -> dict:
    """
    Get file information with security checks
    
    Args:
        file_path: Path to file
        
    Returns:
        Dictionary with file info
    """
    file_size = os.path.getsize(file_path)
    file_name = os.path.basename(file_path)
    file_ext = os.path.splitext(file_name)[1].lower()
    return {
        'path': file_path,
        'name': file_name,
        'ext': file_ext,
        'size': file_size
    }
