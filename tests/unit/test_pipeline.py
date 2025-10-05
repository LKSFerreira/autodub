# tests/unit/test_pipeline.py
import logging
import shutil
import subprocess
import tempfile
from pathlib import Path

import numpy as np
import pytest

from autodub.pipeline import Pipeline


class DummyASR:
    """Mock de ASR que retorna 0, 1 ou vários segmentos controláveis."""

    def __init__(self, num_segmentos=1):
        self.num_segmentos = num_segmentos

    def transcrever(self, caminho_audio: str):
        return [
            {"texto": f"SEG{i}", "inicio": i, "fim": i + 1} for i in range(self.num_segmentos)
        ]


class DummyTTS:
    def sintetizar(self, texto: str, voz_id=None):
        # sempre retorna bytes válidos simulando WAV
        return f"[AUDIO]{texto}".encode("utf-8")


class DummyFFmpeg:
    def extract_audio(self, caminho_video, caminho_audio_saida):
        Path(caminho_audio_saida).write_bytes(b"FAKE_AUDIO")

    def mux_audio(self, caminho_video, caminho_audio, caminho_video_saida):
        Path(caminho_video_saida).write_bytes(b"FAKE_VIDEO_WITH_AUDIO")


class DummyEmbedding:
    def __init__(self, tipo_retorno="numpy"):
        self.tipo_retorno = tipo_retorno

    def extrair(self, caminho_audio: str):
        if self.tipo_retorno == "numpy":
            return np.array([1.0, 2.0, 3.0])
        if self.tipo_retorno == "list":
            return [1.0, 2.0, 3.0]
        if self.tipo_retorno == "tuple":
            return (1.0, 2.0, 3.0)
        return {1.0, 2.0, 3.0}  # set para o fallback


def test_pipeline_sem_segmentos_cria_silencio(tmp_path, monkeypatch):
    """Se ASR retornar lista vazia, pipeline deve cair no fallback do MockTTS."""
    asr_simulado = DummyASR(num_segmentos=0)
    tts_simulado = DummyTTS()
    ffmpeg_simulado = DummyFFmpeg()
    pipeline_instancia = Pipeline(asr=asr_simulado, tts=tts_simulado, ffmpeg=ffmpeg_simulado)

    class MockEmptyTTS:
        def __init__(self, duration_seconds=None):
            pass

        def sintetizar(self, texto):
            return b"SILENCIO"

    monkeypatch.setattr("autodub.adapters.mocks.mock_tts.MockTTS", MockEmptyTTS)

    video_entrada = tmp_path / "input.mp4"
    video_entrada.write_bytes(b"DUMMY_VIDEO")
    saida = tmp_path / "out.mp4"

    resultado = pipeline_instancia.executar(video_entrada, saida)
    assert resultado.exists()
    assert resultado.read_bytes() == b"FAKE_VIDEO_WITH_AUDIO"


def test_pipeline_um_segmento_copia_direto(tmp_path):
    """Se ASR retornar apenas 1 segmento, pipeline deve usar shutil.copyfile."""
    asr_simulado = DummyASR(num_segmentos=1)
    tts_simulado = DummyTTS()
    ffmpeg_simulado = DummyFFmpeg()
    pipeline_instancia = Pipeline(asr=asr_simulado, tts=tts_simulado, ffmpeg=ffmpeg_simulado)

    video_entrada = tmp_path / "input.mp4"
    video_entrada.write_bytes(b"DUMMY_VIDEO")
    saida = tmp_path / "out.mp4"

    resultado = pipeline_instancia.executar(video_entrada, saida)
    assert resultado.exists()
    assert resultado.read_bytes() == b"FAKE_VIDEO_WITH_AUDIO"


def test_pipeline_varios_segmentos_concatena(tmp_path, monkeypatch):
    """Simula concatenação de múltiplos segmentos sem ffmpeg real."""
    asr_simulado = DummyASR(num_segmentos=3)
    tts_simulado = DummyTTS()
    ffmpeg_simulado = DummyFFmpeg()
    pipeline_instancia = Pipeline(asr=asr_simulado, tts=tts_simulado, ffmpeg=ffmpeg_simulado)

    monkeypatch.setattr(subprocess, "run", lambda *a, **k: None)

    video_entrada = tmp_path / "input.mp4"
    video_entrada.write_bytes(b"DUMMY_VIDEO")
    saida = tmp_path / "out.mp4"

    resultado = pipeline_instancia.executar(video_entrada, saida)
    assert resultado.exists()
    assert resultado.read_bytes() == b"FAKE_VIDEO_WITH_AUDIO"


