import os
import re
from pathlib import Path
from typing import Dict, List, Tuple
from .text_processor import TextProcessor


class QRCollector:
    """Сбор блоков из QR-кодов и восстановление исходного файла"""

    def __init__(self):
        self.text_processor = TextProcessor()
        self.start_tag = "#QRSTART:#"
        self.end_tag = "#QREND#"
        self.block_pattern = re.compile(
            r'FILEPATH:(?P<path>[^ ]+) BLOCKID:(?P<id>[^ ]+) TIME:(?P<time>[^ ]+) CHECKSUM:(?P<checksum>[^ ]+)'
        )

    def collect_qr_files(self, qr_directory: str, output_file: str = None) -> Dict[str, any]:
        """
        Считывает QR-коды из папки и восстанавливает исходный файл

        Args:
            qr_directory: Папка с QR-кодами
            output_file: Путь для сохранения восстановленного файла

        Returns:
            Словарь с результатами: { 'blocks': [], 'missing_blocks': [] }
        """
        results = {
            'blocks': [],
            'missing_blocks': [],
            'errors': []
        }

        if not os.path.exists(qr_directory):
            results['errors'].append(f"Папка {qr_directory} не существует")
            return results

        qr_files = sorted([
            f for f in os.listdir(qr_directory)
            if os.path.isfile(os.path.join(qr_directory, f))
        ])

        for i, qr_file in enumerate(qr_files):
            try:
                file_path = os.path.join(qr_directory, qr_file)
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                block_data = self._extract_block_data(content)
                if block_data:
                    results['blocks'].append(block_data)
                else:
                    results['missing_blocks'].append(i + 1)
                    results['errors'].append(f"Не удалось извлечь данные из {qr_file}")

            except Exception as e:
                results['errors'].append(f"Ошибка при чтении {qr_file}: {str(e)}")

        missing_blocks_info = self._check_missing_blocks(results['blocks'])

        if missing_blocks_info:
            results['missing_blocks'] = missing_blocks_info
            results['errors'].append("Обнаружены недостающие блоки")

        if output_file and results['blocks']:
            combined_text = self.text_processor.combine_blocks_by_order(results['blocks'])
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(combined_text)
                results['output_file'] = output_file
            except Exception as e:
                results['errors'].append(f"Ошибка при сохранении {output_file}: {str(e)}")

        return results

    def _extract_block_data(self, content: str) -> Dict[str, str]:
        """Извлекает метаданные и контент из QR-кода"""
        metadata = None

        start_idx = content.find(self.start_tag)
        end_idx = content.find(self.end_tag)

        if start_idx > -1 and end_idx > start_idx:
            metadata_text = content[start_idx:end_idx]

            match = self.block_pattern.search(metadata_text)
            if match:
                metadata = {
                    'file_path': match.group('path'),
                    'block_id': match.group('id'),
                    'timestamp': match.group('time'),
                    'checksum': match.group('checksum'),
                    'raw_qr_text': content,
                    'qr_content': content[end_idx + len(self.end_tag):].replace('\n', ' ')
                }

                return metadata

        return None

    def collect_from_raw_input(self, raw_text: str) -> Dict[str, any]:
        """
        Считывает данные из сырого ввода

        Args:
            raw_text: Текстовый ввод с метаданными

        Returns:
            Словарь с результатами сбора
        """
        results = {
            'blocks': [],
            'missing_blocks': [],
            'errors': []
        }

        block_pattern = re.compile(r'FILEPATH:(?P<path>[^ ]+) BLOCKID:(?P<id>[^ ]+) TIME:(?P<time>[^ ]+) CHECKSUM:(?P<checksum>[^ ]+)')
        start_tag = "#QRSTART:#"
        end_tag = "#QREND#"

        block_text = raw_text.strip()
        if not block_text:
            results['errors'].append("Пустой ввод")
            return results

        start_idx = block_text.find(start_tag)
        end_idx = block_text.find(end_tag)

        if start_idx > -1 and end_idx > start_idx:
            metadata_text = block_text[start_idx:end_idx]

            match = block_pattern.search(metadata_text)
            if match:
                metadata = {
                    'file_path': match.group('path'),
                    'block_id': match.group('id'),
                    'timestamp': match.group('time'),
                    'checksum': match.group('checksum'),
                    'raw_qr_text': block_text,
                    'qr_content': block_text[end_idx + len(end_tag):].replace('\n', ' ')
                }

                results['blocks'].append(metadata)
                return results

        results['errors'].append("Невозможно распознать формат QR-кода")
        return results

    def _check_missing_blocks(self, blocks: List[Dict[str, str]]) -> List[int]:
        """
        Проверяет наличие всех блоков в последовательности

        Args:
            blocks: Список блоков с метаданными

        Returns:
            Список номеров отсутствующих блоков
        """
        if not blocks:
            return []

        block_ids = set([block['block_id'] for block in blocks])
        all_possible_ids = set([block['block_id'] for block in blocks])

        return []