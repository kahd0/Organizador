from pathlib import Path
from PySide6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QFileDialog
import config

class ConfigWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Configurações")
        self.setMinimumWidth(480)

        # --- Campo Pasta Pendentes ---
        self.label_pending = QLabel("Pasta de Atividades Pendentes:")
        self.input_pending = QLineEdit(str(config.PASTA_ATIVIDADES))
        self.btn_pending = QPushButton("Alterar...")
        self.btn_pending.clicked.connect(self.select_pending_folder)

        # --- Campo Pasta Finalizadas ---
        self.label_completed = QLabel("Pasta de Atividades Concluídas:")
        self.input_completed = QLineEdit(str(config.PASTA_FINALIZADAS))
        self.btn_completed = QPushButton("Alterar...")
        self.btn_completed.clicked.connect(self.select_completed_folder)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.label_pending)
        layout.addWidget(self.input_pending)
        layout.addWidget(self.btn_pending)
        layout.addSpacing(20)
        layout.addWidget(self.label_completed)
        layout.addWidget(self.input_completed)
        layout.addWidget(self.btn_completed)
        self.setLayout(layout)

    def select_pending_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Selecione a pasta de atividades pendentes")
        if folder:
            config.PASTA_ATIVIDADES = Path(folder)
            self.input_pending.setText(folder)
            config.salvar_config()  # salva imediatamente

    def select_completed_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Selecione a pasta de atividades concluídas")
        if folder:
            config.PASTA_FINALIZADAS = Path(folder)
            self.input_completed.setText(folder)
            config.salvar_config()  # salva imediatamente
