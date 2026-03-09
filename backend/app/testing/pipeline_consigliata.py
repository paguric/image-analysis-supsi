import cv2
import numpy as np
from scipy.optimize import linear_sum_assignment

from app import cv2_utils
from app import norm

"""
CHAT: https://chatgpt.com/share/69abfa77-7c6c-8013-a860-3c732e2b6a15
CHAT: https://grok.com/share/bGVnYWN5_f4e97958-58eb-486d-8434-ebb476a30192
"""


def ensure_odd(v):
    """
    Semplice controllo di disparità, OpenCV richiede che la dimensione del Kernel sia dispari
    per funziona con Gaussian, Bilaterale e Morfologia
    """
    v = max(1, int(v))
    return v if v % 2 == 1 else v + 1


def match_contours_by_center(dict1, dict2):
    centers1 = list(dict1.keys())
    centers2 = list(dict2.keys())

    n = len(centers1)

    # matrice delle distanze
    dist_matrix = np.zeros((n, n))

    for i, (x1, y1) in enumerate(centers1):
        for j, (x2, y2) in enumerate(centers2):
            dist_matrix[i, j] = np.hypot(x1 - x2, y1 - y2)

    # Hungarian algorithm
    rows, cols = linear_sum_assignment(dist_matrix)

    result1 = {}
    result2 = {}

    for idx, (r, c) in enumerate(zip(rows, cols)):
        result1[idx] = {
            "center": centers1[r],
            "contour": dict1[centers1[r]]
        }

        result2[idx] = {
            "center": centers2[c],
            "contour": dict2[centers2[c]]
        }

    return result1, result2


def compute_contours(
    img: np.ndarray,
    p: dict[str, int | float]
) -> tuple[np.ndarray, int, int, dict[tuple[int, int], np.ndarray]]:
    
    # Struttura dati per salvare come chiave la tupla x/y e come valore il contorno
    contour_map = {}

    bg_blur  = ensure_odd(p["bg_blur_size"])
    morph_k  = ensure_odd(p["morph_kernel_size"])
    min_circ = p["min_circularity"]

    # passo ad una scala di grigi
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # applicando il filtro gaussiano posso sfocare l'immagine e stimare lo sfondo
    # viene passta l'immagine, 
    # la dimensione del kernel (ovvero la distanza da blurrare a partire da ogni pixel) 
    # e la deviazione standard per 
    # controllare il livello di blur (con 0 OpenCV sceglie in automatico)
    background = cv2.GaussianBlur(gray, (bg_blur, bg_blur), 0)

    # rimuovo lo sfondo sottraendo all'immagine originale lo sfondo stimato 
    gray_no_bg = cv2.subtract(gray, background)

    # la normalizzazione permette di enfatizzare le differenze tra i pixel chiari e quelli scuri (aumenta il contrasto)
    gray_norm = cv2.normalize(gray_no_bg, None, 0, 255, cv2.NORM_MINMAX)

    # viene passata alla funzione l'immagine con l'attuale livello di processamento, 
    # il cliplimit (ovvero di quanto il constrasto locale di ogni tile può essere aumentato)
    # e il tileGridSize (ovvero la suddivisione in celle dell'immagine)
    gray_enh = norm.clahe(gray_norm, 3.0, (8,8))

    # questo tipo di filtraggio permette una maggiore precisione perchè 
    # oltre a prendere in considerazione la distanza da blurrare a partire 
    # da ogni pixel guarda anche il contributo che il colore 
    # e la distanza spaziale portano alla media dei pixel
    blurred = cv2.bilateralFilter(
        gray_enh,
        d=int(p["bilateral_d"]),
        sigmaColor=p["bilateral_sigma_color"],
        sigmaSpace=p["bilateral_sigma_space"]
    )


    # Passiamo a Canny un'immagine già preprocessata.
    # Internamente, Canny utilizza operatori (es. Sobel) per calcolare 
    # la derivata verticale e orizzontale di ogni pixel, identificando
    # i potenziali bordi dove ci sono cambiamenti rapidi di intensità.
    # Vengono considerati solo i picchi locali del gradiente (Non-Maximum Suppression).
    # Per decidere effettivamente quali pixel sono bordi, si utilizzano i parametri
    # low e high:
    # - gradiente > high -> bordo sicuro
    # - gradiente < low -> scartato
    # - gradiente tra low e high -> diventa bordo solo se connesso a un pixel sicuro
    # Canny restituisce un'immagine binaria con i bordi identificati
    edges = cv2.Canny(blurred, p["canny_low"], p["canny_high"])


    # Definisco un kernel per l'operazione morfologica, mi permette di 
    # esplicitare la distanza di azione dell'operazione morfologica 
    # rispetto ad un pixel.
    kernel = np.ones((morph_k, morph_k), np.uint8)

    # L'operazione morfologica (MORPH_CLOSE) mi permette di chiudere i bordi che sono stati 
    # trovati da Canny. Per prima cosa effettua una "dilation", i pixel bianchi vengono espansi
    # (quindi parte del bordo), la distanza di applicazione
    # dell'operazione è sempre definita dalla dimensione del kernel; in secondo luogo viene 
    # applicata una "erosion", dato che la diltation potrebbe aver sporcato il bordo l'operazione
    # di erosione serve proprio a rimuovere i pixel bianchi posti sull'esterno del bordo mantenendo 
    # però connessi quelli che erano già uniti in precedenza
    edges_closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel,
                                    iterations=int(p["morph_iterations"]))
    

    # A partire dall'immagine binaria preprocessata con il closing, questa funzione trova i contorni.
    # Restituisce una lista di coordinate (x,y) dei contorni esterni (cv2.RETR_EXTERNAL).
    # L'opzione cv2.CHAIN_APPROX_SIMPLE approssima il contorno rimuovendo punti ridondanti lungo la curva.
    contours, _ = cv2.findContours(edges_closed, cv2.RETR_EXTERNAL,
                                   cv2.CHAIN_APPROX_SIMPLE)

    output  = img.copy()
    matched = 0

    # Viene passata la lista dei contori degli oggetti identificati
    for cnt in contours:        # questo calcolo ritorna in pixel^2 la dimensione di ogni oggetto       
        area = cv2.contourArea(cnt)

        # Lunghezza del perimetro, closed=True significa che il 
        # il punto iniziale e quello finale sono connessi 
        perimeter = cv2.arcLength(cnt, closed=True)

        # Scartiamo i contorni troppo piccoli
        if perimeter < 1e-6:
            continue

        # calcoliamo la circolatià per determinare quanto il contorno
        # assomigli ad un cerchio
        circularity = 4 * np.pi * area / (perimeter ** 2)
        
        # se circolarità ed area sono nei bound stabiliti, il bordo viene disegnato
        if circularity >= min_circ and area >= p["min_area"]:

            cv2.drawContours(output, [cnt], -1, (0, 255, 0), 2)
            matched += 1

            # bounding box
            x, y, w, h = cv2.boundingRect(cnt)

            # disegno bounding box (giallo)
            cv2.rectangle(output, (x, y), (x + w, y + h), (0, 255, 255), 2)

            # indice del contorno (in alto a sx della bounding box)
            cv2.putText(
                output,
                str(matched),
                (x, y - 5),   # leggermente sopra la bounding box
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 255),
                2
            )

            # centro geometrico
            cx = x + w // 2
            cy = y + h // 2

            contour_map[(cx, cy)] = cnt

            # disegno centro (blu)
            cv2.circle(output, (cx, cy), 6, (255, 0, 0), -1)


            # calcolo momenti
            M = cv2.moments(cnt)

            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])

                # disegno centro di massa
                cv2.circle(output, (cx, cy), 6, (0, 0, 255), -1)

    return output, matched, len(contours), contour_map


