## Contexto e Diretrizes do Projeto AutoDub

Este documento fornece o contexto e as diretrizes para o desenvolvimento do projeto AutoDub.

## 1. Visão Geral do Projeto

O AutoDub é um pipeline de dublagem automática de vídeos. O sistema orquestra uma série de componentes para realizar as seguintes tarefas:

1.  **Extração de Áudio**: Extrai a trilha de áudio de um arquivo de vídeo de entrada.
2.  **Transcrição (ASR)**: Converte a fala do áudio original em texto.
3.  **Extração de Embedding**: Analisa o áudio original para extrair a característica vocal (embedding) do locutor.
4.  **Síntese de Voz (TTS)**: Gera um novo áudio a partir do texto transcrito, potencialmente em outro idioma e utilizando o embedding para clonagem de voz.
5.  **Concatenação**: Junta os segmentos de áudio sintetizados em uma única trilha.
6.  **Muxing**: Combina o áudio recém-gerado com o vídeo original, criando o arquivo de vídeo dublado.

## 2. Estrutura e Tecnologias

-   **Linguagem**: Python 3.12+
-   **Gerenciador de Dependências**: Poetry
-   **Estrutura**:
    -   `src/`: Código fonte da aplicação.
    -   `tests/`: Testes unitários e de integração.
-   **Componentes Principais**:
    -   **ASR**: `openai-whisper`
    -   **Embedding**: `resemblyzer`
    -   **Manipulação de Áudio/Vídeo**: `ffmpeg`
-   **Testes**:
    -   **Framework**: `pytest`
    -   **Cobertura**: `coverage.py` (com meta de 100%)

## 3. Diretrizes de Codificação

A principal diretriz é a **padronização do idioma** para facilitar a leitura e manutenção do código.

-   **Idioma Principal**: **Português do Brasil (pt-br)**.
-   **Nomenclatura**:
    -   Nomes de **variáveis, funções, métodos, classes e argumentos** devem ser em pt-br.
    -   Comentários e docstrings também devem ser em pt-br.
-   **Exceções**:
    -   **Palavras-chave da linguagem** (`class`, `def`, `if`, `for`, etc.).
    -   Nomes de **arquivos** e **pastas** podem ser mantidos em inglês para compatibilidade entre sistemas (ex: `src`, `tests`, `test_pipeline.py`).
    -   Funções de teste devem obrigatoriamente começar com o prefixo `test_`.
    -   Nomes de bibliotecas e suas funções (`pytest.raises`, `numpy.array`).

## 4. Exemplo de Código

```python
# CORRETO
def calcular_imposto(valor_total: float) -> float:
    '''Calcula o imposto sobre um valor.'''
    taxa_imposto = 0.05
    return valor_total * taxa_imposto

# INCORRETO
def calculate_tax(total_value: float) -> float:
    '''Calculates tax on a value.'''
    tax_rate = 0.05
    return total_value * tax_rate
```

## Padrão de Commits

Utilize o seguinte padrão para as mensagens de commit, incluindo o emoji correspondente para facilitar a identificação do tipo de alteração:

- 🎉 `:tada: Commit inicial`
- 📚 `:books: docs: Atualização do README`
- 🐛 `:bug: fix: Loop infinito na linha 50`
- ✨ `:sparkles: feat: Página de login`
- 🧱 `:bricks: ci: Modificação no Dockerfile`
- ♻️ `:recycle: refactor: Passando para arrow functions`
- ⚡ `:zap: perf: Melhoria no tempo de resposta`
- 💥 `:boom: fix: Revertendo mudanças ineficientes`
- 💄 `:lipstick: feat: Estilização CSS do formulário`
- 🧪 `:test_tube: test: Criando novo teste`
- 💡 `:bulb: docs: Comentários sobre a função LoremIpsum()`
- 🗃️ `:card_file_box: raw: RAW Data do ano aaaa`
- 🧹 `:broom: cleanup: Eliminando blocos de código comentados e variáveis não utilizadas`
- 🗑️ `:wastebasket: remove: Removendo arquivos não utilizados do projeto`

> Imporante: Os commits devem ser individuais e atômicos, exceto em casos no qual a alteração/adição/remoção seja identica ou muito similar, nesses casos é permitido agrupar o commit em lotes.

## Padrão de Código

Todo o código (nomes de variáveis, funções, classes, métodos, etc.) deve ser escrito em **Português do Brasil (pt-br)**. A escrita deve ser clara, legível e **sem o uso de abreviações**, visando a máxima compreensibilidade do código.


## Análise de Código

Ao realizar a leitura e análise do projeto para obter contexto, todos os arquivos e diretórios listados no arquivo `.gitignore` devem ser ignorados.
