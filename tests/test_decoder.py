"""
Tests for qr_decoder.py CLI
"""

import os
import sys
import pytest
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qr_decoder import parse_args


class TestDecoderArgs:
    """Tests for CLI argument parsing"""
    
    def test_parse_args_no_args(self):
        """No arguments returns defaults"""
        sys.argv = ['qr_decoder.py']
        
        args = parse_args()
        
        assert args.input is None
        assert args.source_type == 'image'
        assert args.output is None
        assert args.frames_dir is None
    
    def test_parse_args_with_input(self):
        """Input argument is parsed"""
        sys.argv = ['qr_decoder.py', 'qr_output']
        
        args = parse_args()
        
        assert args.input == 'qr_output'
    
    def test_parse_args_source_type(self):
        """Source type is parsed"""
        sys.argv = ['qr_decoder.py', 'video.mp4', '--source-type', 'video']
        
        args = parse_args()
        
        assert args.source_type == 'video'
    
    def test_parse_args_short_flags(self):
        """Short flags work"""
        sys.argv = ['qr_decoder.py', 'input', '-t', 'video', '-o', 'output.txt']
        
        args = parse_args()
        
        assert args.input == 'input'
        assert args.source_type == 'video'
        assert args.output == 'output.txt'
    
    def test_parse_args_frames_dir(self):
        """Frames directory is parsed"""
        sys.argv = ['qr_decoder.py', 'video.mp4', '--frames-dir', 'frames']
        
        args = parse_args()
        
        assert args.frames_dir == 'frames'
    
    def test_parse_args_output(self):
        """Output file is parsed"""
        sys.argv = ['qr_decoder.py', 'qr_output', '--output', 'restored.txt']
        
        args = parse_args()
        
        assert args.output == 'restored.txt'
    
    def test_parse_args_invalid_source_type(self):
        """Invalid source type fails"""
        sys.argv = ['qr_decoder.py', '--source-type', 'invalid']
        
        with pytest.raises(SystemExit):
            parse_args()
