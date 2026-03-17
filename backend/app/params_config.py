from typing import TypedDict
from typing import TypeAlias
import numpy as np

class MatchedContour(TypedDict):
    center:  tuple[int, int]
    contour: np.ndarray

Color: TypeAlias = tuple[int, int, int]

# ─────────────────────────────────────────────
#  COSTANTI COLORE
# ─────────────────────────────────────────────

BLUE:   Color = (255, 0, 0)
RED:    Color = (0, 0, 255)
GREEN:  Color = (0, 255, 0)
YELLOW: Color = (0, 255, 255)
WHITE:  Color = (255, 255, 255)
BLACK:  Color = (0, 0, 0)

PARAMS = {
    "bg_blur_size":     101,
    "canny_low":        0,
    "canny_high":       0,
    "clahe_grid_dim":   8,
    "morph_kernel_size": 3,
    "morph_iterations":  4,
    "min_area":          5000,
    "min_circularity":   0.10,
}

# spazio tra immagini
BORDER = 40

# altezza fascia titolo
TITLE_BAR = 200