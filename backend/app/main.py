import os
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

    prima_path = f"{OUTPUT_DIR}/prima.avi"
    dopo_path = f"{OUTPUT_DIR}/dopo.avi"
    diff_path = f"{OUTPUT_DIR}/diff.avi"

    with open(prima_path, "wb") as f:
        f.write(prima_bytes)
    with open(dopo_path, "wb") as f:
        f.write(dopo_bytes)

    pipeline.analyze(prima_path, dopo_path, diff_path)

    return {
        "video_prima_url": "http://localhost:8000/videos/prima.avi",
        "video_dopo_url": "http://localhost:8000/videos/dopo.avi",
        "video_diff_url": "http://localhost:8000/videos/diff.avi",
    }
