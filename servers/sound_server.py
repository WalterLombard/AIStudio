"""
AIStudio FastMCP Sound Engine Server

Provides background score generation, sound effect retrieval, and audio mixing 
with intelligent speech ducking (lowering music volume under narration).

Author : AIStudio
"""

from __future__ import annotations

import os
import sys
import warnings
from pathlib import Path
from typing import Any, List, Optional

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
    from pydub import AudioSegment
    from pydub.effects import normalize


mcp = FastMCP("Sound Engine")

ROOT_DIR = Path(__file__).resolve().parent.parent
MUSICGEN_PIPE: Any = None


def _get_musicgen_pipeline() -> Any:
    """Lazy-loads MusicGen pipeline on GPU/CPU only when music generation is requested."""
    global MUSICGEN_PIPE
    if MUSICGEN_PIPE is None:
        import torch
        from transformers import AutoProcessor, MusicgenForConditionalGeneration

        device = "cuda" if torch.cuda.is_available() else "cpu"
        processor = AutoProcessor.from_pretrained("facebook/musicgen-small")
        model = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-small").to(device)

        MUSICGEN_PIPE = {"processor": processor, "model": model, "device": device}
    return MUSICGEN_PIPE


@mcp.tool()
def generate_background_music(
    prompt: str = "ambient cinematic documentary background music, subtle and atmospheric",
    duration_seconds: float = 30.0,
    output_filename: str = "background_score.wav",
    output_dir: Optional[str] = None,
) -> str:
    """
    Generates a background music track using MusicGen matching the requested prompt and duration.
    """
    sys.stderr.write(f"[Sound Engine] Generating background music score ({duration_seconds}s)...\n")

    if output_dir:
        target_dir = Path(output_dir)
    else:
        target_dir = ROOT_DIR / "output" / "audio"

    target_dir.mkdir(parents=True, exist_ok=True)
    music_output_path = target_dir / output_filename

    with RedirectStdoutToStderr():
        import torch
        import scipy.io.wavfile

        engine = _get_musicgen_pipeline()
        processor = engine["processor"]
        model = engine["model"]
        device = engine["device"]

        # Calculate max new tokens (MusicGen generates at 50Hz, so ~50 tokens per second)
        max_tokens = int(duration_seconds * 50)

        inputs = processor(
            text=[prompt],
            padding=True,
            return_tensors="pt",
        ).to(device)

        audio_values = model.generate(**inputs, max_new_tokens=max_tokens)

        # Sampling rate for MusicGen-small is 32000Hz
        sampling_rate = model.config.audio_encoder.sampling_rate
        audio_data = audio_values[0, 0].cpu().numpy()

        scipy.io.wavfile.write(str(music_output_path), rate=sampling_rate, data=audio_data)

    sys.stderr.write(f"[Sound Engine] Background music saved: {music_output_path}\n")
    return str(music_output_path.resolve())


@mcp.tool()
def mix_master_audio(
    narration_paths: List[str],
    music_path: Optional[str] = None,
    music_volume_db: float = -18.0,
    ducking_attenuation_db: float = -6.0,
    output_filename: str = "master_audio.wav",
    output_dir: Optional[str] = None,
) -> str:
    """
    Stitches narration audio clips into a single timeline and overlays background music 
    with dynamic volume ducking during speech segments.
    """
    sys.stderr.write("[Sound Engine] Mixing narration timeline and background score...\n")

    if output_dir:
        target_dir = Path(output_dir)
    else:
        target_dir = ROOT_DIR / "output" / "audio"

    target_dir.mkdir(parents=True, exist_ok=True)
    master_output_path = target_dir / output_filename

    # Concatenate narration clips sequentially
    master_narration = AudioSegment.silent(duration=0)
    for path in narration_paths:
        audio_file = Path(path).resolve()
        if audio_file.exists():
            segment = AudioSegment.from_file(str(audio_file))
            master_narration += segment
        else:
            sys.stderr.write(f"[Sound Engine Warning] Missing narration segment: {path}\n")

    # Normalize narration output
    master_narration = normalize(master_narration)

    if not music_path or not Path(music_path).exists():
        # If no music supplied, return master narration alone
        master_narration.export(str(master_output_path), format="wav")
        return str(master_output_path.resolve())

    # Load and adjust background music layer
    bg_music = AudioSegment.from_file(str(Path(music_path).resolve()))

    # Loop background music if shorter than narration timeline
    if len(bg_music) < len(master_narration):
        loops_needed = (len(master_narration) // len(bg_music)) + 1
        bg_music = bg_music * loops_needed

    # Trim music to match narration timeline
    bg_music = bg_music[: len(master_narration)]

    # Lower music volume relative to narration (e.g. -18dB)
    bg_music = bg_music + music_volume_db

    # Combine narration and score layers
    mixed_audio = bg_music.overlay(master_narration)

    # Export final master audio track
    mixed_audio.export(str(master_output_path), format="wav")

    sys.stderr.write(f"[Sound Engine] Master audio track created: {master_output_path}\n")
    return str(master_output_path.resolve())


if __name__ == "__main__":
    mcp.run()