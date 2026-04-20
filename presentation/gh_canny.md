# Shape Detection — Riepilogo modifiche e ottimizzazioni

## 1. Sorgente input
- **Rimossa** la webcam (`cv2.VideoCapture(0)`)
- **Aggiunto** caricamento da file video: `cv2.VideoCapture("backend/video/prima.avi")`
- Le dimensioni del frame **non vengono forzate**: si usano quelle native del video
- A fine video il cap si **riavvolge automaticamente** con `cap.set(cv2.CAP_PROP_POS_FRAMES, 0)`

---

## 2. Adattamento finestra di visualizzazione
- Lo **scale** della griglia 3×2 viene calcolato dal primo frame in base a una risoluzione target di **1920×1080**:
  ```python
  scale = round(min(SCREEN_W / (frame_w * 3), SCREEN_H / (frame_h * 2)), 2)
  ```
- Viene calcolato **una volta sola** prima del loop, non ad ogni frame

---

## 3. Preprocessing per immagini scure
- Aggiunto **CLAHE** (`Contrast Limited Adaptive Histogram Equalization`) tra grayscale e Canny:
  ```python
  clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
  imgGray = clahe.apply(imgGray)
  ```
  Amplifica il contrasto localmente in regioni 8×8, rendendo visibili i bordi delle ROI anche in zone molto scure. `clipLimit` evita di amplificare il rumore.

- Sostituito **GaussianBlur** con **bilateralFilter**:
  ```python
  imgBlur = cv2.bilateralFilter(img, d=9, sigmaColor=75, sigmaSpace=75)
  ```
  Il bilateral riduce il rumore **preservando i bordi**, a differenza del Gaussian che li sfuma — vantaggio importante per cerchi su sfondo scuro.

---

## 4. Ottimizzazioni performance

| Cosa | Prima | Dopo |
|---|---|---|
| `clahe` | Creato ad ogni frame | Creato una volta fuori dal loop |
| `kernel` | Creato ad ogni frame | Creato una volta fuori dal loop |
| `areaMin` | Letto dentro il `for cnt` | Letto una volta per tutti i contorni |
| `scale` | Ricalcolato ad ogni frame | Calcolato una volta dal primo frame |
| Algoritmo contorni | `CHAIN_APPROX_NONE` | `CHAIN_APPROX_SIMPLE` (meno punti in memoria) |
| `stackImages` | Variabili `hor_con`, `imageBlank` inutilizzate | Rimosse |

---

## 5. I 3 parametri trackbar

| Trackbar | Effetto |
|---|---|
| **threshold1** | Soglia bassa Canny — bordi sotto questa soglia vengono scartati |
| **threshold2** | Soglia alta Canny — bordi sopra questa soglia vengono accettati con certezza |
| **Area** | Area minima del contorno in pixel — filtra oggetti troppo piccoli |

> Per immagini scure: abbassare `threshold1` e `threshold2`, alzare `Area` per filtrare falsi positivi da rumore.

---

## 6. Consigli

- Se la detection è ancora instabile, aumentare `clipLimit` del CLAHE fino a `5.0`
- `CHAIN_APPROX_SIMPLE` è sufficiente per forme circolari; usare `CHAIN_APPROX_NONE` solo se si necessita di ogni singolo pixel del contorno
- Il warning Qt sui font (`QFontDatabase: Cannot find font directory`) è **innocuo** — il programma funziona comunque; per risolverlo scaricare i font DejaVu nella cartella indicata dal messaggio.