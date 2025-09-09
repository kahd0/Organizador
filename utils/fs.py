import platform
import subprocess
from pathlib import Path

def open_folder(path: str | Path) -> None:
    """Abre uma pasta no explorador de arquivos do SO."""
    p = str(path)
    so = platform.system()
    try:
        if so == "Windows":
            subprocess.Popen(["explorer", p])
        elif so == "Darwin":
            subprocess.Popen(["open", p])
        else:
            subprocess.Popen(["xdg-open", p])
    except Exception as e:
        print(f"Não foi possível abrir a pasta '{p}': {e}")

def safe_remove_dir_if_empty(path: Path) -> bool:
    """
    Remove o diretório se e somente se estiver vazio.
    Retorna True se removeu, False caso contrário.
    """
    try:
        if path.is_dir():
            # se não houver nada dentro, remove
            if not any(path.iterdir()):
                path.rmdir()
                return True
    except Exception as e:
        # não remove se houver erro (por exemplo, permissões)
        print(f"Falha ao remover diretório '{path}': {e}")
    return False
