import os
from pathlib import Path
from typing import List, Dict, Optional


class FileManager:
    """Управление файлами для QR-кодов"""

    def __init__(self):
        pass

    def save_file(self, content: str, file_path: str, create_dirs: bool = True) -> bool:
        """
        Сохраняет контент в файл

        Args:
            content: Контент для сохранения
            file_path: Путь к файлу
            create_dirs: Создавать директории если не существуют

        Returns:
            True если успешно, иначе False
        """
        try:
            path = Path(file_path)
            
            if create_dirs and path.parent:
                path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
        except Exception:
            return False

    def read_file(self, file_path: str) -> Optional[str]:
        """
        Читает контент из файла

        Args:
            file_path: Путь к файлу

        Returns:
            Контент файла или None если ошибка
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return None

    def file_exists(self, file_path: str) -> bool:
        """Проверяет существование файла"""
        return os.path.exists(file_path)

    def get_file_size(self, file_path: str) -> int:
        """Возвращает размер файла в байтах"""
        try:
            return os.path.getsize(file_path)
        except Exception:
            return 0

    def list_files(self, directory: str, extension: Optional[str] = None) -> List[str]:
        """
        Возвращает список файлов в директории

        Args:
            directory: Путь к директории
            extension: Фильтр по расширению (например, '.txt')

        Returns:
            Список имен файлов
        """
        try:
            files = os.listdir(directory)
            if extension:
                files = [f for f in files if f.endswith(extension)]
            return sorted(files)
        except Exception:
            return []

    def create_directory(self, directory: str) -> bool:
        """Создает директорию"""
        try:
            Path(directory).mkdir(parents=True, exist_ok=True)
            return True
        except Exception:
            return False

    def delete_file(self, file_path: str) -> bool:
        """Удаляет файл"""
        try:
            os.remove(file_path)
            return True
        except Exception:
            return False
