"""
Módulo utilitário para pré-processamento de texto usado no ASR/TTS.

Funções principais:
- normalizar_texto: limpa, padroniza e organiza o texto.
- inserir_pontuacao: adiciona pontuação final se necessário.
"""

import re


def normalizar_texto(texto: str) -> str:
    """
    Normaliza o texto de entrada:
    - Valida tipo de entrada (lança TypeError se não for string).
    - Remove espaços extras e quebras de linha.
    - Converte para minúsculas.
    - Garante string limpa para processamento.

    Args:
        texto (str): Texto original.

    Returns:
        str: Texto normalizado.

    Raises:
        TypeError: se `texto` não for uma string.
    """
    if not isinstance(texto, str):
        raise TypeError("A entrada deve ser uma string.")

    # Remove quebras de linha e normaliza espaços
    texto_limpo = re.sub(r"\s+", " ", texto.strip())

    # Converte para minúsculas
    return texto_limpo.lower()


def inserir_pontuacao(texto: str) -> str:
    """
    Insere pontuação final básica no texto, caso não exista.

    Regras:
    - Valida tipo de entrada (lança TypeError se não for string).
    - Remove espaços nas extremidades.
    - Se a string resultante for vazia, retorna "".
    - Se terminar em ., ! ou ?, retorna como está.
    - Caso contrário, adiciona um ponto final.

    Args:
        texto (str): Texto original.

    Returns:
        str: Texto com pontuação final.

    Raises:
        TypeError: se `texto` não for uma string.
    """
    if not isinstance(texto, str):
        raise TypeError("A entrada deve ser uma string.")

    texto = texto.strip()
    if texto == "":
        return ""

    # Se já terminar com pontuação conhecida, retorna como está
    if texto[-1] in ".!?":
        return texto

    # Caso contrário, adiciona ponto final
    return f"{texto}."
