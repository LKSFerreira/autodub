from autodub.implementations.mocks.mock_embedding import MockEmbedding


def test_extrair_embedding_retorna_lista():
    emb = MockEmbedding()
    saida = emb.extrair_embedding("arquivo.wav")
    assert isinstance(saida, list)
    assert all(isinstance(x, float) for x in saida)


def test_extrair_embedding_valores_fixos():
    emb = MockEmbedding()
    saida = emb.extrair_embedding("qualquer.wav")
    assert saida == [0.1, 0.2, 0.3]
