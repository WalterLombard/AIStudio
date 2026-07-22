"""
AIStudio FastMCP Publisher Engine Server

Generates search-optimized metadata, SEO keywords, chapters via gemma4:12b, 
and packages final video assets for export or channel distribution.

Author : AIStudio
"""

from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path
from typing import Any, Dict, List, Optional

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
    import ollama


mcp = FastMCP("Publisher Engine")

ROOT_DIR = Path(__file__).resolve().parent.parent


@mcp.tool()
def generate_metadata(
    topic: str,
    script_summary: str,
    target_platform: str = "YouTube",
) -> Dict[str, Any]:
    """
    Uses local gemma4:12b model to generate engaging titles, descriptions, 
    SEO keywords, and chapter outlines for the completed video.
    """
    sys.stderr.write(f"[Publisher Engine] Generating metadata for platform: {target_platform}...\n")

    prompt = f"""
    You are an expert video producer and YouTube SEO strategist.
    Generate publishing metadata for a video on the following topic and summary:
    
    Topic: {topic}
    Summary: {script_summary}
    
    Provide your output strictly as a valid JSON object with these keys:
    - "titles": [3 high-CTR title variations]
    - "description": "Engaging description (150-250 words) with call-to-actions"
    - "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"]
    - "hashtags": ["#tag1", "#tag2", "#tag3"]
    - "chapters": "00:00 - Introduction\\n01:30 - Main Concepts\\n04:15 - Deep Dive\\n07:00 - Summary"
    """

    with RedirectStdoutToStderr():
        response = ollama.chat(
            model="gemma4:12b",
            messages=[{"role": "user", "content": prompt}],
            format="json",
        )

    content = response.get("message", {}).get("content", "{}")
    
    try:
        metadata = json.loads(content)
    except json.JSONDecodeError:
        metadata = {
            "titles": [f"Deep Dive: {topic}"],
            "description": script_summary,
            "tags": [topic.lower()],
            "hashtags": [f"#{topic.replace(' ', '')}"],
            "chapters": "00:00 - Intro",
            "raw_output": content,
        }

    return metadata


@mcp.tool()
def package_export(
    project_name: str,
    video_path: str,
    thumbnail_path: Optional[str] = None,
    srt_path: Optional[str] = None,
    metadata_json: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Bundles all finalized video assets, subtitles, thumbnail, and metadata JSON 
    into a structured export directory ready for publishing.
    """
    sys.stderr.write(f"[Publisher Engine] Packaging final release for project '{project_name}'...\n")

    export_dir = ROOT_DIR / "output" / "exports" / project_name
    export_dir.mkdir(parents=True, exist_ok=True)

    copied_files: List[str] = []

    # Copy Video
    v_src = Path(video_path).resolve()
    if v_src.exists():
        v_dest = export_dir / f"{project_name}_final.mp4"
        v_dest.write_bytes(v_src.read_bytes())
        copied_files.append(v_dest.name)

    # Copy Thumbnail
    if thumbnail_path:
        t_src = Path(thumbnail_path).resolve()
        if t_src.exists():
            t_dest = export_dir / f"{project_name}_thumbnail.png"
            t_dest.write_bytes(t_src.read_bytes())
            copied_files.append(t_dest.name)

    # Copy Subtitles
    if srt_path:
        s_src = Path(srt_path).resolve()
        if s_src.exists():
            s_dest = export_dir / f"{project_name}_subtitles.srt"
            s_dest.write_bytes(s_src.read_bytes())
            copied_files.append(s_dest.name)

    # Save Metadata
    if metadata_json:
        m_dest = export_dir / "metadata.json"
        with open(m_dest, "w", encoding="utf-8") as f:
            json.dump(metadata_json, f, indent=4)
        copied_files.append(m_dest.name)

    sys.stderr.write(f"[Publisher Engine] Export package ready at: {export_dir}\n")
    return str(export_dir.resolve())


if __name__ == "__main__":
    mcp.run()