PARAMS = {
    "bg_blur_size":          101,   # Kernel il filtro gaussiano (per rimozione sfondo)
    "canny_low":             0,     # Soglia bassa di canny (con 0 va in modalità automatica)
    "canny_high":            0,     # Soglia alta di canny (con 0 va in modalità automatica)
    "bilateral_d":           5,     # Dimensione del kernel per applicazione filtro bilineare
    "bilateral_sigma_color": 50,    # Quanto devono essere simili i colori dei pixel per essere mediati (da 0 a 255)
    "bilateral_sigma_space": 1,     # Quanto devono essere vicini spazialmente dei pixel per essere mediati (da 0 a 15)
    "morph_kernel_size":     3,     # Dimensione del kernel morfologico
    "morph_iterations":      2,     # Quante volte applicare l'operazione morfologica
    "min_area":              5000,  # Area minima in pixel per considerare un contorno valido
    "min_circularity":       0.10,  # Soglia minima per accettare un cerchio
}


def print_params(p, matched):
    print("\n" + "─" * 50)
    print(f"  Contorni validi rilevati: {matched}")
    print("─" * 50)
    for key, val in p.items():
        print(f"  {key:<26} = {val}")
    print("─" * 50)


print("ANALISI VIDEO PRIMA...")
video_path = "video/prima.avi"
imgb_index, _= cv2_utils.brightest_frame(video_path)
imgb_prima = cv2_utils.extract_frame(video_path, imgb_index)
result_imgb_prima, matched, total, contour_map_prima = compute_contours(imgb_prima, PARAMS)
print(f"  Contorni totali trovati: {total}")
print_params(PARAMS, matched)
print("--------------------\n\n")


print("ANALISI VIDEO DOPO...")
video_path = "video/dopo.avi"
imgb_index, _= cv2_utils.brightest_frame(video_path)
imgb_prima = cv2_utils.extract_frame(video_path, imgb_index)
result_imgb_dopo, matched, total, contour_map_dopo = compute_contours(imgb_prima, PARAMS)
print(f"  Contorni totali trovati: {total}")
print_params(PARAMS, matched)
print("--------------------")


cv2.namedWindow("Contour Result", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Contour Result", 1200, 700)
cv2.imshow("Contour Result", result_img)
print("\nPremi un tasto per chiudere la finestra...")
cv2.waitKey(0)
cv2.destroyAllWindows()
