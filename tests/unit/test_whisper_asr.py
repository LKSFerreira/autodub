from unittest.mock import MagicMock, patch

import pytest

from autodub.adapters.whisper_asr_adapter import WhisperAsr


def test_inicializacao_com_modelo_valido():
    """Deve inicializar corretamente com um modelo válido."""
    with patch("autodub.adapters.whisper_asr.whisper") as mock_whisper:
        mock_whisper.load_model.return_value = MagicMock()
        asr = WhisperAsr(model_name="tiny")
        assert asr.model is not None
        mock_whisper.load_model.assert_called_once_with("tiny")


def test_inicializacao_com_erro():
    """Deve lançar exceção se o modelo não puder ser carregado."""
    with patch("autodub.adapters.whisper_asr.whisper") as mock_whisper:
        mock_whisper.load_model.side_effect = Exception("Falha no load")
        with pytest.raises(Exception, match="Falha no load"):
            WhisperAsr(model_name="tiny")


def test_transcricao_retorna_segmentos():
    """Deve retornar lista de segmentos no formato esperado."""
    mock_model = MagicMock()
    mock_model.transcribe.return_value = {
        "segments": [
            {"text": "Olá mundo", "start": 0.0, "end": 1.0},
            {"text": "Teste", "start": 1.0, "end": 2.0},
        ]
    }

    with patch("autodub.adapters.whisper_asr.whisper") as mock_whisper:
        mock_whisper.load_model.return_value = mock_model
        asr = WhisperAsr(model_name="tiny")
        resultado = asr.transcrever("audio_fake.wav")

    assert len(resultado) == 2
    assert resultado[0]["texto"] == "Olá mundo"
    assert resultado[0]["inicio"] == 0.0
    assert resultado[0]["fim"] == 1.0


def test_transcricao_com_erro():
    """Deve propagar erro com RuntimeError em caso de falha."""
    mock_model = MagicMock()
    mock_model.transcribe.side_effect = Exception("Erro interno")

    with patch("autodub.adapters.whisper_asr.whisper") as mock_whisper:
        mock_whisper.load_model.return_value = mock_model
        asr = WhisperAsr(model_name="tiny")
        with pytest.raises(RuntimeError, match="Falha na transcrição com Whisper"):
            asr.transcrever("audio_fake.wav")


def test_init_model_name(monkeypatch):
    """Garante que WhisperAsr inicializa com o nome correto do modelo."""

    def fake_load_model(name):
        assert name == "base"
        return "FAKE_MODEL"

    monkeypatch.setattr("whisper.load_model", fake_load_model)

    asr = WhisperAsr(model_name="base")
    assert asr.model == "FAKE_MODEL"
    assert asr.model_name == "base"


# No final do arquivo tests/unit/test_whisper_asr.py


@pytest.mark.integration  # Marcador para testes de integração - boas práticas
def test_integracao_carregamento_real_modelo():
    """
    Testa a integração real com a biblioteca whisper, carregando um modelo.
    Este teste vai ser mais lento e pode precisar baixar o modelo na primeira vez.
    """
    try:
        # Tenta carregar um modelo real (o menor possível para o teste ser rápido)
        asr = WhisperAsr(model_name="tiny")
        assert asr.model is not None
    except Exception as e:
        pytest.fail(f"Teste de integração falhou ao carregar o modelo real: {e}")
