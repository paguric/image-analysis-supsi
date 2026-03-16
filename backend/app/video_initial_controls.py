import cv2

def count_frames(input_path):
    cap = cv2.VideoCapture(input_path)

    video_name = input_path.split("\\")

    if(cap.isOpened()):
        print(video_name[-1] +" founded")

    count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        count += 1
    cap.release()
    print(f"Extracted {count} frames.")

    return count


def check_frames_number(video_paths):
    first_video = count_frames(video_paths[0])
    second_video = count_frames(video_paths[1])

    return first_video == second_video
   