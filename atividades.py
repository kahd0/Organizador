import json
import datetime
from pathlib import Path
import config  # IMPORTAR O MÓDULO INTEIRO, não a variável

def carregar_atividades():
    """
    Percorre a pasta de atividades recursivamente e retorna a lista de atividades.
    Cada atividade terá o campo 'caminho' com o path da pasta.
    Atualiza status para 'Atrasado' se necessário.
    """
    atividades = []

    for arquivo_json in config.PASTA_ATIVIDADES.rglob("atividade.json"):
        try:
            with open(arquivo_json, "r", encoding="utf-8") as f:
                at = json.load(f)

            # Ajusta status se necessário
            prazo = datetime.date.fromisoformat(at["prazo"])
            hoje = datetime.date.today()
            if at["status"] != "Finalizado" and prazo < hoje:
                at["status"] = "Atrasado"

            # Guarda caminho da atividade
            at["caminho"] = str(arquivo_json.parent)
            atividades.append(at)

        except Exception as e:
            print(f"Erro ao ler {arquivo_json}: {e}")

    return atividades
