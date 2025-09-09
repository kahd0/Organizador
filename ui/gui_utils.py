from PySide6.QtWidgets import QWidget

def show_and_raise(win: QWidget) -> None:
    """Exibe e traz a janela para frente."""
    win.show()
    win.raise_()
    win.activateWindow()
