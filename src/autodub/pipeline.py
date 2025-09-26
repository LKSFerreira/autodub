"""
Pipeline de orquestração do fluxo de dublagem (versão para uso com mocks).

A Pipeline foi projetada para ser injetável (dependency injection): receba as
implementações (mocks ou reais) no construtor. O método `executar` coordena o
fluxo ponta-a-ponta usando somente as assinaturas públicas dos componentes.
"""

from __future__ import annotations

import logging
import shutil
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
        msg = record.getMessage()
        lower_msg = msg.lower()

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
            if key in lower_msg:
                emoji = icon
                break

        return f"{levelname}: {record.name}.py - {record.module}: {emoji} {msg}"


def setup_logger():
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(ColorFormatter())
    logger = logging.getLogger("autodub.pipeline")
    logger.setLevel(logging.INFO)
    logger.handlers = [handler]
    logger.propagate = False
    return logger


# --- substitui o logger padrão ---
logger = setup_logger()


class Pipeline:
    """
    Orquestra o fluxo de dublagem.
    """

    def __init__(self, asr, tts, ffmpeg, embedding=None, vocoder=None) -> None:
        if asr is None or tts is None or ffmpeg is None:
            raise ValueError("asr, tts e ffmpeg são obrigatórios para criar a Pipeline")

        self.asr = asr
        self.tts = tts
        self.embedding = embedding
        self.vocoder = vocoder
        self.ffmpeg = ffmpeg

    def _save_bytes(self, data: bytes, path: Union[str, Path]) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "wb") as f:
            f.write(data)

    def executar(
        self, video_path: Union[str, Path], output_path: Union[str, Path]
    ) -> Path:
        """
        Executa o fluxo de dublagem ponta-a-ponta usando os componentes injetados.
        """
        tmpdir = Path(tempfile.mkdtemp(prefix="autodub_pipeline_"))
        logger.info("Criando diretório temporário %s", tmpdir)

        video_path = str(video_path)
        output_path = Path(output_path)
        combined_audio = tmpdir / "combined_audio.wav"

        try:
            # 1) extrair áudio
            extracted_audio = tmpdir / "extracted_audio.wav"
            logger.info("Extraindo áudio de %s -> %s", video_path, extracted_audio)
            self.ffmpeg.extract_audio(video_path, extracted_audio)

            # 2) transcrever
            logger.info("Transcrevendo áudio %s", extracted_audio)
            segmentos: List[Dict] = self.asr.transcrever(str(extracted_audio))
            logger.info(" Obtidos %d segmentos", len(segmentos))

            # 3) sintetizar cada segmento e salvar temporariamente
            segment_files: List[Path] = []
            for idx, seg in enumerate(segmentos):
                texto = seg.get("texto", "")
                logger.info(" Sintetizando segmento %d: %s", idx, texto)
                audio_bytes = self.tts.sintetizar(texto)
                seg_file = tmpdir / f"segment_{idx}.wav"
                self._save_bytes(audio_bytes, seg_file)
                segment_files.append(seg_file)

            # 4) concatenar arquivos de segmento em um audio combinado
            logger.info(
                "Combinando %d segmentos em %s", len(segment_files), combined_audio
            )
            with open(combined_audio, "wb") as out_f:
                for segf in segment_files:
                    with open(segf, "rb") as rf:
                        out_f.write(rf.read())

            # 5) mux final
            logger.info("Realizando mux de áudio em vídeo -> %s", output_path)
            self.ffmpeg.mux_audio(video_path, combined_audio, str(output_path))

            logger.info("Execução concluída, saída em %s", output_path)
            return Path(output_path)

        except Exception as exc:
            logger.error("Erro durante execução: %s", exc)
            raise

        finally:
            try:
                shutil.rmtree(tmpdir)
            except Exception:
                logger.warning("Falha ao limpar temporários %s", tmpdir)
