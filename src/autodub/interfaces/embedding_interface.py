# src/autodub/interfaces/embedding_interface.py

"""
Interface para módulos de Extração de Embeddings de Voz.

Um embedding é uma representação numérica (vetor) que descreve
características únicas do locutor, como timbre.
"""

from typing import List, Protocol


class IEmbeddingExtractor(Protocol):
    def extrair(self, caminho_audio: str) -> List[float]:
        """
        Extrai o embedding de um locutor a partir de áudio.

        Args:
            caminho_audio (str): Caminho para o arquivo de áudio.

        Returns:
            List[float]: Vetor numérico representando o embedding do locutor.
        """
