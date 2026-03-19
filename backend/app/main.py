import os
from moviepy.editor import VideoFileClip
from app import pipeline
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles


app = FastAPI()
app.mount("/videos", StaticFiles(directory="out"), name="videos")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


OUTPUT_DIR = "out"


@app.post("/analyze")
async def analyze(
    video_prima: UploadFile = File(...), video_dopo: UploadFile = File(...)
):
    prima_bytes = await video_prima.read()
    dopo_bytes = await video_dopo.read()

    prima_avi_path = f"{OUTPUT_DIR}/prima.avi"
    dopo_avi_path = f"{OUTPUT_DIR}/dopo.avi"
    diff_avi_path = f"{OUTPUT_DIR}/diff.avi"

    # Salva i file caricati
    with open(prima_avi_path, "wb") as f:
        f.write(prima_bytes)
    with open(dopo_avi_path, "wb") as f:
        f.write(dopo_bytes)

    pipeline.analyze(prima_avi_path, dopo_avi_path, diff_avi_path)

    # È necessario convertire i video in mp4 perchè i browser non supportano gli avi
    prima_mp4_path = f"{OUTPUT_DIR}/prima.mp4"
    dopo_mp4_path = f"{OUTPUT_DIR}/dopo.mp4"
    diff_mp4_path = f"{OUTPUT_DIR}/diff.mp4"

    clip = VideoFileClip(prima_avi_path)
    clip.write_videofile(prima_mp4_path, codec="libx264", audio_codec="aac")
    clip.close()

    clip = VideoFileClip(dopo_avi_path)
    clip.write_videofile(dopo_mp4_path, codec="libx264", audio_codec="aac")
    clip.close()

    clip = VideoFileClip(diff_avi_path)
    clip.write_videofile(diff_mp4_path, codec="libx264", audio_codec="aac")
    clip.close()

    return {
        "video_prima_url": "http://localhost:8000/videos/prima.mp4",
        "video_dopo_url": "http://localhost:8000/videos/dopo.mp4",
        "video_diff_url": "http://localhost:8000/videos/diff.mp4",
    }
