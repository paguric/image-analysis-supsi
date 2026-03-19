import os
from fastapi import FastAPI, UploadFile, File
from app import pipeline
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

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
        "video_prima_url": prima_path,
        "video_dopo_url": dopo_path,
        "video_diff_url": diff_path,
    }
