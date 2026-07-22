"""
AIStudio FastMCP Video Compiler Server

Stitches audio and visual tracks using MoviePy with dynamic camera motion
(Ken Burns pan/zoom effects) and crossfade transitions.

Author : AIStudio
"""

from __future__ import annotations

import json
import os
import sys
import warnings
from pathlib import Path
from typing import List, Any

from fastmcp import FastMCP

# Suppress library warnings on start
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# Ensure FFmpeg binary path is linked if imageio_ffmpeg is installed
try:
    import imageio_ffmpeg
    os.environ["IMAGEIO_FFMPEG_EXE"] = imageio_ffmpeg.get_ffmpeg_exe()
except ImportError:
    pass

# MoviePy v1 / v2 Compatibility Layer
try:
    from moviepy import AudioFileClip, VideoFileClip, ImageClip, concatenate_videoclips
    from moviepy.video.fx import CrossFadeIn
    def apply_fx(clip: Any, effect: Any, *args: Any, **kwargs: Any) -> Any:
        return clip.with_effects([effect(*args, **kwargs)])
except ImportError:
    from moviepy.editor import AudioFileClip, VideoFileClip, ImageClip, concatenate_videoclips
    from moviepy.video.fx.all import CrossFadeIn
    def apply_fx(clip: Any, effect: Any, *args: Any, **kwargs: Any) -> Any:
        return clip.fx(effect, *args, **kwargs)


mcp = FastMCP("Compiler Engine")

# Base directory aligned with AIStudio workspace root
ROOT_DIR = Path(__file__).resolve().parent.parent


def _apply_dynamic_motion(clip: Any, idx: int) -> Any:
    """Applies subtle zoom/pan motion patterns (Ken Burns effect) across scene clips."""
    duration = clip.duration
    pattern = idx % 4

    # Helper functions for cross-version compatibility
    def set_res(c: Any, factor_fn: Any) -> Any:
        if hasattr(c, "resized"):
            return c.resized(factor_fn)
        return c.resize(factor_fn)

    def set_pos(c: Any, pos_fn: Any) -> Any:
        if hasattr(c, "with_position"):
            return c.with_position(pos_fn)
        return c.set_position(pos_fn)

    try:
        if pattern == 0:
            # Zoom In
            return set_res(clip, lambda t: 1.0 + 0.12 * (t / duration))
        elif pattern == 1:
            # Zoom Out
            return set_res(clip, lambda t: 1.12 - 0.12 * (t / duration))
        elif pattern == 2:
            # Pan Right
            clip_scaled = set_res(clip, 1.15)
            return set_pos(clip_scaled, lambda t: (int(-40 + (40 * (t / duration))), 'center'))
        else:
            # Pan Left
            clip_scaled = set_res(clip, 1.15)
            return set_pos(clip_scaled, lambda t: (int(40 - (40 * (t / duration))), 'center'))
    except Exception as ex:
        sys.stderr.write(f"[Compiler Engine Warning] Motion pattern {pattern} failed: {ex}. Reverting to static clip.\n")
        return clip


@mcp.tool()
def assemble_final_video(scenes_data_json: str, output_path: str = "") -> str:
    """
    Stitches audio and visual tracks together with seamless crossfade transitions 
    and dynamic camera pan/zoom motion.
    
    Parameters
    ----------
    scenes_data_json : str
        JSON array containing scene objects: [{"visual": "...", "audio": "..."}, ...]
    output_path : str, optional
        Target file path for the compiled MP4. Defaults to output/video/final_output.mp4.
    """
    sys.stderr.write("[Compiler Tool] Starting compilation with dynamic camera motion...\n")

    if not output_path:
        target_dir = ROOT_DIR / "output" / "video"
        target_dir.mkdir(parents=True, exist_ok=True)
        final_output_file = target_dir / "final_output.mp4"
    else:
        final_output_file = Path(output_path)
        final_output_file.parent.mkdir(parents=True, exist_ok=True)

    scenes_data = json.loads(scenes_data_json)
    clips: List[Any] = []
    open_audio_clips: List[Any] = []
    transition_duration = 0.8

    try:
        for idx, scene in enumerate(scenes_data):
            audio_path = str(Path(scene["audio"]).resolve())
            audio = AudioFileClip(audio_path)
            open_audio_clips.append(audio)

            visual_path = str(Path(scene["visual"]).resolve())
            if visual_path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                clip = VideoFileClip(visual_path)
            else:
                clip = ImageClip(visual_path)

            # Bind timeline audio
            if hasattr(clip, "with_audio"):
                final = clip.with_duration(audio.duration).with_audio(audio)
            else:
                final = clip.set_duration(audio.duration).set_audio(audio)

            # Apply motion modulation (Ken Burns effect)
            final = _apply_dynamic_motion(final, idx)

            # Apply transition crossfades
            if idx > 0:
                final = apply_fx(final, CrossFadeIn, transition_duration)

            clips.append(final)

        # Concatenate and render final output
        final_video = concatenate_videoclips(clips, method="compose", padding=-transition_duration)
        
        final_video.write_videofile(
            str(final_output_file.resolve()),
            codec="libx264",
            audio_codec="aac",
            temp_audiofile="temp-audio.m4a",
            remove_temp=True,
            threads=4,
        )

        final_video.close()

    finally:
        # Prevent file lock leaks on Windows
        for audio in open_audio_clips:
            try:
                audio.close()
            except Exception:
                pass

        for clip in clips:
            try:
                clip.close()
            except Exception:
                pass

    return str(final_output_file.resolve())


if __name__ == "__main__":
    mcp.run()