import numpy as np
from matplotlib import pyplot as plt


def plot_histogram(
    frame: np.ndarray, log_scale: bool = False, normalized: bool = False
):
    """
    -> Attualmente inutilizzata
    Mostra il frame e a fianco il suo relativo istogramma con Matplotlib
    È possibile attivare la visualizzazione in scala logaritmica e/o con valori normalizzati (da 0.0 a 1.0)
    src: https://docs.opencv.org/4.x/d1/db7/tutorial_py_histogram_begins.html
    chat: https://claude.ai/share/8b8adb6e-83a1-49a0-8dbd-51e286991413
    """
    assert frame is not None, "frame could not be read"

    img = frame.astype(np.float32) / 255.0 if normalized else frame
    x_range = [0, 1] if normalized else [0, 256]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

    # Show image
    ax1.imshow(img, cmap="gray", vmin=0, vmax=1)
    ax1.set_title("Image")
    ax1.axis("off")

    # Show histogram
    ax2.hist(img.ravel(), 256, x_range)
    if log_scale:
        ax2.set_yscale("log")
    ax2.set_title("Histogram")
    ax2.set_xlabel("Intensity")
    ax2.set_ylabel("Pixel Count")

    # plt.yscale('log')
    plt.tight_layout()
    plt.show()


def time_convert(seconds):
    """
    -> Attualmente inutilizzata
    """
    mins = seconds // 60
    secs = seconds % 60
    return f"{int(mins)}:{int(secs):02d}"
