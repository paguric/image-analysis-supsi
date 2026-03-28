import os
import subprocess
import uvicorn

from app.routers import pipeline_controller, roi_controller
from app.db import database

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pipeline_controller.router)
app.include_router(roi_controller.router)

# percorso base ai file statici del frontend
base_path = os.path.dirname(os.path.abspath(__file__))
# cartella che contiene le build dei file react. pyinstaller la copia dentro l'exe
static_dir = os.path.join(base_path, "..", "..", "frontend", "dist")


# aggiungendo queste due righe sto facendo in modo che automaticamente,
# quando avvio il backend, venga lanciato anche un "npm run build", di modo
# da sostituire il codice compilato "vecchio" presente in dist (che è
# la cartella dove viene messo il codice compilato che il browser è
# in grado di interpretare)
frontend_dir = os.path.join(base_path, "..", "..", "frontend")
#subprocess.run(["npm", "run", "build"], cwd=frontend_dir, check=True)

@app.on_event("startup")
def on_startup():
    database.create_db_and_tables()


@app.on_event("shutdown")
def on_shutdown():
    os.remove("database.db")


@app.get("/")
async def root() -> FileResponse:
    return FileResponse(os.path.join(static_dir, "index.html"))


# fallback di sicurezza, se il file richiesto esiste (file statico di React)
# lo restitutisce, altrimenti ti butta all'index
@app.get("/{full_path:path}")
def serve_frontend(full_path: str) -> FileResponse:
    file = os.path.join(static_dir, full_path)
    if os.path.isfile(file):
        return FileResponse(file)
    return FileResponse(os.path.join(static_dir, "index.html"))


# avvia uvicorn che fa da intermediario tra la rete (locale) e FastAPI:
# raccoglie le richieste HTTP da PyWebView, le passa a FastAPI,
# e rimanda le risposte indietro.
def start_server() -> None:
    # i parametri sono: quale fastapi chiamare,
    #                   specificare che deve ascoltare solo connessioni locali,
    #                   la porta da ascoltare,
    #                   stampa solo gli errori.
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")


"""if __name__ == "__main__":
    # avvia il server in un thread separato (daemon).
    # Bisogna fare così perché uvicorn è bloccante, se girasse sul thread
    # principale bloccherebbe l'esecuzione e la finestra non si aprirebbe mai.
    # Essendo daemon, il thread si ferma automaticamente quando la finestra viene chiusa.
    threading.Thread(target=start_server, daemon=True).start()
    # questo semplicemente regista la finestra di PyWebView con le varie specifiche
    webview.create_window(
        "Image Analysis",
        "http://localhost:8000",
        width=1200,
        height=800,
        resizable=True,
    )
    # questo apre effettivamente la finestra e la mantiene aperta
    webview.start(debug=True)"""
