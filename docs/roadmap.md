### **`docs/roadmap.md`**

# Roadmap do Projeto Dublagem AI

Este documento descreve as **milestones** e **issues** planejadas para o desenvolvimento do projeto.

---

## 🎯 Milestone 1 — Estrutura e infra inicial

**Descrição:**  
Preparar o ambiente do projeto com esqueleto de repositório, dependências básicas, ferramentas de qualidade de código e integração contínua. Garantir base sólida com testes, cobertura e padronização.

### Issues

#### 📝 Issue 1.1 — Criar esqueleto do repositório

**Objetivo:** Montar a base do projeto (pastas, pyproject.toml, CI, testes iniciais).  
**Escopo:** Configuração inicial do repositório com linting e testes automatizados.

**Tarefas:**
- ✅ Criar `pyproject.toml` com dependências mínimas (pytest, coverage, ruff, black, isort)
- ✅ Criar estrutura de pastas: `src/dublagem/`, `tests/unit/`, `docs/`, `.github/workflows/`
- ✅ Adicionar `.pre-commit-config.yaml` com hooks (black, ruff, isort)
- ✅ Adicionar workflow GitHub Actions (`ci.yml`) rodando lint, pytest e coverage
- ✅ Criar `README.md` inicial
- ✅ Criar `tests/unit/test_sanity.py` com `assert True`

**Critérios de aceitação:**
- `poetry install` e `pytest` rodam sem erros
- `coverage run -m pytest && coverage report --fail-under=100` passa
- CI no GitHub executa e passa
- Código formatado (black, ruff, isort OK)

#### 📝 Issue 1.2 — Implementar interfaces (protocols) para ASR, TTS, Embedding e Alignment

**Objetivo:** Definir contratos base via `Protocol` para desacoplar implementações futuras.  
**Escopo:** Criação de 4 interfaces principais em `src/dublagem/interfaces/`.

**Tarefas:**
- Criar arquivos:
  - ✅ `asr_interface.py` → `class IAsr(Protocol)` com método `transcrever`
  - ✅ `tts_interface.py` → `class ITts(Protocol)` com método `sintetizar`
  - ✅ `embedding_interface.py` → `class IEmbeddingExtractor(Protocol)` com método `extrair`
  - ✅ `alignment_interface.py` → `class IAlignment(Protocol)` com método `alinhar`
- ✅ Adicionar docstrings em pt-BR
- ✅ Criar `tests/unit/test_interfaces.py` com mocks de exemplo
- ✅ Garantir 100% de coverage

**Critérios de aceitação:**
- Docstrings em pt-BR presentes
- Testes validam conformidade
- `coverage --fail-under=100` passa
- Código segue lint/formatadores

---

## 🎯 Milestone 2 — Pipeline base com mocks

**Descrição:**  
Construir pipeline inicial com mocks para validar fluxo ponta a ponta sem depender de modelos reais.

### Issues

#### 📝 Issue 2.1 — Implementar mocks para ASR, TTS, Embedding, Vocoder e FFmpeg wrapper

**Objetivo:** Criar implementações fictícias previsíveis para testes da pipeline.  
**Escopo:** Mock de todos os módulos principais.

**Tarefas:**
- ✅ Criar `src/dublagem/implementations/mocks/`
- Implementar `mock_asr.py`, `mock_tts.py`, `mock_embedding.py`, `mock_vocoder.py`
- Criar `ffmpeg_wrapper.py` fake
- Escrever testes unitários validando saídas determinísticas

**Critérios de aceitação:**
- Mocks retornam dados consistentes
- Testes unitários cobrem 100%
- Lint + coverage OK

#### 📝 Issue 2.2 — Implementar pipeline.py (orquestrador) com suporte a mocks

**Objetivo:** Orquestrar fluxo completo usando mocks  
**Escopo:** Implementação da `Pipeline` com dependency injection

