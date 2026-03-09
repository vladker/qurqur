#!/usr/bin/env python3
"""
QR Code File Encoder - Основной скрипт
Интерактивное CLI приложение для генерации QR-кодов
"""

from services.text_processor import TextProcessor
from services.qr_generator import QRGenerator
import uuid

def main():
    """Основная функция программы"""
    print("\n╔══════════════════════════════╗")
    print("║   QR CODE FILE ENCODER v1.0   ║")
    print("╚══════════════════════════════╝\n")
    
    input_file = input("1. Введите путь к текстовому файлу: ").strip()

    if not input_file:
        print("Ошибка: путь не может быть пустым")
        return

    if not os.path.exists(input_file):
        print(f"Ошибка: файл '{input_file}' не найден")
        return

    print(f"Файл загружен: {input_file}")

    version = input("2. Версия QR (1-40, по умолчанию 1): ").strip()
    if not version:
        version = 1
    else:
        version = int(version)

    error_correction = input("3. Коррекция ошибок (L/M/Q/H, по умолчанию M): ").strip().upper()
    if not error_correction:
        error_correction = "M"

    style = input("4. Стиль (square/circle, по умолчанию square): ").strip().lower()
    if not style:
        style = "square"

    position = input("5. Позиция метаданных (top/bottom, по умолчанию bottom): ").strip().lower()
    if not position:
        position = "bottom"

    processor = TextProcessor()
    generator = QRGenerator()

    for i in range(5):
        block_text = f"#QRSTART:#Блок {i}#QREND#"
        qr_image = generator.generate_qr(data=block_text, version=version, 
                                        error_correction=error_correction,
                                        style=style)
        output_path = f"qr_output/qr_{i}.png"
        generator.save_qr(qr_image, output_path, "PNG")
        print(f"Готово: {output_path}")

if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(__file__))
    main()
