"""
Tests for services/qr_generator.py
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.qr_generator import QRGenerator
from PIL import Image


class TestQRGenerator:
    """Tests for QRGenerator class"""
    
    def test_generate_qr_basic(self):
        """Basic QR generation works"""
        generator = QRGenerator()
        
        qr = generator.generate_qr("hello world")
        
        assert qr is not None
        # qrcode returns PilImage which has .convert() method
        assert hasattr(qr, 'convert')
    
    def test_generate_qr_with_version(self):
        """QR with specific version works"""
        generator = QRGenerator()
        
        qr = generator.generate_qr("test", version=5)
        
        assert qr is not None
    
    def test_generate_qr_error_correction_levels(self):
        """All error correction levels work"""
        generator = QRGenerator()
        
        for level in ['L', 'M', 'Q', 'H']:
            qr = generator.generate_qr("test", error_correction=level)
            assert qr is not None
    
    def test_generate_qr_square_style(self):
        """Square style QR works"""
        generator = QRGenerator()
        
        qr = generator.generate_qr("test", style='square')
        
        assert qr is not None
    
    def test_generate_qr_circle_style(self):
        """Circle style QR works"""
        generator = QRGenerator()
        
        qr = generator.generate_qr("test", style='circle')
        
        assert qr is not None
    
    def test_generate_qr_auto_version(self):
        """Auto version detection works"""
        generator = QRGenerator()
        
        qr = generator.generate_qr("a" * 100)
        
        assert qr is not None


class TestQRGeneratorSquare:
    """Tests for square QR generation"""
    
    def test_generate_square_qr(self):
        """Square QR generation works"""
        generator = QRGenerator()
        
        qr = generator._generate_square_qr("test", 1, 'M', False)
        
        assert qr is not None
        assert hasattr(qr, 'convert')


class TestQRGeneratorCircle:
    """Tests for circle QR generation"""
    
    def test_generate_circle_qr(self):
        """Circle QR generation works"""
        generator = QRGenerator()
        
        qr = generator._generate_circle_qr("test", 1, 'M', False)
        
        assert qr is not None
        assert isinstance(qr, Image.Image)


class TestQRGeneratorMetadata:
    """Tests for metadata text addition"""
    
    def test_add_metadata_text_top(self):
        """Metadata text on top works"""
        generator = QRGenerator()
        
        qr = generator.generate_qr("test")
        result = generator.add_metadata_text(qr, "Test | Block 1/5", position='top')
        
        assert result is not None
        assert result.size[1] > qr.size[1]  # Height increased
    
    def test_add_metadata_text_bottom(self):
        """Metadata text on bottom works"""
        generator = QRGenerator()
        
        qr = generator.generate_qr("test")
        result = generator.add_metadata_text(qr, "Test | Block 1/5", position='bottom')
        
        assert result is not None
        assert result.size[1] > qr.size[1]
    
    def test_add_metadata_text_long(self):
        """Long metadata text is handled"""
        generator = QRGenerator()
        
        qr = generator.generate_qr("test")
        long_text = "Very long filename.txt | Block 1/100 | 1234567890 | Extra info"
        result = generator.add_metadata_text(qr, long_text, position='top')
        
        assert result is not None


class TestQRGeneratorSave:
    """Tests for QR save functionality"""
    
    def test_save_qr_png(self, tmp_path):
        """QR can be saved as PNG"""
        generator = QRGenerator()
        
        qr = generator.generate_qr("test")
        qr_rgb = qr.convert('RGB')
        output_path = tmp_path / "test.png"
        
        result = generator.save_qr(qr_rgb, str(output_path), "PNG")
        
        assert result is True
        assert output_path.exists()
    
    def test_save_qr_jpg(self, tmp_path):
        """QR can be saved as JPEG"""
        generator = QRGenerator()
        
        qr = generator.generate_qr("test")
        output_path = tmp_path / "test.jpg"
        
        result = generator.save_qr(qr, str(output_path), "JPEG")
        
        assert result is True
        assert output_path.exists()
    
    def test_save_qr_invalid_format(self, tmp_path):
        """Invalid format returns False"""
        generator = QRGenerator()
        
        qr = generator.generate_qr("test")
        output_path = tmp_path / "test.invalid"
        
        result = generator.save_qr(qr, str(output_path), "INVALID")
        
        assert result is False


class TestQRGeneratorMerge:
    """Tests for QR merging functionality"""
    
    def test_merge_qr_images(self, tmp_path):
        """Multiple QR images can be merged"""
        generator = QRGenerator()
        
        qr1 = generator.generate_qr("test1")
        qr2 = generator.generate_qr("test2")
        
        output_path = tmp_path / "merged.png"
        
        result = generator.merge_qr_images(
            [qr1, qr2],
            2,
            str(output_path),
            ["test1", "test2"]
        )
        
        assert result is True
        assert output_path.exists()
    
    def test_merge_empty(self, tmp_path):
        """Empty list returns False"""
        generator = QRGenerator()
        
        output_path = tmp_path / "merged.png"
        
        result = generator.merge_qr_images([], 2, str(output_path), [])
        
        assert result is False
