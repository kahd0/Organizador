import json
from pathlib import Path
import sys

# Ajusta base_dir para exe
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys._MEIPASS)
else:
    BASE_DIR = Path(__file__).parent

# Arquivo de persistência
CONFIG_FILE = BASE_DIR / "config_data.json"

# Caminhos padrão (pode ser personalizado)
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
        except Exception as e:
            print(f"Erro ao carregar configuração: {e}")

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

# Carrega a configuração ao importar
carregar_config()
