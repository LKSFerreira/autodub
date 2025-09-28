import pytest

from autodub.utils.text_processing import inserir_pontuacao, normalizar_texto

# ------------------------
# Testes de normalizar_texto
# ------------------------


def test_normalizar_texto_remove_espacos():
    texto = "   Olá    mundo   "
    resultado = normalizar_texto(texto)
    assert resultado == "olá mundo"


def test_normalizar_texto_quebra_linhas():
    texto = "linha1\nlinha2\tlinha3"
    resultado = normalizar_texto(texto)
    assert resultado == "linha1 linha2 linha3"


def test_normalizar_texto_vazio():
    assert normalizar_texto("") == ""


def test_normalizar_texto_casefold():
    texto = "PYTHON É LEGAL"
    resultado = normalizar_texto(texto)
    assert resultado == "python é legal"


def test_normalizar_texto_type_error():
    with pytest.raises(TypeError):
        normalizar_texto(None)
    with pytest.raises(TypeError):
        normalizar_texto(123)


# ------------------------
# Testes de inserir_pontuacao
# ------------------------


def test_inserir_pontuacao_adiciona_ponto():
    texto = "isto é um teste"
    resultado = inserir_pontuacao(texto)
    assert resultado == "isto é um teste."


@pytest.mark.parametrize("pontuacao", [".", "?", "!"])
def test_inserir_pontuacao_respeita_existente(pontuacao):
    texto = f"isto é um teste{pontuacao}"
    resultado = inserir_pontuacao(texto)
    assert resultado == texto


def test_inserir_pontuacao_vazio():
    assert inserir_pontuacao("") == ""


def test_inserir_pontuacao_remove_espacos_finais():
    texto = "teste   "
    resultado = inserir_pontuacao(texto)
    assert resultado == "teste."


def test_inserir_pontuacao_type_error():
    with pytest.raises(TypeError):
        inserir_pontuacao(None)
    with pytest.raises(TypeError):
        inserir_pontuacao(456)
