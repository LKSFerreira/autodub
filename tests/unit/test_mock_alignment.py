from autodub.adapters.mocks.mock_alignment import alinhar_palavras


def test_texto_normal():
    """Deve alinhar duas palavras com 0.5s cada (mock fixo)."""
    resultado = alinhar_palavras("Olá mundo")
    assert len(resultado) == 2
    assert resultado[0]["palavra"] == "Olá"
    assert resultado[0]["start"] == 0.0
    assert resultado[0]["end"] == 0.5
    assert resultado[1]["palavra"] == "mundo"
    assert resultado[1]["start"] == 0.5
    assert resultado[1]["end"] == 1.0


def test_com_duracao_total():
    """Deve dividir a duração total igualmente entre palavras."""
    resultado = alinhar_palavras("um dois três", inicio=0.0, duracao_total=3.0)
    assert len(resultado) == 3
    for palavra in resultado:
        assert palavra["end"] - palavra["start"] == 1.0


def test_texto_vazio():
    """Texto vazio deve retornar lista vazia."""
    resultado = alinhar_palavras("")
    assert resultado == []


def test_palavra_unica_sem_duracao():
    """Palavra única deve ocupar 0.5s se duração não for fornecida."""
    resultado = alinhar_palavras("único")
    assert len(resultado) == 1
    assert resultado[0]["start"] == 0.0
    assert resultado[0]["end"] == 0.5


def test_palavra_unica_com_duracao():
    """Palavra única deve ocupar toda a duração fornecida."""
    resultado = alinhar_palavras("único", inicio=2.0, duracao_total=3.0)
    assert len(resultado) == 1
    assert resultado[0]["start"] == 2.0
    assert resultado[0]["end"] == 5.0


def test_consistencia_temporal():
    """Verifica que não há sobreposição entre as palavras."""
    resultado = alinhar_palavras("A B C D", duracao_total=4.0)
    for indice in range(1, len(resultado)):
        anterior = resultado[indice - 1]
        atual = resultado[indice]
        assert anterior["end"] == atual["start"]
        assert atual["end"] > atual["start"]
