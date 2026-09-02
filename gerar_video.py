import cv2
import numpy as np

# Configurações do Vídeo
LARGURA, ALTURA = 1280, 720
FPS = 30
DURACAO_SEGUNDOS = 8
TOTAL_FRAMES = FPS * DURACAO_SEGUNDOS

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('estacionamento.mp4', fourcc, FPS, (LARGURA, ALTURA))

print("🎬 Gerando vídeo realista de estacionamento...")

def desenhar_cenario():
    # Asfalto com textura suave
    frame = np.full((ALTURA, LARGURA, 3), (50, 50, 50), dtype=np.uint8)
    
    # Guias/Meio-fio no topo
    cv2.rectangle(frame, (0, 0), (LARGURA, 80), (100, 100, 100), -1)
    cv2.line(frame, (0, 80), (LARGURA, 80), (200, 200, 200), 4)

    # Linhas demarcatórias da Vaga (Amarelo Regulamentar)
    # Vaga PCD/Idoso centralizada: X de 450 a 830, Y de 150 a 650
    cv2.rectangle(frame, (450, 150), (830, 650), (0, 215, 255), 6) # Bordas amarelas
    
    # Pintura interna azul de vaga especial
    overlay = frame.copy()
    cv2.rectangle(overlay, (456, 156), (824, 644), (180, 80, 0), -1) # Azul especial
    cv2.addWeighted(overlay, 0.4, frame, 0.6, 0, frame)

    # Símbolo no chão (Pintura de Vaga Especial)
    cv2.putText(frame, "VAGA RESERVADA", (480, 200), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    cv2.putText(frame, "IDOSO / PCD", (510, 240), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    return frame

def desenhar_carro(frame, x, y, angulo=0, farois_ligados=True):
    # Desenho estilizado de um veículo vindo de cima
    # Tamanho do veículo: 240px de largura x 380px de comprimento
    
    # Sombra projetada do veículo (para ganho de realismo)
    cv2.ellipse(frame, (x + 10, y + 15), (130, 200), 0, 0, 360, (20, 20, 20), -1)

    # Corpo do Veículo (Carro sedan prata/grafite moderno)
    cv2.rectangle(frame, (x - 110, y - 180), (x + 110, y + 180), (80, 80, 80), -1) # Base
    cv2.rectangle(frame, (x - 105, y - 175), (x + 105, y + 175), (160, 160, 160), -1) # Pintura metálica
    
    # Teto e Para-brisas (Vidros escuros)
    cv2.rectangle(frame, (x - 90, y - 80), (x + 90, y + 100), (40, 40, 40), -1) # Teto
    cv2.rectangle(frame, (x - 85, y - 120), (x + 85, y - 85), (20, 20, 20), -1) # Para-brisa dianteiro
    cv2.rectangle(frame, (x - 85, y + 105), (x + 85, y + 140), (20, 20, 20), -1) # Para-brisa traseiro

    # Faróis Dianteiros
    cor_farol = (200, 255, 255) if farois_ligados else (100, 100, 100)
    cv2.rectangle(frame, (x - 100, y - 178), (x - 70, y - 168), cor_farol, -1)
    cv2.rectangle(frame, (x + 70, y - 178), (x + 100, y - 168), cor_farol, -1)
    
    # Luzes de Freio/Traseiras
    cv2.rectangle(frame, (x - 100, y + 168), (x - 70, y + 178), (0, 0, 220), -1)
    cv2.rectangle(frame, (x + 70, y + 168), (x + 100, y + 178), (0, 0, 220), -1)

    # Placa do Carro (Legível para OCR)
    cv2.rectangle(frame, (x - 60, y + 165), (x + 60, y + 182), (255, 255, 255), -1)
    cv2.rectangle(frame, (x - 60, y + 165), (x + 60, y + 182), (0, 0, 0), 1)
    cv2.putText(frame, "XYZ9876", (x - 48, y + 179), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 2)

# Gera os quadros com a animação de estacionar
for i in range(TOTAL_FRAMES):
    cenario = desenhar_cenario()
    
    # Posição inicial: fora da vaga (Y = 900)
    # Posição final: estacionado perfeito na vaga (X = 640, Y = 400)
    
    progresso = min(1.0, i / (TOTAL_FRAMES * 0.7)) # Estaciona nos primeiros 70% do vídeo
    
    # Interpolação suave de movimento
    y_carro = int(880 - (progresso * 480))
    x_carro = 640
    
    farois = True if progresso < 1.0 else False # Desliga os faróis ao estacionar
    
    desenhar_carro(cenario, x_carro, y_carro, farois_ligados=farois)
    
    out.write(cenario)

out.release()
print("✅ Vídeo 'estacionamento.mp4' gerado com SUCESSO na raiz do projeto!")