# C:\Projectsai\servers\audio_server.py
import os
import sys
import warnings
from fastmcp import FastMCP

class RedirectStdoutToStderr:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = sys.stderr
    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = self._original_stdout

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

with RedirectStdoutToStderr():
    from kokoro_onnx import Kokoro
    import soundfile as sf

mcp = FastMCP("Audio Engine")
KOKORO_MODEL = None
BASE_DIR = "C:\\Projectsai"

def normalize_text_for_tts(text: str) -> str:
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
def generate_audio_segment(text: str, scene_idx: int, voice: str = "af_heart") -> str:
    """Converts a single scene's narration text into a local WAV audio file with slow, clear pacing."""
    global KOKORO_MODEL
    output_dir = os.path.join(BASE_DIR, "output", "audio")
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, f"scene_{scene_idx}.wav")
    
    print(f"[Audio Engine] Generating voiceover ({voice}) for scene {scene_idx}...", file=sys.stderr)
    normalized_text = normalize_text_for_tts(text)
    
    with RedirectStdoutToStderr():
        if KOKORO_MODEL is None:
            model_path = os.path.join(BASE_DIR, "kokoro-v1.0.fp16.onnx")
            voices_path = os.path.join(BASE_DIR, "voices-v1.0.bin")
            KOKORO_MODEL = Kokoro(model_path, voices_path)
            
        samples, sample_rate = KOKORO_MODEL.create(normalized_text, voice=voice, speed=0.9)
        sf.write(path, samples, sample_rate)
    
    return os.path.abspath(path)

if __name__ == "__main__":
    mcp.run()# C:\Projectsai\servers\audio_server.py
import os
import sys
import warnings
from fastmcp import FastMCP

class RedirectStdoutToStderr:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = sys.stderr
    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = self._original_stdout

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

with RedirectStdoutToStderr():
    from kokoro_onnx import Kokoro
    import soundfile as sf

mcp = FastMCP("Audio Engine")
KOKORO_MODEL = None
BASE_DIR = "C:\\Projectsai"

def normalize_text_for_tts(text: str) -> str:
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
def generate_audio_segment(text: str, scene_idx: int, voice: str = "af_heart") -> str:
    """Converts a single scene's narration text into a local WAV audio file with slow, clear pacing."""
    global KOKORO_MODEL
    output_dir = os.path.join(BASE_DIR, "output", "audio")
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, f"scene_{scene_idx}.wav")
    
    print(f"[Audio Engine] Generating voiceover ({voice}) for scene {scene_idx}...", file=sys.stderr)
    normalized_text = normalize_text_for_tts(text)
    
    with RedirectStdoutToStderr():
        if KOKORO_MODEL is None:
            model_path = os.path.join(BASE_DIR, "kokoro-v1.0.fp16.onnx")
            voices_path = os.path.join(BASE_DIR, "voices-v1.0.bin")
            KOKORO_MODEL = Kokoro(model_path, voices_path)
            
        samples, sample_rate = KOKORO_MODEL.create(normalized_text, voice=voice, speed=0.9)
        sf.write(path, samples, sample_rate)
    
    return os.path.abspath(path)

if __name__ == "__main__":
    mcp.run()