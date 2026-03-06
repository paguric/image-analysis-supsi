import cv2
import av
import numpy as np
from app import cv2_utils

def min_max_norm(frame: np.ndarray) -> np.ndarray | None:
    """
    minmax prende il valore più basso presente nell'immagine e lo porta a 0, prende il più
    alto e lo porta a 255, e distribuire proporzionalmente tutti gli altri valori nel mezzo
    """
    return cv2.normalize(frame, None, 0, 255, cv2.NORM_MINMAX)


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


def clahe(frame: np.ndarray, clipLimit: float = 2.0, tileGridSize: tuple = (8,8)) -> np.ndarray | None:
    """
    La CLAHE (Contrast Limited Adaptive Histogram Equalization) è l'evoluzione "intelligente" dell'equalizzazione standard
    Mentre l'equalizzazione normale guarda l'intera immagine (globale), la CLAHE lavora su piccole porzioni locali
    """
    # convert the image to grayscale format
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit, tileGridSize)
    return clahe.apply(frame)
