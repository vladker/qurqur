#!/usr/bin/env python3
"""
QR Code Decoder - Read QR codes and restore files
Supports any file types: text, binary with decompression.
"""

import sys
import os
import base64
import argparse
import logging

from config import VERSION, DEFAULTS, get_config_value
from services.utils import setup_windows_encoding, safe_input, normalize_path, validate_dir_exists
from services.qr_scanner import QRScanner
from services.qr_collector import QRCollector
from services.compression import CompressionManager


def setup_logging(log_level: str = None, log_file: str = None):
    """Configure logging for the application"""
    if log_level is None:
        log_level = get_config_value('logging_level', 'INFO')
    if log_file is None:
        log_file = get_config_value('logging_file', 'qr_decoder.log')
    
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='QR Code Decoder - Restore files from QR codes'
    )
    parser.add_argument(
        'input', nargs='?', help='Input directory or video file'
    )
    parser.add_argument(
        '--source-type', '-t', default='image',
        choices=['image', 'video'],
        help='Source type (default: image)'
    )
    parser.add_argument(
        '--output', '-o', default=None,
        help='Output file path (default: auto from QR metadata)'
    )
    parser.add_argument(
        '--frames-dir', '-f', default=None,
        help='Directory to save extracted video frames (optional)'
    )
    return parser.parse_args()


def interactive_mode():
    """Interactive source selection"""
    print("Select QR source:")
    print("  [1] Image directory")
    print("  [2] Video file")
    
    source_choice = safe_input("Choice (1/2, default 1): ").strip()
    
    qr_directory = ""
    frames_dir = None
    
    if source_choice == "2":
        video_path = safe_input("\n1. Enter video path: ").strip()
        video_path = normalize_path(video_path)
        
        if not video_path:
            print("Error: path cannot be empty")
            return None, None
        
        if not os.path.exists(video_path):
            print(f"Error: file not found: {video_path}")
            return None, None
        
        scanner = QRScanner()
        ext = os.path.splitext(video_path)[1].lower()
        if ext not in scanner.get_supported_video_formats():
            print(f"Error: unsupported video format: {ext}")
            print(f"Supported: {', '.join(scanner.get_supported_video_formats())}")
            return None, None
        
        save_frames = safe_input("\nSave extracted frames with QR codes? (y/n, default y): ").strip().lower()
        if save_frames != 'n':
            frames_dir = os.path.join(
                os.path.dirname(video_path),
                f"{os.path.splitext(os.path.basename(video_path))[0]}_frames"
            )
        
        return video_path, frames_dir
    
    else:
        qr_directory = safe_input("\n1. Enter QR directory path: ").strip()
        qr_directory = normalize_path(qr_directory)
        
        error = validate_dir_exists(qr_directory)
        if error:
            print(f"Error: {error}")
            return None, None
        
        print(f"\nScanning directory: {qr_directory}\n")
        
        return qr_directory, None


