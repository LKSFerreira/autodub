"""
Interface para módulos de Síntese de Fala.

Text-to-Speech (TTS).

Este contrato define como gerar áudio a partir de texto.
"""

from typing import Protocol


class ITts(Protocol):
    def sintetizar(self, texto: str, caminho_saida: str) -> None:
        """
        Gera áudio a partir de texto.

        Args:
            texto (str): Texto que será convertido em fala.
            caminho_saida (str): Caminho do arquivo de saída (formato WAV/MP3).
        """
