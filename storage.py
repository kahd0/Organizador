import json
import datetime
from pathlib import Path
import config  # importar o módulo inteiro
from typing import List, Dict
import shutil

def carregar_atividades() -> List[Dict]:
    """
    Percorre a pasta de atividades recursivamente e retorna a lista de atividades.
    Cada atividade terá o campo 'caminho' com o path da pasta.
    Atualiza status para 'Atrasado' se necessário (em memória).
    Remove pastas de Requisitos vazias.
    """
    atividades = []

    try:
        raiz = config.PASTA_ATIVIDADES
        if not raiz.exists():
            raiz.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"Erro ao garantir PASTA_ATIVIDADES: {e}")

    # --- Percorre e carrega atividades ---
    for arquivo_json in config.PASTA_ATIVIDADES.rglob("atividade.json"):
        try:
            with open(arquivo_json, "r", encoding="utf-8") as f:
                at = json.load(f)

            # Ajusta status se necessário
            try:
                prazo = datetime.date.fromisoformat(at["prazo"])
                hoje = datetime.date.today()
                if at.get("status") != "Finalizado" and prazo < hoje:
                    at["status"] = "Atrasado"
            except Exception:
                pass  # prazo ausente ou inválido

            # Guarda caminho da atividade
            at["caminho"] = str(arquivo_json.parent)
            atividades.append(at)

        except Exception as e:
            print(f"Erro ao ler {arquivo_json}: {e}")

    # --- Limpa pastas de Requisitos vazias ---
    for requisito_pasta in raiz.iterdir():
        if requisito_pasta.is_dir():
            # Se não houver nenhum arquivo ou subpasta dentro, remove
            if not any(requisito_pasta.rglob("*")):
                try:
                    shutil.rmtree(requisito_pasta)
                    print(f"Removida pasta vazia de requisito: {requisito_pasta}")
                except Exception as e:
                    print(f"Erro ao remover pasta {requisito_pasta}: {e}")

    return atividades
