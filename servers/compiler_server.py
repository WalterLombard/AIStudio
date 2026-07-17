# C:\Projectsai\servers\compiler_server.py
import os
import sys
import warnings
import json
from fastmcp import FastMCP

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

try:
    import imageio_ffmpeg
    os.environ["IMAGEIO_FFMPEG_EXE"] = imageio_ffmpeg.get_ffmpeg_exe()
except ImportError:
    pass

try:
    from moviepy import AudioFileClip, VideoFileClip, ImageClip, concatenate_videoclips
    from moviepy.video.fx import CrossFadeIn
    def apply_fx(clip, effect, *args, **kwargs):
        return clip.with_effects([effect(*args, **kwargs)])
except ImportError:
    from moviepy.editor import AudioFileClip, VideoFileClip, ImageClip, concatenate_videoclips
    from moviepy.video.fx.all import CrossFadeIn
    def apply_fx(clip, effect, *args, **kwargs):
        return clip.fx(effect, *args, **kwargs)

mcp = FastMCP("Compiler Engine")
BASE_DIR = "C:\\Projectsai"

@mcp.tool()
def assemble_final_video(scenes_data_json: str, output_path: str = "") -> str:
    """Stitches audio and visual tracks together with seamless transitions and dynamic camera motion."""
    sys.stderr.write("[Compiler Tool] Starting compilation with dynamic camera...\n")
    
    if not output_path:
        output_path = os.path.join(BASE_DIR, "output", "final_output.mp4")
        
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    scenes_data = json.loads(scenes_data_json)
    clips = []
    transition_duration = 0.8

    for idx, scene in enumerate(scenes_data):
        audio_path = os.path.abspath(scene["audio"])
        audio = AudioFileClip(audio_path)
        
        visual_path = os.path.abspath(scene["visual"])
        if visual_path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
            clip = VideoFileClip(visual_path)
        else:
            clip = ImageClip(visual_path)

        # Set timeline audio binding
        if hasattr(clip, "with_audio"):
            final = clip.with_duration(audio.duration).with_audio(audio)
        else:
            final = clip.set_duration(audio.duration).set_audio(audio)

        # Apply Dynamic Motion Patterns (Pattern modulation)
        duration = final.duration
        pattern = idx % 4
        
        if pattern == 0:
            final = final.resize(lambda t: 1.0 + 0.15 * (t / duration))
        elif pattern == 1:
            final = final.resize(lambda t: 1.15 - 0.15 * (t / duration))
        elif pattern == 2:
            final = final.resize(1.2).set_position(lambda t: (int(-50 + (50 * (t / duration))), 'center'))
        else:
            final = final.resize(1.2).set_position(lambda t: (int(50 - (50 * (t / duration))), 'center'))

        # Blend transition crossfades
        if idx > 0:
            final = apply_fx(final, CrossFadeIn, transition_duration)
            
        clips.append(final)
            
    final_video = concatenate_videoclips(clips, method="compose", padding=-transition_duration)
    final_video.write_videofile(output_path, codec="libx264", audio_codec="aac", temp_audiofile="temp-audio.m4a", remove_temp=True)
    
    # Close resources to prevent thread locks on temporary workspace files
    for clip in clips:
        clip.close()
    final_video.close()
    
    return os.path.abspath(output_path)

if __name__ == "__main__":
    mcp.run()