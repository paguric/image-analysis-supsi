import cv2
import numpy as np
from app.helpers import cv2_utils


def minmax_norm(
    img: np.ndarray, min_percentile: float = 0.0, max_percentile: float = 99.0
):
    """
    Minmax prende il valore più basso presente nell'immagine e lo porta a 0, prende il più
    Alto e lo porta a 255, e distribuisce proporzionalmente tutti gli altri valori nel mezzo
    Per migliorare la precisione, applichiamo qua percentile clipping (o percentile stretching)
    """

    low = np.percentile(img, min_percentile)
    high = np.percentile(img, max_percentile)

    img_clipped = np.clip(img, low, high)
    img_normalized = cv2.normalize(img_clipped, None, 0, 255, cv2.NORM_MINMAX)

    return img_normalized.astype(np.uint8)


def histogram_equalization(frame: np.ndarray) -> np.ndarray | None:
    """
    Immagina l'istogramma come un grafico che mostra quanti pixel ci sono per ogni tonalità (da nero a bianco):

    Se l'immagine è troppo chiara, i dati sono tutti accumulati a destra
    Se è troppo scura, sono tutti a sinistra
    Se ha poco contrasto, sono tutti ammucchiati in una "montagnetta" al centro

    L'equalizzazione prende quella "montagnetta" e la appiattisce, distribuendo i pixel su tutta la larghezza del grafico
    Questo fa emergere dettagli che prima erano invisibili perché troppo simili tra loro
    """
    # convert the image to grayscale format
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return cv2.equalizeHist(frame)


def clahe(
    frame: np.ndarray, clipLimit: float = 2.0, tileGridSize: tuple = (8, 8)
) -> np.ndarray | None:
    """
    La CLAHE (Contrast Limited Adaptive Histogram Equalization) è l'evoluzione "intelligente" dell'equalizzazione standard.
    Lavora su piccole porzioni locali invece che sull'intera immagine.

    Se l'immagine è già in grayscale, non la converte.
    """
    # Controlla se l'immagine è già in grayscale (2 dimensioni)
    if len(frame.shape) == 3 and frame.shape[2] == 3:
        # Converti in grayscale solo se è un'immagine a colori
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    clahe_obj = cv2.createCLAHE(clipLimit, tileGridSize)
    return clahe_obj.apply(frame)
