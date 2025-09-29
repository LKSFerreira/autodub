# src/autodub/adapters/whisper_asr.py

import whisper

from autodub.interfaces.asr_interface import IAsr


class WhisperAsr(IAsr):
    def __init__(self, model_name: str = "base"):
        """
        Inicializa o adapter do Whisper.

        Args:
            model_name (str): Nome do modelo do Whisper a ser carregado
                              (ex.: "tiny", "base", "small", "medium", "large").
        """
        self.model_name = model_name
        self.model = whisper.load_model(model_name)

    def transcrever(self, audio_path: str):
        """
        Transcreve o áudio usando Whisper.

        Args:
            audio_path (str): Caminho para o arquivo de áudio.

        Returns:
            list[dict]: Lista de segmentos no formato
                        {"texto": str, "inicio": float, "fim": float}
        """
        result = self.model.transcribe(audio_path)
        return [
            {"texto": seg["text"], "inicio": seg["start"], "fim": seg["end"]}
            for seg in result["segments"]
        ]
