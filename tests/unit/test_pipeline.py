# tests/unit/test_pipeline.py
import logging
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from autodub.pipeline import Pipeline


class DummyASR:
    """Mock de ASR que retorna 0, 1 ou vários segmentos controláveis."""

    def __init__(self, num_segments=1):
        self.num_segments = num_segments

    def transcrever(self, audio_path: str):
        return [
            {"texto": f"SEG{i}", "inicio": i, "fim": i + 1} for i in range(self.num_segments)
        ]


class DummyTTS:
    def sintetizar(self, texto: str, voz_id=None):
        # sempre retorna bytes válidos simulando WAV
        return f"[AUDIO]{texto}".encode("utf-8")


class DummyFFmpeg:
    def extract_audio(self, video_path, out_audio_path):
        Path(out_audio_path).write_bytes(b"FAKE_AUDIO")

    def mux_audio(self, video_path, audio_path, out_video_path):
        Path(out_video_path).write_bytes(b"FAKE_VIDEO_WITH_AUDIO")


def test_pipeline_sem_segmentos_cria_silencio(tmp_path, monkeypatch):
    """Se ASR retornar lista vazia, pipeline deve cair no fallback do MockTTS."""
    asr = DummyASR(num_segments=0)
    tts = DummyTTS()
    ffmpeg = DummyFFmpeg()
    pipeline = Pipeline(asr=asr, tts=tts, ffmpeg=ffmpeg)

    # Patch MockTTS usado por fallback para aceitar o parâmetro duration_seconds
    class MockTTSVazia:
        def __init__(self, duration_seconds=None):
            pass

        def sintetizar(self, texto):
            return b"SILENCIO"

    monkeypatch.setattr("autodub.adapters.mocks.mock_tts.MockTTS", MockTTSVazia)

    video_in = tmp_path / "input.mp4"
    video_in.write_bytes(b"DUMMY_VIDEO")
    out = tmp_path / "out.mp4"

    result = pipeline.executar(video_in, out)
    assert result.exists()
    assert result.read_bytes() == b"FAKE_VIDEO_WITH_AUDIO"


def test_pipeline_um_segmento_copia_direto(tmp_path):
    """Se ASR retornar apenas 1 segmento, pipeline deve usar shutil.copyfile."""
    asr = DummyASR(num_segments=1)
    tts = DummyTTS()
    ffmpeg = DummyFFmpeg()
    pipeline = Pipeline(asr=asr, tts=tts, ffmpeg=ffmpeg)

    video_in = tmp_path / "input.mp4"
    video_in.write_bytes(b"DUMMY_VIDEO")
    out = tmp_path / "out.mp4"

    result = pipeline.executar(video_in, out)
    assert result.exists()
    assert result.read_bytes() == b"FAKE_VIDEO_WITH_AUDIO"


def test_pipeline_varios_segmentos_concatena(tmp_path, monkeypatch):
    """Simula concatenação de múltiplos segmentos sem ffmpeg real."""
    asr = DummyASR(num_segments=3)
    tts = DummyTTS()
    ffmpeg = DummyFFmpeg()
    pipeline = Pipeline(asr=asr, tts=tts, ffmpeg=ffmpeg)

    # Não executa ffmpeg real
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: None)

    video_in = tmp_path / "input.mp4"
    video_in.write_bytes(b"DUMMY_VIDEO")
    out = tmp_path / "out.mp4"

    result = pipeline.executar(video_in, out)
    assert result.exists()
    assert result.read_bytes() == b"FAKE_VIDEO_WITH_AUDIO"


def test_save_bytes_cria_pasta(tmp_path):
    """Confere criação de pasta por _save_bytes."""
    pipeline = Pipeline(asr=DummyASR(), tts=DummyTTS(), ffmpeg=DummyFFmpeg())
    file_path = tmp_path / "nova_pasta" / "arq.txt"
    data = b"teste"
    pipeline._save_bytes(data, file_path)
    assert file_path.exists()
    assert file_path.read_bytes() == b"teste"


def test_concatenar_segmentos_fallback(tmp_path, monkeypatch):
    """Caminho de fallback do concatenação: áudio de silêncio."""
    pipeline = Pipeline(asr=DummyASR(), tts=DummyTTS(), ffmpeg=DummyFFmpeg())

    # MockTTS que aceita duration_seconds para o fallback
    class MockTTSVazia:
        def __init__(self, duration_seconds=None):
            pass

        def sintetizar(self, texto):
            return b"SILENCIO"

    monkeypatch.setattr("autodub.adapters.mocks.mock_tts.MockTTS", MockTTSVazia)
    destino = tmp_path / "saida.wav"
    pipeline._concatenar_segmentos([], destino)
    assert destino.read_bytes() == b"SILENCIO"


def test_concatenar_segmentos_erro_ffmpeg(tmp_path, monkeypatch):
    """Garante branch de erro na concatenação com ffmpeg."""
    pipeline = Pipeline(asr=DummyASR(), tts=DummyTTS(), ffmpeg=DummyFFmpeg())
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
    with pytest.raises(RuntimeError) as exc:
        pipeline._concatenar_segmentos([arq1, arq2], destino)
    assert "Falha ao concatenar segmentos" in str(exc.value)