def test_salvar_bytes_cria_pasta(tmp_path):
    """Confere criação de pasta por _save_bytes."""
    pipeline_instancia = Pipeline(asr=DummyASR(), tts=DummyTTS(), ffmpeg=DummyFFmpeg())
    caminho_arquivo = tmp_path / "nova_pasta" / "arq.txt"
    dados = b"teste"
    pipeline_instancia._save_bytes(dados, caminho_arquivo)
    assert caminho_arquivo.exists()
    assert caminho_arquivo.read_bytes() == b"teste"


def test_concatenar_segmentos_fallback(tmp_path, monkeypatch):
    """Caminho de fallback do concatenação: áudio de silêncio."""
    pipeline_instancia = Pipeline(asr=DummyASR(), tts=DummyTTS(), ffmpeg=DummyFFmpeg())

    class MockEmptyTTS:
        def __init__(self, duration_seconds=None):
            pass

        def sintetizar(self, texto):
            return b"SILENCIO"

    monkeypatch.setattr("autodub.adapters.mocks.mock_tts.MockTTS", MockEmptyTTS)
    destino = tmp_path / "saida.wav"
    pipeline_instancia._concatenar_segmentos([], destino)
    assert destino.read_bytes() == b"SILENCIO"


def test_concatenar_segmentos_erro_ffmpeg(tmp_path, monkeypatch):
    """Garante branch de erro na concatenação com ffmpeg."""
    pipeline_instancia = Pipeline(asr=DummyASR(), tts=DummyTTS(), ffmpeg=DummyFFmpeg())
    arq1 = tmp_path / "seg1.wav"
    arq1.write_bytes(b"AUDIO1")
    arq2 = tmp_path / "seg2.wav"
    arq2.write_bytes(b"AUDIO2")
    destino = tmp_path / "dest.wav"

    class FakeError(subprocess.CalledProcessError):
        def __init__(self):
            super().__init__(1, "ffmpeg", b"ERRO_FFMPEG")
            self.stderr = b"ERRO_FFMPEG"

    monkeypatch.setattr(subprocess, "run", lambda *a, **k: (_ for _ in ()).throw(FakeError()))
    with pytest.raises(RuntimeError) as excecao:
        pipeline_instancia._concatenar_segmentos([arq1, arq2], destino)
    assert "Falha ao concatenar segmentos" in str(excecao.value)


def test_pipeline_debug_true(tmp_path, monkeypatch):
    """debug=True salva transcrição; ffmpeg é patchado."""
    asr_simulado = DummyASR(num_segmentos=2)
    tts_simulado = DummyTTS()
    ffmpeg_simulado = DummyFFmpeg()
    pipeline_instancia = Pipeline(asr=asr_simulado, tts=tts_simulado, ffmpeg=ffmpeg_simulado)

    monkeypatch.setattr(subprocess, "run", lambda *a, **k: None)

    video_entrada = tmp_path / "input.mp4"
    video_entrada.write_bytes(b"DUMMY_VIDEO")
    saida = tmp_path / "out.mp4"

    resultado = pipeline_instancia.executar(video_entrada, saida, debug=True)
    assert resultado.exists()


def test_pipeline_init_faltando_componentes():
    """Testa validação obrigatória dos componentes."""
    with pytest.raises(ValueError):
        Pipeline(asr=None, tts=DummyTTS(), ffmpeg=DummyFFmpeg())
    with pytest.raises(ValueError):
        Pipeline(asr=DummyASR(), tts=None, ffmpeg=DummyFFmpeg())
    with pytest.raises(ValueError):
        Pipeline(asr=DummyASR(), tts=DummyTTS(), ffmpeg=None)


def test_pipeline_falha_limpeza_apenas_aviso(tmp_path, monkeypatch, caplog):
    """Se cleanup falhar, deve logar warning."""
    asr_simulado = DummyASR(num_segmentos=1)
    tts_simulado = DummyTTS()
    ffmpeg_simulado = DummyFFmpeg()
    pipeline_instancia = Pipeline(asr=asr_simulado, tts=tts_simulado, ffmpeg=ffmpeg_simulado)

    video_entrada = tmp_path / "input.mp4"
    video_entrada.write_bytes(b"DUMMY_VIDEO")
    saida = tmp_path / "out.mp4"

    monkeypatch.setattr(
        shutil, "rmtree", lambda *a, **k: (_ for _ in ()).throw(OSError("falha"))
    )

    import autodub.pipeline as modulo_pipeline

    modulo_pipeline.logger.propagate = True

    with caplog.at_level(logging.WARNING):
        resultado = pipeline_instancia.executar(video_entrada, saida)
    assert resultado.exists()
    assert "Falha ao limpar temporários" in caplog.text
    assert "falha" in caplog.text


