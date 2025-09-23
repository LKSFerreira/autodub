"""
Interface para módulos de Alinhamento Forçado entre Texto e Áudio.

Este contrato define como alinhar palavras/sentenças com seus
respectivos timestamps no áudio.
"""

from typing import List, Protocol, Tuple


class IAlignment(Protocol):
    def alinhar(self, texto: str, caminho_audio: str) -> List[Tuple[str, float, float]]:
        """
        Alinha o texto ao áudio, retornando timestamps precisos.

        Args:
            texto (str): Texto que será alinhado.
            caminho_audio (str): Caminho para o arquivo de áudio.

        Returns:
            List[Tuple[str, float, float]]: Tuplas[string, float, float].
        """
