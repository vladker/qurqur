"""
Tests for services/compression.py
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.compression import CompressionManager


class TestCompressionManager:
    """Tests for CompressionManager class"""
    
    def test_compress_none(self):
        """No compression returns original data"""
        manager = CompressionManager()
        
        data = b"hello world"
        compressed, method = manager.compress_data(data, 'none')
        
        assert compressed == data
        assert method == 'none'
    
    def test_compress_zip(self):
        """ZIP compression works"""
        manager = CompressionManager()
        
        data = b"hello world test data" * 10
        compressed, method = manager.compress_data(data, 'zip')
        
        assert method == 'zip'
        assert len(compressed) < len(data)
    
    def test_compress_gzip(self):
        """GZIP compression works"""
        manager = CompressionManager()
        
        data = b"hello world test data" * 10
        compressed, method = manager.compress_data(data, 'gzip')
        
        assert method == 'gzip'
        assert len(compressed) < len(data)
    
    def test_compress_bz2(self):
        """BZ2 compression works"""
        manager = CompressionManager()
        
        data = b"hello world test data" * 10
        compressed, method = manager.compress_data(data, 'bz2')
        
        assert method == 'bz2'
        assert len(compressed) < len(data)
    
    def test_compress_lzma(self):
        """LZMA compression works"""
        manager = CompressionManager()
        
        data = b"hello world test data" * 10
        compressed, method = manager.compress_data(data, 'lzma')
        
        assert method == 'lzma'
        assert len(compressed) < len(data)
    
    def test_compress_auto(self):
        """Auto compression selects best method"""
        manager = CompressionManager()
        
        data = b"hello world test data" * 10
        compressed, method = manager.compress_data(data, 'auto')
        
        assert method != 'none'
        assert len(compressed) < len(data)
    
    def test_compress_empty_data(self):
        """Empty data returns unchanged"""
        manager = CompressionManager()
        
        data = b""
        compressed, method = manager.compress_data(data, 'auto')
        
        assert compressed == data
        assert method == 'none'
    
    def test_decompress_zip(self):
        """ZIP decompression works"""
        manager = CompressionManager()
        
        original = b"hello world test data" * 10
        compressed, _ = manager.compress_data(original, 'zip')
        decompressed = manager.decompress_data(compressed, 'zip')
        
        assert decompressed == original
    
    def test_decompress_gzip(self):
        """GZIP decompression works"""
        manager = CompressionManager()
        
        original = b"hello world test data" * 10
        compressed, _ = manager.compress_data(original, 'gzip')
        decompressed = manager.decompress_data(compressed, 'gzip')
        
        assert decompressed == original
    
    def test_decompress_bz2(self):
        """BZ2 decompression works"""
        manager = CompressionManager()
        
        original = b"hello world test data" * 10
        compressed, _ = manager.compress_data(original, 'bz2')
        decompressed = manager.decompress_data(compressed, 'bz2')
        
        assert decompressed == original
    
    def test_decompress_lzma(self):
        """LZMA decompression works"""
        manager = CompressionManager()
        
        original = b"hello world test data" * 10
        compressed, _ = manager.compress_data(original, 'lzma')
        decompressed = manager.decompress_data(compressed, 'lzma')
        
        assert decompressed == original
    
    def test_decompress_none(self):
        """None decompression returns unchanged"""
        manager = CompressionManager()
        
        data = b"hello world"
        result = manager.decompress_data(data, 'none')
        
        assert result == data
    
    def test_get_compression_ratio(self):
        """Compression ratio is calculated correctly"""
        manager = CompressionManager()
        
        ratio = manager.get_compression_ratio(100, 50)
        
        assert "+" in ratio
        assert "50.0%" in ratio
    
    def test_get_compression_ratio_expand(self):
        """Ratio shows expansion when data grows"""
        manager = CompressionManager()
        
        ratio = manager.get_compression_ratio(100, 150)
        
        assert "-" in ratio or "0" in ratio
    
    def test_get_method_name(self):
        """Method names are returned correctly"""
        manager = CompressionManager()
        
        assert "ZIP" in manager.get_method_name('zip')
        assert "GZIP" in manager.get_method_name('gzip')
        assert "BZ2" in manager.get_method_name('bz2')
        assert "LZMA" in manager.get_method_name('lzma')
        assert "Без сжатия" in manager.get_method_name('none')
    
    def test_roundtrip_all_methods(self):
        """All compression methods roundtrip correctly"""
        manager = CompressionManager()
        
        original = b"test data for roundtrip verification"
        methods = ['zip', 'gzip', 'bz2', 'lzma']
        
        for method in methods:
            compressed, _ = manager.compress_data(original, method)
            decompressed = manager.decompress_data(compressed, method)
            assert decompressed == original, f"Roundtrip failed for {method}"


class TestCompressionEdgeCases:
    """Edge case tests for compression"""
    
    def test_very_small_data(self):
        """Very small data is handled"""
        manager = CompressionManager()
        
        data = b"ab"
        compressed, method = manager.compress_data(data, 'auto')
        
        assert method is not None
    
    def test_compress_raw(self):
        """Raw method works like none"""
        manager = CompressionManager()
        
        data = b"test"
        compressed, method = manager.compress_data(data, 'raw')
        
        assert compressed == data
        assert method == 'none'
    
    def test_decompress_raw(self):
        """Raw decompression works"""
        manager = CompressionManager()
        
        data = b"test"
        result = manager.decompress_data(data, 'raw')
        
        assert result == data
