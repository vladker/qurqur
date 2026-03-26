"""
Tests for qr_encoder.py CLI
"""

import os
import sys
import pytest
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qr_encoder import parse_args, encode_file


class TestEncoderArgs:
    """Tests for CLI argument parsing"""
    
    def test_parse_args_no_args(self):
        """No arguments returns defaults"""
        sys.argv = ['qr_encoder.py']
        
        args = parse_args()
        
        assert args.file is None
        assert args.output_dir is None
        assert args.version is None
        assert args.error_correction == 'M'
        assert args.style == 'square'
        assert args.compress == 'auto'
        assert args.mode is None
    
    def test_parse_args_with_file(self):
        """File argument is parsed"""
        sys.argv = ['qr_encoder.py', 'test.txt']
        
        args = parse_args()
        
        assert args.file == 'test.txt'
    
    def test_parse_args_output_dir(self):
        """Output directory is parsed"""
        sys.argv = ['qr_encoder.py', '--output-dir', 'output']
        
        args = parse_args()
        
        assert args.output_dir == 'output'
    
    def test_parse_args_short_flags(self):
        """Short flags work"""
        sys.argv = ['qr_encoder.py', 'test.txt', '-o', 'out', '-v', '10', '-e', 'H']
        
        args = parse_args()
        
        assert args.file == 'test.txt'
        assert args.output_dir == 'out'
        assert args.version == 10
        assert args.error_correction == 'H'
    
    def test_parse_args_version(self):
        """Version argument is parsed"""
        sys.argv = ['qr_encoder.py', '--version', '20']
        
        args = parse_args()
        
        assert args.version == 20
    
    def test_parse_args_error_correction(self):
        """Error correction argument is parsed"""
        sys.argv = ['qr_encoder.py', '--error-correction', 'Q']
        
        args = parse_args()
        
        assert args.error_correction == 'Q'
    
    def test_parse_args_style(self):
        """Style argument is parsed"""
        sys.argv = ['qr_encoder.py', '--style', 'circle']
        
        args = parse_args()
        
        assert args.style == 'circle'
    
    def test_parse_args_compress(self):
        """Compression argument is parsed"""
        sys.argv = ['qr_encoder.py', '--compress', 'gzip']
        
        args = parse_args()
        
        assert args.compress == 'gzip'
    
    def test_parse_args_mode(self):
        """Mode argument is parsed"""
        sys.argv = ['qr_encoder.py', '--mode', 'binary']
        
        args = parse_args()
        
        assert args.mode == 'binary'
    
    def test_parse_args_invalid_error_correction(self):
        """Invalid error correction uses default"""
        sys.argv = ['qr_encoder.py', '--error-correction', 'X']
        
        # Should fail - argparse handles this
        with pytest.raises(SystemExit):
            parse_args()


class TestEncoderFunctions:
    """Tests for encoder functions"""
    
    def test_encode_file_basic(self, tmp_path):
        """Basic encoding works"""
        test_file = tmp_path / "test.txt"
        test_file.write_text("hello world")
        
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        
        params = {
            'file': str(test_file),
            'file_name': 'test.txt',
            'content': 'hello world',
            'is_binary': False,
            'compress_method': 'none',
            'version': None,
            'error_correction': 'M',
            'style': 'square',
            'output_dir': str(output_dir)
        }
        
        encode_file(params)
        
        # Check that QR file was created
        qr_files = list(output_dir.glob("*.png"))
        assert len(qr_files) >= 1
    
    def test_encode_file_binary(self, tmp_path):
        """Binary encoding works"""
        test_file = tmp_path / "test.bin"
        test_file.write_bytes(b'\x00\x01\x02\x03')
        
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        
        # For binary we need base64 encoded content
        import base64
        content = base64.b64encode(b'\x00\x01\x02\x03').decode('ascii')
        
        params = {
            'file': str(test_file),
            'file_name': 'test.bin',
            'content': content,
            'is_binary': True,
            'compress_method': 'none',
            'version': None,
            'error_correction': 'M',
            'style': 'square',
            'output_dir': str(output_dir)
        }
        
        encode_file(params)
        
        qr_files = list(output_dir.glob("*.png"))
        assert len(qr_files) >= 1