def test_pipeline_executar_erro_e_limpeza(tmp_path, monkeypatch, caplog):
    """Força erro dentro do try para cobrir o bloco except e garantir cleanup."""
    temp_fixo = tmp_path / "autodub_pipeline_fixed"
    temp_fixo.mkdir()
    monkeypatch.setattr(tempfile, "mkdtemp", lambda prefix="": str(temp_fixo))

    class ExplodingASR:
        def transcrever(self, caminho_audio: str):
            raise ValueError("boom")

    tts_simulado = DummyTTS()
    ffmpeg_simulado = DummyFFmpeg()
    pipeline_instancia = Pipeline(asr=ExplodingASR(), tts=tts_simulado, ffmpeg=ffmpeg_simulado)

    video_entrada = tmp_path / "input.mp4"
    video_entrada.write_bytes(b"DUMMY_VIDEO")
    saida = tmp_path / "out.mp4"

    with caplog.at_level(logging.ERROR):
        with pytest.raises(ValueError):
            pipeline_instancia.executar(video_entrada, saida)

    assert not temp_fixo.exists()


def test_formatador_cor_ramo_debug_coberto(caplog):
    """Emite log DEBUG para exercitar o 'else' do ColorFormatter (sem cores)."""
    import autodub.pipeline as modulo_pipeline

    logger = modulo_pipeline.logger
    nivel_antigo = logger.level
    propagar_antigo = logger.propagate
    try:
        logger.setLevel(logging.DEBUG)
        logger.propagate = True
        with caplog.at_level(logging.DEBUG):
            logger.debug("mensagem de debug")
        assert "mensagem de debug" in caplog.text
    finally:
        logger.setLevel(nivel_antigo)
        logger.propagate = propagar_antigo


def test_pipeline_debug_false(tmp_path, monkeypatch):
    """debug=False deve apenas logar quantidade de segmentos sem salvar arquivo."""
    asr_simulado = DummyASR(num_segmentos=2)
    tts_simulado = DummyTTS()
    ffmpeg_simulado = DummyFFmpeg()
    pipeline_instancia = Pipeline(asr=asr_simulado, tts=tts_simulado, ffmpeg=ffmpeg_simulado)

    monkeypatch.setattr(subprocess, "run", lambda *a, **k: None)

    video_entrada = tmp_path / "input.mp4"
    video_entrada.write_bytes(b"DUMMY_VIDEO")
    saida = tmp_path / "out.mp4"

    resultado = pipeline_instancia.executar(video_entrada, saida, debug=False)

    assert resultado.exists()
    assert resultado.read_bytes() == b"FAKE_VIDEO_WITH_AUDIO"

    transcricao = saida.parent / "transcricao.jsonl"
    assert not transcricao.exists()


@pytest.mark.parametrize(
    "tipo_embedding, lista_esperada",
    [
        ("numpy", [1.0, 2.0, 3.0]),
        ("list", [1.0, 2.0, 3.0]),
        ("tuple", [1.0, 2.0, 3.0]),
        ("set", [1.0, 2.0, 3.0]),
    ],
)
def test_pipeline_com_embedding_varios_tipos(
    tmp_path, monkeypatch, tipo_embedding, lista_esperada
):
    """Testa o fluxo com embedding para vários tipos de retorno."""
    asr_simulado = DummyASR()
    tts_simulado = DummyTTS()
    ffmpeg_simulado = DummyFFmpeg()
    embedding_simulado = DummyEmbedding(tipo_retorno=tipo_embedding)
    pipeline_instancia = Pipeline(
        asr=asr_simulado, tts=tts_simulado, ffmpeg=ffmpeg_simulado, embedding=embedding_simulado
    )

    monkeypatch.setattr(subprocess, "run", lambda *a, **k: None)

    video_entrada = tmp_path / "input.mp4"
    video_entrada.write_bytes(b"DUMMY_VIDEO")
    saida = tmp_path / "out.mp4"

    pipeline_instancia.executar(video_entrada, saida, debug=True)

    arquivo_embedding = saida.parent / "embedding.json"
    assert arquivo_embedding.exists()
    import json

    with open(arquivo_embedding, "r") as f:
        dados = json.load(f)

    assert sorted(dados) == sorted(lista_esperada)


def test_pipeline_com_embedding_debug_false(tmp_path, monkeypatch):
    """Testa o fluxo com embedding e debug=False para cobrir o branch que não salva o JSON."""
    asr_simulado = DummyASR()
    tts_simulado = DummyTTS()
    ffmpeg_simulado = DummyFFmpeg()
    embedding_simulado = DummyEmbedding()
    pipeline_instancia = Pipeline(
        asr=asr_simulado, tts=tts_simulado, ffmpeg=ffmpeg_simulado, embedding=embedding_simulado
    )

    monkeypatch.setattr(subprocess, "run", lambda *a, **k: None)

    video_entrada = tmp_path / "input.mp4"
    video_entrada.write_bytes(b"DUMMY_VIDEO")
    saida = tmp_path / "out.mp4"

    pipeline_instancia.executar(video_entrada, saida, debug=False)

    arquivo_embedding = saida.parent / "embedding.json"
    assert not arquivo_embedding.exists()
