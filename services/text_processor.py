import re
import os
from typing import List, Tuple
import uuid


class TextProcessor:
    """Обработка текста для разделения на QR-кодные блоки"""

    def __init__(self):
        self.max_qr_chars = 2000
        self.start_tag = "#QRSTART:#"
        self.end_tag = "#QREND#"

    def process_text(self, text: str) -> List[Tuple[str, str, int]]:
        """
        Разбивает текст на блоки, вставляет метки начала и конца

        Returns:
            Список кортежей: (block_id, content, block_number)
        """
        if not text.strip():
            return []

        raw_blocks = self._split_into_blocks(text)
        processed_blocks = []

        for block_id, block_text, block_num in raw_blocks:
            processed_text = self._add_block_markers(block_text)
            processed_blocks.append((block_id, processed_text, block_num))

        return processed_blocks

    def _split_into_blocks(self, text: str) -> List[Tuple[str, str, int]]:
        """Разбивает текст на блоки с учётом разделителей"""
        blocks = []
        current_block = []
        current_id = str(uuid.uuid4())[:8]
        block_num = 1

        for line in text.split('\n'):
            line = line.rstrip('\r\n')

            if current_block:
                current_block.append(line)

                line_without_newline = line.replace('\n', '').replace('\r', '').replace('\t', '')
                current_total_chars = len(' '.join(current_block))

                if current_total_chars > self.max_qr_chars:
                    blocks.append((
                        current_id,
                        ' '.join(current_block),
                        block_num
                    ))
                    current_block = []
                    current_id = str(uuid.uuid4())[:8]
                    block_num += 1
            else:
                current_block.append(line)

        if current_block:
            blocks.append((current_id, ' '.join(current_block), block_num))

        return blocks

    def _add_block_markers(self, block_text: str) -> str:
        """Добавляет минимальные метки в начало и конец блока"""
        return f"{self.start_tag}{block_text}{self.end_tag}"

    def validate_block_metadata(self, metadata: dict) -> bool:
        """Проверяет валидность метаданных блока"""
        required_fields = ['file_path', 'block_id', 'timestamp']
        return all(field in metadata for field in required_fields)

    def parse_block_metadata(self, qr_text: str) -> dict:
        """Извлекает метаданные из QR-кода"""
        metadata = {}

        file_match = re.search(r'FILEPATH:(.+)\s+BLOCKID:(.+)\s+TIME:(.+)\s+CHECKSUM:(.+)', qr_text)
        if file_match:
            metadata = {
                'file_path': file_match.group(1),
                'block_id': file_match.group(2),
                'timestamp': file_match.group(3),
                'checksum': file_match.group(4),
                'raw_qr_text': qr_text
            }

        return metadata

    def generate_block_metadata(self, file_path: str, block_id: str, timestamp: str) -> str:
        """Генерирует минимальную строку метаданных"""
        encoded_path = self._encode_path(file_path)
        checksum = self._calculate_checksum(encoded_path, block_id, timestamp)
        return f"FILEPATH:{encoded_path} BLOCKID:{block_id} TIME:{timestamp} CHECKSUM:{checksum}"

    def _encode_path(self, file_path: str) -> str:
        """Кодирует путь к файлу для экономии места"""
        if file_path == "STDOUT":
            return "STDOT"

        encoded = file_path.replace('\\', '/').replace(':', '_').replace('%', '_')
        return encoded[:100]

    def _calculate_checksum(self, *parts: str) -> str:
        """Формирует короткий контрольный контрольную сумму"""
        combined = ''.join(parts)
        checksum_bytes = len(combined.encode('utf-8'))
        return f"{checksum_bytes:04d}"

    def combine_blocks_by_order(self, blocks_data: List[dict]) -> str:
        """Объединяет блоки в исходный текст, сохраняя порядок"""
        if not blocks_data:
            return ""

        full_text = []
        for block in blocks_data:
            if 'content' in block and 'timestamp' in block:
                block_text = block['content']

                start_idx = block_text.find('#QRSTART:#') + len('#QRSTART:#')
                end_idx = block_text.find('#QREND#')

                if start_idx > -1 and end_idx > start_idx:
                    content_part = block_text[start_idx:end_idx]
                    full_text.append(content_part)

        return '\n\n'.join(full_text)