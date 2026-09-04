# 🚗 VagaCerta — Sistema Inteligente de Monitoramento de Vagas Reservadas (Idoso/PcD)

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-5C3EE8?style=for-the-badge&logo=opencv)](https://opencv.org/)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-FF6F00?style=for-the-badge&logo=ultralytics)](https://docs.ultralytics.com/)

O **VagaCerta** é uma solução de Visão Computacional e IoT voltada ao monitoramento e fiscalização inteligente de vagas de estacionamento reservadas por lei para **Idosos** e **Pessoas com Deficiência (PcD)**.

O sistema monitora continuamente o fluxo do estacionamento através de câmeras, detecta a ocupação da vaga utilizando IA em tempo real, realiza a leitura da placa do veículo via OCR e valida a autorização do condutor através de uma API integradora conectada ao banco de dados. Caso seja identificada uma irregularidade, uma evidência fotográfica é capturada automaticamente e enviada para o **Dashboard de Fiscalização**.

---

## 🎯 Funcionalidades Principais

- 🔍 **Detecção de Veículos em Tempo Real:** Uso do modelo **YOLOv8** para identificar carros, motos, caminhões e ônibus em áreas delimitadas.
- 📐 **Calibração Dinâmica de Vagas:** Ferramenta gráfica via OpenCV para delimitação e seleção de coordenadas de polígonos de vagas.
- 🔤 **Leitura Automática de Placas (ALPR/OCR):** Reconhecimento de caracteres via **EasyOCR** otimizado com execução assíncrona (*multithreading*).
- ⚡ **API de Validação em Tempo Real:** **FastAPI** provendo regras de negócio e checagem de autorização em frações de segundo.
- 📸 **Captura Automática de Evidências:** Gravação de snapshots fotográficos de veículos autuados por infração.
- 📊 **Dashboard Web Interativo:** Painel dinâmico em tempo real para cadastro de beneficiários, consulta de veículos autorizados e exibição do histórico de autuações.

---

## 🏗️ Arquitetura do Sistema

```text
[ Câmera / Vídeo ] ──> [ YOLOv8 (Detecção) ] ──> [ EasyOCR (Thread Paralela) ]
                                                            │
                                                            ▼
[ Dashboard Web ] <─── [ SQLite ] <─── [ FastAPI ] <─── [ Requisição HTTP ]
      │                                    │
      └─── Displays e Evidências Visuais ──┴─── Guardador de Fotos (static/infracoes)
🛠️ Tecnologias Utilizadas
Linguagem Principal: Python 3.10+

Visão Computacional: OpenCV, Ultralytics YOLOv8

Leitura de Texto / OCR: EasyOCR

Back-end & API REST: FastAPI, Uvicorn

Persistência de Dados: SQLite3

Front-end / Dashboard: HTML5, CSS3, JavaScript (Fetch API / Polling)

🚀 Como Executar o Projeto Localmente
Pré-requisitos
Python 3.10+ instalado

Git instalado

1. Clonar o Repositório
Bash
git clone [https://github.com/leandronnet/vagacerta-core.git](https://github.com/leandronnet/vagacerta-core.git)
cd vagacerta-core
2. Criar e Ativar o Ambiente Virtual
Bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / MacOS
python3 -m venv venv
source venv/bin/activate
3. Instalar as Dependências
Bash
pip install -r requirements.txt
💻 Execução do Ecossistema
Para rodar a aplicação completa, utilize dois terminais concorrentes:

Passo 1: Subir o Servidor Web e API (Terminal 1)
Bash
py -m uvicorn server:app --reload
Acesse o Dashboard Web no navegador: http://127.0.0.1:8000/

Passo 2: Executar o Loop de Visão Computacional (Terminal 2)
Bash
python detect_vaga.py
🎯 Ferramentas de Apoio
🎥 Gerador de Vídeo Sintético de Teste
Para rodar a simulação sem dependência de gravações externas:

Bash
python gerar_video.py
📍 Calibrador de Coordenadas da Vaga
Caso precise recalibrar os 4 cantos da vaga em uma nova câmera ou vídeo:

Bash
python calibrar_vaga.py
📂 Estrutura de Pastas
Plaintext
vagacerta-core/
├── static/
│   └── infracoes/        # Evidências fotográficas salvas em tempo real
├── templates/
│   └── index.html        # Dashboard Web
├── server.py             # Servidor FastAPI e Endpoints
├── detect_vaga.py        # Loop de visão computacional, YOLO e EasyOCR
├── calibrar_vaga.py      # Utilitário visual para mapeamento de polígono
├── gerar_video.py        # Gerador sintético de simulação de estacionamento
├── vagacerta.db          # Banco de dados SQLite
├── requirements.txt      # Dependências do projeto
└── README.md             # Documentação do repositório

## 🤝 Créditos e Co-pilotagem

Este projeto foi desenvolvido por **Leandro Silva** com o auxílio do assistente de inteligência artificial **Gemini (Google)** como ferramenta de arquitetura, co-pilotagem de código, otimização de performance e suporte no desenvolvimento.