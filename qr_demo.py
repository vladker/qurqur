#!/usr/bin/env python3
"""
QR Code Demo - Демонстратор QR-кодов
Показ QR-кодов с настраиваемым размером и скоростью
"""
import os
import re
import tkinter as tk
from tkinter import filedialog, ttk
from tkinter import messagebox
from PIL import Image, ImageTk
from typing import List, Tuple


class QRCodeDemo:
    """Демонстратор QR-кодов с GUI"""

    def __init__(self):
        self.qr_files: List[Tuple[str, int]] = []  # (full_path, block_num)
        self.current_index = 0
        self.zoom_level = 1.0
        self.is_playing = False
        self.fps_delay = 1000  # мс между кадрами
        self.root = None
        self.canvas = None
        self.image_label = None
        self.info_label = None
        self.play_button = None
        self.photo_image = None

    def select_directory(self):
        """Выбор папки с QR-кодами"""
        directory = filedialog.askdirectory(title="Выберите папку с QR-кодами")
        if not directory:
            return False

        self.load_qr_codes(directory)
        return len(self.qr_files) > 0

    def load_qr_codes(self, directory: str):
        """Загружает QR-коды из папки, сортирует по номеру"""
        pattern = re.compile(r'(?:qr_|)\s*(?P<num>\d+)\.(png|jpg|jpeg|bmp|gif|tiff|webp)$', re.IGNORECASE)
        valid_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp'}

        self.qr_files = []
        for filename in os.listdir(directory):
            full_path = os.path.join(directory, filename)
            if not os.path.isfile(full_path):
                continue

            ext = os.path.splitext(filename.lower())[1]
            if ext in valid_extensions:
                match = pattern.search(filename)
                block_num = int(match.group('num')) if match else 999
                self.qr_files.append((full_path, block_num))

        if self.qr_files:
            self.qr_files.sort(key=lambda x: x[1])
            self.current_index = 0
            print(f"Загружено QR-кодов: {len(self.qr_files)}")

    def run(self):
        """Запускает GUI"""
        self.root = tk.Tk()
        self.root.title("QR Code Demo")
        self.root.geometry("800x900")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Верхняя панель - кнопки управления
        control_frame = tk.Frame(self.root)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        btn_width = 12
        
        tk.Button(control_frame, text="📁 Открыть папку", command=self.open_folder, width=btn_width).pack(side=tk.LEFT, padx=5)
        
        self.play_button = tk.Button(control_frame, text="▶ Старт", command=self.toggle_play, width=btn_width)
        self.play_button.pack(side=tk.LEFT, padx=5)
        
        tk.Button(control_frame, text="◀ Предыдущий", command=self.prev_qr, width=btn_width).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Следующий ▶", command=self.next_qr, width=btn_width).pack(side=tk.LEFT, padx=5)
        
        # Панель зума
        zoom_frame = tk.Frame(self.root)
        zoom_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        
        tk.Label(zoom_frame, text="Zoom:").pack(side=tk.LEFT)
        
        tk.Button(zoom_frame, text="-", command=self.zoom_out, width=4).pack(side=tk.LEFT, padx=2)
        
        self.zoom_label = tk.Label(zoom_frame, text="1.0x", width=6)
        self.zoom_label.pack(side=tk.LEFT, padx=2)
        
        tk.Button(zoom_frame, text="+", command=self.zoom_in, width=4).pack(side=tk.LEFT, padx=2)
        
        # Панель скорости
        speed_frame = tk.Frame(self.root)
        speed_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        
        tk.Label(speed_frame, text="Скорость:").pack(side=tk.LEFT)
        
        tk.Button(speed_frame, text="◀ Медленнее", command=self.slower, width=btn_width).pack(side=tk.LEFT, padx=5)
        
        self.speed_label = tk.Label(speed_frame, text="1.0 сек")
        self.speed_label.pack(side=tk.LEFT, padx=10)
        
        tk.Button(speed_frame, text="Быстрее ▶", command=self.faster, width=btn_width).pack(side=tk.LEFT, padx=5)

        # Холст для изображения
        self.canvas = tk.Canvas(self.root, bg='black', width=600, height=600)
        self.canvas.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # Информационная панель
        info_frame = tk.Frame(self.root)
        info_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
        
        self.info_label = tk.Label(info_frame, text="Откройте папку с QR-кодами", font=('Arial', 12))
        self.info_label.pack()

        # Запускаем обновление
        self.update_display()
        self.root.mainloop()

    def open_folder(self):
        """Открыть папку"""
        if self.select_directory():
            self.show_qr(self.current_index)
            self.info_label.config(text=f"Блок {self.current_index + 1} из {len(self.qr_files)}")

    def toggle_play(self):
        """Воспроизведение/пауза"""
        if not self.qr_files:
            return

        self.is_playing = not self.is_playing
        self.play_button.config(text="⏸ Пауза" if self.is_playing else "▶ Старт")
        
        if self.is_playing:
            self.auto_play()

    def auto_play(self):
        """Автоматическое воспроизведение"""
        if not self.is_playing or not self.qr_files:
            return

        self.current_index = (self.current_index + 1) % len(self.qr_files)
        self.show_qr(self.current_index)
        
        # Планируем следующий кадр
        self.root.after(self.fps_delay, self.auto_play)

    def prev_qr(self):
        """Предыдущий QR-код"""
        if not self.qr_files:
            return
        self.current_index = (self.current_index - 1) % len(self.qr_files)
        self.show_qr(self.current_index)

    def next_qr(self):
        """Следующий QR-код"""
        if not self.qr_files:
            return
        self.current_index = (self.current_index + 1) % len(self.qr_files)
        self.show_qr(self.current_index)

    def zoom_in(self):
        """Увеличить зум"""
        self.zoom_level = min(3.0, self.zoom_level + 0.1)
        self.zoom_label.config(text=f"{self.zoom_level:.1f}x")
        if self.qr_files:
            self.show_qr(self.current_index)

    def zoom_out(self):
        """Уменьшить зум"""
        self.zoom_level = max(0.3, self.zoom_level - 0.1)
        self.zoom_label.config(text=f"{self.zoom_level:.1f}x")
        if self.qr_files:
            self.show_qr(self.current_index)

    def slower(self):
        """Замедлить (увеличить задержку)"""
        self.fps_delay = min(5000, self.fps_delay + 200)
        self.speed_label.config(text=f"{self.fps_delay/1000:.1f} сек")

    def faster(self):
        """Ускорить (уменьшить задержку)"""
        self.fps_delay = max(100, self.fps_delay - 200)
        self.speed_label.config(text=f"{self.fps_delay/1000:.1f} сек")

    def show_qr(self, index: int):
        """Показать QR-код по индексу"""
        if not self.qr_files or index >= len(self.qr_files):
            return

        path, block_num = self.qr_files[index]

        # Загружаем изображение
        img = Image.open(path)
        
        # Применяем зум
        new_width = int(img.width * self.zoom_level)
        new_height = int(img.height * self.zoom_level)
        img = img.resize((new_width, new_height), Image.LANCZOS)

        # Конвертируем для tkinter
        self.photo_image = ImageTk.PhotoImage(img)
        
        # Очищаем и показываем
        self.canvas.delete("all")
        
        # Центрируем изображение
        canvas_width = self.canvas.winfo_width() or 600
        canvas_height = self.canvas.winfo_height() or 600
        x = (canvas_width - new_width) // 2
        y = (canvas_height - new_height) // 2
        
        self.canvas.create_image(x + new_width//2, y + new_height//2, image=self.photo_image, anchor=tk.CENTER)
        
        # Обновляем информацию
        total = len(self.qr_files)
        status = "▶ Воспроизведение" if self.is_playing else "⏸ Пауза"
        self.info_label.config(
            text=f"Блок {block_num} из {total} | {status} | Zoom: {self.zoom_level:.1f}x | Скорость: {self.fps_delay/1000:.1f} сек"
        )

    def update_display(self):
        """Периодическое обновление"""
        if self.qr_files:
            self.show_qr(self.current_index)
        self.root.after(100, self.update_display)

    def on_close(self):
        """Закрытие окна"""
        self.is_playing = False
        self.root.destroy()


def main():
    """Главное меню"""
    print("\n╔══════════════════════════════════════╗")
    print("║   QR CODE DEMO v1.0                 ║")
    print("║   Демонстратор QR-кодов              ║")
    print("╚══════════════════════════════════════╝\n")

    demo = QRCodeDemo()
    demo.run()


if __name__ == "__main__":
    main()