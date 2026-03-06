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


def main():
    #video_paths = ["video/prima.avi", "video/dopo.avi"]
    #print(f"Does the two videos have the same lenght? {video_reading.check_frames_number(video_paths)}")

    video_dopo_path = "video/dopo.avi"
    video_prima_path = "video/prima.avi"
    
    # <-- EDGE DETECTION --> 
    #roi_identification.compute_roi(video_dopo_path)

    # <-- CONTOUR DETECTION -->

    # <-- CANNY CONTOUR DETECTION -->
    #canny_contour_detection_roi.canny_contour_detection(video_dopo_path)

    # <-- WATERSHED CONTOUR DETECTION -->
    img = cv2.imread("out/prima_fl_161.jpg")
    img = norm.histogram_equalization(img)

    os.makedirs('out/threshold_test', exist_ok=True)
    watershed.watershed_test(img, 42)

if __name__ == "__main__":
    main()
