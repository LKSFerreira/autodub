"""
Adapter ASR real usando Whisper.

Implementa a interface IAsr, convertendo áudio em texto.
"""

import logging
from typing import Dict, List

import whisper  # Biblioteca externa (precisa ser adicionada em pyproject.toml)

from autodub.interfaces.asr_interface import IAsr

logger = logging.getLogger(__name__)


class WhisperAsr(IAsr):
    """
    Implementação real de ASR usando OpenAI Whisper.
    """

    def __init__(self, modelo: str = "tiny"):
        """
        Inicializa o modelo Whisper.

        Args:
            modelo (str): Nome do modelo Whisper (tiny, base, small, medium, large).
        """
        try:
            self.model = whisper.load_model(modelo)
            logger.info("WhisperASR inicializado com modelo: %s", modelo)
        except Exception as e:
            logger.error("Falha ao carregar modelo Whisper: %s", e)
            raise

    def transcrever(self, audio_path: str) -> List[Dict]:
        """
        Transcreve um arquivo de áudio para texto.

        Args:
            audio_path (str): Caminho do arquivo de áudio.

        Returns:
            List[Dict]: Lista de segmentos contendo texto, inicio e fim.
        """
        try:
            resultado = self.model.transcribe(audio_path)
            segmentos = []
            for seg in resultado.get("segments", []):
                segmentos.append(
                    {"texto": seg["text"], "inicio": seg["start"], "fim": seg["end"]}
                )
            return segmentos
        except Exception as e:
            logger.error("Erro durante transcrição: %s", e)
            raise RuntimeError("Falha na transcrição com Whisper") from e
