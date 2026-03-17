#!/usr/bin/env python3
"""
QR Code Decoder - Программа для считывания QR-кодов и восстановления файлов
Поддерживает любые файлы: текстовые, бинарные, с разархивацией
"""

import io
import os
import sys
import base64
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def safe_input(prompt: str = "") -> str:
    """Безопасный ввод с обработкой случая когда stdin недоступен"""
    try:
        return input(prompt)
    except EOFError:
        print("\nОшибка: невозможно получить ввод. Запустите приложение из командной строки.")
        print(f"Пример: qr_decoder.exe <путь_к_папке>")
        sys.exit(1)

from config import VERSION, IMAGE_EXTENSIONS, VIDEO_EXTENSIONS
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
    image_extensions = IMAGE_EXTENSIONS
    
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
                img = cv2.imread(file_path)
                if img is None:
                    print(f"[{i}/{len(files)}] {filename}: не удалось прочитать")
                    continue
                with open(os.devnull, 'w') as devnull:
                    old_stdout = sys.stdout
                    old_stderr = sys.stderr
                    sys.stdout = devnull
                    sys.stderr = devnull
                    try:
                        qr_codes = decode(img)
                    finally:
                        sys.stdout = old_stdout
                        sys.stderr = old_stderr
            else:
                img = Image.open(file_path)
                with open(os.devnull, 'w') as devnull:
                    old_stdout = sys.stdout
                    old_stderr = sys.stderr
                    sys.stdout = devnull
                    sys.stderr = devnull
                    try:
                        qr_codes = decode(img)
                    finally:
                        sys.stdout = old_stdout
                        sys.stderr = old_stderr
            
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


def decode_qr_from_video(video_path: str, output_dir: str = None) -> list:
    """
    Считывает QR-коды из видеофайла, разбивая на кадры
    
    Args:
        video_path: Путь к видеофайлу
        output_dir: Папка для сохранения извлечённых кадров (опционально)
        
    Returns:
        Список расшифрованных данных из QR-кодов
    """
    try:
        import cv2
        from pyzbar.pyzbar import decode
    except ImportError:
        print("Ошибка: для работы с видео требуется opencv-python и pyzbar")
        print("Установите: pip install opencv-python pyzbar")
        return []
    
    if not os.path.exists(video_path):
        print(f"Видеофайл '{video_path}' не найден")
        return []
    
    frames_dir = output_dir
    if frames_dir is None:
        video_name = os.path.splitext(os.path.basename(video_path))[0]
        frames_dir = os.path.join(os.path.dirname(video_path), f"{video_name}_frames")
    
    os.makedirs(frames_dir, exist_ok=True)
    
    # Открываем видео
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Не удалось открыть видео: {video_path}")
        return []
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    duration = total_frames / fps if fps > 0 else 0
    
    print(f"\nВидео: {os.path.basename(video_path)}")
    print(f"  Кадров: {total_frames}, FPS: {fps:.2f}, Длительность: {duration:.1f} сек")
    print(f"  Кадры будут сохранены в: {frames_dir}\n")
    
    decoded_data = []
    seen_qr_data = set()  # Для дедупликации QR-кодов
    frame_count = 0
    saved_count = 0
    duplicate_count = 0
    last_progress = -1
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        # Показываем прогресс каждые 10%
        progress = (frame_count * 10) // total_frames
        if progress > last_progress:
            print(f"Обработка: {progress * 10}% ({frame_count}/{total_frames} кадров)")
            last_progress = progress
        
        # Пробуем распознать QR-коды на кадре (подавляем warnings от zbar)
        with open(os.devnull, 'w') as devnull:
            import sys
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            sys.stdout = devnull
            sys.stderr = devnull
            try:
                qr_codes = decode(frame)
            finally:
                sys.stdout = old_stdout
                sys.stderr = old_stderr
        
        if qr_codes:
            for qr in qr_codes:
                data = qr.data.decode('utf-8')
                
                # Дедупликация - пропускаем уже обработанные QR-коды
                if data in seen_qr_data:
                    duplicate_count += 1
                    continue
                
                seen_qr_data.add(data)
                decoded_data.append({
                    'file': f"frame_{frame_count:05d}.jpg",
                    'data': data
                })
                print(f"  [Кадр {frame_count}] Распознан QR ({len(data)} симв.)")
            
            # Сохраняем кадр с QR-кодом
            frame_path = os.path.join(frames_dir, f"frame_{frame_count:05d}.jpg")
            cv2.imwrite(frame_path, frame)
            saved_count += 1
    
    cap.release()
    
    print(f"\nОбработка завершена:")
    print(f"  Всего кадров обработано: {frame_count}")
    print(f"  QR-кодов найдено: {len(decoded_data)}")
    if duplicate_count > 0:
        print(f"  Дубликатов пропущено: {duplicate_count}")
    print(f"  Кадры с QR сохранены: {saved_count}")
    
    return decoded_data


