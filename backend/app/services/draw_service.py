import cv2
import numpy as np
from app import params_config as parcon


def draw_contour(img, contour, color, thickness=2):
    cv2.drawContours(img, [contour], -1, color, thickness)


def draw_bounding_box(img, contour, color, thickness=2):
    x, y, w, h = cv2.boundingRect(contour)
    cv2.rectangle(img, (x, y), (x + w, y + h), color, thickness)


def draw_circle(img, center, radius=6, color=(255, 0, 0), filled=True):
    thickness = -1 if filled else 2
    cv2.circle(img, center, radius, color, thickness)


def draw_label(img, text, position, color, font_scale=0.6, thickness=2):
    cv2.putText(
        img, str(text), position, cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness
    )


def draw_line(img, pt1, pt2, color, thickness=1):
    cv2.line(img, pt1, pt2, color, thickness, cv2.LINE_AA)


def side_by_side(img_left, img_right):
    return np.hstack([img_left, img_right])


def draw_contours_on_image(img, contour_map):
    black_img = np.zeros_like(img)

    for i, (center, cnt) in enumerate(contour_map.items(), start=1):
        draw_contour(black_img, cnt, color=parcon.GREEN)
        draw_bounding_box(black_img, cnt, color=parcon.YELLOW)
        draw_label(
            black_img, i, position=(center[0], center[1] - 10), color=parcon.YELLOW
        )
        draw_circle(black_img, center, color=parcon.BLUE)

        centroid = geo_help.contour_centroid(cnt)
        if centroid:
            draw_circle(black_img, centroid, color=parcon.RED)

    b, g, r = cv2.split(black_img)
    alpha = cv2.max(cv2.max(b, g), r)
    _, alpha = cv2.threshold(alpha, 0, 255, cv2.THRESH_BINARY)
    transparent_img = cv2.merge((b, g, r, alpha))

    return transparent_img


def draw_centers_on_image(img, contour_map1, contour_map2):
    output = img.copy()
    for center, cnt in contour_map1.items():
        draw_circle(output, center, color=parcon.RED)
    for center, cnt in contour_map2.items():
        draw_circle(output, center, color=parcon.BLUE)
    return output


def draw_matched_contours(
    img: np.ndarray,
    matched_left: dict[int, parcon.MatchedContour],
    matched_right: dict[int, parcon.MatchedContour],
) -> np.ndarray:
    output = img.copy()
    for idx in matched_left:
        center_l, contour_l = matched_left[idx]["center"], matched_left[idx]["contour"]
        center_r, contour_r = (
            matched_right[idx]["center"],
            matched_right[idx]["contour"],
        )

        x, y, w, h = cv2.boundingRect(contour_l)
        draw_circle(
            output, center=center_l, radius=w // 2, color=parcon.BLUE, filled=False
        )
        draw_label(
            output,
            idx,
            (center_l[0] - h // 2, center_l[1] - h // 2),
            parcon.BLUE,
            0.6,
            2,
        )

        x, y, w, h = cv2.boundingRect(contour_r)
        draw_circle(
            output, center=center_l, radius=w // 2, color=parcon.RED, filled=False
        )
        draw_label(
            output,
            idx,
            (center_l[0] + h // 2, center_l[1] + h // 2),
            parcon.RED,
            0.6,
            2,
        )

    return output
