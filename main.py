import sys
from pathlib import Path

# Ajusta o working directory quando rodando como exe
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys._MEIPASS)  # PyInstaller coloca tudo aqui
else:
    BASE_DIR = Path(__file__).parent

# Importa TrayApp depois de ajustar path
from ui.tray_app import TrayApp

if __name__ == "__main__":
    TrayApp().run()
