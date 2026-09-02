from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import sqlite3
from datetime import datetime
import os
from pathlib import Path

app = FastAPI(title="VagaCerta API")

# Define caminho absoluto para a pasta estática
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static" / "infracoes"
STATIC_DIR.mkdir(parents=True, exist_ok=True)

# Servidor de arquivos estáticos
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

def init_db():
    conn = sqlite3.connect("vagacerta.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS credenciados (
            placa TEXT PRIMARY KEY,
            nome TEXT,
            tipo TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS infracoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vaga TEXT,
            placa TEXT,
            data_hora TEXT,
            status TEXT,
            foto TEXT
        )
    """)
    cursor.execute("INSERT OR IGNORE INTO credenciados VALUES ('ABC1D23', 'João Silva', 'Idoso')")
    conn.commit()
    conn.close()

init_db()

class ChecagemVaga(BaseModel):
    vaga_id: str
    placa: str

@app.get("/", response_class=HTMLResponse)
def dashboard():
    html_content = """
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <title>VagaCerta - Painel de Monitoramento</title>
        <style>
            body { font-family: Arial, sans-serif; background-color: #121212; color: #fff; margin: 20px; }
            h1 { color: #00e676; text-align: center; }
            .container { max-width: 1000px; margin: auto; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; background: #1e1e1e; }
            th, td { padding: 12px; text-align: left; border-bottom: 1px solid #333; vertical-align: middle; }
            th { background-color: #2e2e2e; color: #00e676; }
            .badge-infracao { background: #ff1744; padding: 5px 10px; border-radius: 4px; font-weight: bold; }
            .thumb-evidencia { width: 120px; height: 80px; object-fit: cover; border-radius: 4px; border: 1px solid #00e676; }
            .refresh-btn { background: #00e676; border: none; padding: 10px 20px; font-weight: bold; cursor: pointer; border-radius: 4px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚦 VagaCerta - Painel de Controle e Evidências</h1>
            <p>Monitoramento de Vagas Reservadas com Validação Visual</p>
            <button class="refresh-btn" onclick="carregarInfracoes()">🔄 Atualizar Dados</button>
            
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Evidência</th>
                        <th>Vaga</th>
                        <th>Placa</th>
                        <th>Data / Hora</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody id="tabela-infracoes">
                    <tr><td colspan="6">Carregando infrações...</td></tr>
                </tbody>
            </table>
        </div>

        <script>
            async function carregarInfracoes() {
                try {
                    const resposta = await fetch('/api/infracoes');
                    const dados = await resposta.json();
                    const tabela = document.getElementById('tabela-infracoes');
                    tabela.innerHTML = '';

                    if (dados.length === 0) {
                        tabela.innerHTML = '<tr><td colspan="6">Nenhuma infração registrada até o momento.</td></tr>';
                        return;
                    }

                    dados.forEach(item => {
                        const tr = document.createElement('tr');
                        const fotoUrl = item.foto ? `/static/infracoes/${item.foto}` : '';
                        const imgTag = item.foto 
                            ? `<a href="${fotoUrl}" target="_blank"><img src="${fotoUrl}?t=${new Date().getTime()}" class="thumb-evidencia" alt="Foto da Infração"/></a>`
                            : `<span style="color:#888;">Sem Imagem</span>`;
                        
                        tr.innerHTML = `
                            <td>#${item.id}</td>
                            <td>${imgTag}</td>
                            <td>${item.vaga}</td>
                            <td><strong>${item.placa}</strong></td>
                            <td>${item.data_hora}</td>
                            <td><span class="badge-infracao">${item.status}</span></td>
                        `;
                        tabela.appendChild(tr);
                    });
                } catch (erro) {
                    console.error('Erro ao buscar dados:', erro);
                }
            }

            setInterval(carregarInfracoes, 3000);
            carregarInfracoes();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/api/infracoes")
def listar_infracoes():
    conn = sqlite3.connect("vagacerta.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, vaga, placa, data_hora, status, foto FROM infracoes ORDER BY id DESC")
    linhas = cursor.fetchall()
    conn.close()
    
    return [
        {"id": row[0], "vaga": row[1], "placa": row[2], "data_hora": row[3], "status": row[4], "foto": row[5]}
        for row in linhas
    ]

@app.post("/api/checar-vaga")
def checar_vaga(dados: ChecagemVaga):
    conn = sqlite3.connect("vagacerta.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT nome, tipo FROM credenciados WHERE placa = ?", (dados.placa.upper(),))
    veiculo = cursor.fetchone()
    
    data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if veiculo:
        conn.close()
        return {
            "autorizado": True,
            "mensagem": f"Veículo REGULAR ({veiculo[1]} - {veiculo[0]})",
            "placa": dados.placa.upper()
        }
    else:
        nome_foto = f"infracao_{dados.placa.upper()}_{int(datetime.now().timestamp())}.jpg"
        
        cursor.execute(
            "INSERT INTO infracoes (vaga, placa, data_hora, status, foto) VALUES (?, ?, ?, ?, ?)",
            (dados.vaga_id, dados.placa.upper(), data_atual, "PENDENTE_VERIFICACAO", nome_foto)
        )
        conn.commit()
        conn.close()
        
        return {
            "autorizado": False,
            "mensagem": "ALERTA: Veículo NÃO AUTORIZADO! Infração registrada.",
            "placa": dados.placa.upper(),
            "nome_foto": nome_foto
        }