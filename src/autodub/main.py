from autodub.implementations.mocks import FakeFFmpegWrapper, MockASR, MockTTS
from autodub.pipeline import Pipeline

asr = MockASR()
tts = MockTTS()
ffmpeg = FakeFFmpegWrapper()
pipeline = Pipeline(asr=asr, tts=tts, ffmpeg=ffmpeg)

saida = pipeline.executar("video_de_teste.mp4", "video_dublado.mp4")
# Com os mocks atuais, 'video_dublado.mp4' deve existir (conteúdo fake).
