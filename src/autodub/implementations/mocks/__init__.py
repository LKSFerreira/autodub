"""
Mocks de implementações para testes do pipeline de dublagem.

Todos os módulos aqui devem ser determinísticos e documentados em pt-BR.
"""

from .ffmpeg_wrapper import FakeFFmpegWrapper
from .mock_asr import MockASR
from .mock_embedding import MockEmbedding
from .mock_tts import MockTTS
from .mock_vocoder import MockVocoder

__all__ = [
    "MockASR",
    "MockTTS",
    "MockEmbedding",
    "MockVocoder",
    "FakeFFmpegWrapper",
]
