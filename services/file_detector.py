"""
File type detection utilities
"""

import os
from config import TEXT_EXTENSIONS


class FileDetector:
    """Detect file type (text or binary)"""
    
    def __init__(self):
        self.text_extensions = TEXT_EXTENSIONS
    
    def detect(self, file_path: str) -> bool:
        """
        Detect if file is text or binary
        
        Args:
            file_path: Path to file
            
        Returns:
            True if text file, False if binary
        """
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext in self.text_extensions:
            return True
        
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            return True
        
        try:
            with open(file_path, 'rb') as f:
                header = f.read(1024)
            
            if b'\x00' in header:
                return False
            
            try:
                header.decode('utf-8')
                return True
            except UnicodeDecodeError:
                return False
        except Exception:
            return False
    
    def get_file_type(self, file_path: str) -> str:
        """
        Get human-readable file type
        
        Args:
            file_path: Path to file
            
        Returns:
            'text' or 'binary'
        """
        return 'text' if self.detect(file_path) else 'binary'
