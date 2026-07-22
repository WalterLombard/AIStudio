"""
AIStudio FastMCP Audio Engine Server

Provides high-quality offline TTS audio segment generation using Kokoro ONNX.

Author : AIStudio
"""

from __future__ import annotations

import os
import sys
import warnings
from pathlib import Path

from fastmcp import FastMCP


class RedirectStdoutToStderr:
    """Redirects stdout to stderr to prevent corrupting FastMCP JSON-RPC stdout communication."""

    def __enter__(self) -> None:
        self._original_stdout = sys.stdout
        sys.stdout = sys.stderr

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        sys.stdout = self._original_stdout


# Suppress library warnings on start
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

with RedirectStdoutToStderr():
    from kokoro_onnx import Kokoro
    import soundfile as sf


mcp = FastMCP("Audio Engine")
KOKORO_MODEL: Kokoro | None = None

# Base path aligned with AIStudio project root
ROOT_DIR = Path(__file__).resolve().parent.parent


def normalize_text_for_tts(text: str) -> str:
    """Normalizes numerals, abbreviations, and specific terms for optimal TTS pronunciation."""
    replacements = {
        "2026": "twenty twenty-six",
        "1st": "first",
        "2nd": "second",
        "3rd": "third",
        "&": "and",
        "%": " percent",
        "+": " plus ",
        "zodiac": "zo-di-ak",
    }
    cleaned = text
    for target, replacement in replacements.items():
        cleaned = cleaned.replace(target, replacement)
    return cleaned


@mcp.tool()
def generate_audio_segment(
    text: str,
    scene_idx: int,
    voice: str = "af_heart",
    output_dir: str | None = None,
) -> str:
    """Converts a single scene's narration text into a local WAV audio file with slow, clear pacing."""
    global KOKORO_MODEL

    # Route output to provided directory or default AIStudio output path
    if output_dir:
        target_dir = Path(output_dir)
    else:
        target_dir = ROOT_DIR / "output" / "audio"

    target_dir.mkdir(parents=True, exist_ok=True)
    file_path = target_dir / f"scene_{scene_idx}.wav"

    print(
        f"[Audio Engine] Generating voiceover ({voice}) for scene {scene_idx}...",
        file=sys.stderr,
    )

    normalized_text = normalize_text_for_tts(text)

    with RedirectStdoutToStderr():
        if KOKORO_MODEL is None:
            # Model weights located under local_models directory
            model_path = ROOT_DIR / "local_models" / "kokoro-v1.0.fp16.onnx"
            voices_path = ROOT_DIR / "local_models" / "voices-v1.0.bin"

            # Fallback check if models exist at root
            if not model_path.exists():
                model_path = ROOT_DIR / "kokoro-v1.0.fp16.onnx"
                voices_path = ROOT_DIR / "voices-v1.0.bin"

            KOKORO_MODEL = Kokoro(
                model_path=str(model_path),
                voices_path=str(voices_path),
            )

        samples, sample_rate = KOKORO_MODEL.create(
            text=normalized_text,
            voice=voice,
            speed=0.9,
        )
        sf.write(str(file_path), samples, sample_rate)

    return str(file_path.resolve())


if __name__ == "__main__":
    mcp.run()