# src/autodub/adapters/real_ffmpeg_wrapper.py
from __future__ import annotations

import logging
import subprocess
from pathlib import Path
from typing import Union

logger = logging.getLogger(__name__)


class RealFFmpegWrapper:
    """
    Wrapper mínimo para operações com ffmpeg:
    - extract_audio(video_path, out_audio_path)
    - mux_audio(video_path, audio_path, out_video_path)

    Usa o executável 'ffmpeg' disponível no PATH do sistema.
    """

    def extract_audio(
        self, video_path: Union[str, Path], out_audio_path: Union[str, Path]
    ) -> None:
        video_path = str(video_path)
        out_audio_path = str(out_audio_path)
        # Força WAV PCM 16kHz mono (bom para ASR)
        cmd = [
            "ffmpeg",
            "-y",  # overwrite
            "-i",
            video_path,
            "-vn",  # no video
            "-acodec",
            "pcm_s16le",
            "-ac",
            "1",
            "-ar",
            "16000",
            out_audio_path,
        ]
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            logger.debug(
                "RealFFmpegWrapper.extract_audio executado com sucesso: %s",
                out_audio_path,
            )
        except subprocess.CalledProcessError as exc:
            stderr = exc.stderr.decode() if exc.stderr else str(exc)
            logger.error("ffmpeg extract_audio falhou: %s", stderr)
            raise RuntimeError(f"ffmpeg failed to extract audio: {stderr}") from exc

    def mux_audio(
        self,
        video_path: Union[str, Path],
        audio_path: Union[str, Path],
        out_video_path: Union[str, Path],
    ) -> None:
        video_path = str(video_path)
        audio_path = str(audio_path)
        out_video_path = str(out_video_path)
        # Copia vídeo e substitui a trilha de áudio
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            video_path,
            "-i",
            audio_path,
            "-c:v",
            "copy",
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            out_video_path,
        ]
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            logger.debug(
                "RealFFmpegWrapper.mux_audio executado com sucesso: %s", out_video_path
            )
        except subprocess.CalledProcessError as exc:
            stderr = exc.stderr.decode() if exc.stderr else str(exc)
            logger.error("ffmpeg mux_audio falhou: %s", stderr)
            raise RuntimeError(f"ffmpeg failed to mux audio: {stderr}") from exc
