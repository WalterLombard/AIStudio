"""
AIStudio FastMCP Subtitle Engine Server

Generates time-synced SRT/VTT subtitle files and word-level timing metadata 
from generated narration audio using Faster-Whisper.

Author : AIStudio
"""

from __future__ import annotations

import json
import os
import sys
import warnings
from pathlib import Path
from typing import Any, Dict, List

from fastmcp import FastMCP

class RedirectStdoutToStderr:
    """Redirects stdout to stderr to protect FastMCP JSON-RPC communication."""

    def __enter__(self) -> None:
        self._original_stdout = sys.stdout
        sys.stdout = sys.stderr

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        sys.stdout = self._original_stdout


# Suppress library noise on import
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

with RedirectStdoutToStderr():
    from faster_whisper import WhisperModel


mcp = FastMCP("Subtitle Engine")
WHISPER_MODEL: WhisperModel | None = None

ROOT_DIR = Path(__file__).resolve().parent.parent


def _format_timestamp(seconds: float) -> str:
    """Formats float seconds into SRT timestamp format: HH:MM:SS,mmm"""
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"


def _get_whisper_model() -> WhisperModel:
    """Lazy-loads the Whisper transcription model onto CPU/CUDA."""
    global WHISPER_MODEL
    if WHISPER_MODEL is None:
        device = "cuda" if os.environ.get("USE_CUDA", "1") == "1" else "cpu"
        compute_type = "float16" if device == "cuda" else "int8"
        
        # Uses small, high-speed model for rapid alignment
        WHISPER_MODEL = WhisperModel(
            "small.en",
            device=device,
            compute_type=compute_type,
            download_root=str(ROOT_DIR / "local_models" / "whisper"),
        )
    return WHISPER_MODEL


@mcp.tool()
def generate_subtitles(
    audio_path: str,
    scene_idx: int = 0,
    output_dir: str | None = None,
) -> str:
    """
    Transcribes an audio narration file and exports an SRT subtitle file 
    along with JSON word-level alignment metadata.
    """
    sys.stderr.write(f"[Subtitle Engine] Transcribing narration for scene {scene_idx}...\n")

    audio_file = Path(audio_path).resolve()
    if not audio_file.exists():
        raise FileNotFoundError(f"Audio file not found for transcription: {audio_path}")

    if output_dir:
        target_dir = Path(output_dir)
    else:
        target_dir = ROOT_DIR / "output" / "subtitles"

    target_dir.mkdir(parents=True, exist_ok=True)
    srt_output_path = target_dir / f"scene_{scene_idx}.srt"
    json_output_path = target_dir / f"scene_{scene_idx}_words.json"

    with RedirectStdoutToStderr():
        model = _get_whisper_model()
        segments, _ = model.transcribe(
            str(audio_file),
            beam_size=5,
            word_timestamps=True,
            language="en",
        )

        srt_entries: List[str] = []
        word_metadata: List[Dict[str, Any]] = []
        entry_idx = 1

        for segment in segments:
            start_str = _format_timestamp(segment.start)
            end_str = _format_timestamp(segment.end)
            text = segment.text.strip()

            srt_entries.append(f"{entry_idx}\n{start_str} --> {end_str}\n{text}\n")
            entry_idx += 1

            if segment.words:
                for word_info in segment.words:
                    word_metadata.append({
                        "word": word_info.word.strip(),
                        "start": round(word_info.start, 3),
                        "end": round(word_info.end, 3),
                        "probability": round(word_info.probability, 3),
                    })

        # Save SRT file
        with open(srt_output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(srt_entries))

        # Save JSON word timing data (for animated word-by-word captions in MoviePy/FFmpeg)
        with open(json_output_path, "w", encoding="utf-8") as f:
            json.dump(word_metadata, f, indent=4)

    sys.stderr.write(f"[Subtitle Engine] SRT generated: {srt_output_path}\n")
    return str(srt_output_path.resolve())


if __name__ == "__main__":
    mcp.run()