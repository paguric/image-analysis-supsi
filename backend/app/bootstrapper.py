import sys
import os
from pathlib import Path

APP_DIR_NAME = ".image-analysis"


def _is_frozen() -> bool:
    """Ritorna True se il programma è in esecuzione come bundle PyInstaller."""
    return getattr(sys, "frozen", False)


def get_app_dir() -> Path:
    """
    Ritorna la cartella dell'app:
    - In produzione: cartella nascosta nella home dell'utente
    - In sviluppo: root del progetto (due livelli sopra backend/)
    """
    if _is_frozen():
        return Path.home() / APP_DIR_NAME
    return Path(os.path.dirname(os.path.abspath(__file__))).parent.parent


def get_db_path() -> Path:
    return get_app_dir() / "database.db"


def get_out_dir() -> Path:
    return get_app_dir() / "out"


def bootstrap():
    """
    Crea la cartella nascosta nella home dell'utente e le sottocartelle necessarie.
    In sviluppo non fa nulla di speciale — le cartelle esistono già nel progetto.
    Chiamare all'avvio, prima di qualsiasi altra operazione.
    """
    app_dir = get_app_dir()
    app_dir.mkdir(exist_ok=True)

    # Su Windows, nasconde la cartella (su Linux/Mac il punto iniziale basta)
    if _is_frozen() and sys.platform == "win32":
        import subprocess
        subprocess.run(["attrib", "+H", str(app_dir)], check=False, capture_output=True)

    # Cancella il db vecchio — viene ricreato da SQLAlchemy all'avvio
    db_path = get_db_path()
    if db_path.exists():
        db_path.unlink()