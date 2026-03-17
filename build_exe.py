"""Скрипт для сборки exe-версий приложения"""
import subprocess
import shutil
import os


def build():
    exe_path = ".venv/Scripts/python.exe"
    
    shutil.rmtree("dist/qr_encoder", ignore_errors=True)
    shutil.rmtree("dist/qr_decoder", ignore_errors=True)
    
    print("Сборка qr_encoder.exe...")
    subprocess.run([exe_path, "-m", "PyInstaller", "--console", "--clean", "--name", "qr_encoder", "qr_encoder.py"])
    
    print("\nСборка qr_decoder.exe...")
    subprocess.run([exe_path, "-m", "PyInstaller", "--console", "--clean", "--name", "qr_decoder", "--collect-all", "pyzbar", "qr_decoder.py"])
    
    print("\nГотово!")
    print("  dist/qr_encoder/qr_encoder.exe")
    print("  dist/qr_decoder/qr_decoder.exe")


if __name__ == "__main__":
    build()
