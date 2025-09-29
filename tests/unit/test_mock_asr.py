from autodub.adapters.mocks.mock_asr import MockASR


def test_transcricao_deterministica_para_arquivo_teste():
    asr = MockASR()
    saida = asr.transcrever("meu_audio_teste.wav")

    assert isinstance(saida, list)
    assert len(saida) == 2
    assert saida[0]["texto"] == "Olá, este é um teste."
    assert saida[1]["texto"] == "MockASR funcionando."
    assert saida[0]["inicio"] == 0.0
    assert saida[1]["fim"] == 3.0


def test_transcricao_generica_para_outros_arquivos():
    asr = MockASR()
    saida = asr.transcrever("outro_arquivo.wav")

    assert len(saida) == 1
    assert "Arquivo processado" in saida[0]["texto"]
    assert saida[0]["inicio"] == 0.0
    assert saida[0]["fim"] == 2.0
