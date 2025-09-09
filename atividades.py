import json
import datetime
from pathlib import Path
from config import PASTA_ATIVIDADES

def carregar_atividades():
    """
    Percorre a pasta de atividades recursivamente e retorna a lista de atividades.
    Cada atividade terá o campo 'caminho' com o path da pasta.
    Atualiza status para 'Atrasado' se necessário.
    """
    atividades = []

    base = PASTA_ATIVIDADES
    if not base.exists():
        # Não existir a pasta não é erro grave — apenas retorna lista vazia.
        return atividades

    for arquivo_json in base.rglob("atividade.json"):
        try:
            with open(arquivo_json, "r", encoding="utf-8") as f:
                at = json.load(f)

            if not isinstance(at, dict):
                continue

            # Ajusta status se necessário (se houver campo "prazo")
            prazo_str = at.get("prazo")
            if prazo_str:
                try:
                    prazo = datetime.date.fromisoformat(prazo_str)
                    hoje = datetime.date.today()
                    if at.get("status") != "Finalizado" and prazo < hoje:
                        at["status"] = "Atrasado"
                except Exception:
                    # formato inválido: ignora ajuste de prazo
                    pass

            # Guarda caminho da atividade
            at["caminho"] = str(arquivo_json.parent)
            atividades.append(at)

        except Exception as e:
            print(f"Erro ao ler {arquivo_json}: {e}")

    return atividades
