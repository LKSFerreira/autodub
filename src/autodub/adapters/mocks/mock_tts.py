import hashlib
import io
import math
import struct
import wave


class MockTTS:
    def __init__(self, duration_seconds: float = 0.5, sample_rate: int = 16000):
        self.duration_seconds = duration_seconds
        self.sample_rate = sample_rate

    def sintetizar(self, texto: str) -> bytes:
        """
        Gera um WAV válido com onda senoidal.
        - O conteúdo varia conforme o texto (para os testes passarem).
        - A duração mínima é 0.1s.
        """
        # Duração depende do texto
        dur = max(0.1, self.duration_seconds + (len(texto) % 5) * 0.1)
        nframes = int(dur * self.sample_rate)

        # Frequência pseudo-aleatória a partir do hash do texto
        h = int(hashlib.sha1(texto.encode()).hexdigest(), 16)
        tone = (h % 200) + 200  # entre 200Hz e 400Hz

        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16 bits
            wf.setframerate(self.sample_rate)
            for i in range(nframes):
                sample = int(32767 * 0.1 * math.sin(2 * math.pi * tone * i / self.sample_rate))
                wf.writeframesraw(struct.pack("<h", sample))
        return buffer.getvalue()
