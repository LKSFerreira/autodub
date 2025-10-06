# src/autodub/pipeline_manual.py
"""
Runner manual para testar o pipeline com ASR real (Whisper)
e os demais componentes ainda mockados.

Execute com:
    poetry run python -m autodub.pipeline_manual tests/samples/video_teste.mp4
"""

import sys
from pathlib import Path
from shutil import which

from autodub.adapters.embedding_extractor_adapter import ResemblyzerEmbedding
from autodub.adapters.mocks.ffmpeg_wrapper import FakeFFmpegWrapper
from autodub.adapters.mocks.mock_translator import MockTranslator
from autodub.adapters.mocks.mock_tts import MockTTS
from autodub.adapters.mocks.mock_vocoder import MockVocoder
from autodub.adapters.whisper_asr_adapter import WhisperAsr
from autodub.pipeline import Pipeline


def main():
    if len(sys.argv) < 2:
        print("Uso: poetry run python -m autodub.pipeline_manual tests/samples/video_teste.mp4")
        sys.exit(1)

    video_entrada = Path(sys.argv[1])

    if not video_entrada.exists():
        print(f"❌ Erro: arquivo de entrada não encontrado: {video_entrada}")
        sys.exit(1)

    video_saida = video_entrada.with_stem(f"{video_entrada.stem}_dublado")

    # Detecta ffmpeg
    if which("ffmpeg"):
        from autodub.adapters.real_ffmpeg_wrapper_adapter import (
            RealFFmpegWrapper as FFmpegAdapter,
        )

        ffmpeg_adapter = FFmpegAdapter()
        print("ℹ️  ffmpeg detectado no sistema: usando RealFFmpegWrapper")
    else:
        ffmpeg_adapter = FakeFFmpegWrapper()
        print("⚠️  ffmpeg não encontrado — usando FakeFFmpegWrapper (modo simulado)")

    # Monta pipeline completa
    pipeline = Pipeline(
        asr=WhisperAsr(model_name="base"),
        tts=MockTTS(),
        ffmpeg=ffmpeg_adapter,
        vocoder=MockVocoder(),
        embedding=ResemblyzerEmbedding(),
        translator=MockTranslator(),
    )

    print("🚀 Executando pipeline manual...\n")
    saida = pipeline.executar(video_entrada, video_saida, target_lang="pt-br", debug=True)
    print(f"\n✅ Pipeline finalizado com sucesso! Saída: {saida}")


if __name__ == "__main__":
    main()
