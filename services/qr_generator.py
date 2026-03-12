import qrcode
from qrcode.constants import ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q, ERROR_CORRECT_H
from PIL import Image
from typing import Dict, Any, Tuple, List
import io
import uuid


class QRGenerator:
    """Генератор QR-кодов с настройками"""

    def __init__(self):
        self.min_qr_size = 21

    def generate_qr(
        self,
        data: str,
        version: int = None,
        error_correction: str = 'M',
        style: str = 'square',
        use_micro_markers: bool = True
    ) -> Image.Image:
        """
        Генерирует QR-код

        Args:
            data: Текстовые данные для QR-кода
            version: Версия QR-кода (1-40, None для автоподбора)
            error_correction: Степень коррекции ошибок (L, M, Q, H)
            style: Стиль (square, circle)
            use_micro_markers: Использовать микро-метки вместо начала/конца

        Returns:
            Объект PIL.Image с QR-кодом
        """
        error_correction_map = {
            'L': ERROR_CORRECT_L,
            'M': ERROR_CORRECT_M,
            'Q': ERROR_CORRECT_Q,
            'H': ERROR_CORRECT_H
        }
        
        if version is None:
            # Автоподбор версии
            qr = qrcode.QRCode(
                version=None,
                error_correction=error_correction_map.get(error_correction, ERROR_CORRECT_M),
                box_size=10,
                border=4
            )
            qr.add_data(data)
            qr.make(fit=True)
            version = qr.version
        elif version < 1 or version > 40:
            version = 1

        if style == 'circle':
            return self._generate_circle_qr(data, version, error_correction, use_micro_markers)
        else:
            return self._generate_square_qr(data, version, error_correction, use_micro_markers)

    def _generate_square_qr(self, data: str, version: int, error_correction: str, use_micro_markers: bool) -> Image.Image:
        """Генерирует QR-код со стандартными квадратными модулями"""
        error_correction_map = {
            'L': ERROR_CORRECT_L,
            'M': ERROR_CORRECT_M,
            'Q': ERROR_CORRECT_Q,
            'H': ERROR_CORRECT_H
        }

        qr = qrcode.QRCode(
            version=version,
            error_correction=error_correction_map.get(error_correction, ERROR_CORRECT_M),
            box_size=10,
            border=4
        )
        qr.add_data(data)
        qr.make(fit=True)

        qr_image = qr.make_image(
            fill_color="black",
            back_color="white"
        )

        return qr_image

    def _generate_circle_qr(self, data: str, version: int, error_correction: str, use_micro_markers: bool) -> Image.Image:
        """Генерирует QR-код с круглыми модулями"""
        error_correction_map = {
            'L': ERROR_CORRECT_L,
            'M': ERROR_CORRECT_M,
            'Q': ERROR_CORRECT_Q,
            'H': ERROR_CORRECT_H
        }

        qr = qrcode.QRCode(
            version=version,
            error_correction=error_correction_map.get(error_correction, ERROR_CORRECT_M),
            box_size=10,
            border=4
        )
        qr.add_data(data)
        qr.make(fit=True)

        module_data = qr.get_matrix()

        image_width = len(module_data) * 5
        image = Image.new('RGB', (image_width, image_width), color='white')

        for row in range(len(module_data)):
            for col in range(len(module_data[row])):
                if module_data[row][col]:
                    if qr.box_size > 4:
                        circle_radius = qr.box_size // 2

                        circle = Image.new('RGB', (qr.box_size, qr.box_size), color='white')

                        import math

                        def create_ellipse_circle(radius: int):
                            pixels = []
                            for x in range(circle_radius * 2 + 1):
                                for y in range(circle_radius * 2 + 1):
                                    if (x - circle_radius) ** 2 + (y - circle_radius) ** 2 <= circle_radius ** 2:
                                        pixels.append((x, y))
                            return pixels

                        pixels = create_ellipse_circle(circle_radius)
                        for px, py in pixels:
                            if px < qr.box_size and py < qr.box_size:
                                circle.putpixel((px, py), (0, 0, 0))

                        image.paste(circle, (col * qr.box_size, row * qr.box_size))
                    else:
                        image.paste('black', (col * qr.box_size, row * qr.box_size))

        return image

    def add_metadata_text(self, qr_image: Image.Image, metadata_text: str, position: str = 'bottom') -> Image.Image:
        """
        Добавляет текст над/под QR-кодом с ограничением ширины

        Args:
            qr_image: QR-код
            metadata_text: Текст метаданных
            position: Положение (top, bottom)
        """
        from PIL import ImageDraw, ImageFont
        
        text_color = 'black'
        bg_color = 'white'
        font_name = 'Arial'

        img_width, img_height = qr_image.size
        
        # Разбиваем текст на строки чтобы не превысить ширину QR
        max_text_width = img_width * 0.95  # 95% от ширины QR
        font_size = max(8, min(14, img_width // 20))  # Адаптивный размер
        
        try:
            font = ImageFont.truetype(font_name, font_size)
        except:
            font = ImageFont.load_default()
        
        # Разбиваем на строки
        words = metadata_text.split(' | ')
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + (' | ' if current_line else '') + word
            bbox = ImageDraw.Draw(Image.new('RGB', (1, 1))).textbbox((0, 0), test_line, font=font)
            text_width = bbox[2] - bbox[0]
            
            if text_width <= max_text_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        # Рассчитываем высоту текста
        text_height = len(lines) * (font_size + 4) + 10
        
        # Конвертируем qr_image в PIL.Image если это PilImage от qrcode
        if hasattr(qr_image, 'im'):
            # Это PilImage от qrcode, конвертируем в PIL.Image
            qr_image = qr_image.convert('RGB')
        
        # Создаем новое изображение
        if position == 'top':
            new_height = img_height + text_height
            new_image = Image.new('RGB', (img_width, new_height), color=bg_color)
            new_image.paste(qr_image, (0, text_height))
            
            draw = ImageDraw.Draw(new_image)
            y_offset = 5
            for line in lines:
                # Центрируем текст
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                x = (img_width - text_width) // 2
                draw.text((x, y_offset), line, fill=text_color, font=font)
                y_offset += font_size + 4
        else:
            new_height = img_height + text_height
            new_image = Image.new('RGB', (img_width, new_height), color=bg_color)
            new_image.paste(qr_image, (0, 0))
            
            draw = ImageDraw.Draw(new_image)
            y_offset = img_height + 5
            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                x = (img_width - text_width) // 2
                draw.text((x, y_offset), line, fill=text_color, font=font)
                y_offset += font_size + 4
        
        return new_image

    def _get_font(self, font_name: str, size: int) -> Any:
        """Возвращает объект шрифта"""
        try:
            from PIL import ImageFont
            if font_name:
                try:
                    return ImageFont.truetype(font_name, size)
                except:
                    return ImageFont.load_default()
            return ImageFont.load_default()
        except:
            return None

    def _calculate_text_height(self, text: str, font_name: str, max_width: int) -> int:
        """Рассчитывает необходимую высоту для текста"""
        try:
            from PIL import ImageFont, ImageDraw
            font = ImageFont.truetype(font_name, 12) if font_name else ImageFont.load_default()
            temp_img = Image.new('RGB', (1, 1), 'white')
            temp_draw = ImageDraw.Draw(temp_img)
            left, top, right, bottom = temp_draw.textbbox((0, 0), text, font=font)
            height = int(bottom - top)
            return int(height) + 6
        except:
            return 20

    def save_qr(self, qr_image: Image.Image, output_path: str, format: str = 'PNG') -> bool:
        """
        Сохраняет QR-код в указанный формат

        Args:
            qr_image: QR-код
            output_path: Путь для сохранения
            format: Формат (PNG, JPEG, BMP, SVG)

        Returns:
            True если успешно, иначе False
        """
        try:
            if format.upper() in ['PNG', 'JPG', 'JPEG', 'BMP']:
                qr_image.save(output_path, format=format.upper())
                return True
            else:
                return False
        except Exception:
            return False

    def generate_svg(self, data: str, version: int = 1) -> str:
        """Генерирует SVG-код QR-кода"""
        import svgwrite

        qr = qrcode.QRCode(version=version, box_size=10, border=4)
        qr.add_data(data)
        qr.make(fit=True)

        module_data = qr.get_matrix()

        svg_width = len(module_data) * 10
        svg = svgwrite.Drawing(f"{uuid.uuid4()}.svg", size=(svg_width, svg_width))

        for row in range(len(module_data)):
            for col in range(len(module_data[row])):
                if module_data[row][col]:
                    x = col * 10
                    y = row * 10
                    svg.add(svg.element('rect', xy=(x, y), size=('10', '10'), fill='black'))

        return svg.tostring()

    def merge_qr_images(
        self,
        qr_images: list,
        columns: int,
        output_path: str,
        metadata_positions: list
    ) -> bool:
        """
        Объединяет несколько QR-кодов в одно изображение для сетки

        Args:
            qr_images: Список QR-кодов
            columns: Количество столбцов в сетке
            output_path: Путь для сохранения результата
            metadata_positions: Список позиций для метаданных

        Returns:
            True если успешно, иначе False
        """
        try:
            from PIL import Image

            if not qr_images:
                return False

            for position in ('top', 'bottom'):
                image_with_text = [qr_img.copy() for qr_img in qr_images]
                for i, qr_img in enumerate(image_with_text):
                    if i < len(metadata_positions):
                        image_with_text[i] = self.add_metadata_text(
                            qr_img,
                            metadata_positions[i],
                            position=position
                        )

            image_with_text = [qr_img.copy() for qr_img in qr_images]

            rows = (len(image_with_text) + columns - 1) // columns
            image_width = image_with_text[0].size[0]

            combined_width = image_width * columns
            combined_height = image_width * rows

            result = Image.new('RGB', (combined_width, combined_height), color='white')

            for i, qr_image in enumerate(image_with_text):
                row = i // columns
                col = i % columns

                x = col * image_width
                y = row * image_width
                result.paste(qr_image, (x, y))

            result.save(output_path, 'PNG')
            return True

        except Exception:
            return False