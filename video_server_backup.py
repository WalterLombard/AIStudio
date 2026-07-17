import os
import sys
import time
import warnings
import logging

# ==========================================
# STDOUT PROTECTOR & SILENCER
# ==========================================
# This prevents external libraries from printing banners or logs to stdout,
# which immediately corrupts the JSON-RPC pipe and crashes the MCP connection.
class RedirectStdoutToStderr:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = sys.stderr

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = self._original_stdout

# Silence standard alerts
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# Wrap all third-party imports to keep stdout pristine
with RedirectStdoutToStderr():
    import torch
    import httpx
    from fastmcp import FastMCP
    from PIL import Image
    
    # Lazy/Quiet imports for heavy dependencies
    logging.getLogger("diffusers").setLevel(logging.ERROR)
    logging.getLogger("transformers").setLevel(logging.ERROR)

# Initialize MCP Server
mcp = FastMCP("Auto Video Agent Engine")

# Ensure target directories exist locally
os.makedirs("./output/images", exist_ok=True)
os.makedirs("./output/audio", exist_ok=True)
os.makedirs("./output/videos", exist_ok=True)

# Global Model Cache to prevent reloading models on every scene
MODEL_CACHE = {
    "sd_pipe": None,
    "svd_pipe": None,
    "kokoro": None,
}

def clear_vram(force_all=False):
    """Flushes GPU VRAM. If force_all is True, all cached pipelines are purged."""
    global MODEL_CACHE
    
    if force_all:
        if MODEL_CACHE["sd_pipe"] is not None:
            print("[System] Purging SDXL Pipeline from GPU memory...", file=sys.stderr)
            del MODEL_CACHE["sd_pipe"]
            MODEL_CACHE["sd_pipe"] = None
        if MODEL_CACHE["svd_pipe"] is not None:
            print("[System] Purging SVD Pipeline from GPU memory...", file=sys.stderr)
            del MODEL_CACHE["svd_pipe"]
            MODEL_CACHE["svd_pipe"] = None
            
    torch.cuda.empty_cache()
    try:
        with httpx.Client() as client:
            client.post(
                "http://localhost:11434/api/generate", 
                json={"model": "gemma4-video-agent", "keep_alive": 0}, 
                timeout=2.0
            )
        time.sleep(1)
    except Exception as e:
        print(f"[System Warning] Could not offload Ollama: {e}", file=sys.stderr)


@mcp.tool()
def generate_audio_segment(text: str, scene_idx: int, voice: str = "af_heart") -> str:
    """Converts a single scene's narration text into a local WAV audio file with slow, clear pacing."""
    with RedirectStdoutToStderr():
        from kokoro_onnx import Kokoro
        import soundfile as sf
    
    path = f"./output/audio/scene_{scene_idx}.wav"
    print(f"[MCP Audio Engine] Generating voiceover ({voice}) for scene {scene_idx}...", file=sys.stderr)
    
    # Clean up dates, symbols, and special numbers for natural pronunciation
    normalized_text = normalize_text_for_tts(text)
    
    if MODEL_CACHE["kokoro"] is None:
        MODEL_CACHE["kokoro"] = Kokoro("kokoro-v1.0.fp16.onnx", "voices-v1.0.bin")
        
    samples, sample_rate = MODEL_CACHE["kokoro"].create(normalized_text, voice=voice, speed=0.9)
    sf.write(path, samples, sample_rate)
    
    return os.path.abspath(path)


def normalize_text_for_tts(text: str) -> str:
    """Cleans up common formatting patterns so the TTS engine pronounces them perfectly."""
    replacements = {
        "2026": "twenty twenty-six",
        "1st": "first",
        "2nd": "second",
        "3rd": "third",
        "&": "and",
        "%": " percent",
        "+": " plus ",
        "zodiac": "zo-di-ak"
    }
    cleaned = text
    for target, replacement in replacements.items():
        cleaned = cleaned.replace(target, replacement)
    return cleaned