**Tarefas:**
- Criar `src/dublagem/pipeline.py`
- Implementar classe `Pipeline` com método `executar(video_path, output_path)`
- Criar `tests/unit/test_pipeline.py` simulando fluxo completo com mocks
- Garantir geração de arquivo final fake

**Critérios de aceitação:**
- Pipeline roda ponta a ponta com mocks
- Testes cobrem fluxo e erros
- Coverage 100%

---

## 🎯 Milestone 3 — Alinhamento e tempo

**Descrição:**  
Adicionar sincronização entre texto e áudio, ainda com mocks, garantindo que pipeline lida corretamente com timestamps e normalização textual.

### Issues

#### 📝 Issue 3.1 — Implementar adaptação de timestamps (mock)

**Objetivo:** Simular alinhamento de palavras com timestamps  
**Escopo:** Mock que gera `{palavra, start, end}`

**Tarefas:**
- Criar `mock_alignment.py` em `mocks/`
- Implementar função de alinhamento falso
- Escrever testes validando consistência (ordem, sem sobreposição)

**Critérios de aceitação:**
- Mock gera timestamps válidos
- Testes cobrem casos de borda
- Coverage 100%

#### 📝 Issue 3.2 — Criar utilitários de normalização de texto e testes de alinhamento

**Objetivo:** Normalizar texto para ASR/TTS  
**Escopo:** Funções auxiliares em `utils/text_processing.py`

**Tarefas:**
- Implementar `normalizar_texto` e `inserir_pontuacao`
- Escrever `test_text_processing.py`
- Cobrir casos de borda (texto vazio, múltiplos espaços)

**Critérios de aceitação:**
- Funções tratam entradas irregulares
- Testes cobrem cenários comuns e extremos
- Coverage 100%

---

## 🎯 Milestone 4 — Substituir mocks por implementações reais

**Descrição:**  
Trocar gradualmente mocks por modelos reais (Whisper, Resemblyzer, YourTTS, Wav2Lip opcional). Garantir cobertura total com testes unitários mockados.

### Issues

#### 📝 Issue 4.1 — Criar adapter ASR real (Whisper/WhisperX)

**Objetivo:** Substituir mock ASR por Whisper real  
**Escopo:** Adapter que implementa `IAsr`

**Tarefas:**
- Criar `whisper_asr.py`
- Implementar `transcrever` usando Whisper
- Criar testes com mocks
- Documentar instalação no README

**Critérios de aceitação:**
- Adapter roda com áudio curto real
- Testes unitários passam com mocks
- Coverage 100%

#### 📝 Issue 4.2 — Criar adapter de extração de embedding real

**Objetivo:** Substituir mock de embeddings por modelo real  
**Escopo:** Adapter que implementa `IEmbeddingExtractor`

**Tarefas:**
- Criar `embedding_extractor.py`
- Implementar `extrair` usando Resemblyzer/ECAPA
- Criar testes com mocks
- Documentar dependências extras

**Critérios de aceitação:**
- Adapter gera embedding real
- Testes unitários com mocks
- Coverage 100%

#### 📝 Issue 4.3 — Criar adapter TTS/conversão de voz real

**Objetivo:** Gerar voz real condicionada ao embedding  
**Escopo:** Adapter que implementa `ITts`

**Tarefas:**
- Criar `tts_converter.py`
- Implementar `sintetizar` usando modelo condicional (YourTTS/so-vits-svc/VITS)
- Escrever testes com mocks
- Documentar dependências

**Critérios de aceitação:**
- Gera áudio real condicionado
- Testes unitários com mocks
- Coverage 100%

#### 📝 Issue 4.4 — Integração Wav2Lip para sincronização labial (opcional)

**Objetivo:** Sincronizar lábios no vídeo final  
**Escopo:** Etapa opcional na pipeline

**Tarefas:**
- Criar `wav2lip_sync.py`
- Integrar Wav2Lip na pipeline
- Testar com vídeo curto real
- Criar mocks para manter coverage

**Critérios de aceitação:**
- Pipeline sincroniza lábios em exemplo real
- Testes unitários cobrem mock
- Coverage 100%
