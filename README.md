# Projeto Dublagem AI

Projeto de pipeline de dublagem automatizada utilizando ASR, TTS, embeddings e alinhamento de áudio.  
Permite converter texto em fala sincronizada, com possibilidade de integração labial opcional via Wav2Lip.

## Funcionalidades

- Estrutura modular baseada em Protocols (ASR, TTS, Embedding, Alignment)
- Pipeline ponta a ponta com mocks para testes
- Substituição gradual de mocks por modelos reais (Whisper, Resemblyzer, YourTTS, etc.)
- Cobertura de testes 100% e integração contínua configurada

## Instalação

```bash
# Clonar repositório
git clone <URL_DO_REPOSITORIO>
cd <PASTA_DO_REPOSITORIO>
```

# Instalar o Poetry
```bash
curl -sSL https://install.python-poetry.org | python3 -
```
```bash
export PATH="$HOME/.local/bin:$PATH"
```
```bash
source ~/.bashrc   # ou source ~/.zshrc
```
```bash
poetry --version
```

# Observação: Se você preferir, também dá pra instalar com pipx:
```bash
pipx install poetry
```


# Instalar dependências
````bash
poetry install
````

## Testes

```bash
# Rodar testes unitários
pytest

# Cobertura completa
coverage run -m pytest
coverage report --fail-under=100
```

## Documentação

O roadmap completo do projeto, com milestones e issues detalhadas, está em:

[docs/roadmap.md](docs/roadmap.md)

## Contribuição

* Seguir padrões de lint (black, isort, ruff)
* Manter 100% de cobertura de testes
* Criar novas issues no GitHub para funcionalidades futuras
