@echo off
echo Iniciando VagaCerta...
start cmd /k "python -m uvicorn server:app --reload"
timeout /t 3
python detect_vaga.py