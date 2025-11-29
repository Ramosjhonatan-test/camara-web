import cv2
import numpy as np
import requests
import csv
import os
import json
import time
from datetime import datetime
from collections import Counter
from ultralytics import YOLO

# ==============================
# CONFIGURACIÓN
# ==============================
STREAM_URL = "https://vision-ia-server.onrender.com/stream"  # URL del stream MJPEG
CSV_PATH = "detecciones.csv"                                 # archivo de salida
LABELS_FILE = "coco_labels_es.json"                          # archivo con etiquetas en español

MODEL_PATH = "yolov8n.pt"   # opciones: yolov8n.pt (rápido), yolov8s.pt (balance), yolov8m/l/x.pt (más preciso)
CONF_THRESHOLD = 0.45       # confianza mínima (más estricto = menos ruido)
IOU_THRESHOLD = 0.5         # umbral de IoU
IMG_SIZE = 320              # tamaño de entrada (menor = más rápido)
SKIP_FRAMES = 3             # procesar 1 de cada N frames (ej: 3 = cada 3 frames)
PRINT_INTERVAL = 2          # segundos entre impresiones en consola
MIN_BOX_AREA = 600          # área mínima de caja para evitar falsos positivos

# ==============================
# FUNCIONES AUXILIARES
# ==============================
def load_labels(path: str):
    """Carga etiquetas COCO en español desde archivo JSON."""
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        print("⚠️ No se encontró el archivo de etiquetas, se usarán nombres en inglés.")
        return {}

def to_spanish(label: str, labels_dict: dict) -> str:
    """Convierte etiqueta a español si existe en el diccionario."""
    return labels_dict.get(label, label)

# ==============================
# INICIALIZACIÓN
# ==============================
labels_dict = load_labels(LABELS_FILE)
model = YOLO(MODEL_PATH)

# Crear CSV si no existe
if not os.path.exists(CSV_PATH):
    with open(CSV_PATH, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "clase", "confianza", "x1", "y1", "x2", "y2"])

# ==============================
# PROCESAMIENTO DEL STREAM
# ==============================
stream = requests.get(STREAM_URL, stream=True, timeout=10)
bytes_data = b""
frame_id = 0
last_summary = None
last_print = 0

print("📡 Procesando stream desde Render con YOLOv8 optimizado…")

try:
    for chunk in stream.iter_content(chunk_size=8192):
        if not chunk:
            continue
        bytes_data += chunk

        start = bytes_data.find(b'\xff\xd8')
        end = bytes_data.find(b'\xff\xd9')
        if start != -1 and end != -1 and end > start:
            jpg = bytes_data[start:end+2]
            bytes_data = bytes_data[end+2:]

            frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
            if frame is None:
                continue

            frame_id += 1
            if frame_id % SKIP_FRAMES != 0:
                continue  # saltar frames para optimizar

            # Redimensionar para inferencia
            frame_infer = cv2.resize(frame, (640, 480))

            # Inferencia YOLO
            results = model.predict(
                frame_infer,
                imgsz=IMG_SIZE,
                conf=CONF_THRESHOLD,
                iou=IOU_THRESHOLD,
                device="cpu",   # fuerza CPU (AMD Ryzen)
                verbose=False
            )

            detections = []
            if len(results) > 0:
                res = results[0]
                boxes = res.boxes
                names = res.names if hasattr(res, "names") else model.names

                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                    cls_id = int(box.cls[0]) if box.cls is not None else -1
                    conf = float(box.conf[0]) if box.conf is not None else 0.0
                    label_en = names.get(cls_id, str(cls_id))
                    label_es = to_spanish(label_en, labels_dict)

                    # Filtrar cajas pequeñas o baja confianza
                    if conf < CONF_THRESHOLD:
                        continue
                    if (x2 - x1) * (y2 - y1) < MIN_BOX_AREA:
                        continue

                    detections.append((label_es, conf, x1, y1, x2, y2))

            # Guardar en CSV
            if detections:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                with open(CSV_PATH, mode="a", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    for label_es, conf, x1, y1, x2, y2 in detections:
                        writer.writerow([timestamp, label_es, f"{conf:.2f}", x1, y1, x2, y2])

            # Resumen en consola (solo si cambió o cada PRINT_INTERVAL segundos)
            if detections:
                counts = Counter([d[0] for d in detections])
                summary = ", ".join([f"{cls}:{cnt}" for cls, cnt in counts.items()])
                now = time.time()
                if summary != last_summary or (now - last_print > PRINT_INTERVAL):
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Detecciones → {summary}")
                    last_summary = summary
                    last_print = now
            else:
                now = time.time()
                if now - last_print > PRINT_INTERVAL:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Sin detecciones")
                    last_print = now

except KeyboardInterrupt:
    print("🛑 Procesamiento detenido por el usuario.")
except Exception as e:
    print(f"❌ Error: {e}")
