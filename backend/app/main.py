import os
import sys
import threading
import uvicorn
import webview

from app.routers import pipeline_controller, roi_controller, analysis_controller
from app.db import database

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse


from app.db.database import get_db_path


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pipeline_controller.router)
app.include_router(roi_controller.router)
app.include_router(analysis_controller.router)


# NON CANCELLARE
def get_base_path() -> str:
    """Percorso root dei file bundlati (o del sorgente in dev)."""
    if getattr(sys, "frozen", False):
        # Siamo dentro il bundle PyInstaller
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


# NON CANCELLARE
def get_exe_dir() -> str:
    """Cartella dove si trova l'exe (o il sorgente in dev).
    Usata per file scrivibili (db, output) — mai dentro _MEIPASS che è read-only."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    # In dev, risale alla root del progetto (due livelli sopra backend/)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")


# Percorso base ai file statici del frontend
base_path = get_base_path()
exe_dir = get_exe_dir()

# Cartella che contiene le build dei file React - PyInstaller la copia dentro il bundle
static_dir = os.path.join(base_path, "frontend", "dist")

# Percorso del database - accanto all'exe (mai dentro _MEIPASS che è read-only)
db_path = get_db_path()


# Creazione db all'avvio dell'app
@app.on_event("startup")
def on_startup():

    # Rimozione db vecchio
    if os.path.isfile(db_path):
        os.remove(db_path)
        print(f"{db_path} è stato eliminato con successo")
    else:
        print(f"Nessun db precedente trovato in {db_path}")

    database.create_db_and_tables()


@app.get("/")
async def root() -> FileResponse:
    return FileResponse(os.path.join(static_dir, "index.html"))


# Fallback di sicurezza: se il file richiesto esiste (file statico di React)
# lo restituisce, altrimenti rimanda all'index
@app.get("/{full_path:path}")
def serve_frontend(full_path: str) -> FileResponse:
    file = os.path.join(static_dir, full_path)
    if os.path.isfile(file):
        return FileResponse(file)
    return FileResponse(os.path.join(static_dir, "index.html"))


# Avvia uvicorn che fa da intermediario tra la rete (locale) e FastAPI:
# raccoglie le richieste HTTP da PyWebView, le passa a FastAPI,
# e rimanda le risposte indietro.
def start_server() -> None:
    # i parametri sono: quale fastapi chiamare,
    #                   specificare che deve ascoltare solo connessioni locali,
    #                   la porta da ascoltare,
    #                   stampa solo gli errori.
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")


if __name__ == "__main__":
    # Avvia il server in un thread separato (daemon).
    # Bisogna fare così perché uvicorn è bloccante: se girasse sul thread
    # principale bloccherebbe l'esecuzione e la finestra non si aprirebbe mai.
    # Essendo daemon, il thread si ferma automaticamente quando la finestra viene chiusa.
    threading.Thread(target=start_server, daemon=True).start()
    # Registra la finestra di PyWebView con le varie specifiche
    webview.create_window(
        "Image Analysis",
        "http://localhost:8000",
        width=1200,
        height=800,
        resizable=True,
    )
    # Apre effettivamente la finestra e la mantiene aperta
    webview.start()
