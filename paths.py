from pathlib import Path
from typing import Optional

REQUISITO_PREFIX = "Requisito - "

def requisito_folder_name(requisito: str) -> str:
    return f"{REQUISITO_PREFIX}{requisito}"

def activity_folder_name(tipo: str, id_: str) -> str:
    return f"{tipo} - {id_}"

def requisito_dir(base: Path, requisito: Optional[str]) -> Path:
    """Se houver requisito, retorna base/Requisito - X. Senão, retorna base."""
    if requisito:
        return base / requisito_folder_name(requisito)
    return base

def is_requisito_dir(path: Path) -> bool:
    return path.is_dir() and path.name.startswith(REQUISITO_PREFIX)
