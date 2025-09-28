class FakeFFmpegWrapper:
    """
    Mock simples do ffmpeg para testes de pipeline.
    """

    def extract_audio(self, video_path: str, out_audio_path: str) -> None:
        """
        Simula extração de áudio de um vídeo.
        Cria apenas um placeholder.
        """
        with open(out_audio_path, "wb") as f:
            f.write(b"FAKE_AUDIO")

    def mux_audio(self, video_path: str, audio_path: str, out_video_path: str) -> None:
        """
        Simula inserção de áudio em um vídeo.
        Cria apenas um arquivo placeholder.
        """
        with open(out_video_path, "wb") as f:
            f.write(b"FAKE_VIDEO_WITH_AUDIO")
