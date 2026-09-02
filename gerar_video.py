import cv2
import numpy as np

# Configurações do vídeo de teste
largura, altura = 800, 600
fps = 30
duracao_segundos = 8
quadros_totais = fps * duracao_segundos

# Cria o arquivo de vídeo MP4
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('estacionamento.mp4', fourcc, fps, (largura, altura))

print("Gerando arquivo 'estacionamento.mp4' diretamente no seu computador...")

for i in range(quadros_totais):
    # Cria o fundo (estacionamento)
    frame = np.full((altura, largura, 3), 80, dtype=np.uint8)

    # Desenha a vaga marcada
    vaga = np.array([[300, 200], [500, 200], [500, 450], [300, 450]], np.int32)
    cv2.polylines(frame, [vaga], isClosed=True, color=(255, 255, 255), thickness=2)
    cv2.putText(frame, "VAGA RESERVADA", (320, 190), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    # Simula o veículo entrando e estacionando a partir do segundo 2
    pos_y = int(np.clip(50 + (i * 3), 50, 240))
    
    # Desenha o veículo em movimento
    cv2.rectangle(frame, (330, pos_y), (470, pos_y + 160), (180, 100, 50), -1)
    cv2.putText(frame, "CARRO", (370, pos_y + 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    out.write(frame)

out.release()
print("✅ Vídeo 'estacionamento.mp4' criado com SUCESSO na sua pasta!")