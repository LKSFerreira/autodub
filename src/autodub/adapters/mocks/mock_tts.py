import hashlib


class MockTTS:
    """
    Mock determinístico de TTS (Síntese de Fala).

    Gera dados binários previsíveis a partir de um texto de entrada,
    simulando a geração de áudio sem precisar de modelo real.
    """

    def sintetizar(self, texto: str, voz_id: str | None = None) -> bytes:
        """
        Simula a síntese de fala.

        Args:
            texto (str): Texto a ser convertido em "áudio".
            voz_id (str | None): Identificador de voz (opcional).

        Returns:
            bytes: Dados binários simulando áudio.
        """
        hash_val = hashlib.md5(texto.encode("utf-8")).digest()
        return hash_val
