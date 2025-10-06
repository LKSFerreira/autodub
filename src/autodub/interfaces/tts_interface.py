# src/autodub/interfaces/tts_interface.py

"""
Interface para módulos de Síntese de Fala (Text-to-Speech, TTS).

Define o contrato para geração de áudio a partir de texto.
"""

from __future__ import annotations

from typing import Optional, Protocol, Union

import numpy as np


class ITts(Protocol):
    """
    Interface para sistemas de Text-to-Speech (TTS).
    """

    def sintetizar(
        self, texto: str, embedding: Optional[Union[list, np.ndarray]] = None
    ) -> bytes:
        """
        Gera áudio (em bytes WAV/PCM 16kHz mono) a partir do texto e,
        opcionalmente, condicionado a um embedding de voz.

        Args:
            texto (str): Texto a ser convertido em fala.
            embedding (list | np.ndarray, opcional): Vetor de características vocais.

        Returns:
            bytes: Dados binários do áudio gerado (formato WAV PCM16 mono 16kHz).
        """
        ...
