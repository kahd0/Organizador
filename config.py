import json
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QFileDialog
)

# Arquivo de persistência
CONFIG_FILE = Path("config_data.json")

# Caminhos padrão
DEFAULT_PENDING = Path(r"C:\Atividades\Pendentes")
DEFAULT_COMPLETED = Path(r"C:\Atividades\Finalizadas")

# Variáveis globais
PASTA_ATIVIDADES = DEFAULT_PENDING
PASTA_FINALIZADAS = DEFAULT_COMPLETED

# Ícones de status
ICONES_STATUS = {
    "Finalizado": "✔️",
    "Em andamento": "⏳",
    "Aguardando": "💤",
    "Atrasado": "⚠️"
}

# ------------------------
# Funções de persistência
# ------------------------
def carregar_config():
    global PASTA_ATIVIDADES, PASTA_FINALIZADAS
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            pending = data.get("pending")
            completed = data.get("completed")
            if pending:
                PASTA_ATIVIDADES = Path(pending)
            if completed:
                PASTA_FINALIZADAS = Path(completed)
        except Exception:
            pass  # se falhar, continua com valores padrão

def salvar_config():
    data = {
        "pending": str(PASTA_ATIVIDADES),
        "completed": str(PASTA_FINALIZADAS)
    }
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Erro ao salvar configuração: {e}")

# ------------------------
# Janela de configuração
# ------------------------
class ConfigWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Configurações")
        self.setMinimumWidth(400)

        # --- Campo Pasta Pendentes ---
        self.label_pending = QLabel("Pasta de Atividades Pendentes:")
        self.input_pending = QLineEdit(str(PASTA_ATIVIDADES))
        self.btn_pending = QPushButton("Alterar...")
        self.btn_pending.clicked.connect(self.select_pending_folder)

        # --- Campo Pasta Finalizadas ---
        self.label_completed = QLabel("Pasta de Atividades Concluídas:")
        self.input_completed = QLineEdit(str(PASTA_FINALIZADAS))
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
        global PASTA_ATIVIDADES
        folder = QFileDialog.getExistingDirectory(self, "Selecione a pasta de atividades pendentes")
        if folder:
            PASTA_ATIVIDADES = Path(folder)
            self.input_pending.setText(folder)
            salvar_config()  # salva imediatamente

    def select_completed_folder(self):
        global PASTA_FINALIZADAS
        folder = QFileDialog.getExistingDirectory(self, "Selecione a pasta de atividades concluídas")
        if folder:
            PASTA_FINALIZADAS = Path(folder)
            self.input_completed.setText(folder)
            salvar_config()  # salva imediatamente

# Carrega a configuração ao importar
carregar_config()
