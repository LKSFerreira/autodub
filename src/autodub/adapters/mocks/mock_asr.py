from typing import Dict, List


class MockASR:
    """
    Mock determinístico de ASR (Reconhecimento Automático de Fala).

    Este mock retorna transcrições previsíveis baseadas no nome do arquivo
    de entrada, permitindo testes de pipeline sem depender de modelos reais.
    """

    def transcrever(self, audio_path: str) -> List[Dict]:
        """
        Simula a transcrição de áudio.

        Args:
            audio_path (str): Caminho para o arquivo de áudio.

        Returns:
            List[Dict]: Lista de segmentos com texto e marcações de tempo.
        """
        if "teste" in audio_path.lower():
            return [
                {"texto": "Olá, este é um teste.", "inicio": 0.0, "fim": 1.5},
                {"texto": "MockASR funcionando.", "inicio": 1.5, "fim": 3.0},
            ]

        return [{"texto": f"Arquivo processado: {audio_path}", "inicio": 0.0, "fim": 2.0}]
