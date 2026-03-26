"""
QR code scanning utilities for images and videos
"""

import os
from typing import List, Dict, Optional
from config import IMAGE_EXTENSIONS, VIDEO_EXTENSIONS


class QRScanner:
    """Scan QR codes from images and videos"""
    
    def __init__(self):
        self.image_extensions = IMAGE_EXTENSIONS
        self.video_extensions = VIDEO_EXTENSIONS
    
    def scan_images(self, qr_directory: str) -> List[Dict[str, str]]:
        """
        Scan QR codes from images in directory
        
        Args:
            qr_directory: Directory containing QR images
            
        Returns:
            List of decoded data dicts
        """
        try:
            import cv2
            from pyzbar.pyzbar import decode
            from PIL import Image
            use_cv = True
        except ImportError:
            try:
                from pyzbar.pyzbar import decode
                from PIL import Image
                use_cv = False
            except ImportError:
                print("Error: Missing pyzbar or Pillow. Install: pip install pyzbar Pillow")
                return []
        
        decoded_data = []
        
        if not os.path.exists(qr_directory):
            print(f"Directory '{qr_directory}' does not exist")
            return []
        
        files = [
            f for f in os.listdir(qr_directory)
            if os.path.isfile(os.path.join(qr_directory, f))
            and os.path.splitext(f)[1].lower() in self.image_extensions
        ]
        
        if not files:
            print(f"No images found ({', '.join(self.image_extensions)})")
            return []
        
        print(f"Found images: {len(files)}")
        
        for i, filename in enumerate(sorted(files), 1):
            file_path = os.path.join(qr_directory, filename)
            try:
                if use_cv:
                    img = cv2.imread(file_path)
                    if img is None:
                        print(f"[{i}/{len(files)}] {filename}: failed to read")
                        continue
                    qr_codes = self._decode_zbar(decode, img)
                else:
                    img = Image.open(file_path)
                    qr_codes = self._decode_zbar(decode, img)
                
                if qr_codes:
                    for qr in qr_codes:
                        data = qr.data.decode('utf-8')
                        decoded_data.append({
                            'file': filename,
                            'data': data
                        })
                        print(f"[{i}/{len(files)}] {filename}: decoded ({len(data)} chars)")
                else:
                    print(f"[{i}/{len(files)}] {filename}: no QR found")
                    
            except Exception as e:
                print(f"[{i}/{len(files)}] {filename}: error - {e}")
        
        return decoded_data
    
    def _decode_zbar(self, decode_func, img):
        """Decode QR codes with suppressed output"""
        import sys
        from io import open as io_open
        
        with open(os.devnull, 'w') as devnull:
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            sys.stdout = devnull
            sys.stderr = devnull
            try:
                return decode_func(img)
            finally:
                sys.stdout = old_stdout
                sys.stderr = old_stderr
    
    def scan_video(self, video_path: str, output_dir: str = None) -> List[Dict[str, str]]:
        """
        Scan QR codes from video file
        
        Args:
            video_path: Path to video file
            output_dir: Directory to save extracted frames (optional)
            
        Returns:
            List of decoded data dicts
        """
        try:
            import cv2
            from pyzbar.pyzbar import decode
        except ImportError:
            print("Error: opencv-python and pyzbar required. Install: pip install opencv-python pyzbar")
            return []
        
        if not os.path.exists(video_path):
            print(f"Video file not found: {video_path}")
            return []
        
        frames_dir = output_dir
        if frames_dir is None:
            video_name = os.path.splitext(os.path.basename(video_path))[0]
            frames_dir = os.path.join(os.path.dirname(video_path), f"{video_name}_frames")
        
        os.makedirs(frames_dir, exist_ok=True)
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"Failed to open video: {video_path}")
            return []
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        duration = total_frames / fps if fps > 0 else 0
        
        print(f"\nVideo: {os.path.basename(video_path)}")
        print(f"  Frames: {total_frames}, FPS: {fps:.2f}, Duration: {duration:.1f}s")
        print(f"  Frames will be saved to: {frames_dir}\n")
        
        decoded_data = []
        seen_qr_data = set()
        frame_count = 0
        saved_count = 0
        last_progress = -1
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            progress = (frame_count * 10) // total_frames
            if progress > last_progress:
                print(f"Processing: {progress * 10}% ({frame_count}/{total_frames} frames)")
                last_progress = progress
            
            qr_codes = self._decode_zbar(decode, frame)
            
            if qr_codes:
                for qr in qr_codes:
                    data = qr.data.decode('utf-8')
                    
                    if data in seen_qr_data:
                        continue
                    
                    seen_qr_data.add(data)
                    decoded_data.append({
                        'file': f"frame_{frame_count:05d}.jpg",
                        'data': data
                    })
                    print(f"  [Frame {frame_count}] Decoded QR ({len(data)} chars)")
                
                frame_path = os.path.join(frames_dir, f"frame_{frame_count:05d}.jpg")
                cv2.imwrite(frame_path, frame)
                saved_count += 1
        
        cap.release()
        
        print(f"\nProcessing complete:")
        print(f"  Frames processed: {frame_count}")
        print(f"  QR codes found: {len(decoded_data)}")
        print(f"  Frames saved: {saved_count}")
        
        return decoded_data
    
    def get_supported_image_formats(self) -> set:
        """Get supported image formats"""
        return self.image_extensions
    
    def get_supported_video_formats(self) -> set:
        """Get supported video formats"""
        return self.video_extensions
