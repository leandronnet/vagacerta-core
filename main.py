import subprocess
import time
import sys

print("🚀 Iniciando o ecossistema VagaCerta...")

# 1. Inicia o Servidor FastAPI (server.py) em segundo plano
servidor = subprocess.Popen([sys.executable, "-m", "uvicorn", "server:app"])
print("🌐 Servidor Web iniciado na porta 8000!")

# Aguarda 3 segundos para garantir que a API subiu completamente
time.sleep(3)

# 2. Inicia o Monitoramento de Vídeo (detect_vaga.py)
print("📹 Iniciando Visão Computacional (detect_vaga.py)...")
try:
    subprocess.run([sys.executable, "detect_vaga.py"])
except KeyboardInterrupt:
    pass
finally:
    # Quando você fechar a janela do vídeo ou parar o script, fecha o servidor também
    print("\n🛑 Encerrando o servidor VagaCerta...")
    servidor.terminate()
    print("✅ Sistema finalizado com sucesso.")