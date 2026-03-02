from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import video_reading
from app import roi_identification
from app import contour_detection
from app import canny_contour_detection_roi
from app import threshold

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

    video_to_analyze_path = "video/dopo.avi"
    
    # <-- EDGE DETECTION -->
    #roi_identification.compute_roi(video_to_analyze_path)

    # <-- CONTOUR DETECTION -->
    #rm -rf video/threshold_test/*
    threshold.threshold_test(video_to_analyze_path)

    # <-- CANNY CONTOUR DETECTION -->
    #canny_contour_detection_roi.canny_contour_detection(video_to_analyze_path)

if __name__ == "__main__":
    main()
