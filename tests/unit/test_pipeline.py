import logging
import shutil
from pathlib import Path

import pytest

from autodub.pipeline import ColorFormatter, Pipeline


class DummyASR:
    """Mock de ASR que retorna 1 segmento fixo ou lança erro."""

    def __init__(self, should_fail=False, empty=False):
        self.should_fail = should_fail
        self.empty = empty

    def transcrever(self, audio_path: str):
        if self.should_fail:
            raise RuntimeError("Falha na transcrição")
        if self.empty:
            return []
        return [
            {"texto": f"Arquivo processado: {audio_path}", "inicio": 0.0, "fim": 1.0}
        ]


class DummyTTS:
    """Mock de TTS que transforma texto em bytes determinísticos."""

    def sintetizar(self, texto: str, voz_id=None):
        return f"[AUDIO]{texto}".encode("utf-8")


class DummyFFmpeg:
    """Mock de FFmpeg que cria arquivos fake para simular operações."""

    def extract_audio(self, video_path, out_audio_path):
        Path(out_audio_path).write_bytes(b"FAKE_AUDIO")

    def mux_audio(self, video_path, audio_path, out_video_path):
        Path(out_video_path).write_bytes(b"FAKE_VIDEO_WITH_AUDIO")


def test_pipeline_rodar_ponta_a_ponta(tmp_path):
    """Pipeline deve rodar de ponta a ponta e gerar arquivo final."""
    asr = DummyASR()
    tts = DummyTTS()
    ffmpeg = DummyFFmpeg()
    pipeline = Pipeline(asr=asr, tts=tts, ffmpeg=ffmpeg)

    video_in = tmp_path / "input.mp4"
    video_in.write_bytes(b"DUMMY_VIDEO")
    output = tmp_path / "output.mp4"

    result = pipeline.executar(video_in, output)

    assert result.exists()
    assert result.read_bytes() == b"FAKE_VIDEO_WITH_AUDIO"


def test_pipeline_falha_ao_criar_com_dependencias_ausentes():
    """Pipeline deve levantar ValueError se dependências obrigatórias forem None."""
    with pytest.raises(ValueError, match="asr, tts e ffmpeg são obrigatórios"):
        Pipeline(asr=None, tts=DummyTTS(), ffmpeg=DummyFFmpeg())
    with pytest.raises(ValueError, match="asr, tts e ffmpeg são obrigatórios"):
        Pipeline(asr=DummyASR(), tts=None, ffmpeg=DummyFFmpeg())
    with pytest.raises(ValueError, match="asr, tts e ffmpeg são obrigatórios"):
        Pipeline(asr=DummyASR(), tts=DummyTTS(), ffmpeg=None)


def test_pipeline_trata_erro_na_transcricao(tmp_path):
    """Pipeline deve propagar erro de transcrição e limpar temporários."""
    asr = DummyASR(should_fail=True)
    tts = DummyTTS()
    ffmpeg = DummyFFmpeg()
    pipeline = Pipeline(asr=asr, tts=tts, ffmpeg=ffmpeg)

    video_in = tmp_path / "input.mp4"
    video_in.write_bytes(b"DUMMY_VIDEO")

    with pytest.raises(RuntimeError, match="Falha na transcrição"):
        pipeline.executar(video_in, tmp_path / "saida.mp4")


def test_pipeline_com_audio_vazio_cria_arquivo_final(tmp_path):
    """Mesmo sem segmentos, Pipeline deve criar arquivo final fake."""
    asr = DummyASR(empty=True)
    tts = DummyTTS()
    ffmpeg = DummyFFmpeg()
    pipeline = Pipeline(asr=asr, tts=tts, ffmpeg=ffmpeg)

    video_in = tmp_path / "input.mp4"
    video_in.write_bytes(b"DUMMY_VIDEO")
    output = tmp_path / "output.mp4"

    result = pipeline.executar(video_in, output)

    assert result.exists()
    # mesmo sem áudio, mux cria saída fake
    assert result.read_bytes() == b"FAKE_VIDEO_WITH_AUDIO"


def test_logger_format_else_branch(capsys):
    """Força nível de log não previsto para cobrir branch do ColorFormatter."""
    record = logging.LogRecord(
        name="autodub.pipeline",
        level=logging.DEBUG,  # nível não coberto antes
        pathname=__file__,
        lineno=10,
        msg="Mensagem genérica",
        args=(),
        exc_info=None,
    )
    formatter = ColorFormatter()
    output = formatter.format(record)
    assert "Mensagem genérica" in output


def test_pipeline_falha_cleanup(tmp_path, monkeypatch):
    """Simula falha ao limpar temporários para cobrir warning no finally."""
    asr = DummyASR()
    tts = DummyTTS()
    ffmpeg = DummyFFmpeg()
    pipeline = Pipeline(asr=asr, tts=tts, ffmpeg=ffmpeg)

    video_in = tmp_path / "input.mp4"
    video_in.write_bytes(b"DUMMY_VIDEO")
    output = tmp_path / "output.mp4"

    # Força shutil.rmtree a lançar exceção
    monkeypatch.setattr(
        shutil,
        "rmtree",
        lambda *a, **kw: (_ for _ in ()).throw(OSError("Falha de remoção")),
    )

    result = pipeline.executar(video_in, output)
    assert result.exists()
    assert result.read_bytes() == b"FAKE_VIDEO_WITH_AUDIO"
