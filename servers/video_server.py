"""
AIStudio FastMCP Video Engine Server

Provides VRAM-managed generation of static base images via SDXL-Lightning 
and cinematic motion clips via Stable Video Diffusion (SVD).

Author : AIStudio
"""

from __future__ import annotations

import gc
import os
import sys
import warnings
from pathlib import Path

from fastmcp import FastMCP
import torch
from diffusers import (
    EulerDiscreteScheduler,
    StableDiffusionXLPipeline,
    StableVideoDiffusionPipeline,
    UNet2DConditionModel,
)
from diffusers.utils import export_to_video, load_image


class RedirectStdoutToStderr:
    """Redirects stdout to stderr to protect FastMCP JSON-RPC communication."""

    def __enter__(self) -> None:
        self._original_stdout = sys.stdout
        sys.stdout = sys.stderr

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        sys.stdout = self._original_stdout


# Suppress noisy library warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

mcp = FastMCP("Video Engine")
SDXL_PIPE: StableDiffusionXLPipeline | None = None
SVD_PIPE: StableVideoDiffusionPipeline | None = None

ROOT_DIR = Path(__file__).resolve().parent.parent


def flush_vram() -> None:
    """Aggressively flushes system garbage collection and CUDA cache to prevent OOM errors."""
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


@mcp.tool()
def generate_base_image(
    prompt: str,
    scene_idx: int,
    video_type: str = "long",
    output_dir: str | None = None,
) -> str:
    """Renders a high-quality static base image using SDXL Lightning (4-step)."""
    global SDXL_PIPE, SVD_PIPE

    if output_dir:
        target_dir = Path(output_dir)
    else:
        target_dir = ROOT_DIR / "output" / "images"

    target_dir.mkdir(parents=True, exist_ok=True)
    img_path = target_dir / f"scene_{scene_idx}.png"

    width, height = (1024, 576) if video_type == "long" else (576, 1024)

    # Unload SVD pipeline to reclaim VRAM
    if SVD_PIPE is not None:
        del SVD_PIPE
        SVD_PIPE = None
        flush_vram()

    print(
        f"[Video Engine] Rendering SDXL-Lightning image for scene {scene_idx}...",
        file=sys.stderr,
    )

    with RedirectStdoutToStderr():
        if SDXL_PIPE is None:
            base_model = "stabilityai/stable-diffusion-xl-base-1.0"
            repo = "ByteDance/SDXL-Lightning"
            ckpt = "sdxl_lightning_4step_unet.safetensors"

            from huggingface_hub import hf_hub_download
            from safetensors.torch import load_file

            unet = UNet2DConditionModel.from_pretrained(
                base_model,
                subfolder="unet",
                torch_dtype=torch.float16,
            ).to("cuda")
            
            unet.load_state_dict(load_file(hf_hub_download(repo, ckpt), device="cuda"))

            SDXL_PIPE = StableDiffusionXLPipeline.from_pretrained(
                base_model,
                unet=unet,
                torch_dtype=torch.float16,
                variant="fp16",
            ).to("cuda")

            SDXL_PIPE.scheduler = EulerDiscreteScheduler.from_config(
                SDXL_PIPE.scheduler.config,
                timestep_spacing="trailing",
            )

        image = SDXL_PIPE(
            prompt,
            num_inference_steps=4,
            guidance_scale=0.0,
            width=width,
            height=height,
        ).images[0]

        image.save(str(img_path))

    return str(img_path.resolve())


@mcp.tool()
def animate_scene_image(
    image_path: str,
    scene_idx: int,
    video_type: str = "long",
    output_dir: str | None = None,
) -> str:
    """Generates motion frames from a static image file using Stable Video Diffusion (SVD)."""
    global SDXL_PIPE, SVD_PIPE

    if output_dir:
        target_dir = Path(output_dir)
    else:
        target_dir = ROOT_DIR / "output" / "video"

    target_dir.mkdir(parents=True, exist_ok=True)
    video_path = target_dir / f"scene_{scene_idx}.mp4"

    width, height = (1024, 576) if video_type == "long" else (576, 1024)

    # Unload SDXL pipeline to reclaim VRAM
    if SDXL_PIPE is not None:
        del SDXL_PIPE
        SDXL_PIPE = None
        flush_vram()

    print(
        f"[Video Engine] Animating scene {scene_idx} via SVD...",
        file=sys.stderr,
    )

    with RedirectStdoutToStderr():
        if SVD_PIPE is None:
            SVD_PIPE = StableVideoDiffusionPipeline.from_pretrained(
                "stabilityai/stable-video-diffusion-img2vid-xt",
                torch_dtype=torch.float16,
                variant="fp16",
            ).to("cuda")
            SVD_PIPE.enable_model_cpu_offload()

        image = load_image(image_path).resize((width, height))
        generator = torch.manual_seed(42)

        frames = SVD_PIPE(
            image,
            decode_chunk_size=8,
            generator=generator,
            motion_bucket_id=127,
            noise_aug_strength=0.1,
        ).frames[0]

        export_to_video(frames, str(video_path), fps=7)

    return str(video_path.resolve())


if __name__ == "__main__":
    mcp.run()