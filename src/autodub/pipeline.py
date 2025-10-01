# src/autodub/pipeline.py

"""
Pipeline de orquestração do fluxo de dublagem.

A Pipeline é injetável (dependency injection): recebe as implementações
(mocks ou reais) no construtor. O método `executar` coordena o fluxo ponta-a-ponta
usando somente as assinaturas públicas dos componentes.
"""

from __future__ import annotations

import json
import logging
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Union

# --- CORES ANSI ---
RESET = "\033[0m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"

# --- EMOJIS PARA A PIPELINE ---
EMOJIS = {
    "criando diretório temporário": "📂",
    "extraindo áudio": "🎵",
    "transcrevendo áudio": "📝",
    "obtidos": "✂️",
    "sintetizando": "🗣️",
    "combinando": "🎶",
    "realizando mux": "🎬",
    "execução concluída": "✅",
    "erro": "❌",
    "falha": "⚠️",
}


class ColorFormatter(logging.Formatter):
    def format(self, record):
        msg = record.getMessage().lower()

        # cor do nível
        if record.levelno == logging.INFO:
            levelname = f"{GREEN}{record.levelname}{RESET}"
        elif record.levelno == logging.WARNING:
            levelname = f"{YELLOW}{record.levelname}{RESET}"
        elif record.levelno >= logging.ERROR:
            levelname = f"{RED}{record.levelname}{RESET}"
        else:
            levelname = record.levelname

        # emoji de acordo com a mensagem
        emoji = ""
        for key, icon in EMOJIS.items():
            if key in msg:
                emoji = icon
                break

        return (
            f"{levelname}: {record.name}.py - "
            f"{record.module}: {emoji} {record.getMessage()}"
        )


def setup_logger():
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(ColorFormatter())
    logger = logging.getLogger("autodub.pipeline")
    logger.setLevel(logging.INFO)
    logger.handlers = [handler]
    logger.propagate = False
    return logger


logger = setup_logger()


class Pipeline:
    """Orquestra o fluxo de dublagem."""

    def __init__(self, asr, tts, ffmpeg, embedding=None, vocoder=None) -> None:
        if asr is None or tts is None or ffmpeg is None:
            raise ValueError("asr, tts e ffmpeg são obrigatórios para criar a Pipeline")

        self.asr = asr
        self.tts = tts
        self.embedding = embedding
        self.vocoder = vocoder
        self.ffmpeg = ffmpeg

    def _save_bytes(self, data: bytes, path: Union[str, Path]) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            f.write(data)

    def _concatenar_segmentos(self, arquivos: List[Path], destino: Path) -> None:
        """Concatena segmentos WAV em um único arquivo usando ffmpeg."""
        if not arquivos:
            # fallback: cria wav de silêncio
            from autodub.adapters.mocks.mock_tts import MockTTS

            logger.warning("Nenhum segmento para combinar — criando áudio vazio")
            empty_bytes = MockTTS(duration_seconds=0.1).sintetizar("")
            self._save_bytes(empty_bytes, destino)
            return

        if len(arquivos) == 1:
            # só copiar o único segmento
            shutil.copyfile(arquivos[0], destino)
            return

        # concat de múltiplos arquivos
        cmd = ["ffmpeg", "-y"]
        for seg in arquivos:
            cmd += ["-i", str(seg)]
        cmd += [
            "-filter_complex",
            f"concat=n={len(arquivos)}:v=0:a=1[out]",
            "-map",
            "[out]",
            "-ar",
            "16000",
            "-ac",
            "1",
            "-c:a",
            "pcm_s16le",
            str(destino),
        ]
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as exc:
            stderr = exc.stderr.decode() if exc.stderr else str(exc)
            logger.error("Falha ao concatenar segmentos com ffmpeg: %s", stderr)
            raise RuntimeError(f"Falha ao concatenar segmentos com ffmpeg: {stderr}") from exc

    def executar(
        self,
        video_path: Union[str, Path],
        output_path: Union[str, Path],
        debug: bool = True,
    ) -> Path:
        """
        Executa o fluxo de dublagem ponta-a-ponta usando os componentes injetados.

        Args:
            video_path: Caminho para vídeo ou áudio de entrada
            output_path: Caminho de saída do vídeo dublado
            debug: Se True, mantém arquivos auxiliares de transcrição/tradução
        """
        output_path = Path(output_path)
        tmpdir = Path(tempfile.mkdtemp(prefix="autodub_pipeline_"))

        try:
            combined_audio = tmpdir / "combined_audio.wav"

            # 1) extrair áudio
            extracted_audio = tmpdir / "extracted_audio.wav"
            logger.info("Extraindo áudio de %s -> %s", video_path, extracted_audio)
            self.ffmpeg.extract_audio(str(video_path), extracted_audio)

            # 2) transcrever
            logger.info("Transcrevendo áudio %s", extracted_audio)
            segmentos: List[Dict] = self.asr.transcrever(str(extracted_audio))

            if debug:
                transcript_file = output_path.parent / "transcricao.jsonl"
                with open(transcript_file, "w", encoding="utf-8") as tf:
                    for seg in segmentos:
                        tf.write(json.dumps(seg, ensure_ascii=False) + "\n")
                logger.info(
                    "Obtidos %d segmentos (transcrição salva em %s)",
                    len(segmentos),
                    transcript_file,
                )
            else:
                logger.info("Obtidos %d segmentos", len(segmentos))

            # 3) sintetizar cada segmento
            segment_files: List[Path] = []
            for idx, seg in enumerate(segmentos):
                texto = seg.get("texto", "")
                logger.info("Sintetizando segmento %d: %s", idx, texto)
                audio_bytes = self.tts.sintetizar(texto)
                seg_file = tmpdir / f"segment_{idx}.wav"
                self._save_bytes(audio_bytes, seg_file)
                segment_files.append(seg_file)

            # 4) concatenar segmentos
            logger.info("Combinando %d segmentos em %s", len(segment_files), combined_audio)
            self._concatenar_segmentos(segment_files, combined_audio)

            # 5) mux final
            logger.info("Realizando mix de áudio em vídeo -> %s", output_path)
            self.ffmpeg.mux_audio(str(video_path), combined_audio, str(output_path))

            logger.info("Execução concluída, saída em %s", output_path)
            return output_path

        except Exception as exc:
            logger.error("Erro durante execução: %s", exc)
            raise

        finally:
            try:
                shutil.rmtree(tmpdir)
            except Exception as cleanup_err:
                logger.warning("Falha ao limpar temporários %s: %s", tmpdir, cleanup_err)