@mcp.tool()
def generate_base_image(prompt: str, scene_idx: int, video_type: str = "long") -> str:
    """Renders a high-quality, sharp static base image."""
    with RedirectStdoutToStderr():
        from diffusers import StableDiffusionXLPipeline, UNet2DConditionModel, EulerDiscreteScheduler
        from huggingface_hub import hf_hub_download
        from safetensors.torch import load_file
    
    img_path = f"./output/images/scene_{scene_idx}.png"
    width, height = (1024, 576) if video_type == "long" else (576, 1024)
    
    global MODEL_CACHE
    
    if MODEL_CACHE["svd_pipe"] is not None:
        print("[System] Temporarily offloading SVD Pipeline to free VRAM for SDXL...", file=sys.stderr)
        del MODEL_CACHE["svd_pipe"]
        MODEL_CACHE["svd_pipe"] = None
        torch.cuda.empty_cache()

    if MODEL_CACHE["sd_pipe"] is None:
        print(f"[MCP Visual Engine] Initializing SDXL Lightning Pipeline on GPU...", file=sys.stderr)
        base_model = "stabilityai/stable-diffusion-xl-base-1.0"
        
        unet = UNet2DConditionModel.from_config(base_model, subfolder="unet").to("cuda", torch.float16)
        unet.load_state_dict(load_file(hf_hub_download("ByteDance/SDXL-Lightning", "sdxl_lightning_4step_unet.safetensors"), device="cuda"))
        
        sd_pipe = StableDiffusionXLPipeline.from_pretrained(
            base_model, unet=unet, torch_dtype=torch.float16, variant="fp16"
        ).to("cuda")
        
        sd_pipe.scheduler = EulerDiscreteScheduler.from_config(sd_pipe.scheduler.config, timestep_spacing="trailing")
        sd_pipe.enable_attention_slicing()
        
        MODEL_CACHE["sd_pipe"] = sd_pipe

    print(f"[MCP Visual Engine] Rendering sharp {video_type} frame for scene {scene_idx}...", file=sys.stderr)
    
    image = MODEL_CACHE["sd_pipe"](
        prompt=prompt, 
        num_inference_steps=4, 
        guidance_scale=1.2, 
        width=width, 
        height=height
    ).images[0]
    
    image.save(img_path)
    return os.path.abspath(img_path)


@mcp.tool()
def animate_scene_image(image_path: str, scene_idx: int, video_type: str = "long") -> str:
    """Animates a static PNG image using SVD, scaling with Lanczos and exporting at max codec quality."""
    with RedirectStdoutToStderr():
        from diffusers import StableVideoDiffusionPipeline
        from diffusers.utils import load_image, export_to_video
    
    global MODEL_CACHE
    
    if MODEL_CACHE["sd_pipe"] is not None:
        print("[System] Offloading SDXL Pipeline from memory to accommodate SVD cache...", file=sys.stderr)
        del MODEL_CACHE["sd_pipe"]
        MODEL_CACHE["sd_pipe"] = None
        torch.cuda.empty_cache()
    
    output_video_path = f"./output/videos/motion_scene_{scene_idx}.mp4"
    
    resize_dims = (1024, 576) if video_type == "long" else (576, 1024)
    
    # Use Lanczos resampling to prevent resolution/pixel degradation before SVD processing
    base_image = load_image(image_path).resize(resize_dims, Image.Resampling.LANCZOS)
    
    if MODEL_CACHE["svd_pipe"] is None:
        print(f"[MCP Motion Engine] Initializing SVD Pipeline on GPU...", file=sys.stderr)
        
        video_pipe = StableVideoDiffusionPipeline.from_pretrained(
            "stabilityai/stable-video-diffusion-img2vid", 
            torch_dtype=torch.float16, 
            variant="fp16"
        ).to("cuda")
        
        video_pipe.enable_attention_slicing()
        video_pipe.enable_model_cpu_offload()
        video_pipe.unet.enable_forward_chunking()  
        
        MODEL_CACHE["svd_pipe"] = video_pipe
    else:
        print(f"[MCP Motion Engine] Reusing cached SVD Pipeline for Scene {scene_idx}...", file=sys.stderr)
    
    generator = torch.manual_seed(42)
    
    with torch.amp.autocast("cuda"):
        frames = MODEL_CACHE["svd_pipe"](
            base_image, 
            decode_chunk_size=1,            
            generator=generator, 
            num_frames=14,                  
            num_inference_steps=20,          
            motion_bucket_id=127,
            noise_aug_strength=0.02
        ).frames[0]
    
    # Set export quality to 10.0 (maximum lossless bitrate) to stop compression artifact blur
    export_to_video(frames, output_video_path, fps=6, quality=10.0)
    
    return os.path.abspath(output_video_path)


