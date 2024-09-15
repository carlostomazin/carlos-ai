@echo off

echo 1. Criando virtualenv
python -m venv .venv-ai

echo 2. Selecionando virtualenv
call .\.venv-ai\Scripts\activate

echo 3. Atualizando pip
python -m pip install --upgrade pip

echo 4. Definir a variavel de ambiente CMAKE_ARGS
set CMAKE_ARGS=-DGGML_CUDA=on

echo 5. Executar o pip com a instalacao dos pacotes
pip install --no-cache-dir -r requirements.txt

echo 6. Fazendo download do modelo LLM
python models/download_model.py

:: 5. Pausar o script até que o usuário pressione uma tecla
echo Todos os comandos foram executados!
pause
