# C:\Projectsai\run_agent.py
import os
import sys
import asyncio
import json
import shutil
import re
from duckduckgo_search import DDGS
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

BASE_DIR = "C:\\Projectsai"
os.makedirs(os.path.join(BASE_DIR, "output", "images"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "output", "audio"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "output", "videos"), exist_ok=True)

def clean_temp_folders():
    temp_dirs = [
        os.path.join(BASE_DIR, "output", "images"),
        os.path.join(BASE_DIR, "output", "audio"),
        os.path.join(BASE_DIR, "output", "videos")
    ]
    print("\n" + "=" * 50)
    print("[Cleanup] Purging temporary compilation work-folders...")
    print("=" * 50)
    for folder in temp_dirs:
        if os.path.exists(folder):
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    pass

#async def get_video_blueprint(user_prompt: str, video_layout: str) -> list:
#    print(f"\n[Search] Gathering real-time data on: '{user_prompt}'...", flush=True)
#    
#    search_context = "General historical and factual context."
#    try:
#        with DDGS(headers={"User-Agent": "Mozilla/5.0"}) as ddgs:
#            search_results = list(ddgs.text(user_prompt, max_results=5))
#             if search_results:
#                 search_context = "\n\n".join([f"Research Point: {res.get('body')}" for res in search_results])
#     except Exception as e:
#         print(f"[Warning] Web search skipped: {e}.")

#     print(f"\n[Brainstorming] Constructing dynamic persona and [{video_layout.upper()}] JSON script...", flush=True)
    
#     # DYNAMIC SYSTEM INSTRUCTION
#     # We ask the AI to determine the persona based on the topic before writing
#     system_instruction = (
#         f"You are a master content creator. Your topic is: '{user_prompt}'.\n"
#         "1. Adopt an engaging persona suitable for the topic (e.g., teacher, expert, narrator).\n"
#         "2. Generate a 5-scene script in raw JSON.\n"
#         "3. Output ONLY the raw JSON object. No chatter, no markdown, no backticks.\n\n"
#         "EXAMPLE JSON FORMAT (Use this exact structure):\n"
#         "{\n"
#         "  \"scenes\": [\n"
#         "    {\"narration\": \"Start with a strong hook about the core concept.\", \"visual_prompt\": \"Cinematic close-up of subject, high detail, 85mm lens\"},\n"
#         "    {\"narration\": \"Explain the first key mechanism or fact.\", \"visual_prompt\": \"Mid-shot showing action, studio lighting\"},\n"
#         "    {\"narration\": \"Provide an interesting deeper detail.\", \"visual_prompt\": \"Macro photography of a specific detail, shallow depth of field\"},\n"
#         "    {\"narration\": \"Introduce a conflict or comparison.\", \"visual_prompt\": \"Wide shot for context, cinematic colors\"},\n"
#         "    {\"narration\": \"Conclude with a summary and final thought.\", \"visual_prompt\": \"Slow motion pull-back, dramatic atmosphere\"}\n"
#         "  ]\n"
#         "}"
#     )
    

#     try:
#         async with httpx.AsyncClient() as client:
#             response = await client.post(
#                 "http://127.0.0.1:11434/api/chat",
#                 json={
#                     "model": "gemma4-video-agent",
#                     "messages": [
#                         {"role": "system", "content": system_instruction},
#                         {"role": "user", "content": f"Topic: {user_prompt}\nContext: {search_context}"}
#                     ],
#                     "options": {"temperature": 1.0, "top_p": 0.95, "top_k": 64, "num_predict": 2048},
#                     "stream": False
#                 },
#                 timeout=120.0
#             )
#             raw_content = response.json()["message"]["content"].strip()
            
#             json_match = re.search(r'\{.*\}', raw_content, re.DOTALL)
#             parsed_data = {"scenes": []}
            
#             if json_match:
#                 try:
#                     parsed_data = json.loads(json_match.group(0))
#                 except json.JSONDecodeError:
#                     print("[Warning] AI output was not valid JSON.")

#             # Normalization logic remains the same to ensure robustness
#             normalized_scenes = []
#             scenes_list = parsed_data.get("scenes", [])
#             if isinstance(scenes_list, list):
#                 for scene in scenes_list:
#                     if isinstance(scene, dict):
#                         normalized_scenes.append({
#                             "narration": scene.get("narration", "Continuing the exploration."),
#                             "visual_prompt": scene.get("visual_prompt", "Cinematic shot of the subject.")
#                         })
            
#             if not normalized_scenes:
#                 normalized_scenes = [{"narration": f"Let's explore {user_prompt}.", "visual_prompt": f"Cinematic shot of {user_prompt}"}]
            
#             return normalized_scenes
            
#     except Exception as e:
#         print(f"[CRITICAL ERROR] Blueprint creation failed: {e}")
#         return [{"narration": f"An overview of {user_prompt}.", "visual_prompt": f"Cinematic shot of {user_prompt}"}]

# async def run_pipeline():
#     print("="*60)
#     print("🎬  WELCOME TO THE DISTRIBUTED AGENTIC VIDEO ENGINE")
#     print("="*60)
    
