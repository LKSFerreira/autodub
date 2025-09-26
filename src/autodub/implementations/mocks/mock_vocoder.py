class MockVocoder:
    """
    Mock simples de vocoder para testes.
    """

    def sintetizar_from_mel(self, mel) -> bytes:
        """
        Simula a conversão de espectrograma mel em áudio.
        """
        return b"FAKE_VOCODER_AUDIO"
