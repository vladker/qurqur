# Session Summary — QR Code File Encoder/Decoder

## Проект: qurqur

**Тип:** Python CLI утилита для кодирования файлов в QR-коды и восстановления

---

## Архитектура

```
qurqur/
├── qr_encoder.py       # CLI: файл → QR-коды
├── qr_decoder.py       # CLI: QR-коды → файл
├── services/
│   ├── text_processor.py   # Разбиение на блоки, метаданные
│   ├── qr_generator.py     # Генерация QR (qrcode + PIL)
│   ├── qr_collector.py     # Сборка блоков из QR
│   ├── compression.py      # Сжатие (ZIP/GZIP/BZ2/LZMA)
│   └── file_manager.py     # Операции с файлами
└── requirements.txt
```

---

## Ключевые решения

### Формат метаданных (компактный)
```
BN:1 TOT:25 M:B C:zip #QRS#...данные...#QRE#
```
- `BN:` — номер блока
- `TOT:` — всего блоков  
- `M:` — тип (T=текст, B=бинарный)
- `C:` — сжатие

### Теги блоков
- Start: `#QRS#`
- End: `#QRE#`

### Поддерживаемые форматы
- **Вход:** любые файлы (текст UTF-8 / бинарные Base64)
- **Выход:** PNG, JPEG, BMP, SVG, PDF
- **QR стили:** square, circle
- **Сжатие:** auto, zip, gzip, bz2, lzma, none

---

## Исправленные ошибки (Session 16fa2794)

| Файл | Проблема | Решение |
|------|----------|---------|
| `services/file_manager.py` | Пустой/неверный контент | Создан класс `FileManager` |
| `qr_encoder.py` | Missing `import sys`, `os` | Добавлены импорты |
| `services/qr_generator.py` | LSP ошибки (svgwrite, ImageDraw) | Исправлены типы, импорты |
| `services/__init__.py` | Некорректные импорты | Обновлён `__all__` |

---

## Функционал (Session ses_3317)

### Encoder (qr_encoder.py)
1. Чтение файла (автоопределение текст/бинарный)
2. Архивация (выбор метода или auto)
3. Разбиение на блоки (200 символов макс.)
4. Генерация QR с метаданными
5. Сохранение в `qr_output/`

### Decoder (qr_decoder.py)
1. Сканирование папки (pyzbar + Pillow/OpenCV)
2. Парсинг метаданных (regex)
3. Сборка блоков по порядку
4. Разархивация
5. Сохранение/вывод результата

---

## Зависимости
```
qrcode>=7.4.0
Pillow>=10.0.0
reportlab>=4.0.0
svgwrite>=1.4.3
pyzbar>=0.1.9
python-dateutil>=2.8.0
```

---

## Команды

```bash
# Установка
pip install -r requirements.txt

# Кодирование
python qr_encoder.py

# Декодирование
python qr_decoder.py

#Lint
pylint *.py services/*.py
flake8 .

# Format
autopep8 --in-place --aggressive *.py services/*.py
```

---

## Известные ограничения

- Макс. размер блока: 200 символов (`TextProcessor.max_qr_chars`)
- Требуется pyzbar + PIL/OpenCV для декодирования
- Нет тестов (pytest не настроен)

---

## Roadmap

- [ ] Unit-тесты для `services/`
- [ ] CLI аргументы (argparse)
- [ ] Пакетная обработка
- [ ] Веб-интерфейс
- [ ] Оптимизация размера блоков

---

**Exported:** 2026-03-13  
**Sessions:** 16fa2794-3d88-4437-bd7c-d8416989928c, ses_33179b734ffeHHE2q3GQdmT4Yw
