import cv2
import av
import numpy as np
import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# =========================
# PATH
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VIDEO_DIR = os.path.join(BASE_DIR, "..", "video")

videoA_path   = os.path.join(VIDEO_DIR, "prima.avi")
videoB_path   = os.path.join(VIDEO_DIR, "dopo.avi")
output_path   = os.path.join(VIDEO_DIR, "differenza.avi")
heatmap_path  = os.path.join(VIDEO_DIR, "heatmap.png")

# =========================
# PARAMETRI CONFIGURABILI
# =========================
LOG_RATIO_THRESHOLD  = 0.5
SCALE                = 0.50
CLAHE_CLIP_LIMIT     = 2.0
CLAHE_TILE_SIZE      = (8, 8)

# Parametri blob detection per rilevare i pozzetti.
# Regola MIN/MAX_AREA in base alla dimensione dei pozzetti nel tuo video.
BLOB_MIN_AREA        = 200
BLOB_MAX_AREA        = 50000
BLOB_MIN_CIRCULARITY = 0.5

# =========================
# LUT divergente blu → bianco → rosso
# =========================
# Semantica biologica:
#   blu   (0)   → downregulation
#   bianco(128) → nessun cambiamento
#   rosso (255) → upregulation
lut = np.zeros((256, 1, 3), dtype=np.uint8)
for i in range(256):
    if i < 128:
        t = i / 127.0
        lut[i, 0] = [255, int(255 * t), int(255 * t)]
    else:
        t = (i - 128) / 127.0
        lut[i, 0] = [int(255 * (1 - t)), int(255 * (1 - t)), 255]

# =========================
# Apertura video con PyAV
# =========================
container_A = av.open(videoA_path)
container_B = av.open(videoB_path)

streamA = container_A.streams.video[0]
streamB = container_B.streams.video[0]

fps    = float(streamA.average_rate)
width  = streamA.codec_context.width
height = streamA.codec_context.height

# =========================
# Video writer — differenziale frame per frame
# =========================
ext    = os.path.splitext(output_path)[1].lower()
fourcc = cv2.VideoWriter_fourcc(*("mp4v" if ext == ".mp4" else "XVID"))
writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

# =========================
# CLAHE
# =========================
clahe = cv2.createCLAHE(
    clipLimit=CLAHE_CLIP_LIMIT,
    tileGridSize=CLAHE_TILE_SIZE
)

# =========================
# SimpleBlobDetector — rilevamento pozzetti
# =========================
# Individua regioni connesse (blob) circolari che corrispondono
# ai pozzetti del microarray, filtrando per area e circolarità.
blob_params = cv2.SimpleBlobDetector_Params()
blob_params.filterByArea         = True
blob_params.minArea              = BLOB_MIN_AREA
blob_params.maxArea              = BLOB_MAX_AREA
blob_params.filterByCircularity  = True
blob_params.minCircularity       = BLOB_MIN_CIRCULARITY
blob_params.filterByConvexity    = False
blob_params.filterByInertia      = False
blob_detector = cv2.SimpleBlobDetector_create(blob_params)

# =========================
# Parametri allineamento ECC
# (Enhanced Correlation Coefficient Maximization)
# =========================
# Ref: Evangelidis & Psarakis, IEEE TPAMI 2008.
# MOTION_HOMOGRAPHY: trasformazione proiettiva a 8 parametri (matrice 3x3)
# per correggere anche distorsioni prospettiche tra le due acquisizioni.
warp_mode   = cv2.MOTION_HOMOGRAPHY
warp_matrix = np.eye(3, 3, dtype=np.float32)
criteria = (
    cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT,
    30, 1e-4
)

# =========================
# Strutture dati per la heatmap statica
# =========================
# Dizionario che accumula i log-ratio di ogni pozzetto su tutti i frame.
# Chiave: indice del keypoint (int)
# Valore: lista di log-ratio float frame per frame
# Alla fine verrà calcolata la media temporale per produrre la heatmap.
well_ratios_accumulator = {}   # { well_idx: [ratio_frame0, ratio_frame1, ...] }
well_positions          = {}   # { well_idx: (cx, cy, r) } — posizione e raggio
keypoints_reference     = None # keypoints rilevati sul primo frame (riferimento)

# =========================
# Loop principale
# =========================
frame_count = 0

