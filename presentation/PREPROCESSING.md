## Tecniche di Pre-processing per Image Segmentation

### Analisi preliminare

- **Istogramma** — capire la distribuzione dei pixel prima di scegliere qualsiasi parametro

### Normalizzazione del contrasto

- **CLAHE** — equalizzazione adattiva locale, preferibile a luminosità/contrasto manuali

### Denoising

- **GaussianBlur** — smoothing prima del threshold per ridurre falsi contorni
- **fastNlMeans** — per immagini molto rumorose

### Thresholding

- **Otsu** — soglia ottimale automatica, funziona bene con istogramma bimodale
- **Adaptive Threshold** — soglia locale, per illuminazione non uniforme

### Pulizia maschera binaria (Morfologia)

- **Opening** (`MORPH_OPEN`) — rimuove piccoli punti di rumore
- **Closing** (`MORPH_CLOSE`) — riempie buchi interni agli oggetti

### Rilevamento contorni

- **findContours** — estrazione contorni dalla maschera binaria
- **Canny** — alternativa al threshold binario per bordi sfumati

### Ottimizzazione parametri

- **Grid search + metrica custom** — ricerca sistematica dei parametri migliori basata su una funzione di score definita sul dominio specifico

## Trovare la combinazione ottimale per Image Segmentation

Non esiste un metodo universale, ma un approccio sistematico. Dipende molto dal tuo dominio (oggetti su sfondo uniforme? immagini mediche? outdoor?).

---

### 1. Capire prima il problema

Prima di toccare parametri, analizza l'istogramma del frame:

```python
import cv2
import numpy as np
import matplotlib.pyplot as plt

def analyze_frame(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    plt.figure(figsize=(12, 4))

    plt.subplot(1, 3, 1)
    plt.imshow(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    plt.title("Frame originale")

    plt.subplot(1, 3, 2)
    plt.hist(gray.ravel(), bins=256, range=(0, 256))
    plt.title("Istogramma")
    plt.xlabel("Intensità pixel")

    plt.subplot(1, 3, 3)
    plt.imshow(gray, cmap='gray')
    plt.title("Grayscale")

    plt.tight_layout()
    plt.savefig('video/analysis/histogram.jpg')
```

L'istogramma ti dice subito:

- **Picchi separati** → soglia facile da trovare (oggetto e sfondo ben distinti)
- **Distribuzione piatta/sovrapposta** → serve più pre-processing
- **Immagine sottoesposta/sovraesposta** → normalizzazione prima di tutto

---

### 2. Pipeline consigliata

```
Frame grezzo
    │
    ▼
Normalizzazione / CLAHE          ← adatta il range dinamico
    │
    ▼
Denoising (opzionale)            ← riduce falsi contorni
    │
    ▼
Thresholding                     ← Otsu o Adaptive
    │
    ▼
Operazioni morfologiche          ← pulizia maschera binaria
    │
    ▼
Contour detection
```

---

### 3. Luminosità/Contrasto: meglio CLAHE che parametri manuali

Invece di cercare `alpha`/`beta` ottimali a mano, usa **CLAHE** (Contrast Limited Adaptive Histogram Equalization): adatta il contrasto _localmente_, preservando i dettagli senza saturare:

```python
def apply_clahe(frame, clip_limit=2.0, tile_size=(8, 8)):
    """
    clip_limit: quanto contrasto massimo applicare (più alto = più aggressivo)
    tile_size: dimensione delle regioni locali
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_size)
    return clahe.apply(gray)
```

> Regola pratica: `clip_limit` tra 1.0 e 4.0, `tile_size` tra (4,4) e (16,16)

---

### 4. Thresholding: usa Otsu invece di cercare la soglia manualmente

**Otsu** trova automaticamente la soglia ottimale analizzando l'istogramma (minimizza la varianza intra-classe):

```python
def threshold_otsu(gray):
    # Otsu funziona meglio se l'istogramma è bimodale
    blur = cv2.GaussianBlur(gray, (5, 5), 0)  # denoising prima di Otsu
    ret, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    print(f"Soglia trovata da Otsu: {ret}")
    return thresh
```

Se gli oggetti hanno **illuminazione non uniforme** (es. ombre), usa invece **Adaptive Threshold**:

```python
def threshold_adaptive(gray):
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(
        blur, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,  # o MEAN_C
        cv2.THRESH_BINARY,
        blockSize=11,   # dimensione neighborhood (deve essere dispari)
        C=2             # costante sottratta dalla media locale
    )
    return thresh
```

---

### 5. Pulizia della maschera binaria (morfologia)

Dopo il threshold quasi sempre ci sono rumori e buchi. Le operazioni morfologiche li rimuovono:

```python
def clean_mask(thresh):
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))

    # Rimuove piccoli punti bianchi isolati (rumore)
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

    # Riempie piccoli buchi dentro gli oggetti
    closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)

    return closing
```

---

### 6. Pipeline completa + grid search automatica

Se vuoi comunque trovare parametri ottimali in modo sistematico, definisci una **metrica di qualità** e fai una ricerca:

```python
def score_segmentation(thresh):
    """
    Metrica euristica: premia contorni grandi e pochi,
    penalizza troppo rumore (tanti contorni minuscoli).
    Da adattare al tuo caso specifico.
    """
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) == 0:
        return 0

    areas = [cv2.contourArea(c) for c in contours]
    large = [a for a in areas if a > 500]   # soglia area minima

    # Vogliamo: tanti pixel nei contorni grandi, pochi contorni in totale
    score = sum(large) / (len(contours) + 1)
    return score


def grid_search(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    best_score = -1
    best_params = {}

    for clip_limit in [1.0, 2.0, 3.0, 4.0]:
        for tile_size in [(4,4), (8,8), (16,16)]:
            for block_size in [7, 11, 15, 21]:  # solo per adaptive
                clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_size)
                enhanced = clahe.apply(gray)
                blurred = cv2.GaussianBlur(enhanced, (5,5), 0)
                thresh = cv2.adaptiveThreshold(
                    blurred, 255,
                    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                    cv2.THRESH_BINARY, block_size, 2
                )
                cleaned = clean_mask(thresh)
                score = score_segmentation(cleaned)

                if score > best_score:
                    best_score = score
                    best_params = {
                        'clip_limit': clip_limit,
                        'tile_size': tile_size,
                        'block_size': block_size
                    }

    print(f"Best score: {best_score:.2f} | Params: {best_params}")
    return best_params
```

---

### Quando usare cosa

| Scenario                             | Approccio                                      |
| ------------------------------------ | ---------------------------------------------- |
| Sfondo uniforme, buona illuminazione | Otsu diretto                                   |
| Illuminazione variabile/ombre        | CLAHE + Adaptive Threshold                     |
| Immagine molto rumorosa              | GaussianBlur o fastNlMeans prima del threshold |
| Oggetti con bordi sfumati            | Canny invece di threshold binario              |
| Non sai da dove partire              | Grid search con metrica custom                 |

Il punto chiave è che la **metrica di qualità** nella grid search va definita in base al tuo obiettivo specifico: numero di oggetti atteso, dimensione minima, forma, ecc.
