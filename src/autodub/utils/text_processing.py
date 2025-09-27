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
    - Remove espaços extras e quebras de linha.
    - Converte para minúsculas.
    - Garante string limpa para processamento.

    Args:
        texto (str): Texto original.

    Returns:
        str: Texto normalizado.
    """
    if not texto:
        return ""

    # Remove quebras de linha e normaliza espaços
    texto_limpo = re.sub(r"\s+", " ", texto.strip())

    # Converte para minúsculas
    return texto_limpo.lower()


def inserir_pontuacao(texto: str) -> str:
    """
    Insere pontuação final básica no texto, caso não exista.

    Args:
        texto (str): Texto original.

    Returns:
        str: Texto com pontuação final.
    """
    if not texto:
        return ""

    texto = texto.strip()

    # Se já terminar com pontuação conhecida, retorna como está
    if texto[-1] in ".!?":
        return texto

    # Caso contrário, adiciona ponto final
    return f"{texto}."