def test_pipeline_debug_true(tmp_path, monkeypatch):
    """debug=True salva transcrição; ffmpeg é patchado."""
    asr = DummyASR(num_segments=2)
    tts = DummyTTS()
    ffmpeg = DummyFFmpeg()
    pipeline = Pipeline(asr=asr, tts=tts, ffmpeg=ffmpeg)

    # Patch subprocess.run para não executar ffmpeg real
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: None)

    video_in = tmp_path / "input.mp4"
    video_in.write_bytes(b"DUMMY_VIDEO")
    out = tmp_path / "out.mp4"

    result = pipeline.executar(video_in, out, debug=True)
    assert result.exists()


def test_pipeline_init_faltando_componentes():
    """Testa validação obrigatória dos componentes."""
    with pytest.raises(ValueError):
        Pipeline(asr=None, tts=DummyTTS(), ffmpeg=DummyFFmpeg())
    with pytest.raises(ValueError):
        Pipeline(asr=DummyASR(), tts=None, ffmpeg=DummyFFmpeg())
    with pytest.raises(ValueError):
        Pipeline(asr=DummyASR(), tts=DummyTTS(), ffmpeg=None)


def test_pipeline_falha_cleanup_apenas_warning(tmp_path, monkeypatch, caplog):
    """Se cleanup falhar, deve logar warning."""
    asr = DummyASR(num_segments=1)
    tts = DummyTTS()
    ffmpeg = DummyFFmpeg()
    pipeline = Pipeline(asr=asr, tts=tts, ffmpeg=ffmpeg)

    video_in = tmp_path / "input.mp4"
    video_in.write_bytes(b"DUMMY_VIDEO")
    out = tmp_path / "out.mp4"

    monkeypatch.setattr(
        shutil, "rmtree", lambda *a, **k: (_ for _ in ()).throw(OSError("falha"))
    )

    import autodub.pipeline as pipeline_module

    pipeline_module.logger.propagate = True

    with caplog.at_level(logging.WARNING):
        result = pipeline.executar(video_in, out)
    assert result.exists()
    assert "Falha ao limpar temporários" in caplog.text
    assert "falha" in caplog.text


def test_pipeline_executar_erro_e_cleanup(tmp_path, monkeypatch, caplog):
    """Força erro dentro do try para cobrir o bloco except e garantir cleanup."""
    # Força tmpdir determinístico para poder verificar limpeza
    fixed_tmp = tmp_path / "autodub_pipeline_fixed"
    fixed_tmp.mkdir()
    monkeypatch.setattr(tempfile, "mkdtemp", lambda prefix="": str(fixed_tmp))

    class ExplodingASR:
        def transcrever(self, audio_path: str):
            raise ValueError("boom")

    tts = DummyTTS()
    ffmpeg = DummyFFmpeg()
    pipeline = Pipeline(asr=ExplodingASR(), tts=tts, ffmpeg=ffmpeg)

    video_in = tmp_path / "input.mp4"
    video_in.write_bytes(b"DUMMY_VIDEO")
    out = tmp_path / "out.mp4"

    with caplog.at_level(logging.ERROR):
        with pytest.raises(ValueError):
            pipeline.executar(video_in, out)

    # Diretório temporário deve ter sido limpo pelo finally
    assert not fixed_tmp.exists()


def test_colorformatter_debug_branch_coberto(caplog):
    """Emite log DEBUG para exercitar o 'else' do ColorFormatter (sem cores)."""
    import autodub.pipeline as pipeline_module

    logger = pipeline_module.logger
    old_level = logger.level
    old_propagate = logger.propagate
    try:
        logger.setLevel(logging.DEBUG)
        logger.propagate = True  # permite caplog capturar via root
        with caplog.at_level(logging.DEBUG):
            logger.debug("mensagem de debug")
        assert "mensagem de debug" in caplog.text
    finally:
        logger.setLevel(old_level)
        logger.propagate = old_propagate


def test_pipeline_debug_false(tmp_path, monkeypatch):
    """debug=False deve apenas logar quantidade de segmentos sem salvar arquivo."""
    asr = DummyASR(num_segments=2)
    tts = DummyTTS()
    ffmpeg = DummyFFmpeg()
    pipeline = Pipeline(asr=asr, tts=tts, ffmpeg=ffmpeg)

    # Evita chamar ffmpeg real
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: None)

    video_in = tmp_path / "input.mp4"
    video_in.write_bytes(b"DUMMY_VIDEO")
    out = tmp_path / "out.mp4"

    result = pipeline.executar(video_in, out, debug=False)

    assert result.exists()
    assert result.read_bytes() == b"FAKE_VIDEO_WITH_AUDIO"

    # garante que não criou transcricao.jsonl no diretório
    transcript = out.parent / "transcricao.jsonl"
    assert not transcript.exists()
