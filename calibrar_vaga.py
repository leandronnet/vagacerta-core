import cv2
import numpy as np

# Guarda os pontos clicados
pontos = []

def clicar_ponto(event, x, y, flags, param):
    global pontos, frame_copia
    if event == cv2.EVENT_LBUTTONDOWN:
        if len(pontos) < 4:
            pontos.append([x, y])
            print(f"📍 Ponto {len(pontos)} capturado: [{x}, {y}]")
            
            # Desenha o ponto na imagem
            cv2.circle(frame_copia, (x, y), 5, (0, 255, 0), -1)
            
            # Se já marcou 4 pontos, desenha o polígono final
            if len(pontos) == 4:
                pts = np.array(pontos, np.int32)
                cv2.polylines(frame_copia, [pts], isClosed=True, color=(0, 255, 0), thickness=2)
                
            cv2.imshow("Calibrador de Vaga - Clique nos 4 cantos", frame_copia)

# Carrega o vídeo e pega o primeiro frame
cap = cv2.VideoCapture('estacionamento.mp4')
ret, frame = cap.read()
cap.release()

if not ret:
    print("❌ Erro ao abrir o arquivo 'estacionamento.mp4'. Verifique o nome do arquivo!")
    exit()

frame_copia = frame.copy()

print("="*60)
print("🎯 CALIBRADOR DE VAGA CERTA")
print("1. Clique com o botão ESQUERDO do mouse nos 4 cantos da vaga.")
print("2. A sequência recomendada é: Superior-Esquerdo -> Superior-Direito -> Inferior-Direito -> Inferior-Esquerdo.")
print("3. Pressione qualquer tecla para encerrar e gerar o código.")
print("="*60)

cv2.imshow("Calibrador de Vaga - Clique nos 4 cantos", frame_copia)
cv2.setMouseCallback("Calibrador de Vaga - Clique nos 4 cantos", clicar_ponto)

cv2.waitKey(0)
cv2.destroyAllWindows()

if len(pontos) == 4:
    print("\n✅ COPIE E COLE O CÓDIGO ABAIXO NO SEU 'detect_vaga.py':\n")
    print(f"VAGA_PCD_01 = np.array({pontos}, np.int32)")
    print("\n" + "="*60)
else:
    print("\n⚠️ Você não selecionou exatamente 4 pontos. Tente rodar o script novamente.")