import video_reading
import roi_identification


def main():
    video_paths = [r"video\\prima.avi", r"video\\dopo.avi"]
    # print(f"Does the two videos have the same lenght? {video_reading.check_frames_number(video_paths)}")

    video_to_analyze_path = "video/dopo.avi"
    roi_identification.compute_roi(video_to_analyze_path)




if __name__ == "__main__":
    main()