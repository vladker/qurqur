#!/usr/bin/env python3
"""
QR Code File Encoder - Main CLI
Interactive CLI application for generating QR codes from any file type.
Supports text, binary files with compression.
"""

import sys
import os
import base64
import argparse

from config import VERSION, COMPRESSION_METHODS, DEFAULTS
from services.utils import setup_windows_encoding, safe_input, normalize_path, validate_file_exists, get_file_info
from services.file_detector import FileDetector
from services.text_processor import TextProcessor
from services.qr_generator import QRGenerator
from services.compression import CompressionManager


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='QR Code File Encoder - Generate QR codes from files'
    )
    parser.add_argument(
        'file', nargs='?', help='Input file path'
    )
    parser.add_argument(
        '--output-dir', '-o', default=None,
        help='Output directory for QR codes (default: qr_output)'
    )
    parser.add_argument(
        '--version', '-v', type=int, default=None,
        help='QR code version (1-40, auto if not specified)'
    )
    parser.add_argument(
        '--error-correction', '-e', default='M',
        choices=['L', 'M', 'Q', 'H'],
        help='Error correction level (default: M)'
    )
    parser.add_argument(
        '--style', '-s', default='square',
        choices=['square', 'circle'],
        help='QR code style (default: square)'
    )
    parser.add_argument(
        '--compress', '-c', default='auto',
        choices=['auto', 'zip', 'gzip', 'bz2', 'lzma', 'none'],
        help='Compression method (default: auto)'
    )
    parser.add_argument(
        '--mode', '-m', default=None,
        choices=['text', 'binary'],
        help='Encoding mode (auto-detected if not specified)'
    )
    return parser.parse_args()


def interactive_mode():
    """Interactive file selection and encoding"""
    input_file = safe_input("1. Enter file path: ").strip()
    input_file = normalize_path(input_file)
    
    error = validate_file_exists(input_file)
    if error:
        print(f"Error: {error}")
        return
    
    file_info = get_file_info(input_file)
    file_size = file_info['size']
    file_ext = file_info['ext']
    file_name = file_info['name']
    
    print(f"\nFile loaded: {input_file}")
    print(f"Size: {file_size:,} bytes")
    print(f"Type: {file_ext or 'no extension'}")
    
    detector = FileDetector()
    is_text = detector.detect(input_file)
    
    print(f"\n2. Encoding mode:")
    if is_text:
        print("  [1] Text (UTF-8)")
        print("  [2] Binary (Base64, universal)")
        default_mode = '1'
    else:
        print("  [1] Binary (Base64, recommended)")
        print("  [2] Text (only if file is text)")
        default_mode = '1'
    
    encode_mode = safe_input(f"Choice (1/2, default {default_mode}): ").strip()
    if not encode_mode:
        encode_mode = default_mode
    
    if is_text:
        is_binary = encode_mode == '2'
    else:
        is_binary = encode_mode == '1'
    
    # Read file
    try:
        if is_binary:
            with open(input_file, 'rb') as f:
                file_data = f.read()
            file_content = base64.b64encode(file_data).decode('ascii')
            print(f"Data encoded to Base64: {len(file_content)} chars")
        else:
            with open(input_file, 'r', encoding='utf-8') as f:
                file_content = f.read()
            print(f"Text loaded: {len(file_content)} chars")
    except Exception as e:
        print(f"Error reading file: {e}")
        print("Trying as binary...")
        with open(input_file, 'rb') as f:
            file_data = f.read()
        file_content = base64.b64encode(file_data).decode('ascii')
        is_binary = True
        print(f"Data encoded to Base64: {len(file_content)} chars")
    
    # Compression
    print("\n3. Compression:")
    print("  [1] Auto (recommended)")
    print("  [2] ZIP")
    print("  [3] GZIP")
    print("  [4] BZ2")
    print("  [5] LZMA")
    print("  [6] None")
    
    compress_choice = safe_input("Choice (1-6, default 1): ").strip()
    compress_method = COMPRESSION_METHODS.get(compress_choice, 'auto')
    
    compression = CompressionManager()
    
    original_size = len(file_content.encode('utf-8'))
    if is_binary or original_size > 10000:
        file_bytes = file_content.encode('utf-8')
        compressed_data, used_method = compression.compress_data(file_bytes, compress_method)
        compressed_content = base64.b64encode(compressed_data).decode('ascii')
        
        ratio = compression.get_compression_ratio(original_size, len(compressed_content.encode('utf-8')))
        
        print(f"\nCompression:")
        print(f"  Method: {compression.get_method_name(used_method)}")
        print(f"  Original: {original_size:,} bytes")
        print(f"  Compressed: {len(compressed_content.encode('utf-8')):,} bytes (base64)")
        print(f"  Ratio: {ratio}")
        
        file_content = compressed_content
        compress_method = used_method
    else:
        compress_method = 'none'
        print("\nCompression skipped (small size)")
    
    # QR settings
    print("\n4. QR version (1-40, Enter for auto): ", end='')
    version_input = safe_input().strip()
    version = None
    if version_input:
        version = int(version_input)
        if version < 1 or version > 40:
            print("Version must be 1-40. Using auto.")
            version = None
    
    print("5. Error correction (L/M/Q/H, default M): ", end='')
    error_correction = safe_input().strip().upper()
    if not error_correction:
        error_correction = "M"
    
    print("6. Style (square/circle, default square): ", end='')
    style = safe_input().strip().lower()
    if not style:
        style = "square"
    
    return {
        'file': input_file,
        'file_name': file_name,
        'content': file_content,
        'is_binary': is_binary,
        'compress_method': compress_method,
        'version': version,
        'error_correction': error_correction,
        'style': style,
        'output_dir': DEFAULTS['output_dir']
    }