def decode_and_restore(qr_directory: str, frames_dir: str = None, source_type: str = 'image'):
    """Main decoding and restoration logic"""
    scanner = QRScanner()
    
    if source_type == 'video':
        decoded_data = scanner.scan_video(qr_directory, frames_dir)
    else:
        decoded_data = scanner.scan_images(qr_directory)
    
    if not decoded_data:
        print("\nFailed to decode any QR codes")
        return
    
    print(f"\nTotal QR codes decoded: {len(decoded_data)}")
    
    collector = QRCollector()
    blocks = []
    mode_flag = 'T'
    compress_method = 'none'
    total_blocks = 0
    original_file_name = "restored_file"
    
    for item in decoded_data:
        block_data = collector._extract_block_data(item['data'])
        if block_data:
            blocks.append(block_data)
            
            if 'mode' in block_data:
                mode_flag = block_data['mode']
            if 'compress' in block_data:
                compress_method = block_data['compress']
            if 'total_blocks' in block_data:
                total_blocks = block_data['total_blocks']
            
            if original_file_name == "restored_file" and block_data.get('file_name'):
                original_file_name = block_data['file_name']
            
            print(f"  Block {block_data['block_num']}: ID={block_data.get('block_id', 'N/A')}")
        else:
            print(f"  NOT extracted: {item['file']}")
    
    if not blocks:
        print("\nFailed to extract data from decoded QR codes")
        return
    
    blocks.sort(key=lambda b: b.get('block_num', 0))
    
    missing = collector._check_missing_blocks(blocks)
    if missing:
        print(f"\nWarning: missing blocks: {missing}")
        print(f"  Found: {len(blocks)}, Expected: {total_blocks}")
        print("  File may be restored partially!")
    
    if blocks:
        first_block = blocks[0]
        if 'mode' in first_block:
            mode_flag = first_block['mode']
        if 'compress' in first_block:
            compress_method = first_block['compress']
        if 'total_blocks' in first_block:
            total_blocks = first_block['total_blocks']
    
    combined_content = ''.join([b['qr_content'] for b in blocks])
    file_content = combined_content
    
    print(f"\nCombined size: {len(file_content):,} chars")
    
    is_binary = mode_flag == 'B'
    
    print(f"\nParameters:")
    print(f"  File type: {'Binary' if is_binary else 'Text'}")
    print(f"  Compression: {compress_method}")
    print(f"  Total blocks: {total_blocks}")
    print(f"  Data size: {len(file_content):,} chars")
    
    # Decompression
    decompression_failed = False
    if compress_method != 'none':
        try:
            compression = CompressionManager()
            compressed_bytes = base64.b64decode(file_content)
            decompressed_data = compression.decompress_data(compressed_bytes, compress_method)
            
            ratio = compression.get_compression_ratio(len(decompressed_data), len(compressed_bytes))
            print(f"\nDecompression:")
            print(f"  Method: {compression.get_method_name(compress_method)}")
            print(f"  Ratio: {ratio}")
            
            file_content = decompressed_data.decode('utf-8')
            print(f"  Size after decompression: {len(file_content):,} chars")
        except Exception as e:
            print(f"\nWarning: decompression error: {e}")
            decompression_failed = True
            print("  Continuing without decompression (data may be corrupted)...")
    
    # Base64 decode for binary files
    if is_binary:
        try:
            decoded_bytes = base64.b64decode(file_content)
            print(f"\nBase64 decode: {len(decoded_bytes):,} bytes")
            file_data = decoded_bytes
        except Exception as e:
            print(f"\nWarning: Base64 decode error: {e}")
            if decompression_failed:
                print("  Data may have been compressed but failed to decompress")
            print("  Saving as-is (file may be corrupted)...")
            file_data = file_content.encode('utf-8', errors='replace')
    else:
        file_data = file_content.encode('utf-8')
    
    # Output file path
    if '.' in os.path.splitext(original_file_name)[1]:
        default_output = os.path.join(qr_directory, original_file_name)
    else:
        default_ext = '.bin' if is_binary else '.txt'
        default_output = os.path.join(qr_directory, f"{original_file_name}{default_ext}")
    
    # Save choice
    print("\n2. Save method:")
    print("  [1] Save to file")
    print("  [2] Print to console (text only)")
    
    save_choice = safe_input("Choice (1/2, default 1): ").strip()
    
    if save_choice != '2':
        output_file = safe_input(f"3. Output path (default {default_output}): ").strip()
        
        if not output_file:
            output_file = default_output
        
        try:
            output_dir = os.path.dirname(output_file)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            
            if is_binary:
                with open(output_file, 'wb') as f:
                    f.write(file_data)
            else:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(file_content)
            
            file_size = os.path.getsize(output_file)
            print(f"\nDone! File saved: {output_file}")
            print(f"Size: {file_size:,} bytes")
        except Exception as e:
            print(f"\nError saving: {e}")
    else:
        if is_binary:
            print("\nWarning: Binary data cannot be printed to console")
        else:
            print("\n" + "=" * 50)
            print("RESTORED CONTENT:")
            print("=" * 50)
            print(file_content)
            print("=" * 50)
    
    if len(blocks) < len(decoded_data):
        print(f"\nWarning: not all QR codes were processed")
        print(f"  Decoded: {len(decoded_data)}, Processed: {len(blocks)}")


def main():
    """Main entry point"""
    setup_windows_encoding()
    logger = setup_logging()
    
    try:
        args = parse_args()
        
        logger.info(f"QR Code Decoder v{VERSION} started")
        
        print(f"\n+==================================+")
        print(f"|   QR CODE DECODER v{VERSION}           |")
        print("|   Restore any files             |")
        print("+==================================+\n")
        
        # CLI mode
        if args.input:
            input_path = normalize_path(args.input)
            
            if args.source_type == 'video':
                scanner = QRScanner()
                ext = os.path.splitext(input_path)[1].lower()
                if ext not in scanner.get_supported_video_formats():
                    logger.error(f"Unsupported video format: {ext}")
                    print(f"Error: unsupported video format: {ext}")
                    return
                
                decode_and_restore(input_path, args.frames_dir, 'video')
            else:
                error = validate_dir_exists(input_path)
                if error:
                    logger.error(f"Validation error: {error}")
                    print(f"Error: {error}")
                    return
                
                decode_and_restore(input_path, None, 'image')
        
        # Interactive mode
        else:
            logger.info("Starting interactive mode")
            qr_directory, frames_dir = interactive_mode()
            if qr_directory:
                source_type = 'video' if frames_dir else 'image'
                decode_and_restore(qr_directory, frames_dir, source_type)
    
    except KeyboardInterrupt:
        logger.warning("Operation cancelled by user")
        print("\n\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        print(f"\nFatal error: {e}")
        print("Check log file for details")
        sys.exit(1)


if __name__ == "__main__":
    main()
