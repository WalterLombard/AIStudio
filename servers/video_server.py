# C:\Projectsai\servers\video_server.py
import os
import sys
import warnings
import gc
import torch
from PIL import Image
from fastmcp import FastMCP
from diffusers import StableDiffusionXLPipeline, UNet2DConditionModel, EulerDiscreteScheduler, StableVideoDiffusionPipeline
from diffusers.utils import load_image, export_to_video

class RedirectStdoutToStderr:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = sys.stderr
    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = self._original_stdout

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

mcp = FastMCP("Video Engine")
SDXL_PIPE = None
SVD_PIPE = None
BASE_DIR = "C:\\Projectsai"

def flush_vram():
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

@mcp.tool()
def generate_base_image(prompt: str, scene_idx: int, video_type: str = "long") -> str:
    """Renders a high-quality, sharp static base image using SDXL Lightning."""
    global SDXL_PIPE, SVD_PIPE
    output_dir = os.path.join(BASE_DIR, "output", "images")
    os.makedirs(output_dir, exist_ok=True)
    img_path = os.path.join(output_dir, f"scene_{scene_idx}.png")
    width, height = (1024, 576) if video_type == "long" else (576, 1024)
    
    # Aggressively unload animation model to avoid OOM crashes
    if SVD_PIPE is not None:
        del SVD_PIPE
        SVD_PIPE = None
        flush_vram()

    with RedirectStdoutToStderr():
        if SDXL_PIPE is None:
            base_model = "stabilityai/stable-diffusion-xl-base-1.0"
            repo = "ByteDance/SDXL-Lightning"
            ckpt = "sdxl_lightning_4step_unet.safetensors"
            
            from huggingface_hub import hf_hub_download
            from safetensors.torch import load_file
            
            unet = UNet2DConditionModel.from_config(base_model, subfolder="unet").to("cuda", torch.float16)
            unet.load_state_dict(load_file(hf_hub_download(repo, ckpt), device="cuda"))
            
            SDXL_PIPE = StableDiffusionXLPipeline.from_pretrained(
                base_model, unet=unet, torch_dtype=torch.float16, variant="fp16"
            ).to("cuda")
            SDXL_PIPE.scheduler = EulerDiscreteScheduler.from_config(
                SDXL_PIPE.scheduler.config, timestep_spacing="trailing"
            )
            
        image = SDXL_PIPE(
            prompt, num_inference_steps=4, guidance_scale=0.0, width=width, height=height
        ).images[0]
        image.save(img_path)
        
    return os.path.abspath(img_path)

@mcp.tool()
def animate_scene_image(image_path: str, scene_idx: int, video_type: str = "long") -> str:
    """Generates motion frames from a static image file using SVD."""
    global SDXL_PIPE, SVD_PIPE
    output_dir = os.path.join(BASE_DIR, "output", "videos")
    os.makedirs(output_dir, exist_ok=True)
    video_path = os.path.join(output_dir, f"scene_{scene_idx}.mp4")
    width, height = (1024, 576) if video_type == "long" else (576, 1024)

    # Aggressively unload image generation model to free GPU allocation
    if SDXL_PIPE is not None:
        del SDXL_PIPE
        SDXL_PIPE = None
        flush_vram()

    with RedirectStdoutToStderr():
        if SVD_PIPE is None:
            SVD_PIPE = StableVideoDiffusionPipeline.from_pretrained(
                "stabilityai/stable-video-diffusion-img2vid-xt",
                torch_dtype=torch.float16,
                variant="fp16"
            ).to("cuda")
            SVD_PIPE.enable_model_cpu_offload()

        image = load_image(image_path).resize((width, height))
        generator = torch.manual_seed(42)
        frames = SVD_PIPE(
            image, decode_chunk_size=8, generator=generator, motion_bucket_id=127, noise_aug_strength=0.1
        ).frames[0]
        
        export_to_video(frames, video_path, fps=7)
        
    return os.path.abspath(video_path)

if __name__ == "__main__":
    mcp.run()