for frameA, frameB in zip(
    container_A.decode(streamA),
    container_B.decode(streamB)
):
    imgA = frameA.to_ndarray(format="bgr24")
    imgB = frameB.to_ndarray(format="bgr24")

    if imgB.shape[:2] != imgA.shape[:2]:
        imgB = cv2.resize(imgB, (width, height))

    # --------------------------------------------------
    # Normalizzazione illuminazione con CLAHE
    # --------------------------------------------------
    # Conversione luminanza BT.601: Y = 0.114B + 0.587G + 0.299R
    # Per fluorofori specifici sostituire con:
    #   grayA = imgA[:, :, 1]  # canale verde (FITC)
    #   grayA = imgA[:, :, 2]  # canale rosso (Cy5)
    grayA    = cv2.cvtColor(imgA, cv2.COLOR_BGR2GRAY)
    grayB    = cv2.cvtColor(imgB, cv2.COLOR_BGR2GRAY)
    grayA_eq = clahe.apply(grayA)
    grayB_eq = clahe.apply(grayB)

    # --------------------------------------------------
    # ECC Image Registration con MOTION_HOMOGRAPHY
    # --------------------------------------------------
    small_A = cv2.resize(grayA_eq, None, fx=SCALE, fy=SCALE, interpolation=cv2.INTER_AREA)
    small_B = cv2.resize(grayB_eq, None, fx=SCALE, fy=SCALE, interpolation=cv2.INTER_AREA)
    small_A = cv2.GaussianBlur(small_A, (5, 5), 0)
    small_B = cv2.GaussianBlur(small_B, (5, 5), 0)

    try:
        cc, warp_small = cv2.findTransformECC(
            small_A, small_B, warp_matrix.copy(), warp_mode, criteria
        )
        # Rescaling omografia: tx/ty scalati di 1/SCALE,
        # termini prospettici H[2,0] e H[2,1] scalati di SCALE.
        warp_full = warp_small.copy()
        warp_full[0, 2] /= SCALE
        warp_full[1, 2] /= SCALE
        warp_full[2, 0] *= SCALE
        warp_full[2, 1] *= SCALE
        warp_matrix = warp_small

        aligned_B = cv2.warpPerspective(
            imgB, warp_full, (width, height),
            flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP
        )
    except cv2.error:
        aligned_B = imgB
        warp_matrix = np.eye(3, 3, dtype=np.float32)

    # --------------------------------------------------
    # Rilevamento pozzetti
    # --------------------------------------------------
    # I keypoints vengono rilevati solo sul primo frame e riutilizzati
    # per tutti i frame successivi: i pozzetti sono fissi nella piastra,
    # quindi la loro posizione non cambia tra i frame.
    if keypoints_reference is None:
        keypoints_reference = blob_detector.detect(grayA_eq)
        for idx, kp in enumerate(keypoints_reference):
            cx, cy = int(kp.pt[0]), int(kp.pt[1])
            r      = max(3, int(kp.size / 2))
            well_positions[idx]          = (cx, cy, r)
            well_ratios_accumulator[idx] = []
        print(f"Pozzetti rilevati: {len(keypoints_reference)}")

    # --------------------------------------------------
    # Calcolo log-ratio per pozzetto — frame corrente
    # --------------------------------------------------
    grayA_float = grayA.astype(np.float32)
    grayB_float = cv2.cvtColor(aligned_B, cv2.COLOR_BGR2GRAY).astype(np.float32)

    # Sfondo grigio come base del frame differenziale
    output_frame = cv2.cvtColor(grayA, cv2.COLOR_GRAY2BGR)

    for idx, (cx, cy, r) in well_positions.items():
        # Maschera circolare per il singolo pozzetto
        mask_well = np.zeros((height, width), dtype=np.uint8)
        cv2.circle(mask_well, (cx, cy), r, 255, -1)

        # Intensità media del pozzetto in A e B.
        # Il confronto su valore medio per pozzetto elimina gli artefatti
        # da misallineamento residuo ECC (nessun confronto pixel per pixel).
        mean_A = np.mean(grayA_float[mask_well > 0])
        mean_B = np.mean(grayB_float[mask_well > 0])

        # Log-ratio: log2(mean_B / mean_A)
        # +1 = raddoppio (upregulation), -1 = dimezzamento (downregulation)
        ratio = np.log2((mean_B + 1.0) / (mean_A + 1.0)) if mean_A > 1.0 else 0.0

        # Azzera se sotto soglia
        if abs(ratio) < LOG_RATIO_THRESHOLD:
            ratio = 0.0

        # Accumula il ratio per la heatmap statica finale
        well_ratios_accumulator[idx].append(ratio)

        # --------------------------------------------------
        # Rendering frame per frame (video differenziale)
        # --------------------------------------------------
        # Normalizzazione log-ratio [-4, +4] → [0, 255] per la LUT
        norm_val  = int(np.clip((ratio + 4.0) / 8.0 * 255, 0, 255))
        color_bgr = tuple(int(c) for c in lut[norm_val, 0])

        # Pozzetto colorato + bordo bianco sottile
        cv2.circle(output_frame, (cx, cy), r, color_bgr, -1)
        cv2.circle(output_frame, (cx, cy), r, (200, 200, 200), 1)

    writer.write(output_frame)

    frame_count += 1
    if frame_count % 10 == 0:
        print(f"Frame elaborati: {frame_count}")

