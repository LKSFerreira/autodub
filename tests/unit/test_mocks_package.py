import importlib

MODULES = [
    "autodub.adapters.mocks.mock_asr",
    "autodub.adapters.mocks.mock_tts",
    "autodub.adapters.mocks.mock_embedding",
    "autodub.adapters.mocks.mock_vocoder",
    "autodub.adapters.mocks.ffmpeg_wrapper",
]


def test_modulos_importaveis():
    for mod in MODULES:
        m = importlib.import_module(mod)
        assert m is not None


def test_classes_existentes():
    mod = importlib.import_module("autodub.adapters.mocks")
    for expected in [
        "MockASR",
        "MockTTS",
        "MockEmbedding",
        "MockVocoder",
        "FakeFFmpegWrapper",
    ]:
        assert hasattr(mod, expected)
