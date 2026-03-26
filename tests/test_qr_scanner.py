"""
Tests for services/qr_scanner.py
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.qr_scanner import QRScanner


class TestQRScanner:
    """Tests for QRScanner class"""
    
    def test_init(self):
        """Scanner initializes correctly"""
        scanner = QRScanner()
        
        assert scanner.image_extensions is not None
        assert scanner.video_extensions is not None
    
    def test_get_supported_image_formats(self):
        """Returns supported image formats"""
        scanner = QRScanner()
        
        formats = scanner.get_supported_image_formats()
        
        assert '.png' in formats
        assert '.jpg' in formats
        assert '.jpeg' in formats
    
    def test_get_supported_video_formats(self):
        """Returns supported video formats"""
        scanner = QRScanner()
        
        formats = scanner.get_supported_video_formats()
        
        assert '.mp4' in formats
        assert '.avi' in formats


class TestQRScannerImages:
    """Tests for image scanning"""
    
    def test_scan_nonexistent_directory(self, tmp_path):
        """Nonexistent directory returns empty list"""
        scanner = QRScanner()
        
        result = scanner.scan_images("/nonexistent")
        
        assert result == []
    
    def test_scan_empty_directory(self, tmp_path):
        """Empty directory returns empty list"""
        scanner = QRScanner()
        
        result = scanner.scan_images(str(tmp_path))
        
        assert result == []


class TestQRScannerVideo:
    """Tests for video scanning"""
    
    def test_scan_nonexistent_video(self):
        """Nonexistent video returns empty list"""
        scanner = QRScanner()
        
        result = scanner.scan_video("/nonexistent/video.mp4")
        
        assert result == []
