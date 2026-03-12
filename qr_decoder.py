#!/usr/bin/env python3
"""
QR Code Decoder - Программа для считывания QR-кодов и восстановления файлов
Поддерживает любые файлы: текстовые, бинарные, с разархивацией
"""

import os
import sys
import base64

from services.qr_collector import QRCollector
from services.compression import CompressionManager


def decode_qr_images(qr_directory: str) -> list:
    """
    Считывает QR-коды из изображений в папке
    
    Args:
        qr_directory: Папка с изображениями QR-кодов
        
    Returns:
        Список расшифрованных данных из QR-кодов
    """
    try:
        import cv2
        from pyzbar.pyzbar import decode
        from PIL import Image
        USE_CV = True
    except ImportError:
        try:
            from pyzbar.pyzbar import decode
            from PIL import Image
            USE_CV = False
        except ImportError:
            print("Ошибка: не установлены библиотеки pyzbar, Pillow или opencv-python")
            print("Установите: pip install pyzbar Pillow opencv-python")
            return []
    
    decoded_data = []
    
    # Поддерживаемые форматы изображений
    image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp'}
    
    if not os.path.exists(qr_directory):
        print(f"Папка '{qr_directory}' не существует")
        return []
    
    files = [f for f in os.listdir(qr_directory) 
             if os.path.isfile(os.path.join(qr_directory, f)) 
             and os.path.splitext(f)[1].lower() in image_extensions]
    
    if not files:
        print(f"В папке не найдено изображений ({', '.join(image_extensions)})")
        return []
    
    print(f"Найдено изображений: {len(files)}")
    
    for i, filename in enumerate(sorted(files), 1):
        file_path = os.path.join(qr_directory, filename)
        try:
            if USE_CV:
                # Используем OpenCV для чтения
                img = cv2.imread(file_path)
                if img is None:
                    print(f"[{i}/{len(files)}] {filename}: не удалось прочитать")
                    continue
                qr_codes = decode(img)
            else:
                # Используем PIL
                img = Image.open(file_path)
                qr_codes = decode(img)
            
            if qr_codes:
                for qr in qr_codes:
                    data = qr.data.decode('utf-8')
                    decoded_data.append({
                        'file': filename,
                        'data': data
                    })
                    print(f"[{i}/{len(files)}] {filename}: распознан ({len(data)} симв.)")
            else:
                print(f"[{i}/{len(files)}] {filename}: QR-код не найден")
                
        except Exception as e:
            print(f"[{i}/{len(files)}] {filename}: ошибка - {e}")
    
    return decoded_data