@mcp.tool()
def assemble_final_video(scenes_data_json: str, output_path: str = "./output/final_output.mp4") -> str:
    """Stitches audio and visual tracks sequentially. 
    Applies a seamless cross-dissolve transition between scenes so that the motion
    of one scene smoothly melts into the next.
    """
    with RedirectStdoutToStderr():
        import json
        import moviepy.video.fx.all as vfx
        # Safe import wrapper to support MoviePy v1.x and v2.x environments seamlessly
        try:
            from moviepy.editor import AudioFileClip, VideoFileClip, ImageClip, concatenate_videoclips
        except ImportError:
            from moviepy import AudioFileClip, VideoFileClip, ImageClip, concatenate_videoclips
    
    # Completely flush all ML models from VRAM for video assembly
    clear_vram(force_all=True)
    
    print("[MCP Compiler Engine] Stitching timeline with dynamic camera extensions and cross-dissolves...", file=sys.stderr)
    scenes_data = json.loads(scenes_data_json)
    clips = []
    
    # Helper function to guarantee even dimensions (width/height divisible by 2)
    def make_even(clip):
        w, h = clip.size
        new_w = w if w % 2 == 0 else w - 1
        new_h = h if h % 2 == 0 else h - 1
        if (new_w, new_h) != (w, h):
            return clip.resized((new_w, new_h))
        return clip

    transition_duration = 0.8  # Overlap window (in seconds) where Scene A melts into Scene B

    for idx, scene in enumerate(scenes_data):
        with RedirectStdoutToStderr():
            audio_clip = AudioFileClip(scene["audio"])
            duration = audio_clip.duration
        
        if scene["is_video"]:
            with RedirectStdoutToStderr():
                visual_clip = VideoFileClip(scene["visual"])
            
            # If the SVD motion clip is shorter than the audio narration
            if visual_clip.duration < duration:
                extra_duration = duration - visual_clip.duration
                
                # Grab the very last frame of the SVD clip
                last_frame_path = f"./output/images/temp_freeze_{idx}.png"
                with RedirectStdoutToStderr():
                    visual_clip.save_frame(last_frame_path, t=visual_clip.duration - 0.05)
                    extension_clip = ImageClip(last_frame_path).with_duration(extra_duration)
                
                # Apply a continuous cinematic camera movement to the extension clip
                camera_style = idx % 4
                if camera_style == 0:
                    print(f"Scene {idx}: Extending SVD clip with slow Zoom-In", file=sys.stderr)
                    extension_clip = extension_clip.resized(lambda t: 1.0 + 0.05 * (t / extra_duration))
                elif camera_style == 1:
                    print(f"Scene {idx}: Extending SVD clip with slow Zoom-Out", file=sys.stderr)
                    extension_clip = extension_clip.resized(lambda t: 1.05 - 0.05 * (t / extra_duration))
                elif camera_style == 2:
                    print(f"Scene {idx}: Extending SVD clip with slow Pan-Right", file=sys.stderr)
                    extension_clip = extension_clip.with_position(lambda t: (int(-15 + (15 * (t / extra_duration))), 'center'))
                    extension_clip = extension_clip.resized(1.05)
                else:
                    print(f"Scene {idx}: Extending SVD clip with slow Pan-Left", file=sys.stderr)
                    extension_clip = extension_clip.with_position(lambda t: (int(0 - (15 * (t / extra_duration))), 'center'))
                    extension_clip = extension_clip.resized(1.05)
                
                # Concatenate the natural SVD movement with the cinematic camera slide
                with RedirectStdoutToStderr():
                    visual_clip = concatenate_videoclips([visual_clip, extension_clip], method="compose")
                
            final_clip = visual_clip.with_audio(audio_clip)
        else:
            # Fallback for static image slides
            pattern = idx % 4
            with RedirectStdoutToStderr():
                img_clip = ImageClip(scene["visual"]).with_duration(duration)
            
            if pattern == 0:
                print(f"Scene {idx}: Applying Dynamic Zoom-In", file=sys.stderr)
                visual_clip = img_clip.resized(lambda t: 1.0 + 0.07 * (t / duration))
            elif pattern == 1:
                print(f"Scene {idx}: Applying Dynamic Zoom-Out", file=sys.stderr)
                visual_clip = img_clip.resized(lambda t: 1.07 - 0.07 * (t / duration))
            elif pattern == 2:
                print(f"Scene {idx}: Applying Pan-Right", file=sys.stderr)
                visual_clip = img_clip.with_position(lambda t: (int(-20 + (20 * (t / duration))), 'center'))
                visual_clip = visual_clip.resized(1.05)
            else:
                print(f"Scene {idx}: Applying Pan-Left", file=sys.stderr)
                visual_clip = img_clip.with_position(lambda t: (int(0 - (20 * (t / duration))), 'center'))
                visual_clip = visual_clip.resized(1.05)
            
            final_clip = visual_clip.with_audio(audio_clip)
            
        # Ensure correct scale for FFMPEG
        final_clip = make_even(final_clip)
        
        # Apply the crossfade transition setup to blend clips
        if idx > 0:
            final_clip = final_clip.with_effects([vfx.CrossFadeIn(transition_duration)])
            
        clips.append(final_clip)
        
    # Stitch video sequences with overlapping padding to create the crossfade melt
    with RedirectStdoutToStderr():
        final_video = concatenate_videoclips(clips, method="compose", padding=-transition_duration)
        
        final_video.write_videofile(
            output_path, 
            fps=24, 
            codec="libx264", 
            audio_codec="aac",
            ffmpeg_params=["-pix_fmt", "yuv420p", "-crf", "17"],
            logger=None         
        )
    
    for clip in clips:
        clip.close()
        
    return os.path.abspath(output_path)


if __name__ == "__main__":
    mcp.run()