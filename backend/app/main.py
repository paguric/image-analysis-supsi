import os
import sys
import threading
import subprocess
import uvicorn
import mimetypes
import webview
from fastapi.responses import FileResponse
from moviepy.editor import VideoFileClip
from app import pipeline
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles



# se il codice sta eseguendo dentro l'exe allora la cartella contenente i video
# sarà creata di fianco a all'exe dell'applicazione (perché essendo tutto già compresso
# non possiamo salvare in posizioni interne al programma). Se invece il codice sta eseguendo
# "normalmente" (nel senso che lo avviamo tramite comando), la cartella con i video sarà 
# creata di fianco al main. 
if getattr(sys, 'frozen', False):
    output_dir = os.path.join(os.path.dirname(sys.executable), "out")
else:
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")

os.makedirs(output_dir, exist_ok=True)


# usiamo WebM con codec video VP8, un formato apposta per il web
# meglio non usare mp4, altrimenti su linux potrebbe causare problemi
# in quanto mp4 è un formato proprietario.
mimetypes.add_type('video/webm', '.webm')


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
# - dentro l'exe (frozen): PyInstaller ha copiato frontend/dist → static/
# - in sviluppo: punta direttamente a frontend/dist
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
    static_dir = os.path.join(base_path, "static")
else:
    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "frontend", "dist")
    # in sviluppo rebuilda automaticamente il frontend
    frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "frontend")
    subprocess.run(["npm", "run", "build"], cwd=frontend_dir, check=True)



# NON AVEVI MESSO IL TIPE HINT!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! tennis
@app.get("/")
async def root() -> FileResponse:
    return FileResponse(os.path.join(static_dir, "index.html"))



# NON AVEVI MESSO IL TIPE HINT!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! pallina
@app.post("/analyze")
async def analyze(
    video_prima: UploadFile = File(...), video_dopo: UploadFile = File(...)
) -> dict[str, str]:
    prima_bytes = await video_prima.read()
    dopo_bytes = await video_dopo.read()

    prima_avi_path = os.path.join(output_dir, "prima.avi")
    dopo_avi_path  = os.path.join(output_dir, "dopo.avi")
    diff_avi_path  = os.path.join(output_dir, "diff.avi")

    # Salva i file caricati
    with open(prima_avi_path, "wb") as f:
        f.write(prima_bytes)
    with open(dopo_avi_path, "wb") as f:
        f.write(dopo_bytes)

    pipeline.analyze(prima_avi_path, dopo_avi_path, diff_avi_path)

    # È necessario convertire i video in WebM perchè i browser non supportano gli avi
    prima_webm_path = os.path.join(output_dir, "prima.webm")
    dopo_webm_path  = os.path.join(output_dir, "dopo.webm")
    diff_webm_path  = os.path.join(output_dir, "diff.webm")

    clip = VideoFileClip(prima_avi_path)
    clip.write_videofile(prima_webm_path, codec="libvpx", audio=False)
    clip.close()

    clip = VideoFileClip(dopo_avi_path)
    clip.write_videofile(dopo_webm_path, codec="libvpx", audio=False)
    clip.close()

    clip = VideoFileClip(diff_avi_path)
    clip.write_videofile(diff_webm_path, codec="libvpx", audio=False)
    clip.close()

    return {
        "video_prima_url": "/videos/prima.webm",
        "video_dopo_url": "/videos/dopo.webm",
        "video_diff_url": "/videos/diff.webm",
    }




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
    
    
    

if __name__ == "__main__":
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
    webview.start()