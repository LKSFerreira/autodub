# src/autodub/adapters/tts_yourtts.py

"""
Adapter de Text-to-Speech (TTS) real usando modelo tipo YourTTS ou Coqui TTS.

Este módulo implementa a interface ITts, aceitando opcionalmente embeddings
de locutores (gerados via Resemblyzer) para clonagem de voz.
"""

from __future__ import annotations

import io
from typing import Optional

import numpy as np
import soundfile as sf

from autodub.interfaces.tts_interface import ITts


def load_model(model_path: str, device: str):
    """
    Placeholder para carregamento de modelo TTS real (YourTTS/Coqui/etc).

    No modo mock, apenas retorna None. Na implementação real,
    deverá carregar o modelo YourTTS pré-treinado.
    """
    # Exemplo real (futuro):
    # from TTS.api import TTS
    # return TTS(model_path, gpu=device == "cuda")
    return None


def load_vocoder(device: str):
    """
    Placeholder para vocoder (HiFi-GAN, WaveGlow, etc).
    """
    return None


def wav_bytes_from_array(audio: np.ndarray, sr: int = 16000) -> bytes:
    """
    Converte um array NumPy em bytes WAV PCM16.
    """
    buffer = io.BytesIO()
    sf.write(buffer, audio, sr, subtype="PCM_16", format="WAV")
    return buffer.getvalue()


class YourTTSAdapter(ITts):
    """
    Implementação real de TTS condicional (YourTTS-style).

    Args:
        model_path (str): Caminho ou nome do modelo.
        device (str): 'cuda' ou 'cpu'.
    """

    def __init__(self, model_path: str = "yourtts_base.pt", device: str = "cpu"):
        self.device = device
        self.model = load_model(model_path, device)
        self.vocoder = load_vocoder(device)

    def sintetizar(self, texto: str, embedding: Optional[np.ndarray] = None) -> bytes:
        """
        Converte texto em fala, opcionalmente condicionada ao embedding do locutor.

        Args:
            texto (str): Texto de entrada.
            embedding (np.ndarray, opcional): Vetor de características vocais.

        Returns:
            bytes: Áudio WAV 16kHz PCM16.
        """
        # --- Simulação (mock funcional) ---
        # Gera senoide simples para debug
        import numpy as np

        sr = 16000
        t = np.linspace(0, 0.8, int(sr * 0.8), endpoint=False)
        freq = 220 + (hash(texto) % 200)
        audio = 0.2 * np.sin(2 * np.pi * freq * t)

        # futuro: usar modelo real
        # mel = model.text_to_mel(texto, embedding)
        # audio = vocoder(mel)
        wav_bytes = wav_bytes_from_array(audio, sr=sr)
        return wav_bytes
