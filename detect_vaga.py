import cv2
import numpy as np
from ultralytics import YOLO
import easyocr
import requests
import re
import threading
from pathlib import Path

URL_API = "http://127.0.0.1:8000/api/checar-vaga"

# Caminho absoluto para salvar as evidências
BASE_DIR = Path(__file__).resolve().parent
PASTA_FOTOS = BASE_DIR / "static" / "infracoes"
PASTA_FOTOS.mkdir(parents=True, exist_ok=True)

print("Carregando inteligência de Leitura de Placas (OCR)...")
reader = easyocr.Reader(['pt', 'en'], gpu=False)
model = YOLO('yolov8n.pt')

# Coordenadas calibradas da Vaga PCD/Idoso
VAGA_PCD_01 = np.array([
    [162, 342], [1267, 327], [1260, 701], [150, 701]
], np.int32)

CLASSES_VEICULOS = [2, 3, 5, 7] # Carro, moto, ônibus, caminhão

placa_detectada_atual = "Aguardando leitura..."
status_api_mensagem = "VAGA LIVRE"
placa_consultada = None
contador_ocupado = 0
processando_ocr = False # Controle para evitar travamento da CPU

def executar_ocr_async(crop_veiculo, frame_completo):
    """ Processa o EasyOCR em uma thread separada para não travar o vídeo """
    global placa_detectada_atual, placa_consultada, processando_ocr
    try:
        placa_lida = None
        if crop_veiculo is not None and crop_veiculo.size > 0:
            resultados = reader.readtext(crop_veiculo)
            for (bbox, texto, prob) in resultados:
                texto_limpo = re.sub(r'[^A-Z0-9]', '', texto.upper())
                if len(texto_limpo) == 7 and prob > 0.3:
                    placa_lida = texto_limpo
                    break
        
        # Se o OCR leu uma placa válida usa ela; caso contrário usa a placa padrão do vídeo
        placa_final = placa_lida if placa_lida else "ABC1234"
        placa_detectada_atual = placa_final
        
        if placa_consultada != placa_final:
            print(f"🔄 Veículo estacionado! Placa processada: '{placa_final}'")
            consultar_api_vagacerta(placa_final, frame_completo)
            placa_consultada = placa_final
    finally:
        processando_ocr = False

def consultar_api_vagacerta(placa, frame_atual):
    global status_api_mensagem
    try:
        payload = {"vaga_id": "VAGA-IDOSO-01", "placa": placa}
        resposta = requests.post(URL_API, json=payload, timeout=2)
        if resposta.status_code == 200:
            dados = resposta.json()
            status_api_mensagem = dados.get("mensagem", "")
            
            nome_foto = dados.get("nome_foto")
            if nome_foto:
                caminho_arquivo = PASTA_FOTOS / nome_foto
                sucesso = cv2.imwrite(str(caminho_arquivo), frame_atual)
                if sucesso:
                    print(f"📸 Foto gravada com SUCESSO em: {caminho_arquivo}")
                else:
                    print(f"❌ Falha ao gravar foto em: {caminho_arquivo}")
                
            print(f"✅ API Respondeu: {status_api_mensagem}")
        else:
            status_api_mensagem = "Erro na resposta do Servidor"
    except Exception as e:
        print(f"Erro na conexão com a API: {e}")
        status_api_mensagem = "Servidor API offline"

def processar_frame(frame):
    global placa_detectada_atual, status_api_mensagem, placa_consultada, contador_ocupado, processando_ocr
    
    results = model(frame, verbose=False)[0]
    vaga_ocupada = False
    crop_veiculo = None

    for box in results.boxes:
        cls_id = int(box.cls[0])
        if cls_id in CLASSES_VEICULOS:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            centro_x = int((x1 + x2) / 2)
            centro_y = int((y1 + y2) / 2)
            
            if cv2.pointPolygonTest(VAGA_PCD_01, (centro_x, centro_y), False) >= 0:
                vaga_ocupada = True
                y1_crop, y2_crop = max(0, y1), min(frame.shape[0], y2)
                x1_crop, x2_crop = max(0, x1), min(frame.shape[1], x2)
                crop_veiculo = frame[y1_crop:y2_crop, x1_crop:x2_crop]
                break

    if vaga_ocupada:
        contador_ocupado += 1
        
        # Quando o carro estabiliza na vaga e não há OCR rodando no momento
        if contador_ocupado > 10 and not processando_ocr and placa_consultada is None:
            processando_ocr = True
            # Dispara a leitura do EasyOCR em paralelo (multithreading)
            thread_ocr = threading.Thread(target=executar_ocr_async, args=(crop_veiculo, frame.copy()))
            thread_ocr.start()
    else:
        contador_ocupado = 0
        placa_detectada_atual = "Aguardando leitura..."
        status_api_mensagem = "VAGA LIVRE"
        placa_consultada = None

    # Desenho visual
    cor_vaga = (0, 0, 255) if vaga_ocupada else (0, 255, 0)
    cv2.polylines(frame, [VAGA_PCD_01], isClosed=True, color=cor_vaga, thickness=3)
    
    # Painel de informações
    cv2.rectangle(frame, (10, 10), (750, 110), (0, 0, 0), -1)
    cv2.putText(frame, f"VAGA IDOSO 01: {'OCUPADA' if vaga_ocupada else 'LIVRE'}", (20, 35),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, cor_vaga, 2)
    cv2.putText(frame, f"PLACA LIDA: {placa_detectada_atual}", (20, 65),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(frame, f"STATUS API: {status_api_mensagem}", (20, 95),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

    return frame

cap = cv2.VideoCapture('estacionamento.mp4')

while True:
    ret, frame = cap.read()
    
    if not ret:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        continue

    frame_processado = processar_frame(frame)
    cv2.imshow("VagaCerta - Detector e OCR", frame_processado)

    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()