from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import video_reading
from app import roi_identification
from app import contour_detection
from app import canny_contour_detection_roi
from app import preprocessing

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


def main():
    #video_paths = ["video/prima.avi", "video/dopo.avi"]
    #print(f"Does the two videos have the same lenght? {video_reading.check_frames_number(video_paths)}")

    video_dopo_path = "video/dopo.avi"
    video_prima_path = "video/prima.avi"
    
    # <-- EDGE DETECTION -->
    #roi_identification.compute_roi(video_dopo_path)

    # preprocessing
    #rm -rf video/threshold_test/*
    #rm -rf video/brightness_test/*
    #rm -rf video/contrast_test/*
    #preprocessing.threshold_test(video_dopo_path)
    #preprocessing.brightness_test(video_dopo_path)
    #preprocessing.contrast_test(video_dopo_path)

    preprocessing.extract_frame(video_prima_path, f"video_prima_{i}")
    preprocessing.extract_frame(video_dopo_path, f"video_dopo_{i}")

    # <-- CONTOUR DETECTION -->

    # <-- CANNY CONTOUR DETECTION -->
    #canny_contour_detection_roi.canny_contour_detection(video_dopo_path)

if __name__ == "__main__":
    main()
