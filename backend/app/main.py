from http.client import HTTPException
import io
import os
import sys
import cv2
import threading
import subprocess
import uvicorn
import mimetypes
import webview
import numpy as np
from PIL import Image

from app import pipeline
from app import cv2_utils
from app import roi_controller
from app import pipeline_controller
from app.roi_controller import ROI

from fastapi.responses import FileResponse
from moviepy.editor import VideoFileClip
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from fastapi import FastAPI, UploadFile, File, HTTPException


# se il codice sta eseguendo dentro l'exe allora la cartella contenente i video
# sarà creata di fianco a all'exe dell'applicazione (perché essendo tutto già compresso
# non possiamo salvare in posizioni interne al programma). Se invece il codice sta eseguendo
# "normalmente" (nel senso che lo avviamo tramite comando), la cartella con i video sarà
# creata di fianco al main.
if getattr(sys, "frozen", False):
    output_dir = os.path.join(os.path.dirname(sys.executable), "out")
else:
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")

os.makedirs(output_dir, exist_ok=True)


# usiamo WebM con codec video VP8, un formato apposta per il web
# meglio non usare mp4, altrimenti su linux potrebbe causare problemi
# in quanto mp4 è un formato proprietario.
mimetypes.add_type("video/webm", ".webm")


app = FastAPI()


# monta la cartella dei video sull'endpoint /videos, così il frontend
# può accedere ai video generati tramite URL (es. http://localhost:8000/videos/prima.webm)
app.mount("/videos", StaticFiles(directory=output_dir), name="videos")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


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
subprocess.run(["npm", "run", "build"], cwd=frontend_dir, check=True)


@app.get("/")
async def root() -> FileResponse:
    return FileResponse(os.path.join(static_dir, "index.html"))


roi_prima: list[ROI] | None = None
roi_dopo: list[ROI] | None = None

@app.post("/analyze")
async def analyze(
    video_prima: UploadFile = File(...), video_dopo: UploadFile = File(...)
) -> dict[str, str]:
    global roi_prima, roi_dopo

    prima_bytes = await video_prima.read()
    dopo_bytes = await video_dopo.read()

    prima_avi_path = os.path.join(output_dir, "prima.avi")
    dopo_avi_path = os.path.join(output_dir, "dopo.avi")

    # Salva i file caricati
    with open(prima_avi_path, "wb") as f:
        f.write(prima_bytes)
    with open(dopo_avi_path, "wb") as f:
        f.write(dopo_bytes)

    roi_prima = pipeline_controller.extract_rois(prima_avi_path)
    roi_dopo = pipeline_controller.extract_rois(dopo_avi_path)

    # NON DIMENTICARLO
    roi_controller.match_rois_by_center(roi_prima, roi_dopo)

    return {"TODO": "TODO"}


@app.get("/diff/{frame}")
def get_diff(frame: int) -> str:
    if roi_prima is None or roi_dopo is None:
        raise HTTPException(status_code=400, detail="No images uploaded yet")

    diff = roi_controller.compute_aligned_roi_diff(roi_prima, roi_dopo, frame)

    diff_rgb = cv2.cvtColor(diff, cv2.COLOR_BGR2RGB)
    _, buffer = cv2.imencode(".jpg", diff_rgb)
    io_buffer = io.BytesIO(buffer)

    return StreamingResponse(io_buffer, media_type="image/jpeg")


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
