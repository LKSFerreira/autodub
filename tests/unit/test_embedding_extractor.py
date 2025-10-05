# tests/unit/test_embedding_extractor.py

import numpy as np
import pytest

from autodub.adapters.embedding_extractor import ResemblyzerEmbedding


class DummyEmbeddingExtractor:
    def extrair(self, caminho_audio: str):
        return np.array([1.0, 2.0, 3.0])


def test_extrator_simulado_extrai_embedding(tmp_path):
    simulador = DummyEmbeddingExtractor()
    saida = simulador.extrair("fake.wav")
    assert isinstance(saida, np.ndarray)
    assert saida.shape == (3,)


def test_extrator_real_instancia_com_mocks(monkeypatch, tmp_path):
    """Garante que o adapter inicializa sem crash (mocka preprocess_wav/VoiceEncoder)."""
    monkeypatch.setattr(
        "autodub.adapters.embedding_extractor.preprocess_wav", lambda p: [0.1, 0.2]
    )

    class FakeEncoder:
        def __init__(self, device=None):
            pass

        def embed_utterance(self, wav):
            return np.array([0.5, 0.6, 0.7])

    monkeypatch.setattr("autodub.adapters.embedding_extractor.VoiceEncoder", FakeEncoder)

    extrator = ResemblyzerEmbedding()
    embedding = extrator.extrair("dummy.wav")
    assert embedding.shape == (3,)
    assert np.allclose(embedding, [0.5, 0.6, 0.7])


def test_extrator_real_converte_lista_para_numpy(monkeypatch):
    """Testa se a conversão para numpy array funciona se o encoder não retornar um."""
    monkeypatch.setattr(
        "autodub.adapters.embedding_extractor.preprocess_wav", lambda p: [0.1, 0.2]
    )

    class FakeEncoder:
        def __init__(self, device=None):
            pass

        def embed_utterance(self, wav):
            return [0.5, 0.6, 0.7]  # Retorna lista

    monkeypatch.setattr("autodub.adapters.embedding_extractor.VoiceEncoder", FakeEncoder)

    extrator = ResemblyzerEmbedding()
    embedding = extrator.extrair("dummy.wav")
    assert isinstance(embedding, np.ndarray)  # Garante que foi convertido
    assert embedding.shape == (3,)
    assert np.allclose(embedding, [0.5, 0.6, 0.7])


def test_extracao_falha(monkeypatch):
    """Testa se uma exceção é levantada quando a extração falha."""

    def mock_preprocess_wav_que_falha(caminho):
        raise ValueError("Arquivo de áudio corrompido")

    monkeypatch.setattr(
        "autodub.adapters.embedding_extractor.preprocess_wav", mock_preprocess_wav_que_falha
    )

    extrator = ResemblyzerEmbedding()

    with pytest.raises(
        RuntimeError,
        match="Falha ao extrair embedding de dummy.wav: Arquivo de áudio corrompido",
    ):
        extrator.extrair("dummy.wav")
