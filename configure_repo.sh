#!/bin/bash
#
# Script de configuração para inicializar e ATIVAR o ambiente de desenvolvimento.
#
# IMPORTANTE: Este script deve ser executado com o comando 'source'.
# Exemplo: source ./configure_repo.sh
#
# Ele irá:
# 1. Instalar o Poetry.
# 2. Configurar o ambiente virtual dentro do diretório do projeto.
# 3. Instalar as dependências.
# 4. Instalar os hooks de pre-commit.
# 5. Ativar o ambiente virtual na sessão atual do terminal.

# --- Configuração de Segurança ---
# Encerra o script imediatamente se um comando falhar.
set -e

# --- Passo 1: Instalar o Poetry ---
echo "--> Passo 1/5: Verificando e instalando o Poetry..."
if ! command -v poetry &> /dev/null
then
    echo "Poetry não encontrado. Instalando..."
    pip install poetry -q
    echo "Poetry instalado com sucesso."
else
    echo "Poetry já está instalado."
fi

# --- Passo 2: Configurar a criação do ambiente virtual localmente ---
echo "--> Passo 2/5: Configurando Poetry para criar ambiente virtual no projeto..."
poetry config virtualenvs.in-project true

# --- Passo 3: Instalar as dependências do projeto ---
echo "--> Passo 3/5: Instalando dependências do projeto com Poetry..."
poetry install

# --- Passo 4: Instalar os hooks do pre-commit ---
echo "--> Passo 4/5: Instalando hooks de pre-commit..."
poetry run pre-commit install

# --- Passo 5: Ativar o ambiente virtual ---
echo "--> Passo 5/5: Ativando o ambiente virtual..."

ACTIVATION_SCRIPT_PATH=""

# Detecta o sistema operacional para encontrar o script de ativação correto.
if [[ -f ".venv/bin/activate" ]]; then
    # Linux ou macOS
    ACTIVATION_SCRIPT_PATH=".venv/bin/activate"
elif [[ -f ".venv/Scripts/activate" ]]; then
    # Windows
    ACTIVATION_SCRIPT_PATH=".venv/Scripts/activate"
else
    echo "ERRO: Não foi possível encontrar o script de ativação do ambiente virtual."
    # Retorna um código de erro para indicar falha
    return 1
fi

# Ativa o ambiente no shell atual
source "$ACTIVATION_SCRIPT_PATH"

echo ""
echo "------------------------------------------------------------------"
echo " Ambiente de desenvolvimento configurado e ATIVADO com sucesso!"
echo " O prompt do seu terminal deve ter sido modificado."
echo "------------------------------------------------------------------"

# Desativa o 'set -e' ao final para não impactar a sessão do terminal do usuário
set +e