# =========================
# Cleanup video
# =========================
writer.release()
container_A.close()
container_B.close()

print(f"Completato! {frame_count} frame elaborati.")
print(f"  → Differenziale: {output_path}")

# =========================
# HEATMAP STATICA
# =========================
# Per ogni pozzetto calcola la media temporale dei log-ratio accumulati
# su tutti i frame → rappresenta il cambiamento medio di espressione
# genica tra "prima" e "dopo" integrato sull'intera sequenza video.
#
# La heatmap viene prodotta con matplotlib su sfondo nero,
# con i pozzetti colorati secondo la stessa LUT divergente del video
# e annotati con il valore medio di fold change (log2).

print("Generazione heatmap statica...")

# Canvas nero (BGR) delle stesse dimensioni del video
heatmap_img = np.zeros((height, width, 3), dtype=np.uint8)

for idx, (cx, cy, r) in well_positions.items():
    ratios     = well_ratios_accumulator[idx]
    mean_ratio = float(np.mean(ratios)) if ratios else 0.0

    # Colore dalla LUT divergente
    norm_val  = int(np.clip((mean_ratio + 4.0) / 8.0 * 255, 0, 255))
    color_bgr = tuple(int(c) for c in lut[norm_val, 0])

    # Pozzetto colorato
    cv2.circle(heatmap_img, (cx, cy), r, color_bgr, -1)
    cv2.circle(heatmap_img, (cx, cy), r, (200, 200, 200), 1)

    # Annotazione numerica: valore medio log2 fold change
    # Testo piccolo centrato sul pozzetto
    label = f"{mean_ratio:+.2f}"
    font_scale = max(0.3, r / 40.0)
    (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 1)
    cv2.putText(
        heatmap_img, label,
        (cx - tw // 2, cy + th // 2),
        cv2.FONT_HERSHEY_SIMPLEX, font_scale,
        (0, 0, 0), 1, cv2.LINE_AA
    )

# Converti BGR → RGB per matplotlib
heatmap_rgb = cv2.cvtColor(heatmap_img, cv2.COLOR_BGR2RGB)

# Plot matplotlib con colorbar e legenda
fig, ax = plt.subplots(figsize=(16, 10))
ax.imshow(heatmap_rgb)
ax.set_title("Heatmap differenziale microarray — media log2(dopo/prima)", fontsize=14)
ax.axis("off")

# Colorbar simulata come gradient image verticale
grad = np.linspace(0, 1, 256).reshape(256, 1)
grad_rgb = np.zeros((256, 1, 3), dtype=np.uint8)
for i in range(256):
    if i < 128:
        t = i / 127.0
        grad_rgb[i, 0] = [int(255 * t), int(255 * t), 255]  # RGB: blu→bianco
    else:
        t = (i - 128) / 127.0
        grad_rgb[i, 0] = [255, int(255 * (1 - t)), int(255 * (1 - t))]  # RGB: bianco→rosso

ax_cb = fig.add_axes([0.92, 0.15, 0.02, 0.7])
ax_cb.imshow(grad_rgb[::-1], aspect="auto", extent=[0, 1, -4, 4])
ax_cb.set_ylabel("log2 fold change", fontsize=10)
ax_cb.yaxis.set_label_position("right")
ax_cb.yaxis.tick_right()
ax_cb.set_xticks([])
ax_cb.set_yticks([-4, -3, -2, -1, 0, 1, 2, 3, 4])

# Legenda
patches = [
    mpatches.Patch(color=(0.0, 0.0, 1.0), label="Downregulation (log2 < 0)"),
    mpatches.Patch(color=(1.0, 1.0, 1.0), label="Nessun cambiamento (log2 ≈ 0)"),
    mpatches.Patch(color=(1.0, 0.0, 0.0), label="Upregulation (log2 > 0)"),
]
ax.legend(handles=patches, loc="lower left", fontsize=9,
          facecolor="black", labelcolor="white", framealpha=0.7)

plt.savefig(heatmap_path, dpi=150, bbox_inches="tight", facecolor="black")
plt.close()

print(f"  → Heatmap statica: {heatmap_path}")