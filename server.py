from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import sqlite3
from datetime import datetime

app = FastAPI(title="VagaCerta API")

# --- BANCO DE DADOS (SQLite Local) ---
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
            status TEXT
        )
    """)
    cursor.execute("INSERT OR IGNORE INTO credenciados VALUES ('ABC1D23', 'João Silva', 'Idoso')")
    conn.commit()
    conn.close()

init_db()

class ChecagemVaga(BaseModel):
    vaga_id: str
    placa: str

# --- ENDPOINTS DA API ---

@app.get("/", response_class=HTMLResponse)
def dashboard():
    """Painel de Controle do Operador em HTML/JS"""
    html_content = """
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <title>VagaCerta - Painel de Monitoramento</title>
        <style>
            body { font-family: Arial, sans-serif; background-color: #121212; color: #fff; margin: 20px; }
            h1 { color: #00e676; text-align: center; }
            .container { max-width: 900px; margin: auto; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; background: #1e1e1e; }
            th, td { padding: 12px; text-align: left; border-bottom: 1px solid #333; }
            th { background-color: #2e2e2e; color: #00e676; }
            .badge-infracao { background: #ff1744; padding: 5px 10px; border-radius: 4px; font-weight: bold; }
            .refresh-btn { background: #00e676; border: none; padding: 10px 20px; font-weight: bold; cursor: pointer; border-radius: 4px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚦 VagaCerta - Painel de Controle e Infrações</h1>
            <p>Monitoramento de Vagas Reservadas em Tempo Real</p>
            <button class="refresh-btn" onclick="carregarInfracoes()">🔄 Atualizar Dados</button>
            
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Vaga</th>
                        <th>Placa</th>
                        <th>Data / Hora</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody id="tabela-infracoes">
                    <tr><td colspan="5">Carregando infrações...</td></tr>
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
                        tabela.innerHTML = '<tr><td colspan="5">Nenhuma infração registrada até o momento.</td></tr>';
                        return;
                    }

                    dados.forEach(item => {
                        const tr = document.createElement('tr');
                        tr.innerHTML = `
                            <td>#${item.id}</td>
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

            // Atualiza automaticamente a cada 3 segundos
            setInterval(carregarInfracoes, 3000);
            carregarInfracoes();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/api/infracoes")
def listar_infracoes():
    """Retorna todas as infrações registradas no banco"""
    conn = sqlite3.connect("vagacerta.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, vaga, placa, data_hora, status FROM infracoes ORDER BY id DESC")
    linhas = cursor.fetchall()
    conn.close()
    
    resultado = [
        {"id": row[0], "vaga": row[1], "placa": row[2], "data_hora": row[3], "status": row[4]}
        for row in linhas
    ]
    return resultado

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
        cursor.execute(
            "INSERT INTO infracoes (vaga, placa, data_hora, status) VALUES (?, ?, ?, ?)",
            (dados.vaga_id, dados.placa.upper(), data_atual, "PENDENTE_VERIFICACAO")
        )
        conn.commit()
        conn.close()
        
        return {
            "autorizado": False,
            "mensagem": "ALERTA: Veículo NÃO AUTORIZADO! Infração registrada.",
            "placa": dados.placa.upper()
        }