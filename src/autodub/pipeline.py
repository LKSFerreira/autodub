"""
Pipeline de orquestração do fluxo de dublagem.

A Pipeline é injetável (dependency injection): recebe as implementações
(mocks ou reais) no construtor. O método `executar` coordena o fluxo ponta-a-ponta
usando apenas as assinaturas públicas dos componentes.
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
    "áudio extraído": "🎵",
    "extraindo embedding": "🧠",
    "embedding extraído": "✨",
    "embedding salvo": "💾",
    "transcrevendo áudio": "📝",
    "obtidos": "✂️",
    "traduzindo segmentos": "🌍",
    "tradução salva": "💾",
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

        # Cor do nível
        if record.levelno == logging.INFO:
            levelname = f"{GREEN}{record.levelname}{RESET}"
        elif record.levelno == logging.WARNING:
            levelname = f"{YELLOW}{record.levelname}{RESET}"
        elif record.levelno >= logging.ERROR:
            levelname = f"{RED}{record.levelname}{RESET}"
        else:
            levelname = record.levelname

        # Emoji de acordo com a mensagem
        emoji = next((icon for key, icon in EMOJIS.items() if key in msg), "")

        return f"{levelname}: {record.name}.py - {record.module}: {emoji} {record.getMessage()}"


def setup_logger():
    logging.captureWarnings(True)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(ColorFormatter())

    # Logger principal da pipeline
    logger = logging.getLogger("autodub.pipeline")
    logger.setLevel(logging.INFO)
    logger.handlers = [handler]
    logger.propagate = False

    # Logger para warnings
    warnings_logger = logging.getLogger("py.warnings")
    warnings_logger.handlers = [handler]
    warnings_logger.propagate = False

    return logger


logger = setup_logger()


class Pipeline:
    """Orquestra o fluxo completo de dublagem."""

    def __init__(
        self,
        asr,
        tts,
        ffmpeg,
        embedding=None,
        vocoder=None,
        translator=None,
    ) -> None:
        if not all([asr, tts, ffmpeg]):
            raise ValueError("asr, tts e ffmpeg são obrigatórios para criar a Pipeline")

        self.asr = asr
        self.tts = tts
        self.embedding = embedding
        self.vocoder = vocoder
        self.ffmpeg = ffmpeg
        self.translator = translator

    def _save_bytes(self, data: bytes, path: Union[str, Path]) -> None:
        """Salva bytes binários em disco."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            f.write(data)

    def _concatenar_segmentos(self, arquivos: List[Path], destino: Path) -> None:
        """Concatena arquivos WAV em um único áudio usando ffmpeg."""
        if not arquivos:
            from autodub.adapters.mocks.mock_tts import MockTTS

            logger.warning("Nenhum segmento para combinar — criando áudio vazio.")
            empty_bytes = MockTTS(duration_seconds=0.1).sintetizar("")
            self._save_bytes(empty_bytes, destino)
            return

        if len(arquivos) == 1:
            shutil.copyfile(arquivos[0], destino)
            return

        cmd = [
            "ffmpeg",
            "-y",
            *[f"-i {seg}" for seg in arquivos],
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
            subprocess.run(
                " ".join(cmd),
                check=True,
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
            )
        except subprocess.CalledProcessError as exc:
            stderr = exc.stderr.decode() if exc.stderr else str(exc)
            raise RuntimeError(f"Falha ao concatenar segmentos com ffmpeg: {stderr}") from exc

    def executar(
        self,
        video_path: Union[str, Path],
        output_path: Union[str, Path],
        target_lang: str = "pt-br",
        debug: bool = False,
    ) -> Path:
        """
        Executa o fluxo ponta a ponta da dublagem:
        1) Extrai áudio
        2) Extrai embedding
        3) Transcreve
        4) Traduz
        5) Sintetiza
        6) Concatena
        7) Faz o mux final
        """
        output_path = Path(output_path)
        tmpdir = Path(tempfile.mkdtemp(prefix="autodub_pipeline_"))
        logger.info(f"Criando diretório temporário em {tmpdir}")

        try:
            combined_audio = tmpdir / "combined_audio.wav"

            # 1) Extração de áudio
            extracted_audio = tmpdir / "extracted_audio.wav"
            logger.info(f"Extraindo áudio de {video_path} → {extracted_audio}")
            self.ffmpeg.extract_audio(str(video_path), extracted_audio)

            if debug:
                debug_audio_copy = output_path.parent / "audio_extraido.wav"
                shutil.copyfile(extracted_audio, debug_audio_copy)
                logger.info(f"Áudio extraído salvo para debug em {debug_audio_copy}")

            # 2) Embedding
            if self.embedding:
                logger.info(f"Extraindo embedding do locutor de {extracted_audio}")
                embedding_vetor = self.embedding.extrair(str(extracted_audio))
                emb_list = (
                    embedding_vetor.tolist()
                    if hasattr(embedding_vetor, "tolist")
                    else list(embedding_vetor)
                )
                logger.info(f"Embedding extraído: {len(emb_list)} dimensões")
                if debug:
                    emb_path = output_path.parent / "embedding.json"
                    with open(emb_path, "w", encoding="utf-8") as f:
                        json.dump(emb_list, f, ensure_ascii=False)
                    logger.info(f"Embedding salvo para debug em {emb_path}")

            # 3) Transcrição
            logger.info(f"Transcrevendo áudio {extracted_audio}")
            segmentos: List[Dict] = self.asr.transcrever(str(extracted_audio))

            if debug:
                transcript_file = output_path.parent / "transcricao.jsonl"
                with open(transcript_file, "w", encoding="utf-8") as tf:
                    for seg in segmentos:
                        tf.write(json.dumps(seg, ensure_ascii=False) + "\n")
                logger.info(
                    f"Obtidos {len(segmentos)} segmentos "
                    f"(transcrição salva em {transcript_file})"
                )

            # 4) Tradução
            if self.translator:
                logger.info(f"Traduzindo segmentos para {target_lang}")
                for seg in segmentos:
                    seg_text = seg.get("texto", "")
                    seg["texto_traduzido"] = self.translator.traduzir(seg_text, target_lang)

                if debug:
                    trad_path = output_path.parent / "transcricao_traduzida.jsonl"
                    with open(trad_path, "w", encoding="utf-8") as tf:
                        for seg in segmentos:
                            tf.write(json.dumps(seg, ensure_ascii=False) + "\n")
                    logger.info(f"Tradução salva em {trad_path}")
            else:
                logger.info("Nenhum tradutor configurado — etapa ignorada.")

            # 5) Síntese
            segment_files: List[Path] = []
            for idx, seg in enumerate(segmentos):
                texto = seg.get("texto_traduzido") or seg.get("texto", "")
                logger.info(f"Sintetizando segmento {idx}: {texto}")
                audio_bytes = self.tts.sintetizar(texto)
                seg_file = tmpdir / f"segment_{idx}.wav"
                self._save_bytes(audio_bytes, seg_file)
                segment_files.append(seg_file)

            # 6) Concatenação
            logger.info(f"Combinando {len(segment_files)} segmentos em {combined_audio}")
            self._concatenar_segmentos(segment_files, combined_audio)

            # 7) Mux final
            logger.info(f"Realizando mux de áudio em vídeo → {output_path}")
            self.ffmpeg.mux_audio(str(video_path), combined_audio, str(output_path))

            logger.info(f"Execução concluída ✅ Saída final em: {output_path}")
            return output_path

        except Exception as exc:
            logger.error(f"Erro durante execução: {exc}")
            raise

        finally:
            try:
                shutil.rmtree(tmpdir)
            except Exception as cleanup_err:
                logger.warning(f"Falha ao limpar temporários {tmpdir}: {cleanup_err}")
