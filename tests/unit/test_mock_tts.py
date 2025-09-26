from autodub.implementations.mocks.mock_tts import MockTTS


def test_sintetizar_retorna_bytes():
    tts = MockTTS()
    saida = tts.sintetizar("Olá mundo")
    assert isinstance(saida, bytes)
    assert len(saida) > 0


def test_sintetizar_deterministico():
    tts = MockTTS()
    texto = "Determinístico"
    saida1 = tts.sintetizar(texto)
    saida2 = tts.sintetizar(texto)
    assert saida1 == saida2  # mesma entrada gera mesma saída


def test_sintetizar_varia_com_texto():
    tts = MockTTS()
    saida1 = tts.sintetizar("Texto A")
    saida2 = tts.sintetizar("Texto B")
    assert saida1 != saida2  # entradas diferentes geram saídas diferentes
