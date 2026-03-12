#!/usr/bin/env python3
"""
QR Code File Encoder - Основной скрипт
Интерактивное CLI приложение для генерации QR-кодов
Поддерживает любые файлы: текстовые, бинарные, с архивацией
"""

import os
import sys
import base64

from services.text_processor import TextProcessor
from services.qr_generator import QRGenerator
from services.compression import CompressionManager

def main():
    """Основная функция программы"""
    print("\n╔══════════════════════════════╗")
    print("║   QR CODE FILE ENCODER v2.0   ║")
    print("║   Поддержка любых файлов      ║")
    print("╚══════════════════════════════╝\n")

    input_file = input("1. Введите путь к файлу: ").strip()
    
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
    print(f"\nФайл загружен: {input_file}")
    print(f"Размер: {file_size:,} байт")

    # Выбор режима кодирования
    print("\n2. Выберите режим кодирования:")
    print("  [1] Текстовый (для текстовых файлов)")
    print("  [2] Бинарный (для любых файлов, Base64)")
    
    encode_mode = input("Ваш выбор (1/2, по умолчанию 2): ").strip()
    is_binary = encode_mode != '1'
    
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
    
    compress_choice = input("Ваш выбор (1-6, по умолчанию 1): ").strip()
    
    compress_map = {
        '1': 'auto', '2': 'zip', '3': 'gzip', '4': 'bz2', '5': 'lzma', '6': 'none'
    }
    compress_method = compress_map.get(compress_choice, 'auto')
    
    compression = CompressionManager()
    
    # Архивация (только для бинарных или больших файлов)
    original_size = len(file_content.encode('utf-8'))
    if is_binary or original_size > 10000:
        file_bytes = file_content.encode('utf-8')
        compressed_data, used_method = compression.compress_data(file_bytes, compress_method)
        compressed_content = compressed_data.decode('latin-1')  # Сохраняем байты как строку
        
        compressed_size = len(compressed_data)
        ratio = compression.get_compression_ratio(original_size, compressed_size)
        
        print(f"\nАрхивация:")
        print(f"  Метод: {compression.get_method_name(used_method)}")
        print(f"  Было: {original_size:,} байт")
        print(f"  Стало: {compressed_size:,} байт")
        print(f"  Сжатие: {ratio}")
        
        file_content = compressed_content
        compress_method = used_method  # Запоминаем использованный метод
    else:
        compress_method = 'none'
        print("\nАрхивация пропущена (маленький размер)")

    # Настройки QR-кода
    print("\n4. Версия QR (1-40, Enter для автоподбора): ", end='')
    version_input = input().strip()
    if not version_input:
        version = None
    else:
        version = int(version_input)
        if version < 1 or version > 40:
            print("Версия должна быть от 1 до 40. Будет использован автоподбор.")
            version = None

    print("5. Коррекция ошибок (L/M/Q/H, по умолчанию M): ", end='')
    error_correction = input().strip().upper()
    if not error_correction:
        error_correction = "M"

    print("6. Стиль (square/circle, по умолчанию square): ", end='')
    style = input().strip().lower()
    if not style:
        style = "square"

    # Обработка данных
    processor = TextProcessor()
    generator = QRGenerator()

    # Разбиваем на блоки
    blocks = processor.process_text(file_content)
    
    # Генерируем метаданные
    timestamp = str(int(os.path.getmtime(input_file)))
    
    # Создаем папку для вывода
    output_dir = "qr_output"
    os.makedirs(output_dir, exist_ok=True)

    print(f"\nГенерация QR-кодов...")
    print(f"Всего блоков: {len(blocks)}")

    for i, (block_id, block_content, block_num) in enumerate(blocks):
        # Формируем полные данные с метаданными
        metadata = processor.generate_block_metadata(
            input_file, block_id, timestamp, block_num
        )
        # Добавляем информацию о режиме и сжатии
        mode_flag = 'B' if is_binary else 'T'
        full_data = f"{metadata} MODE:{mode_flag} CMP:{compress_method} {block_content}"
        
        qr_image = generator.generate_qr(
            data=full_data, 
            version=version,
            error_correction=error_correction,
            style=style
        )
        output_path = f"{output_dir}/qr_{block_num}.png"
        generator.save_qr(qr_image, output_path, "PNG")
        print(f"  Создан: {output_path} (блок {block_num})")

    print(f"\n✓ Готово! Всего создано QR-кодов: {len(blocks)}")
    print(f"Папка сохранения: {os.path.abspath(output_dir)}")
    
    # Информация для восстановления
    print(f"\nДля восстановления файла используйте:")
    print(f"  python qr_decoder.py")
    print(f"  и укажите папку: {os.path.abspath(output_dir)}")

if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()
