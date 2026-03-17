import cv2
import numpy as np
import time
from . import estrazione_contorni
from app import cv2_utils
from app import video_initial_controls as vic


video_to_analyze_path = "video/prima.avi"


def overlay_transparent(background, overlay):
    result = background.copy()
    mask = overlay[:, :, 3] > 0
    result[mask] = overlay[mask, :3]
    return result

def play_video_with_opencv_overlay(video_path, overlay_img):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Errore: impossibile aprire il video.")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    delay = int(1000 / fps) if fps > 0 else 1

    print("Inizio riproduzione...")

    start_time = time.time()
    frame_count = 0

    while cap.isOpened():
        ret, img = cap.read()
        if not ret:
            break

        if img.shape[:2] != overlay_img.shape[:2]:
            overlay_img = cv2.resize(overlay_img, (img.shape[1], img.shape[0]))

        frame_sovrapposto = overlay_transparent(img, overlay_img)
        frame_ridimensionato = cv2.resize(frame_sovrapposto, (1400, 800))

        cv2.imshow(video_to_analyze_path, frame_ridimensionato)

        # Sincronizzazione approssimativa con FPS reale
        elapsed = (time.time() - start_time) * 1000
        expected_time = frame_count * delay
        sleep_time = max(1, int(expected_time - elapsed))
        key = cv2.waitKey(sleep_time) & 0xFF
        if key == ord('q'):
            break

        frame_count += 1

    end_time = time.time()
    
    print(f"Riproduzione terminata. Frame elaborati: {frame_count} su {vic.count_frames(video_path)}")
    cap.release()
    cv2.destroyAllWindows()
    
    

    print("Durata video:", cv2_utils.time_convert(end_time - start_time))



print("Avvio estrazione contorni...")
contours = estrazione_contorni.return_computed_contours(video_to_analyze_path)
print("Estrazione completata. Avvio player...")
play_video_with_opencv_overlay(video_to_analyze_path, contours)