"""
Interface para módulos do Reconhecimento de Fala Automático.

Automatic Speech Recognition (ASR).

Este contrato define o comportamento esperado de qualquer classe
que implemente um sistema de transcrição de áudio em texto.
"""

from typing import List, Protocol, Tuple


class IAsr(Protocol):
    def transcrever(self, caminho_audio: str) -> List[Tuple[str, float, float]]:
        """
        Transcreve um arquivo de áudio em texto com timestamps.

        Args:
            caminho_audio (str): Caminho para o arquivo de áudio.

        Returns:
            List[Tuple[str, float, float]]: Uma lista de tuplas contendo
                (trecho_transcrito, tempo_inicio, tempo_fim).
        """
