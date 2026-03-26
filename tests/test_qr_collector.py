"""
Tests for services/qr_collector.py
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.qr_collector import QRCollector


class TestQRCollector:
    """Tests for QRCollector class"""
    
    def test_extract_block_data_basic(self):
        """Basic block data extraction works"""
        collector = QRCollector()
        
        # Create test data matching the format
        content = "FN:test.txt BN:1 TOT:5 M:T C:zip #QRS#hello world#QRE#"
        
        result = collector._extract_block_data(content)
        
        assert result is not None
        assert result['block_num'] == 1
        assert result['total_blocks'] == 5
        assert result['mode'] == 'T'
        assert result['compress'] == 'zip'
        assert result['file_name'] == 'test.txt'
        assert 'hello world' in result['qr_content']
    
    def test_extract_block_data_no_filename(self):
        """Block without filename works"""
        collector = QRCollector()
        
        content = "BN:2 TOT:10 M:B C:gzip #QRS#test#QRE#"
        
        result = collector._extract_block_data(content)
        
        assert result is not None
        assert result['block_num'] == 2
        assert result['total_blocks'] == 10
        assert result['mode'] == 'B'
        assert result['file_name'] == ''
    
    def test_extract_block_data_no_match(self):
        """Invalid format returns None"""
        collector = QRCollector()
        
        content = "not a valid qr format"
        
        result = collector._extract_block_data(content)
        
        assert result is None
    
    def test_extract_block_data_empty(self):
        """Empty content returns None"""
        collector = QRCollector()
        
        result = collector._extract_block_data("")
        
        assert result is None
    
    def test_check_missing_blocks_no_missing(self):
        """No missing blocks returns empty list"""
        collector = QRCollector()
        
        blocks = [
            {'block_num': 1},
            {'block_num': 2},
            {'block_num': 3},
        ]
        
        result = collector._check_missing_blocks(blocks)
        
        assert result == []
    
    def test_check_missing_blocks_with_gaps(self):
        """Missing blocks are detected"""
        collector = QRCollector()
        
        blocks = [
            {'block_num': 1},
            {'block_num': 3},  # 2 is missing
        ]
        
        result = collector._check_missing_blocks(blocks)
        
        assert 2 in result
    
    def test_check_missing_blocks_empty(self):
        """Empty blocks returns empty list"""
        collector = QRCollector()
        
        result = collector._check_missing_blocks([])
        
        assert result == []
    
    def test_check_missing_blocks_unsorted(self):
        """Blocks can be unsorted"""
        collector = QRCollector()
        
        blocks = [
            {'block_num': 3},
            {'block_num': 1},
        ]
        
        result = collector._check_missing_blocks(blocks)
        
        # 2 should be missing
        assert 2 in result


class TestQRCollectorCollectQRFiles:
    """Tests for collect_qr_files method"""
    
    def test_nonexistent_directory(self, tmp_path):
        """Nonexistent directory returns error"""
        collector = QRCollector()
        
        result = collector.collect_qr_files("/nonexistent")
        
        assert len(result['errors']) > 0
    
    def test_empty_directory(self, tmp_path):
        """Empty directory returns no blocks"""
        collector = QRCollector()
        
        result = collector.collect_qr_files(str(tmp_path))
        
        assert result['blocks'] == []


class TestQRCollectorRawInput:
    """Tests for collect_from_raw_input method"""
    
    def test_empty_input(self):
        """Empty input returns error"""
        collector = QRCollector()
        
        result = collector.collect_from_raw_input("")
        
        assert len(result['errors']) > 0
    
    def test_invalid_format(self):
        """Invalid format returns error"""
        collector = QRCollector()
        
        result = collector.collect_from_raw_input("invalid data")
        
        assert len(result['errors']) > 0
