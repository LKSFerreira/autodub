# src/autodub/adapters/embedding_extractor.py
"""
Adapter real para extração de embeddings de voz usando Resemblyzer.

Implementa a interface `IEmbeddingExtractor`, convertendo um arquivo de áudio
em um vetor numérico (embedding) que representa as características vocais
do locutor — útil para identificação, clonagem ou correspondência de vozes.
"""

from __future__ import annotations

import numpy as np
from resemblyzer import VoiceEncoder, preprocess_wav

from autodub.interfaces.embedding_interface import IEmbeddingExtractor


class ResemblyzerEmbedding(IEmbeddingExtractor):
    """
    Extrai embeddings de voz usando o modelo `Resemblyzer`.

    Este adapter utiliza o encoder pré-treinado baseado em redes neurais
    para gerar vetores representativos da voz de um locutor.
    """

    def __init__(self, device: str | None = None) -> None:
        """
        Inicializa o encoder do Resemblyzer.

        Args:
            device (str, opcional): Define o dispositivo de execução ('cpu' ou 'cuda').
                                    Se None, o Resemblyzer escolhe automaticamente.
        """
        self.encoder = VoiceEncoder(device=device)

    def extrair(self, caminho_audio: str) -> np.ndarray:
        """
        Extrai o embedding de um arquivo de áudio.

        Args:
            caminho_audio (str): Caminho completo para o áudio (ex: WAV ou MP3).

        Returns:
            np.ndarray: Vetor do embedding de voz (dimensão típica: 256).
        """
        try:
            # Pré-processa o áudio para o formato esperado (16 kHz, mono)
            wav = preprocess_wav(caminho_audio)

            # Extrai o vetor de características da voz
            embedding = self.encoder.embed_utterance(wav)

            # Garante tipo consistente para cálculos futuros
            if not isinstance(embedding, np.ndarray):
                embedding = np.array(embedding, dtype=np.float32)

            return embedding

        except Exception as e:
            raise RuntimeError(f"Falha ao extrair embedding de {caminho_audio}: {e}") from e