def encode_file(params: dict):
    """Main encoding logic"""
    processor = TextProcessor()
    generator = QRGenerator()
    
    blocks = processor.process_text(params['content'])
    total_blocks = len(blocks)
    
    timestamp = str(int(os.path.getmtime(params['file'])))
    mode_flag = 'B' if params['is_binary'] else 'T'
    
    output_dir = params['output_dir']
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\nGenerating QR codes...")
    print(f"Total blocks: {total_blocks}")
    
    for i, (block_id, block_content, block_num) in enumerate(blocks):
        qr_metadata = processor.generate_block_metadata(
            block_num, total_blocks, mode_flag, params['compress_method'], params['file_name']
        )
        full_data = f"{qr_metadata} {block_content}"
        
        qr_image = generator.generate_qr(
            data=full_data,
            version=params['version'],
            error_correction=params['error_correction'],
            style=params['style']
        )
        
        header_text = f"{params['file_name']} | Block {block_num}/{total_blocks} | {timestamp}"
        qr_with_text = generator.add_metadata_text(qr_image, header_text, position='top')
        
        output_path = f"{output_dir}/qr_{block_num}.png"
        generator.save_qr(qr_with_text, output_path, "PNG")
        print(f"  Created: {output_path} (block {block_num})")
    
    print(f"\nDone! Total QR codes: {len(blocks)}")
    print(f"Output directory: {os.path.abspath(output_dir)}")
    
    print(f"\nTo restore the file use:")
    print(f"  python qr_decoder.py")
    print(f"  and specify directory: {os.path.abspath(output_dir)}")


def main():
    """Main entry point"""
    setup_windows_encoding()
    
    args = parse_args()
    
    print(f"\n╔══════════════════════════════╗")
    print(f"║   QR CODE FILE ENCODER v{VERSION}   ║")
    print("║   Support for any files       ║")
    print("╚══════════════════════════════╝\n")
    
    # CLI mode
    if args.file:
        input_file = normalize_path(args.file)
        error = validate_file_exists(input_file)
        if error:
            print(f"Error: {error}")
            return
        
        file_info = get_file_info(input_file)
        
        print(f"File: {input_file}")
        print(f"Size: {file_info['size']:,} bytes")
        
        # Detect file type
        detector = FileDetector()
        is_binary = args.mode == 'binary'
        if args.mode is None:
            is_binary = not detector.detect(input_file)
        
        # Read file
        if is_binary:
            with open(input_file, 'rb') as f:
                file_data = f.read()
            file_content = base64.b64encode(file_data).decode('ascii')
        else:
            with open(input_file, 'r', encoding='utf-8') as f:
                file_content = f.read()
        
        # Compression
        compression = CompressionManager()
        original_size = len(file_content.encode('utf-8'))
        compress_method = args.compress
        
        if is_binary or original_size > 10000:
            file_bytes = file_content.encode('utf-8')
            compressed_data, used_method = compression.compress_data(file_bytes, compress_method)
            compressed_content = base64.b64encode(compressed_data).decode('ascii')
            file_content = compressed_content
            compress_method = used_method
        
        params = {
            'file': input_file,
            'file_name': file_info['name'],
            'content': file_content,
            'is_binary': is_binary,
            'compress_method': compress_method,
            'version': args.version,
            'error_correction': args.error_correction,
            'style': args.style,
            'output_dir': args.output_dir or DEFAULTS['output_dir']
        }
        
        encode_file(params)
    
    # Interactive mode
    else:
        params = interactive_mode()
        if params:
            encode_file(params)


if __name__ == "__main__":
    main()
