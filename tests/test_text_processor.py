"""
Tests for services/text_processor.py
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.text_processor import TextProcessor


class TestTextProcessor:
    """Tests for TextProcessor class"""
    
    def test_process_text_basic(self):
        """Basic text processing works"""
        processor = TextProcessor()
        blocks = processor.process_text("hello world")
        
        assert len(blocks) >= 1
        assert blocks[0][2] == 1  # block_num
    
    def test_process_text_empty(self):
        """Empty text returns empty list"""
        processor = TextProcessor()
        blocks = processor.process_text("")
        
        assert blocks == []
    
    def test_process_text_whitespace(self):
        """Whitespace-only text returns empty list"""
        processor = TextProcessor()
        blocks = processor.process_text("   \n\t  ")
        
        assert blocks == []
    
    def test_generate_block_metadata(self):
        """Metadata generation works"""
        processor = TextProcessor()
        
        metadata = processor.generate_block_metadata(
            block_num=1,
            total_blocks=5,
            mode='T',
            compress='zip',
            file_name='test.txt'
        )
        
        assert 'BN:1' in metadata
        assert 'TOT:5' in metadata
        assert 'M:T' in metadata
        assert 'C:zip' in metadata
        assert 'test.txt' in metadata
    
    def test_generate_block_metadata_no_filename(self):
        """Metadata without filename works"""
        processor = TextProcessor()
        
        metadata = processor.generate_block_metadata(
            block_num=2,
            total_blocks=10,
            mode='B',
            compress='gzip',
            file_name=''
        )
        
        assert 'BN:2' in metadata
        assert 'TOT:10' in metadata
        assert 'M:B' in metadata
        assert 'C:gzip' in metadata
    
    def test_combine_blocks_by_order(self):
        """Blocks can be combined in order"""
        processor = TextProcessor()
        
        blocks_data = [
            {'block_num': 1, 'content': 'hello '},
            {'block_num': 2, 'content': 'world'},
        ]
        
        result = processor.combine_blocks_by_order(blocks_data)
        
        assert result == "hello world"
    
    def test_combine_blocks_with_tags(self):
        """Blocks with tags are handled correctly"""
        processor = TextProcessor()
        
        blocks_data = [
            {'block_num': 1, 'content': '#QRSTART:#hello#QREND#'},
            {'block_num': 2, 'content': '#QRSTART:# world#QREND#'},
        ]
        
        result = processor.combine_blocks_by_order(blocks_data)
        
        assert "hello" in result
        assert "world" in result
    
    def test_combine_empty(self):
        """Empty blocks list returns empty string"""
        processor = TextProcessor()
        
        result = processor.combine_blocks_by_order([])
        
        assert result == ""
    
    def test_combine_missing_block_num(self):
        """Blocks without block_num use index"""
        processor = TextProcessor()
        
        blocks_data = [
            {'content': 'first'},
            {'content': 'second'},
        ]
        
        result = processor.combine_blocks_by_order(blocks_data)
        
        assert result == "firstsecond"


class TestTextProcessorBlockSplitting:
    """Tests for block splitting logic"""
    
    def test_long_text_splits(self):
        """Long text is split into multiple blocks"""
        processor = TextProcessor()
        
        # Create text longer than max_qr_chars
        long_text = "a" * 500
        blocks = processor.process_text(long_text)
        
        # Should be split into multiple blocks
        assert len(blocks) > 1
    
    def test_multiple_lines(self):
        """Multiple lines are preserved"""
        processor = TextProcessor()
        
        text = "line1\nline2\nline3"
        blocks = processor.process_text(text)
        
        # At least one block should exist
        assert len(blocks) >= 1
    
    def test_add_block_markers(self):
        """Block markers are added correctly"""
        processor = TextProcessor()
        
        result = processor._add_block_markers("test content")
        
        assert result.startswith(processor.start_tag)
        assert result.endswith(processor.end_tag)
        assert "test content" in result
