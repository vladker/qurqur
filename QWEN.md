# QR Code File Encoder/Decoder (qurqur)

**Версия:** 2.0  
**Язык:** Python 3.8+

---

## Обзор

**qurqur** — CLI-утилита для кодирования любых файлов в QR-коды и восстановления файлов из QR-кодов. Поддерживает текстовые и бинарные файлы с автоматической архивацией.

---

## Структура проекта

```
qurqur/
├── qr_encoder.py          # Точка входа: файл → QR-коды
├── qr_decoder.py          # Точка входа: QR-коды → файл
├── config.py              # Константы и настройки
├── services/
│   ├── __init__.py        # Пакет services
│   ├── text_processor.py  # Разбиение на блоки, метаданные
│   ├── qr_generator.py    # Генерация QR (PIL, qrcode)
│   ├── qr_collector.py    # Сборка блоков из QR
│   ├── compression.py     # Сжатие (ZIP/GZIP/BZ2/LZMA)
│   └── file_manager.py    # Операции с файлами
├── .env.example           # Шаблон переменных окружения
├── requirements.txt       # Зависимости Python
├── README.md              # Документация пользователя
└── AGENTS.md              # Инструкции для AI-агентов
```

**Удалить вручную (не нужны):**
- `utils/` — пустая папка
- `SESSION_SUMMARY.md` — дублирует QWEN.md

---

## Быстрый старт

### Установка

```bash
pip install -r requirements.txt
```

### Кодирование (файл → QR)

```bash
python qr_encoder.py
```

### Декодирование (QR → файл)

```bash
python qr_decoder.py
```

---

## Формат данных

**Внутри QR-кода:**
```
BN:1 TOT:25 M:B C:zip #QRS#...данные...#QRE#
```

| Тег | Описание |
|-----|----------|
| `BN:` | Номер блока (1-999) |
| `TOT:` | Всего блоков |
| `M:` | Тип (T=текст, B=бинарный) |
| `C:` | Сжатие (none/zip/gzip/bz2/lzma) |
| `#QRS#` / `#QRE#` | Теги начала/конца |

---

## Константы (config.py)

| Константа | Значение |
|-----------|----------|
| `VERSION` | "2.0" |
| `TEXT_EXTENSIONS` | Сет текстовых расширений |
| `COMPRESSION_METHODS` | {'1':'auto', '2':'zip', ...} |
| `IMAGE_EXTENSIONS` | {.png, .jpg, .jpeg, ...} |
| `DEFAULTS` | Настройки по умолчанию |
| `MAX_QR_BLOCK_CHARS` | 200 |
| `BLOCK_START_TAG` | "#QRS#" |
| `BLOCK_END_TAG` | "#QRE#" |

---

## Зависимости

```
qrcode>=7.4.0      # Генерация QR
Pillow>=10.0.0     # Изображения
reportlab>=4.0.0   # PDF
svgwrite>=1.4.3    # SVG
pyzbar>=0.1.9      # Декодирование QR
python-dateutil>=2.8.0
```

---

## Development

### Стиль кода

- **PEP 8**, 4 пробела, 79 символов
- **Type hints** для всех функций
- **Docstrings** Google/NumPy стиль

### Именование

- Классы: `PascalCase`
- Функции: `snake_case`
- Константы: `UPPER_CASE`
- Приватные: `_prefix`

### Команды

```bash
# Lint
pylint *.py services/*.py
flake8 .

# Format
autopep8 --in-place --aggressive *.py services/*.py
```

---

## Ограничения

- Макс. блок: 200 символов
- Требуется `pyzbar` + `Pillow`/`OpenCV` для декодирования
- Нет тестов

---

## Roadmap

- [ ] Unit-тесты для `services/`
- [ ] CLI аргументы (argparse)
- [ ] Пакетная обработка
- [ ] Веб-интерфейс
- [ ] Оптимизация размера блоков
