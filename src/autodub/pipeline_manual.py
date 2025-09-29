"""
Runner manual para testar o pipeline com ASR real (Whisper)
e os demais componentes ainda mockados.

Execute com:
    poetry run python pipeline_manual.py tests/samples/video_teste.mp4
"""

import sys
from pathlib import Path

from autodub.adapters.mocks.ffmpeg_wrapper import FakeFFmpegWrapper
from autodub.adapters.mocks.mock_tts import MockTTS
from autodub.adapters.mocks.mock_vocoder import MockVocoder
from autodub.adapters.whisper_asr import WhisperAsr
from autodub.pipeline import Pipeline


def main():
    if len(sys.argv) < 2:
        print("Uso: poetry run python pipeline_manual.py <video_entrada>")
        sys.exit(1)

    video_entrada = Path(sys.argv[1])

    if not video_entrada.exists():
        print(f"Erro: arquivo de entrada não encontrado: {video_entrada}")
        sys.exit(1)

    # Define saída automaticamente
    video_saida = video_entrada.with_stem(video_entrada.stem + "_dublado")

    # Monta pipeline com Whisper real
    pipeline = Pipeline(
        asr=WhisperAsr(model_name="base"),
        tts=MockTTS(),
        ffmpeg=FakeFFmpegWrapper(),
        vocoder=MockVocoder(),
    )

    print("🚀 Executando pipeline manual...\n")
    saida = pipeline.executar(video_entrada, video_saida)
    print(f"\n✅ Pipeline finalizado com sucesso! Saída: {saida}")


if __name__ == "__main__":
    main()
