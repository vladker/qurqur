#!/usr/bin/env python3
"""
Конфигурационные константы проекта QR Code Encoder/Decoder
Поддерживает внешнюю конфигурацию через config.json
"""

import os
import json
from typing import Any, Dict, Optional

# Версия приложения
VERSION = "2.1"

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

# Поддерживаемые форматы видео для декодера
VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv'}

# Настройки по умолчанию
DEFAULTS: Dict[str, Any] = {
    'output_dir': 'qr_output',
    'qr_version': None,  # Автоподбор
    'error_correction': 'M',
    'style': 'square',
    'metadata_position': 'top',
    'compress_method': 'auto',
    'encode_mode': 'auto',  # 'text' или 'binary'
    'max_qr_block_chars': 2000,  # Увеличенный лимит для QR-кода версии 40
    'logging_level': 'INFO',
    'logging_file': 'qr_encoder.log',
}

# Максимальное количество символов в блоке QR-кода
# Версия 40 с коррекцией M вмещает ~2331 байт, с учетом метаданных (~100 символов)
MAX_QR_BLOCK_CHARS = 2000  # Безопасный лимит для Base64 данных

# Теги для маркировки блоков (единый формат для всего проекта)
BLOCK_START_TAG = "#QRS#"
BLOCK_END_TAG = "#QRE#"


def load_external_config(config_path: str = "config.json") -> Dict[str, Any]:
    """
    Загружает внешнюю конфигурацию из JSON файла
    
    Args:
        config_path: Путь к файлу конфигурации
        
    Returns:
        Словарь с конфигурацией или пустой словарь если файл не найден
    """
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Failed to load config from {config_path}: {e}")
    return {}


def get_config_value(key: str, default: Any = None) -> Any:
    """
    Получает значение конфигурации с приоритетом: внешняя конфигурация > DEFAULTS
    
    Args:
        key: Ключ конфигурации
        default: Значение по умолчанию
        
    Returns:
        Значение конфигурации
    """
    external_config = load_external_config()
    return external_config.get(key, DEFAULTS.get(key, default))
