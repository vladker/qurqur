#!/usr/bin/env python3
"""
Конфигурационные константы проекта QR Code Encoder/Decoder
"""

# Версия приложения
VERSION = "2.0"

# Поддерживаемые текстовые расширения для автоопределения
TEXT_EXTENSIONS = {
    '.txt', '.md', '.py', '.js', '.ts', '.html', '.css', '.json',
    '.xml', '.yaml', '.yml', '.csv', '.log', '.ini', '.cfg', '.conf',
    '.sh', '.bat', '.cmd', '.ps1', '.sql', '.rst', '.rtf'
}

# Методы сжатия
COMPRESSION_METHODS = {
    '1': 'auto',
    '2': 'zip',
    '3': 'gzip',
    '4': 'bz2',
    '5': 'lzma',
    '6': 'none'
}

# Поддерживаемые форматы изображений для декодера
IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp'}

# Настройки по умолчанию
DEFAULTS = {
    'output_dir': 'qr_output',
    'qr_version': None,  # Автоподбор
    'error_correction': 'M',
    'style': 'square',
    'metadata_position': 'top',
    'compress_method': 'auto',
    'encode_mode': 'auto',  # 'text' или 'binary'
}

# Максимальное количество символов в блоке QR-кода
MAX_QR_BLOCK_CHARS = 200

# Теги для маркировки блоков
BLOCK_START_TAG = "#QRS#"
BLOCK_END_TAG = "#QRE#"
