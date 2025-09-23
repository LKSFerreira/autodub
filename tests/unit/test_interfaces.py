"""
Testes de sanidade para as interfaces do projeto.

O objetivo não é testar implementações reais, mas garantir que
mocks conseguem ser usados conforme os contratos definidos.
"""

from typing import List, Tuple

from autodub.interfaces.alignment_interface import IAlignment
from autodub.interfaces.asr_interface import IAsr
from autodub.interfaces.embedding_interface import IEmbeddingExtractor
from autodub.interfaces.tts_interface import ITts


# --- Mocks de exemplo --- #
class MockAsr:
    def transcrever(self, caminho_audio: str) -> List[Tuple[str, float, float]]:
        return [("Olá mundo", 0.0, 1.0)]


class MockTts:
    def sintetizar(self, texto: str, caminho_saida: str) -> None:
        with open(caminho_saida, "w") as f:
            f.write("AUDIO_MOCK")


class MockEmbedding:
    def extrair(self, caminho_audio: str) -> List[float]:
        return [0.1, 0.2, 0.3]


class MockAlignment:
    def alinhar(self, texto: str, caminho_audio: str) -> List[Tuple[str, float, float]]:
        return [(texto, 0.0, 1.0)]


# --- Testes --- #
def test_asr_interface():
    asr: IAsr = MockAsr()
    resultado = asr.transcrever("fake.wav")
    assert resultado[0][0] == "Olá mundo"


def test_tts_interface(tmp_path):
    saida = tmp_path / "saida.txt"
    tts: ITts = MockTts()
    tts.sintetizar("teste", str(saida))
    assert saida.exists()
    assert "AUDIO_MOCK" in saida.read_text()


def test_embedding_interface():
    emb: IEmbeddingExtractor = MockEmbedding()
    vetor = emb.extrair("fake.wav")
    assert isinstance(vetor, list)
    assert len(vetor) == 3


def test_alignment_interface():
    align: IAlignment = MockAlignment()
    resultado = align.alinhar("teste", "fake.wav")
    assert resultado[0][0] == "teste"
