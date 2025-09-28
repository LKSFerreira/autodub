class MockEmbedding:
    """
    Mock simples para extração de embeddings de áudio, timbre do voz.
    """

    def extrair_embedding(self, audio_path: str) -> list[float]:
        """
        Retorna um vetor fixo para testes determinísticos.
        """
        return [0.1, 0.2, 0.3]
