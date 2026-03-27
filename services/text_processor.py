import re
import os
from typing import List, Tuple
import uuid
from config import BLOCK_START_TAG, BLOCK_END_TAG, MAX_QR_BLOCK_CHARS


class TextProcessor:
    """Обработка текста для разделения на QR-кодные блоки"""

    def __init__(self):
        # Максимальное количество символов для QR-кода
        # Версия 40 с коррекцией M вмещает ~2331 байт
        # С учётом метаданных (~100 символов) устанавливаем безопасный лимит
        self.max_qr_chars = MAX_QR_BLOCK_CHARS
        self.start_tag = BLOCK_START_TAG
        self.end_tag = BLOCK_END_TAG

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
        """Разбивает текст на блоки с сохранением переводов строк"""
        blocks = []
        current_block = ""
        current_id = str(uuid.uuid4())[:8]
        block_num = 1

        # Разбиваем по строкам, сохраняя информацию о переводах строк
        lines = text.split('\n')
        total_lines = len(lines)
        
        for i, line in enumerate(lines):
            line = line.rstrip('\r')
            
            # Добавляем '\n' после каждой строки, кроме последней
            if i < total_lines - 1:
                line += '\n'
            
            # Проверяем, поместится ли строка в текущий блок
            test_block = current_block + line
            
            if len(test_block) > self.max_qr_chars:
                # Если текущий блок не пустой, сохраняем его
                if current_block:
                    blocks.append((current_id, current_block, block_num))
                    current_id = str(uuid.uuid4())[:8]
                    block_num += 1
                
                # Разбиваем длинную строку на части
                remaining = line
                while len(remaining) > self.max_qr_chars:
                    chunk = remaining[:self.max_qr_chars]
                    blocks.append((current_id, chunk, block_num))
                    current_id = str(uuid.uuid4())[:8]
                    block_num += 1
                    remaining = remaining[self.max_qr_chars:]
                
                current_block = remaining
            else:
                current_block = test_block

        # Добавляем последний блок
        if current_block:
            blocks.append((current_id, current_block, block_num))

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

        # Поддерживаем старый и новый формат с BLOCKNUM
        file_match = re.search(r'FILEPATH:(.+)\s+BLOCKID:(.+)\s+BLOCKNUM:(\d+)\s+TIME:(.+)\s+CHECKSUM:(.+)', qr_text)
        if file_match:
            metadata = {
                'file_path': file_match.group(1),
                'block_id': file_match.group(2),
                'block_num': int(file_match.group(3)),
                'timestamp': file_match.group(4),
                'checksum': file_match.group(5),
                'raw_qr_text': qr_text
            }
        else:
            # Старый формат без BLOCKNUM
            file_match = re.search(r'FILEPATH:(.+)\s+BLOCKID:(.+)\s+TIME:(.+)\s+CHECKSUM:(.+)', qr_text)
            if file_match:
                metadata = {
                    'file_path': file_match.group(1),
                    'block_id': file_match.group(2),
                    'block_num': 1,  # По умолчанию
                    'timestamp': file_match.group(3),
                    'checksum': file_match.group(4),
                    'raw_qr_text': qr_text
                }

        return metadata

    def generate_block_metadata(self, block_num: int, total_blocks: int, mode: str, compress: str, file_name: str = "") -> str:
        """Генерирует строку метаданных для QR-кода"""
        # Формат: FN:filename.ext BN:X TOT:Y M:Z C:W (компактно)
        if file_name:
            return f"FN:{file_name} BN:{block_num} TOT:{total_blocks} M:{mode} C:{compress}"
        return f"BN:{block_num} TOT:{total_blocks} M:{mode} C:{compress}"

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

        # Сортируем блоки по block_num
        sorted_blocks = sorted(blocks_data, key=lambda b: b.get('block_num', 0))
        
        full_text = []
        for i, block in enumerate(sorted_blocks):
            # Поддерживаем оба ключа: 'content' и 'qr_content'
            block_text = block.get('content') or block.get('qr_content') or ''

            if block_text:
                # Извлекаем контент между тегами
                start_tag = self.start_tag
                end_tag = self.end_tag

                if block_text.startswith(start_tag):
                    # Теги ещё не удалены - извлекаем контент
                    end_idx = block_text.rfind(end_tag)
                    if end_idx > len(start_tag):
                        block_text = block_text[len(start_tag):end_idx]
                # else: теги уже удалены qr_collector - используем блок как есть

                full_text.append(block_text)

        # Соединяем блоки без разделителя - каждый блок уже содержит свои переводы строк
        return ''.join(full_text)