def main():
    """Основная функция программы"""
    print("\n╔══════════════════════════════════╗")
    print("║   QR CODE DECODER v2.0           ║")
    print("║   Восстановление любых файлов    ║")
    print("╚══════════════════════════════════╝\n")
    
    # Запрос пути к папке с QR-кодами
    qr_directory = input("1. Введите путь к папке с QR-кодами: ").strip()
    
    # Удаляем кавычки если пользователь их ввёл
    if qr_directory.startswith('"') and qr_directory.endswith('"'):
        qr_directory = qr_directory[1:-1]
    elif qr_directory.startswith("'") and qr_directory.endswith("'"):
        qr_directory = qr_directory[1:-1]
    
    if not qr_directory:
        print("Ошибка: путь не может быть пустым")
        return
    
    if not os.path.exists(qr_directory):
        print(f"Ошибка: папка '{qr_directory}' не найдена")
        return
    
    print(f"\nСканирование папки: {qr_directory}\n")
    
    # Декодирование QR-кодов
    decoded_data = decode_qr_images(qr_directory)
    
    if not decoded_data:
        print("\nНе удалось распознать ни одного QR-кода")
        return
    
    print(f"\nВсего распознано QR-кодов: {len(decoded_data)}")
    
    # Сборка данных
    collector = QRCollector()
    blocks = []
    mode_flag = 'T'  # По умолчанию текстовый
    compress_method = 'none'
    total_blocks = 0
    original_file_name = "restored_file"  # По умолчанию

    for item in decoded_data:
        block_data = collector._extract_block_data(item['data'])
        if block_data:
            blocks.append(block_data)
            
            # Извлекаем режим и метод сжатия из метаданных блока
            if 'mode' in block_data:
                mode_flag = block_data['mode']
            if 'compress' in block_data:
                compress_method = block_data['compress']
            if 'total_blocks' in block_data:
                total_blocks = block_data['total_blocks']
            
            # Извлекаем имя файла из текста над QR (если есть)
            if original_file_name == "restored_file" and 'file' in item:
                # Пытаемся извлечь из имени файла QR
                pass
            
            print(f"  Блок {block_data['block_num']}: ID={block_data.get('block_id', 'N/A')}")
        else:
            print(f"  НЕ извлечён: {item['file']}")

    if not blocks:
        print("\nНе удалось извлечь данные из распознанных QR-кодов")
        return

    # Сортировка блоков по номеру
    blocks.sort(key=lambda b: b.get('block_num', 0))

    # Проверка на недостающие блоки
    missing = collector._check_missing_blocks(blocks)
    if missing:
        print(f"\n⚠ Внимание: отсутствуют блоки: {missing}")
        print(f"  Найдено: {len(blocks)}, Ожидается: {total_blocks}")
        print("  Файл может быть восстановлен не полностью!")

    # Проверка первого блока на наличие MODE и CMP
    if blocks:
        first_block = blocks[0]
        if 'mode' in first_block:
            mode_flag = first_block['mode']
        if 'compress' in first_block:
            compress_method = first_block['compress']
        if 'total_blocks' in first_block:
            total_blocks = first_block['total_blocks']

    # Объединение блоков - qr_content уже очищен от тегов
    combined_content = ''.join([b['qr_content'] for b in blocks])
    file_content = combined_content

    print(f"\nОбъединённый размер: {len(file_content):,} символов")

    # Определение типа файла
    is_binary = mode_flag == 'B'
    
    print(f"\nПараметры:")
    print(f"  Тип файла: {'Бинарный' if is_binary else 'Текстовый'}")
    print(f"  Сжатие: {compress_method}")
    print(f"  Всего блоков: {total_blocks}")
    print(f"  Размер данных: {len(file_content):,} символов")

    # Разархивация
    decompression_failed = False
    if compress_method != 'none':
        try:
            compression = CompressionManager()
            # Декодируем latin-1 строку обратно в байты (как было заархивировано)
            file_bytes = file_content.encode('latin-1')
            decompressed_data = compression.decompress_data(file_bytes, compress_method)

            ratio = compression.get_compression_ratio(len(decompressed_data), len(file_bytes))
            print(f"\nРазархивация:")
            print(f"  Метод: {compression.get_method_name(compress_method)}")
            print(f"  Сжатие: {ratio}")

            # После разархивации получаем UTF-8 строку (Base64 для бинарных файлов)
            file_content = decompressed_data.decode('utf-8')
            print(f"  Размер после разархивации: {len(file_content):,} символов")
        except Exception as e:
            print(f"\n⚠ Ошибка при разархивации: {e}")
            decompression_failed = True
            print("  Продолжаем без разархивации (данные могут быть повреждены)...")

    # Декодирование из Base64 (для бинарных файлов)
    if is_binary:
        try:
            decoded_bytes = base64.b64decode(file_content)
            print(f"\nДекодирование из Base64: {len(decoded_bytes):,} байт")
            file_data = decoded_bytes
        except Exception as e:
            print(f"\n⚠ Ошибка при декодировании Base64: {e}")
            if decompression_failed:
                print("  Возможно, данные были заархивированы, но не удалось разархивировать")
            print("  Сохраняем как есть (файл может быть повреждён)...")
            file_data = file_content.encode('utf-8', errors='replace')
    else:
        file_data = file_content.encode('utf-8')

    # Определение имени файла для сохранения
    # Используем имя по умолчанию или из параметров
    default_ext = '.bin' if is_binary else '.txt'
    default_output = os.path.join(qr_directory, f"{original_file_name}{default_ext}")

    # Выбор способа сохранения
    print("\n2. Выберите способ сохранения:")
    print("  [1] Сохранить в файл")
    print("  [2] Вывести в консоль (только для текста)")

    save_choice = input("Ваш выбор (1/2, по умолчанию 1): ").strip()

    if save_choice != '2':
        output_file = input(f"3. Путь для сохранения (по умолчанию {default_output}): ").strip()

        if not output_file:
            output_file = default_output
        
        try:
            # Создаем папку если нужно
            output_dir = os.path.dirname(output_file)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            
            # Сохраняем файл
            if is_binary:
                with open(output_file, 'wb') as f:
                    f.write(file_data)
            else:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(file_content)
            
            file_size = os.path.getsize(output_file)
            print(f"\n✓ Файл сохранён: {output_file}")
            print(f"Размер: {file_size:,} байт")
        except Exception as e:
            print(f"\n✗ Ошибка при сохранении: {e}")
    else:
        if is_binary:
            print("\n⚠ Бинарные данные не могут быть выведены в консоль")
        else:
            print("\n" + "=" * 50)
            print("ВОССТАНОВЛЕННОЕ СОДЕРЖИМОЕ:")
            print("=" * 50)
            print(file_content)
            print("=" * 50)

    # Отчёт об ошибках
    if len(blocks) < len(decoded_data):
        print(f"\n⚠ Внимание: не все QR-коды удалось обработать")
        print(f"  Распознано: {len(decoded_data)}, Обработано: {len(blocks)}")


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()
