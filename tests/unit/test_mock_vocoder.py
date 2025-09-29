from autodub.adapters.mocks.mock_vocoder import MockVocoder


def test_sintetizar_from_mel_retorna_bytes():
    vocoder = MockVocoder()
    saida = vocoder.sintetizar_from_mel([[0.1, 0.2], [0.3, 0.4]])
    assert isinstance(saida, bytes)
    assert saida == b"FAKE_VOCODER_AUDIO"
