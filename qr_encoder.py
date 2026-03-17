#!/usr/bin/env python3
"""
QR Code File Encoder - Основной скрипт
Интерактивное CLI приложение для генерации QR-кодов
Поддерживает любые файлы: текстовые, бинарные, с архивацией
"""

import sys
import io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import os
import base64

from config import VERSION, TEXT_EXTENSIONS, COMPRESSION_METHODS, DEFAULTS
from services.text_processor import TextProcessor
from services.qr_generator import QRGenerator
from services.compression import CompressionManager


def safe_input(prompt: str = "") -> str:
    """Безопасный ввод с обработкой случая когда stdin недоступен"""
    try:
        return input(prompt)
    except EOFError:
        print("\nОшибка: невозможно получить ввод. Запустите приложение из командной строки.")
        print(f"Пример: qr_encoder.exe <путь_к_файлу>")
        sys.exit(1)


def main():
    """Основная функция программы"""
    print(f"\n╔══════════════════════════════╗")
    print(f"║   QR CODE FILE ENCODER v{VERSION}   ║")
    print("║   Поддержка любых файлов      ║")
    print("╚══════════════════════════════╝\n")

    input_file = safe_input("1. Введите путь к файлу: ").strip()

    # Удаляем кавычки если пользователь их ввёл
    if input_file.startswith('"') and input_file.endswith('"'):
        input_file = input_file[1:-1]
    elif input_file.startswith("'") and input_file.endswith("'"):
        input_file = input_file[1:-1]

    if not input_file:
        print("Ошибка: путь не может быть пустым")
        return

    if not os.path.exists(input_file):
        print(f"Ошибка: файл '{input_file}' не найден")
        return

    # Получаем информацию о файле
    file_size = os.path.getsize(input_file)
    file_name = os.path.basename(input_file)
    file_ext = os.path.splitext(file_name)[1].lower()

    print(f"\nФайл загружен: {input_file}")
    print(f"Размер: {file_size:,} байт")
    print(f"Тип: {file_ext or 'без расширения'}")

    # Автоматическое определение режима кодирования
    # Пытаемся определить, текстовый ли файл
    is_text = file_ext in TEXT_EXTENSIONS

    if not is_text and file_size > 0:
        # Проверяем первые байты файла
        try:
            with open(input_file, 'rb') as f:
                header = f.read(1024)
            # Проверяем на наличие бинарных данных
            if b'\x00' in header:
                is_text = False
            else:
                # Пытаемся декодировать как UTF-8
                try:
                    header.decode('utf-8')
                    is_text = True
                except:
                    is_text = False
        except:
            is_text = False

    print(f"\n2. Режим кодирования:")
    if is_text:
        print("  [1] Текстовый (UTF-8)")
        print("  [2] Бинарный (Base64, универсальный)")
        default_mode = '1'
    else:
        print("  [1] Бинарный (Base64, рекомендуется)")
        print("  [2] Текстовый (только если файл текстовый)")
        default_mode = '1'

    encode_mode = safe_input(f"Ваш выбор (1/2, по умолчанию {default_mode}): ").strip()
    if not encode_mode:
        encode_mode = default_mode

    # Определяем режим: is_binary=True для бинарного режима
    if is_text:
        is_binary = encode_mode == '2'  # Для текстовых файлов бинарный = вариант 2
    else:
        is_binary = encode_mode == '1'  # Для бинарных файлов бинарный = вариант 1

    # Чтение файла
    try:
        if is_binary:
            with open(input_file, 'rb') as f:
                file_data = f.read()
            # Кодируем в Base64
            file_content = base64.b64encode(file_data).decode('ascii')
            print(f"Данные закодированы в Base64: {len(file_content)} символов")
        else:
            with open(input_file, 'r', encoding='utf-8') as f:
                file_content = f.read()
            print(f"Текст загружён: {len(file_content)} символов")
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        # Пробуем как бинарный
        print("Попытка чтения как бинарного файла...")
        with open(input_file, 'rb') as f:
            file_data = f.read()
        file_content = base64.b64encode(file_data).decode('ascii')
        is_binary = True
        print(f"Данные закодированы в Base64: {len(file_content)} символов")

    # Выбор архивации
    print("\n3. Архивация данных:")
    print("  [1] Автовыбор (рекомендуется)")
    print("  [2] ZIP")
    print("  [3] GZIP")
    print("  [4] BZ2")
    print("  [5] LZMA")
    print("  [6] Без сжатия")

    compress_choice = safe_input(f"Ваш выбор (1-6, по умолчанию 1): ").strip()
    compress_method = COMPRESSION_METHODS.get(compress_choice, 'auto')

    compression = CompressionManager()

    # Архивация (только для бинарных или больших файлов)
    original_size = len(file_content.encode('utf-8'))
    if is_binary or original_size > 10000:
        file_bytes = file_content.encode('utf-8')
        compressed_data, used_method = compression.compress_data(file_bytes, compress_method)
        # Кодируем сжатые байты в base64 для безопасной передачи
        compressed_content = base64.b64encode(compressed_data).decode('ascii')

        compressed_size = len(compressed_data)
        ratio = compression.get_compression_ratio(original_size, len(compressed_content.encode('utf-8')))

        print(f"\nАрхивация:")
        print(f"  Метод: {compression.get_method_name(used_method)}")
        print(f"  Было: {original_size:,} байт")
        print(f"  Стало: {len(compressed_content.encode('utf-8')):,} байт (base64)")
        print(f"  Сжатие: {ratio}")

        file_content = compressed_content
        compress_method = used_method  # Запоминаем использованный метод
    else:
        compress_method = 'none'
        print("\nАрхивация пропущена (маленький размер)")

    # Настройки QR-кода
    print("\n4. Версия QR (1-40, Enter для автоподбора): ", end='')
    version_input = safe_input().strip()
    if not version_input:
        version = None
    else:
        version = int(version_input)
        if version < 1 or version > 40:
            print("Версия должна быть от 1 до 40. Будет использован автоподбор.")
            version = None

    print("5. Коррекция ошибок (L/M/Q/H, по умолчанию M): ", end='')
    error_correction = safe_input().strip().upper()
    if not error_correction:
        error_correction = "M"

    print("6. Стиль (square/circle, по умолчанию square): ", end='')
    style = safe_input().strip().lower()
    if not style:
        style = "square"

    # Обработка данных
    processor = TextProcessor()
    generator = QRGenerator()

    # Разбиваем на блоки
    blocks = processor.process_text(file_content)
    total_blocks = len(blocks)

    # Генерируем метаданные файла (для отображения над QR)
    timestamp = str(int(os.path.getmtime(input_file)))
    mode_flag = 'B' if is_binary else 'T'

    # Создаем папку для вывода
    output_dir = DEFAULTS['output_dir']
    os.makedirs(output_dir, exist_ok=True)

    print(f"\nГенерация QR-кодов...")
    print(f"Всего блоков: {total_blocks}")

    for i, (block_id, block_content, block_num) in enumerate(blocks):
        # Формируем метаданные для QR (включая имя файла)
        qr_metadata = processor.generate_block_metadata(
            block_num, total_blocks, mode_flag, compress_method, file_name
        )
        # Данные внутри QR: только метаданные блока + контент
        full_data = f"{qr_metadata} {block_content}"

        # Генерируем QR-код
        qr_image = generator.generate_qr(
            data=full_data,
            version=version,
            error_correction=error_correction,
            style=style
        )

        # Добавляем текст над QR-кодом с полной информацией
        header_text = f"{file_name} | Блок {block_num}/{total_blocks} | {timestamp}"
        qr_with_text = generator.add_metadata_text(qr_image, header_text, position='top')

        output_path = f"{output_dir}/qr_{block_num}.png"
        generator.save_qr(qr_with_text, output_path, "PNG")
        print(f"  Создан: {output_path} (блок {block_num})")

    print(f"\n✓ Готово! Всего создано QR-кодов: {len(blocks)}")
    print(f"Папка сохранения: {os.path.abspath(output_dir)}")

    # Информация для восстановления
    print(f"\nДля восстановления файла используйте:")
    print(f"  python qr_decoder.py")
    print(f"  и укажите папку: {os.path.abspath(output_dir)}")


if __name__ == "__main__":
    main()
