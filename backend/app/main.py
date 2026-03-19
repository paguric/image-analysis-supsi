from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import cv2

from app import preprocessing
from app import cv2_utils
from app import norm
from app import video_reading
from app import edge_detection
from app import contour_detection
from app import canny_contour_detection_roi
from app import watershed

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
