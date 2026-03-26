"""
Tests for services/file_detector.py
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.file_detector import FileDetector


class TestFileDetector:
    """Tests for FileDetector class"""
    
    def test_text_extension(self, tmp_path):
        """Python file is detected as text"""
        test_file = tmp_path / "script.py"
        test_file.write_text("print('hello')")
        
        detector = FileDetector()
        assert detector.detect(str(test_file)) is True
    
    def test_binary_extension(self, tmp_path):
        """PNG file is detected as binary"""
        test_file = tmp_path / "image.png"
        test_file.write_bytes(b'\x89PNG\r\n\x1a\n\x00\x00\x00')
        
        detector = FileDetector()
        assert detector.detect(str(test_file)) is False
    
    def test_text_with_null_byte(self, tmp_path):
        """File with null byte is binary"""
        test_file = tmp_path / "mixed.bin"
        test_file.write_bytes(b'hello\x00world')
        
        detector = FileDetector()
        assert detector.detect(str(test_file)) is False
    
    def test_utf8_text(self, tmp_path):
        """UTF-8 encoded file is text"""
        test_file = tmp_path / "utf8.txt"
        test_file.write_text("Привет мир")
        
        detector = FileDetector()
        assert detector.detect(str(test_file)) is True
    
    def test_get_file_type_text(self, tmp_path):
        """get_file_type returns 'text' for text files"""
        test_file = tmp_path / "data.txt"
        test_file.write_text("hello")
        
        detector = FileDetector()
        assert detector.get_file_type(str(test_file)) == "text"
    
    def test_get_file_type_binary(self, tmp_path):
        """get_file_type returns 'binary' for binary files"""
        test_file = tmp_path / "data.bin"
        test_file.write_bytes(b'\x00\x01\x02')
        
        detector = FileDetector()
        assert detector.get_file_type(str(test_file)) == "binary"
    
    def test_empty_file_is_text(self, tmp_path):
        """Empty file is treated as text"""
        test_file = tmp_path / "empty.txt"
        test_file.write_text("")
        
        detector = FileDetector()
        assert detector.detect(str(test_file)) is True
    
    def test_json_file(self, tmp_path):
        """JSON file is detected as text"""
        test_file = tmp_path / "data.json"
        test_file.write_text('{"key": "value"}')
        
        detector = FileDetector()
        assert detector.detect(str(test_file)) is True
    
    def test_html_file(self, tmp_path):
        """HTML file is detected as text"""
        test_file = tmp_path / "page.html"
        test_file.write_text("<html><body></body></html>")
        
        detector = FileDetector()
        assert detector.detect(str(test_file)) is True
