# src/autodub/interfaces/translator_interface.py

"""
Interface para tradutores de texto.
"""

from typing import Protocol


class ITranslator(Protocol):
    """
    Interface para adaptadores de tradução.
    """

    def traduzir(self, texto: str, target_lang: str) -> str:
        """
        Traduz o texto para o idioma alvo especificado.

        Args:
            texto (str): Texto de entrada.
            target_lang (str): Idioma de destino (ex: "en", "pt", "es").

        Returns:
            str: Texto traduzido.
        """
        ...
