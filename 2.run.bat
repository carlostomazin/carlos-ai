@echo off

echo 1. Selecionando virtualenv
call .\.venv-ai\Scripts\activate

echo 2. Executando a aplicacao
python -B ./app/main.py

pause
