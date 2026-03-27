"""
Модуль для работы с архивами и сжатием данных
Поддерживает несколько алгоритмов для оптимального сжатия
"""

import io
import zipfile
import gzip
import bz2
import lzma
from typing import Tuple, Optional


class CompressionManager:
    """Управление архивацией и сжатием данных"""
    
    # Методы сжатия
    METHODS = {
        'none': 'Без сжатия',
        'zip': 'ZIP (Deflate)',
        'gzip': 'GZIP',
        'bz2': 'BZ2',
        'lzma': 'LZMA',
        'auto': 'Автовыбор (рекомендуется)'
    }
    
    def __init__(self):
        self._compression_cache = {}  # Кэш для результатов сжатия
    
    def compress_data(self, data: bytes, method: str = 'auto') -> Tuple[bytes, str]:
        """
        Сжимает данные указанным методом
        
        Args:
            data: Исходные байтовые данные
            method: Метод сжатия (none, zip, gzip, bz2, lzma, auto)
            
        Returns:
            Кортеж: (сжатые данные, использованный метод)
        """
        if method == 'none' or method == 'raw':
            return data, 'none'
        
        if method == 'auto':
            # Автовыбор оптимального метода с кэшированием
            return self._auto_compress_optimized(data)
        
        if method == 'zip':
            compressed = self._zip_compress(data)
            return compressed, 'zip'
        
        if method == 'gzip':
            compressed = gzip.compress(data)
            return compressed, 'gzip'
        
        if method == 'bz2':
            compressed = bz2.compress(data)
            return compressed, 'bz2'
        
        if method == 'lzma':
            compressed = lzma.compress(data)
            return compressed, 'lzma'
        
        # По умолчанию без сжатия
        return data, 'none'
    
    def decompress_data(self, data: bytes, method: str) -> bytes:
        """
        Разархивирует данные
        
        Args:
            data: Сжатые данные
            method: Метод сжатия, который использовался
            
        Returns:
            Исходные данные
        """
        if method == 'none' or method == 'raw':
            return data
        
        if method == 'zip':
            return self._zip_decompress(data)
        
        if method == 'gzip':
            return gzip.decompress(data)
        
        if method == 'bz2':
            return bz2.decompress(data)
        
        if method == 'lzma':
            return lzma.decompress(data)
        
        # Пытаемся определить формат автоматически
        return self._auto_decompress(data)
    
    def _auto_compress_optimized(self, data: bytes) -> Tuple[bytes, str]:
        """Автоматически выбирает лучший метод сжатия с оптимизацией"""
        if len(data) == 0:
            return data, 'none'
        
        # Для малых данных используем быстрый gzip вместо тестирования всех методов
        if len(data) < 10000:
            try:
                compressed = gzip.compress(data)
                ratio = len(compressed) / len(data)
                if ratio < 1.0:
                    return compressed, 'gzip'
            except Exception:
                pass
            return data, 'none'
        
        results = []
        
        # Тестируем каждый метод параллельно для больших данных
        methods_to_test = ['zip', 'gzip', 'bz2', 'lzma']
        
        for method in methods_to_test:
            try:
                if method == 'zip':
                    compressed = self._zip_compress(data)
                elif method == 'gzip':
                    compressed = gzip.compress(data)
                elif method == 'bz2':
                    compressed = bz2.compress(data)
                elif method == 'lzma':
                    compressed = lzma.compress(data)
                else:
                    continue
                
                ratio = len(compressed) / len(data)
                results.append((method, compressed, ratio))
                
                # Раннее завершение если нашли хорошее сжатие
                if ratio < 0.5:
                    break
            except Exception:
                continue
        
        # Добавляем вариант без сжатия
        results.append(('none', data, 1.0))
        
        # Выбираем метод с лучшим сжатием
        if results:
            best = min(results, key=lambda x: x[2])
            return best[1], best[0]
        
        return data, 'none'
    
    def _auto_compress(self, data: bytes) -> Tuple[bytes, str]:
        """Устаревший метод автовыбора (для обратной совместимости)"""
        return self._auto_compress_optimized(data)
    
    def _auto_decompress(self, data: bytes) -> bytes:
        """Пытается автоматически определить и разархивировать данные"""
        # Пробуем каждый метод
        methods = ['zip', 'gzip', 'bz2', 'lzma']
        
        for method in methods:
            try:
                if method == 'zip':
                    return self._zip_decompress(data)
                elif method == 'gzip':
                    return gzip.decompress(data)
                elif method == 'bz2':
                    return bz2.decompress(data)
                elif method == 'lzma':
                    return lzma.decompress(data)
            except Exception:
                continue
        
        # Если ничего не подошло, возвращаем как есть
        return data
    
    def _zip_compress(self, data: bytes) -> bytes:
        """Сжатие ZIP методом"""
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr('data.bin', data)
        return buffer.getvalue()
    
    def _zip_decompress(self, data: bytes) -> bytes:
        """Разархивация ZIP"""
        buffer = io.BytesIO(data)
        with zipfile.ZipFile(buffer, 'r') as zf:
            return zf.read('data.bin')
    
    def get_compression_ratio(self, original_size: int, compressed_size: int) -> str:
        """Возвращает строку с процентом сжатия"""
        if original_size == 0:
            return "0%"
        ratio = (1 - compressed_size / original_size) * 100
        sign = "+" if ratio > 0 else ""
        return f"{sign}{ratio:.1f}%"
    
    def get_method_name(self, method: str) -> str:
        """Возвращает человеческое название метода сжатия"""
        return self.METHODS.get(method, method)
