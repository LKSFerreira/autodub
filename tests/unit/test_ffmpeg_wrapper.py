from autodub.implementations.mocks.ffmpeg_wrapper import FakeFFmpegWrapper


def test_extract_audio_cria_arquivo(tmp_path):
    wrapper = FakeFFmpegWrapper()
    out_path = tmp_path / "audio.wav"
    wrapper.extract_audio("video.mp4", out_path)

    assert out_path.exists()
    with open(out_path, "rb") as f:
        conteudo = f.read()
    assert conteudo == b"FAKE_AUDIO"


def test_mux_audio_cria_arquivo(tmp_path):
    wrapper = FakeFFmpegWrapper()
    out_path = tmp_path / "video_com_audio.mp4"
    wrapper.mux_audio("video.mp4", "audio.wav", out_path)

    assert out_path.exists()
    with open(out_path, "rb") as f:
        conteudo = f.read()
    assert conteudo == b"FAKE_VIDEO_WITH_AUDIO"
