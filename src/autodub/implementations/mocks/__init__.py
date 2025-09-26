"""
Mocks de implementações para testes do pipeline de dublagem.

Todos os módulos aqui devem ser determinísticos e documentados em pt-BR.
"""

from .mock_asr import MockASR
from .mock_tts import MockTTS
from .mock_embedding import MockEmbedding
from .mock_vocoder import MockVocoder
from .ffmpeg_wrapper import FakeFFmpegWrapper

__all__ = [
    "MockASR",
    "MockTTS",
    "MockEmbedding",
    "MockVocoder",
    "FakeFFmpegWrapper",
]
