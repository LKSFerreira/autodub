# 🤖 autodub: Pipeline de Dublagem Automática com IA

![CI - Teste e Qualidade do Código](https://github.com/LKSFerreira/autodub/actions/workflows/ci.yml/badge.svg)
[![Coverage Status](https://coveralls.io/repos/github/LKSFerreira/autodub/badge.svg?branch=main)](https://coveralls.io/github/LKSFerreira/autodub?branch=main)
[![code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Projeto de um pipeline de dublagem automatizada utilizando ASR (Reconhecimento de Fala), TTS (Síntese de Fala) e embeddings de voz para preservar o timbre do locutor original.

A arquitetura é modular e projetada para ser extensível, com uma base sólida de testes e automação de qualidade de código.

## ✨ Funcionalidades Principais

- **Estrutura Modular:** Baseado em interfaces (Protocols) para cada componente (ASR, TTS, Embedding, etc.), permitindo a fácil substituição de modelos.
- **Pipeline Completo:** Orquestração de ponta a ponta, desde a ingestão do vídeo até a reinserção do áudio dublado.
- **Qualidade de Código Automatizada:** Uso de `pre-commit` com `ruff`, `black` e `isort` para garantir um padrão de código consistente.
- **Testes e CI/CD:** Pipeline de Integração Contínua com GitHub Actions que valida o código e exige **100% de cobertura de testes**.

## 🛠️ Tecnologias Principais

- **Linguagem:** Python 3.12+
- **Gerenciador de Dependências:** Poetry
- **Testes:** Pytest & Coverage.py
- **Qualidade de Código:** Ruff, Black, isort
- **Automação:** Pre-commit & GitHub Actions

## 🚀 Começando

Siga os passos abaixo para configurar seu ambiente de desenvolvimento.

### Pré-requisitos

- Git
- Python 3.12 ou superior
- [Poetry](https://python-poetry.org/docs/#installation) (recomendamos a instalação via `pipx`)

### Configuração do Ambiente

**Clone o Repositório:**
```bash
git clone https://github.com/LKSFerreira/autodub.git
cd autodub
```

#### Execute o script bash `configure_repo.sh` localizado na raiz do projeto:
```bash
./configure_repo.sh
```
---
#### Configuração Manual do ambiente após clonar o repositório:
1. **Instale o Poetry**
    ```bash
    pipx install poetry
    ```

2. **Configura o ambiente para criar ambientes virtuais dentro da pasta do projeto:**
    ```bash
    poetry config virtualenvs.in-project true
    ```

2.  **Instale as Dependências:**
    O Poetry criará um ambiente virtual e instalará todas as dependências listadas no `pyproject.toml`.
    ```bash
    poetry install
    ```

3.  **Instale os Hooks de Git (Passo Crucial!):**
    Este comando ativa a automação de qualidade de código local. Ele rodará `ruff`, `black` e `isort` automaticamente antes de cada commit. **É obrigatório rodá-lo uma vez após clonar o projeto.**
    ```bash
    poetry run pre-commit install
    ```


🎉🎉 **Seu ambiente está pronto !** 🎉🎉

---

## 🧪 Rodando os Testes

Para garantir que tudo está funcionando corretamente, execute a suíte de testes.

- **Executar todos os testes:**
  ```bash
  poetry run pytest
````

  - **Executar os testes e gerar o relatório de cobertura:**
    Este comando validará se a cobertura de 100% está sendo mantida.
    ```bash
    poetry run coverage run -m pytest
    poetry run coverage report --fail-under=100
    ```

## 🤖 Qualidade de Código e CI/CD

Este projeto leva a qualidade de código a sério. Duas camadas de automação garantem isso:

1.  **Pre-commit Hooks (Local):** Antes de cada commit, as ferramentas de formatação (`black`, `isort`) e linting (`ruff`) são executadas. Commits com código fora do padrão são bloqueados até que os problemas sejam corrigidos (muitas vezes, automaticamente).

2.  **Integração Contínua (GitHub Actions):** A cada `push` ou `pull request`, um workflow é acionado para rodar todos os testes e validar a cobertura em um ambiente limpo. Ele é o guardião final da qualidade do projeto.

## 🤝 Contribuindo

1.  Crie uma nova `branch` para sua funcionalidade (`git checkout -b feat/minha-feature`).
2.  Adicione seu código, sempre com testes correspondentes para manter a cobertura de 100%.
3.  Faça o commit das suas alterações (os hooks de pre-commit serão executados).
4.  Abra um `Pull Request`.

## 📄 Licença

Este projeto é distribuído sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

```
```