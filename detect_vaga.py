import cv2
import numpy as np
from ultralytics import YOLO
import easyocr
import re
import requests

URL_API = "http://127.0.0.1:8000/api/checar-vaga"

print("Carregando inteligência de Leitura de Placas (OCR)...")
reader = easyocr.Reader(['pt', 'en'], gpu=False)
model = YOLO('yolov8n.pt')

VAGA_PCD_01 = np.array([
    [300, 200], [500, 200], [500, 450], [300, 450]
], np.int32)

CLASSES_VEICULOS = [2, 3, 5, 7]

placa_detectada_atual = "Aguardando leitura..."
status_api_mensagem = "Vaga em monitoramento"
placa_consultada = None
contador_frames = 0

def consultar_api_vagacerta(placa):
    global status_api_mensagem
    try:
        payload = {"vaga_id": "VAGA-IDOSO-01", "placa": placa}
        resposta = requests.post(URL_API, json=payload, timeout=2)
        if resposta.status_code == 200:
            dados = resposta.json()
            status_api_mensagem = dados.get("mensagem", "")
            print(f"✅ API Respondeu: {status_api_mensagem}")
        else:
            status_api_mensagem = "Erro na resposta do Servidor"
    except Exception as e:
        status_api_mensagem = "Servidor API offline"

def processar_frame(frame):
    global placa_detectada_atual, status_api_mensagem, placa_consultada, contador_frames
    
    contador_frames += 1
    results = model(frame, verbose=False)[0]
    vaga_ocupada = False

    # Tenta detecção normal via YOLO
    for box in results.boxes:
        cls_id = int(box.cls[0])
        if cls_id in CLASSES_VEICULOS:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            centro_x = int((x1 + x2) / 2)
            centro_y = int(y2)
            if cv2.pointPolygonTest(VAGA_PCD_01, (centro_x, centro_y), False) >= 0:
                vaga_ocupada = True

    # SIMULAÇÃO DE VAGA OCUPADA:
    # Como o vídeo sintético não tem foto real de carro, forçamos a ocupação a partir do quadro 30
    if contador_frames > 30:
        vaga_ocupada = True
        placa_detectada_atual = "XYZ9876"

    if vaga_ocupada and placa_consultada != placa_detectada_atual:
        print(f"🔄 Disparando consulta da placa '{placa_detectada_atual}' para a API...")
        consultar_api_vagacerta(placa_detectada_atual)
        placa_consultada = placa_detectada_atual

    if not vaga_ocupada:
        placa_detectada_atual = "Aguardando leitura..."
        status_api_mensagem = "VAGA LIVRE"

    cor_vaga = (0, 0, 255) if vaga_ocupada else (0, 255, 0)
    cv2.polylines(frame, [VAGA_PCD_01], isClosed=True, color=cor_vaga, thickness=3)
    
    cv2.rectangle(frame, (10, 10), (700, 110), (0, 0, 0), -1)
    cv2.putText(frame, f"VAGA IDOSO 01: {'OCUPADA' if vaga_ocupada else 'LIVRE'}", (20, 35),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, cor_vaga, 2)
    cv2.putText(frame, f"PLACA LIDA: {placa_detectada_atual}", (20, 65),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(frame, f"STATUS API: {status_api_mensagem}", (20, 95),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

    return frame

cap = cv2.VideoCapture('estacionamento.mp4')

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame_processado = processar_frame(frame)
    cv2.imshow("VagaCerta - Detector e OCR", frame_processado)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()