def main():
    """Основная функция программы"""
    print(f"\n+==================================+")
    print(f"|   QR CODE DECODER v{VERSION}           |")
    print("|   Восстановление любых файлов    |")
    print("+==================================+\n")
    
    # Выбор источника
    print("Выберите источник QR-кодов:")
    print("  [1] Папка с изображениями")
    print("  [2] Видеофайл")
    
    source_choice = safe_input("Ваш выбор (1/2, по умолчанию 1): ").strip()
    
    decoded_data = []
    qr_directory = ""
    frames_dir = None
    
    if source_choice == "2":
        # Работа с видео
        video_path = safe_input("\n1. Введите путь к видеофайлу: ").strip()
        
        # Удаляем кавычки
        if video_path.startswith('"') and video_path.endswith('"'):
            video_path = video_path[1:-1]
        elif video_path.startswith("'") and video_path.endswith("'"):
            video_path = video_path[1:-1]
        
        if not video_path:
            print("Ошибка: путь не может быть пустым")
            return
        
        if not os.path.exists(video_path):
            print(f"Ошибка: файл '{video_path}' не найден")
            return
        
        # Проверяем расширение
        ext = os.path.splitext(video_path)[1].lower()
        if ext not in VIDEO_EXTENSIONS:
            print(f"Ошибка: неподдерживаемый формат видео '{ext}'")
            print(f"Поддерживаемые: {', '.join(VIDEO_EXTENSIONS)}")
            return
        
        # Опционально: папка для сохранения кадров
        frames_dir = None
        save_frames = safe_input("\nСохранить извлечённые кадры с QR-кодами? (д/н, по умолчанию д): ").strip().lower()
        if save_frames != 'н':
            frames_dir = os.path.join(os.path.dirname(video_path), 
                                       f"{os.path.splitext(os.path.basename(video_path))[0]}_frames")
        
        # Декодирование из видео
        decoded_data = decode_qr_from_video(video_path, frames_dir)
        qr_directory = os.path.dirname(video_path)
    else:
        # Работа с папкой изображений (существующая логика)
        qr_directory = safe_input("1. Введите путь к папке с QR-кодами: ").strip()
        
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
            
            # Извлекаем имя файла из метаданных QR
            if original_file_name == "restored_file" and block_data.get('file_name'):
                original_file_name = block_data['file_name']
            
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
            # Сначала декодируем base64 (которым закодированы сжатые данные)
            compressed_bytes = base64.b64decode(file_content)

            # Затем разархивируем
            decompressed_data = compression.decompress_data(compressed_bytes, compress_method)

            ratio = compression.get_compression_ratio(len(decompressed_data), len(compressed_bytes))
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
    if '.' in os.path.splitext(original_file_name)[1]:
        # Расширение уже есть в имени файла
        default_output = os.path.join(qr_directory, original_file_name)
    else:
        # Нет расширения - добавляем по типу
        default_ext = '.bin' if is_binary else '.txt'
        default_output = os.path.join(qr_directory, f"{original_file_name}{default_ext}")

    # Выбор способа сохранения
    print("\n2. Выберите способ сохранения:")
    print("  [1] Сохранить в файл")
    print("  [2] Вывести в консоль (только для текста)")

    save_choice = safe_input("Ваш выбор (1/2, по умолчанию 1): ").strip()

    if save_choice != '2':
        output_file = safe_input(f"3. Путь для сохранения (по умолчанию {default_output}): ").strip()

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
    main()
