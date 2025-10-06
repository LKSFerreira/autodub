from typing import Dict, List


def alinhar_palavras(
    texto: str, inicio: float = 0.0, duracao_total: float = None
) -> List[Dict[str, float]]:
    """
    Simula o alinhamento de palavras com timestamps.

    Args:
        texto (str): Texto a ser alinhado.
        inicio (float): Tempo inicial do segmento.
        duracao_total (float, opcional): Duração total para distribuir as palavras.

    Returns:
        List[Dict]: Lista de dicionários no formato:
            [{"palavra": str, "start": float, "end": float}, ...]
    """
    palavras = texto.strip().split()

    if not palavras:
        return []

    # Define duração de cada palavra
    if duracao_total is not None:
        duracao_por_palavra = duracao_total / len(palavras)
    else:
        duracao_por_palavra = 0.5  # mock fixo

    alinhamento = []
    tempo_atual = inicio

    for palavra in palavras:
        entrada = {
            "palavra": palavra,
            "start": round(tempo_atual, 3),
            "end": round(tempo_atual + duracao_por_palavra, 3),
        }
        alinhamento.append(entrada)
        tempo_atual += duracao_por_palavra

    return alinhamento
