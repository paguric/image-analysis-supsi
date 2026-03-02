import cv2

# Carica i due video (aggiungi l'estensione corretta, ad esempio .mp4)
cap1 = cv2.VideoCapture('video\\prima.avi')  # Video di sottofondo
cap2 = cv2.VideoCapture('video\\post_detection.avi')   # Video da sovrapporre

# Verifica che i video siano stati caricati correttamente
if not cap1.isOpened() or not cap2.isOpened():
    print("Errore: Impossibile caricare uno o entrambi i video. Controlla il percorso e l'estensione.")
    exit()

# Imposta le dimensioni del video finale
width = int(cap1.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap1.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Imposta la posizione del video sovrapposto (es. in alto a destra)
x_offset = width / 2
y_offset = height / 2


cv2.namedWindow("Video con Overlay", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Video con Overlay", 1400, 800)

while True:
    ret1, frame1 = cap1.read()
    ret2, frame2 = cap2.read()

    # Se uno dei due video finisce o c'è un errore, interrompi il loop
    if not ret1 or not ret2:
        break

    # Ridimensiona il video da sovrapporre
    # frame2_resized = cv2.resize(frame2, (width, height))

    # Sovrapposizione: inserisce frame2_resized su frame1
    # frame1[y_offset:y_offset + 150, x_offset:x_offset + 200] = frame2_resized

    # Visualizza in anteprima
    cv2.imshow('Video con Overlay', frame1)
    
    # Premi 'q' per uscire
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Rilascia le risorse
cap1.release()
cap2.release()
cv2.destroyAllWindows()