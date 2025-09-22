# tests/unit/test_sanidade.py

import autodub


def test_sanidade_importacao():
    """
    Garante que o pacote principal pode ser importado.
    """
    assert autodub is not None


def test_versao_pacote():
    """
    Verifica se a variável de versão está definida no pacote.
    """
    assert autodub.__version__ == "0.1.0"
