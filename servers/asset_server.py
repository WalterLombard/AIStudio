"""
AIStudio FastMCP Asset Manager Engine Server

Manages local asset registries, image upscaling (Super-Resolution), 
and automated YouTube thumbnail banner layout creation using Pillow.

Author : AIStudio
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import warnings
from pathlib import Path
from typing import Any, Dict, Optional

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
    from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont


mcp = FastMCP("Asset Engine")

ROOT_DIR = Path(__file__).resolve().parent.parent
REGISTRY_PATH = ROOT_DIR / "registry" / "assets.json"


def _ensure_registry() -> Dict[str, Any]:
    """Ensures the asset registry file exists and returns its contents."""
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not REGISTRY_PATH.exists():
        initial_data = {"images": {}, "videos": {}, "audio": {}}
        with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
            json.dump(initial_data, f, indent=4)
        return initial_data

    try:
        with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"images": {}, "videos": {}, "audio": {}}


def _save_registry(data: Dict[str, Any]) -> None:
    """Saves updated data back to the registry file."""
    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


@mcp.tool()
def register_asset(
    file_path: str,
    asset_type: str = "images",
    tags: Optional[str] = None,
) -> str:
    """
    Computes an SHA256 checksum for a file and registers it in local inventory 
    to track reuse across video projects.
    """
    path = Path(file_path).resolve()
    if not path.exists():
        raise FileNotFoundError(f"Cannot register missing asset: {file_path}")

    sys.stderr.write(f"[Asset Engine] Registering {path.name} into inventory...\n")

    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    file_hash = hasher.hexdigest()

    registry = _ensure_registry()
    category = registry.get(asset_type, {})

    category[file_hash] = {
        "file_name": path.name,
        "full_path": str(path),
        "file_size_bytes": path.stat().st_size,
        "tags": [t.strip() for t in tags.split(",")] if tags else [],
    }

    registry[asset_type] = category
    _save_registry(registry)

    return f"Asset registered successfully. SHA256: {file_hash[:12]}..."


@mcp.tool()
def upscale_image(
    image_path: str,
    scale_factor: int = 2,
    output_filename: Optional[str] = None,
    output_dir: Optional[str] = None,
) -> str:
    """
    Upscales a rendered base image using Lanczos high-fidelity filtering 
    and subtle unsharp masking for enhanced clarity.
    """
    input_file = Path(image_path).resolve()
    if not input_file.exists():
        raise FileNotFoundError(f"Input image not found: {image_path}")

    sys.stderr.write(f"[Asset Engine] Upscaling image x{scale_factor}: {input_file.name}...\n")

    if output_dir:
        target_dir = Path(output_dir)
    else:
        target_dir = ROOT_DIR / "output" / "images" / "upscaled"

    target_dir.mkdir(parents=True, exist_ok=True)
    
    out_name = output_filename or f"upscaled_{input_file.stem}.png"
    output_path = target_dir / out_name

    with RedirectStdoutToStderr():
        img = Image.open(input_file).convert("RGB")
        new_width = img.width * scale_factor
        new_height = img.height * scale_factor

        # Perform high-quality Lanczos resampling
        upscaled = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Apply mild sharpening pass to boost fine detail edge contrast
        sharpened = upscaled.filter(ImageFilter.UnsharpMask(radius=1.5, percent=120, threshold=3))
        sharpened.save(str(output_path), quality=95)

    sys.stderr.write(f"[Asset Engine] Upscaled image saved to: {output_path}\n")
    return str(output_path.resolve())


@mcp.tool()
def create_thumbnail(
    base_image_path: str,
    headline_text: str,
    sub_text: Optional[str] = None,
    video_type: str = "long",
    output_filename: str = "thumbnail.png",
    output_dir: Optional[str] = None,
) -> str:
    """
    Composes a video thumbnail with gradient darkeners, contrast enhancements, 
    and bold typography layout.
    """
    input_file = Path(base_image_path).resolve()
    if not input_file.exists():
        raise FileNotFoundError(f"Base thumbnail image not found: {base_image_path}")

    sys.stderr.write("[Asset Engine] Generating video thumbnail...\n")

    if output_dir:
        target_dir = Path(output_dir)
    else:
        target_dir = ROOT_DIR / "output" / "thumbnails"

    target_dir.mkdir(parents=True, exist_ok=True)
    thumbnail_path = target_dir / output_filename

    canvas_size = (1280, 720) if video_type == "long" else (1080, 1920)

    with RedirectStdoutToStderr():
        img = Image.open(input_file).convert("RGB")
        img = img.resize(canvas_size, Image.Resampling.LANCZOS)

        # Boost saturation and contrast slightly for dynamic thumbnail pop
        enhancer_sat = ImageEnhance.Color(img)
        img = enhancer_sat.enhance(1.25)
        enhancer_con = ImageEnhance.Contrast(img)
        img = enhancer_con.enhance(1.15)

        draw = ImageDraw.Draw(img)

        # Draw a semi-transparent dark gradient overlay on the bottom third for text readability
        overlay = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        
        gradient_start_y = int(canvas_size[1] * 0.5)
        for y in range(gradient_start_y, canvas_size[1]):
            alpha = int(210 * ((y - gradient_start_y) / (canvas_size[1] - gradient_start_y)))
            overlay_draw.line([(0, y), (canvas_size[0], y)], fill=(0, 0, 0, alpha))

        img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
        draw = ImageDraw.Draw(img)

        # Load font (fallback to default if custom font not found)
        try:
            font_main = ImageFont.truetype("arialbd.ttf", 64 if video_type == "long" else 80)
            font_sub = ImageFont.truetype("arial.ttf", 36 if video_type == "long" else 48)
        except IOError:
            font_main = ImageFont.load_default()
            font_sub = ImageFont.load_default()

        # Render Main Headline with Text Shadow
        text_x = 60
        text_y = int(canvas_size[1] * 0.65)

        # Draw Shadow
        draw.text((text_x + 4, text_y + 4), headline_text.upper(), font=font_main, fill=(0, 0, 0))
        # Draw Main Yellow Text
        draw.text((text_x, text_y), headline_text.upper(), font=font_main, fill=(255, 220, 0))

        # Render Subtitle Text if provided
        if sub_text:
            sub_y = text_y + 80
            draw.text((text_x + 2, sub_y + 2), sub_text, font=font_sub, fill=(0, 0, 0))
            draw.text((text_x, sub_y), sub_text, font=font_sub, fill=(255, 255, 255))

        img.save(str(thumbnail_path), quality=95)

    sys.stderr.write(f"[Asset Engine] Thumbnail saved: {thumbnail_path}\n")
    return str(thumbnail_path.resolve())


if __name__ == "__main__":
    mcp.run()