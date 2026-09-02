from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse
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
    # Insere veículos de exemplo para teste
    cursor.execute("INSERT OR IGNORE INTO credenciados VALUES ('ABC1D23', 'João Silva', 'Idoso')")
    cursor.execute("INSERT OR IGNORE INTO credenciados VALUES ('XYZ9876', 'Maria Oliveira', 'PcD')")
    conn.commit()
    conn.close()

init_db()

class ChecagemVaga(BaseModel):
    vaga_id: str
    placa: str

# --- PAINEL WEB ---

@app.get("/", response_class=HTMLResponse)
def dashboard():
    html_content = """
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <title>VagaCerta - Painel de Controle</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #121212; color: #fff; margin: 0; padding: 20px; }
            h1, h2 { color: #00e676; margin-bottom: 10px; }
            .container { max-width: 1100px; margin: auto; }
            .card { background: #1e1e1e; padding: 20px; border-radius: 8px; margin-bottom: 25px; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }
            
            /* Formulário */
            .form-group { display: flex; gap: 15px; margin-top: 15px; flex-wrap: wrap; }
            input, select, button { padding: 12px; border-radius: 6px; border: 1px solid #333; background: #2a2a2a; color: #fff; font-size: 14px; }
            input:focus, select:focus { outline: none; border-color: #00e676; }
            .btn-submit { background: #00e676; color: #121212; font-weight: bold; cursor: pointer; border: none; transition: 0.2s; }
            .btn-submit:hover { background: #00c853; }
            
            /* Tabelas */
            table { width: 100%; border-collapse: collapse; margin-top: 15px; background: #181818; border-radius: 6px; overflow: hidden; }
            th, td { padding: 12px 15px; text-align: left; border-bottom: 1px solid #2a2a2a; vertical-align: middle; }
            th { background-color: #252525; color: #00e676; text-transform: uppercase; font-size: 13px; }
            .badge-infracao { background: #ff1744; color: #fff; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 12px; }
            .badge-tipo { background: #29b6f6; color: #121212; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 12px; }
            .thumb-evidencia { width: 110px; height: 70px; object-fit: cover; border-radius: 4px; border: 1px solid #00e676; }
            .flex-header { display: flex; justify-content: space-between; align-items: center; }
            .refresh-btn { background: #333; color: #00e676; border: 1px solid #00e676; padding: 8px 15px; font-weight: bold; cursor: pointer; border-radius: 4px; }
            .refresh-btn:hover { background: #00e676; color: #121212; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚦 VagaCerta - Sistema de Monitoramento</h1>
            <p style="color: #aaa;">Gestão de vagas reservadas (Idosos / PcDs) com Validação Visual em Tempo Real</p>

            <!-- CARD 1: FORMULÁRIO DE CADASTRO -->
            <div class="card">
                <h2>📝 Cadastrar Novo Motorista Credenciado</h2>
                <form action="/api/cadastrar-credenciado" method="POST" class="form-group">
                    <input type="text" name="placa" placeholder="Placa (ex: ABC1D23)" required style="flex: 1; text-transform: uppercase;">
                    <input type="text" name="nome" placeholder="Nome do Beneficiário" required style="flex: 2;">
                    <select name="tipo" required style="flex: 1;">
                        <option value="Idoso">Idoso</option>
                        <option value="PcD">PcD</option>
                    </select>
                    <button type="submit" class="btn-submit">➕ Cadastrar Placa</button>
                </form>
            </div>

            <!-- CARD 2: TABELA DE REGISTRO DE INFRAÇÕES -->
            <div class="card">
                <div class="flex-header">
                    <h2>🚨 Registro de Infrações Detectadas</h2>
                    <button class="refresh-btn" onclick="carregarInfracoes()">🔄 Atualizar</button>
                </div>
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

            <!-- CARD 3: TABELA DE MOTORISTAS CREDENCIADOS -->
            <div class="card">
                <h2>✅ Motoristas Credenciados no Sistema</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Placa</th>
                            <th>Nome do Motorista</th>
                            <th>Credencial</th>
                        </tr>
                    </thead>
                    <tbody id="tabela-credenciados">
                        <tr><td colspan="3">Carregando credenciados...</td></tr>
                    </tbody>
                </table>
            </div>
        </div>

        <script>
            async function carregarInfracoes() {
                try {
                    const resposta = await fetch('/api/infracoes');
                    const dados = await resposta.json();
                    const tabela = document.getElementById('tabela-infracoes');
                    tabela.innerHTML = '';

                    if (dados.length === 0) {
                        tabela.innerHTML = '<tr><td colspan="6" style="color:#aaa;">Nenhuma infração registrada até o momento.</td></tr>';
                        return;
                    }

                    dados.forEach(item => {
                        const tr = document.createElement('tr');
                        const fotoUrl = item.foto ? `/static/infracoes/${item.foto}` : '';
                        const imgTag = item.foto 
                            ? `<a href="${fotoUrl}" target="_blank"><img src="${fotoUrl}?t=${new Date().getTime()}" class="thumb-evidencia" alt="Evidência"/></a>`
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
                    console.error('Erro ao buscar infrações:', erro);
                }
            }

            async function carregarCredenciados() {
                try {
                    const resposta = await fetch('/api/credenciados');
                    const dados = await resposta.json();
                    const tabela = document.getElementById('tabela-credenciados');
                    tabela.innerHTML = '';

                    dados.forEach(item => {
                        const tr = document.createElement('tr');
                        tr.innerHTML = `
                            <td><strong>${item.placa}</strong></td>
                            <td>${item.nome}</td>
                            <td><span class="badge-tipo">${item.tipo}</span></td>
                        `;
                        tabela.appendChild(tr);
                    });
                } catch (erro) {
                    console.error('Erro ao buscar credenciados:', erro);
                }
            }

            setInterval(carregarInfracoes, 3000);
            carregarInfracoes();
            carregarCredenciados();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# --- ENDPOINTS DA API ---

@app.post("/api/cadastrar-credenciado")
def cadastrar_credenciado(placa: str = Form(...), nome: str = Form(...), tipo: str = Form(...)):
    conn = sqlite3.connect("vagacerta.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO credenciados (placa, nome, tipo) VALUES (?, ?, ?)",
        (placa.strip().upper(), nome.strip(), tipo)
    )
    conn.commit()
    conn.close()
    return RedirectResponse(url="/", status_code=303)

@app.get("/api/credenciados")
def listar_credenciados():
    conn = sqlite3.connect("vagacerta.db")
    cursor = conn.cursor()
    cursor.execute("SELECT placa, nome, tipo FROM credenciados ORDER BY nome ASC")
    linhas = cursor.fetchall()
    conn.close()
    return [{"placa": row[0], "nome": row[1], "tipo": row[2]} for row in linhas]

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