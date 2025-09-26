import importlib

MODULES = [
    "autodub.implementations.mocks.mock_asr",
    "autodub.implementations.mocks.mock_tts",
    "autodub.implementations.mocks.mock_embedding",
    "autodub.implementations.mocks.mock_vocoder",
    "autodub.implementations.mocks.ffmpeg_wrapper",
]


def test_modulos_importaveis():
    for mod in MODULES:
        m = importlib.import_module(mod)
        assert m is not None


def test_classes_existentes():
    mod = importlib.import_module("autodub.implementations.mocks")
    for expected in [
        "MockASR",
        "MockTTS",
        "MockEmbedding",
        "MockVocoder",
        "FakeFFmpegWrapper",
    ]:
        assert hasattr(mod, expected)
