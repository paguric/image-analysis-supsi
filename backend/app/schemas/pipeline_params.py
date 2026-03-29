from pydantic import BaseModel


class PipelineParams(BaseModel):
    bg_blur_size:       int = 101
    canny_low:          int = 0
    canny_high:         int = 0
    clahe_grid_dim:     int = 8
    morph_kernel_size:  int = 3
    morph_iterations:   int = 4
    min_area:           int = 5000
    min_circularity:    float = 0.10