#     user_prompt = input("What is the topic or concept for your video?\n> ").strip()
#     video_layout = "short" if input("Layout [1] Long, [2] Short: ").strip() == "2" else "long"
    
#     print("\nSelect the voice-over style:")
#     print("[1] Warm & Friendly Female (Classic) - af_heart")
#     print("[2] High Energy / Broadcast Female - af_nova")
#     print("[3] Elegant / Narrative British Female - bf_alice")
#     print("[4] Clear Professional Male - am_michael")
#     print("[5] Deep Baritone / Dramatic Male - am_onyx")
#     print("[6] Authoritative Mature British Male - bm_george")
#     print("[7] Youthful & Casual Male - am_liam")
#     voice_choice = input("Select a voice style 1-7 (default is 1): ").strip()

#     voice_map = {
#         "1": "af_heart", "2": "af_nova", "3": "bf_alice", 
#         "4": "am_michael", "5": "am_onyx", "6": "bm_george", "7": "am_liam"
#     }
#     selected_voice = voice_map.get(voice_choice, "af_heart")
#     print(f"\n[System] Configured pipeline for [{video_layout.upper()} format] and [{selected_voice}] voiceover.")

#     scenes = await get_video_blueprint(user_prompt, video_layout)
#     print(f"\n[Success] Brainstormed {len(scenes)} scenes.")

#     audio_params = StdioServerParameters(command="python", args=["C:\\Projectsai\\servers\\audio_server.py"])
#     video_params = StdioServerParameters(command="python", args=["C:\\Projectsai\\servers\\video_server.py"])
#     compiler_params = StdioServerParameters(command="python", args=["C:\\Projectsai\\servers\\compiler_server.py"])

#     final_timeline_data = []

#     # PHASE 1: AUDIO
#     print("\n🎧 [Phase 1/3] Processing audio tracks...")
#     async with stdio_client(audio_params) as (r, w), ClientSession(r, w) as session:
#         await session.initialize()
#         for idx, scene in enumerate(scenes):
#             print(f" -> Scene {idx+1}: Processing voice track...")
#             try:
#                 audio_res = await session.call_tool(
#                     "generate_audio_segment",
#                     arguments={"text": scene["narration"], "scene_idx": idx, "voice": selected_voice}
#                 )
#                 final_timeline_data.append({
#                     "audio": audio_res.content[0].text.strip(),
#                     "visual": "",
#                     "is_video": True
#                 })
#             except Exception as e:
#                 print(f"[Error] Audio failed for scene {idx+1}: {e}")

#     # C:\Projectsai\run_agent.py (Optimized Visual Phase Block)

#     # PHASE 2: VISUAL GENERATION (BATCH-OPTIMIZED)
#     print("\n🖥️ [Phase 2/3] Processing GPU rendering workloads...")
#     async with stdio_client(video_params) as (r, w), ClientSession(r, w) as session:
#         await session.initialize()
        
#         # Step 2A: Generate ALL Static Base Frames (SDXL remains hot in VRAM)
#         print("\n -> Generating all base image frames...")
#         image_paths = []
#         for idx, scene in enumerate(scenes):
#             print(f"    [SDXL] Scene {idx+1}/{len(scenes)}: Rendering base image...")
#             try:
#                 img_res = await session.call_tool(
#                     "generate_base_image",
#                     arguments={"prompt": scene["visual_prompt"], "scene_idx": idx, "video_type": video_layout}
#                 )
#                 image_paths.append(img_res.content[0].text.strip())
#             except Exception as e:
#                 print(f"[Error] Image generation failed for scene {idx+1}: {e}")
#                 image_paths.append("")

#         # Step 2B: Animate ALL Frames to Video (SVD remains hot in VRAM)
#         print("\n -> Animating all frames...")
#         for idx, img_path in enumerate(image_paths):
#             if not img_path:
#                 continue
#             print(f"    [SVD] Scene {idx+1}/{len(scenes)}: Rendering motion sequences...")
#             try:
#                 video_res = await session.call_tool(
#                     "animate_scene_image",
#                     arguments={"image_path": img_path, "scene_idx": idx, "video_type": video_layout}
#                 )
#                 final_timeline_data[idx]["visual"] = video_res.content[0].text.strip()
#             except Exception as e:
#                 print(f"[Error] Animation failed for scene {idx+1}: {e}")

#     # PHASE 3: COMPILATION
#     print("\n🎬 [Phase 3/3] Compiling video sequences...")
#     async with stdio_client(compiler_params) as (r, w), ClientSession(r, w) as session:
#         await session.initialize()
#         output_filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", "final_output.mp4")
#         compile_res = await session.call_tool(
#             "assemble_final_video",
#             arguments={"scenes_data_json": json.dumps(final_timeline_data), "output_path": output_filepath}
#         )
#         print(f"\n🎉 VIDEO SUCCESS: {compile_res.content[0].text.strip()}")
#         if os.path.exists(output_filepath) and os.path.getsize(output_filepath) > 1024:
#             clean_temp_folders()
#         else:
#             print(f"[Warning] Final video check failed at {output_filepath}. Skipping cleanup to preserve source data.")

# if __name__ == "__main__":
# ##    asyncio.run(run_pipeline())