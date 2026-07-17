# C:\Projectsai\gui_app.py
import os
import sys
import json
import asyncio
import threading
import re
import customtkinter as ctk
import pygame
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

PYGAME_MIXER_ACTIVE = False
try:
    pygame.mixer.init()
    PYGAME_MIXER_ACTIVE = True
except Exception as e:
    print(f"[Warning] Pygame mixer offline: {e}", file=sys.stderr)

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

VOICE_MAP = {
    "Warm & Friendly Female (Classic)": "af_heart",
    "High Energy / Broadcast Female": "af_nova",
    "Elegant Narrative British Female": "bf_alice",
    "Clear Professional Male": "am_michael",
    "Deep Baritone / Dramatic Male": "am_onyx",
    "Authoritative Mature British Male": "bm_george",
    "Youthful & Casual Male": "am_liam"
}

BASE_DIR = "C:\\Projectsai"

class VideoAgentApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Agentic Video Engine")
        self.geometry("900x850")
        self.configure(fg_color="#0f0f13")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(7, weight=1)

        self.cancel_event = threading.Event()
        self.loop = None
        self.current_task = None

        # ------------------ Graphical Layout Setup ------------------
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, padx=30, pady=(30, 15), sticky="ew")
        
        self.title_label = ctk.CTkLabel(
            self.header_frame, text="AGENTIC VIDEO ENGINE", 
            font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold")
        )
        self.title_label.pack(anchor="w")

        self.config_frame = ctk.CTkFrame(self, fg_color="#14141a", corner_radius=16, border_width=1, border_color="#1f1f2e")
        self.config_frame.grid(row=1, column=0, padx=30, pady=10, sticky="ew")
        self.config_frame.grid_columnconfigure((0, 1), weight=1)

        # Layout selection
        self.layout_label = ctk.CTkLabel(self.config_frame, text="🎬 Layout Mode", font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"))
        self.layout_label.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")
        self.layout_dropdown = ctk.CTkOptionMenu(self.config_frame, values=["Short Form (9:16)", "Long Form (16:9)"], fg_color="#1c1c28", button_color="#6366f1", button_hover_color="#4f46e5")
        self.layout_dropdown.grid(row=1, column=0, padx=20, pady=(0, 15), sticky="ew")

        # Duration selection
        self.duration_label = ctk.CTkLabel(self.config_frame, text="⏳ Max Target Length", font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"))
        self.duration_label.grid(row=0, column=1, padx=20, pady=(15, 5), sticky="w")
        self.duration_dropdown = ctk.CTkOptionMenu(self.config_frame, values=["30 Seconds", "60 Seconds", "90 Seconds", "2 Minutes"], fg_color="#1c1c28", button_color="#6366f1", button_hover_color="#4f46e5")
        self.duration_dropdown.grid(row=1, column=1, padx=20, pady=(0, 15), sticky="ew")

        # Prompt Box
        self.prompt_label = ctk.CTkLabel(self, text="💡 Production Guidelines & Concept Prompt", font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"))
        self.prompt_label.grid(row=2, column=0, padx=30, pady=(15, 5), sticky="w")
        
        self.prompt_textbox = ctk.CTkTextbox(self, height=120, fg_color="#14141a", border_width=1, border_color="#1f1f2e", corner_radius=16, font=ctk.CTkFont(family="Segoe UI", size=13))
        self.prompt_textbox.grid(row=3, column=0, padx=30, pady=5, sticky="ew")
        self.prompt_textbox.insert("1.0", "Astrology forecast for Aries for August 2026, do not use images containing Rams, include detailed forecast for wealth, finance, health, relationships and future outlook")

        # Audio Config
        self.voice_frame = ctk.CTkFrame(self, fg_color="#14141a", corner_radius=16, border_width=1, border_color="#1f1f2e")
        self.voice_frame.grid(row=4, column=0, padx=30, pady=10, sticky="ew")
        self.voice_frame.grid_columnconfigure((0, 1), weight=1)

        self.voice_label = ctk.CTkLabel(self.voice_frame, text="🎙️ Narration voice model", font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"))
        self.voice_label.grid(row=0, column=0, columnspan=2, padx=20, pady=(15, 5), sticky="w")
        
        self.voice_dropdown = ctk.CTkOptionMenu(self.voice_frame, values=list(VOICE_MAP.keys()), fg_color="#1c1c28", button_color="#6366f1", button_hover_color="#4f46e5")
        self.voice_dropdown.grid(row=1, column=0, padx=20, pady=(0, 15), sticky="ew")
        self.voice_dropdown.set("High Energy / Broadcast Female")

        self.preview_button = ctk.CTkButton(self.voice_frame, text="▶ Preview Voice", font=ctk.CTkFont(family="Segoe UI", weight="bold"), fg_color="#1c1c28", hover_color="#2b2b3d", corner_radius=12, border_width=1, border_color="#313145", command=self.play_voice_preview)
        self.preview_button.grid(row=1, column=1, padx=20, pady=(0, 15), sticky="ew")

        # Action Trigger
        self.generate_btn = ctk.CTkButton(self, text="🚀 GENERATE CINEMATIC VIDEO", font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"), fg_color="#6366f1", hover_color="#4f46e5", height=50, corner_radius=16, command=self.start_pipeline_thread)
        self.generate_btn.grid(row=5, column=0, padx=30, pady=15, sticky="ew")

        self.status_box = ctk.CTkTextbox(self, fg_color="#09090c", border_width=1, border_color="#14141a", corner_radius=16, font=ctk.CTkFont(family="Consolas", size=11), text_color="#a5b4fc")
        self.status_box.grid(row=6, column=0, padx=30, pady=(5, 25), sticky="nsew")
        self.status_box.configure(state="disabled")

    def log(self, text: str):
        self.status_box.configure(state="normal")
        self.status_box.insert("end", text + "\n")
        self.status_box.see("end")
        self.status_box.configure(state="disabled")

    def play_voice_preview(self):
        pass

    def start_pipeline_thread(self):
        if self.current_task is not None:
            self.cancel_event.set()
            if self.loop:
                self.loop.call_soon_threadsafe(self.current_task.cancel)
            self.generate_btn.configure(text="🚀 GENERATE CINEMATIC VIDEO", fg_color="#6366f1")
            return

        self.cancel_event.clear()
        self.generate_btn.configure(text="🛑 CANCEL PIPELINE RUN", fg_color="#ef4444")
        self.status_box.configure(state="normal")
        self.status_box.delete("1.0", "end")
        self.status_box.configure(state="disabled")

        threading.Thread(target=self.run_pipeline_async_loop, daemon=True).start()

    def run_pipeline_async_loop(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        async def execute_mcp_pipeline():
            def check_cancel():
                if self.cancel_event.is_set():
                    raise asyncio.CancelledError()

            user_prompt = self.prompt_textbox.get("1.0", "end-1c").strip()
            layout_selection = "short" if "Short" in self.layout_dropdown.get() else "long"
            voice_label = self.voice_dropdown.get()
            voice_id = VOICE_MAP.get(voice_label, "af_nova")

            # ------------------ Phase 1: Context Filtering & Scraper ------------------
            check_cancel()
            self.log(f"[1/4] Starting live search parsing for: '{user_prompt}'...")
            
            search_query = user_prompt
            clean_match = re.search(r"^([^,.:;]+)", user_prompt)
            if clean_match:
                search_query = clean_match.group(1).replace("do not use", "").replace("without", "").strip()
                
            self.log(f" -> Sanitized search query: '{search_query}'")
            search_context = ""
            try:
                from duckduckgo_search import DDGS
                with DDGS() as ddgs:
                    raw_results = ddgs.text(search_query, max_results=3)
                    results = list(raw_results) if raw_results else []
                    if results:
                        processed = []
                        for r in results:
                            title = r.get('title') or "Web Reference"
                            body = r.get('body') or ""
                            processed.append(f"Title: {title}\nContent: {body}")
                        search_context = "\n\n".join(processed)
                        self.log(" -> Dynamic live context successfully gathered from the web.")
                    else:
                        self.log(" -> [Warning] Web lookup returned zero hits. Relying on model weights.")
            except Exception as e:
                self.log(f" -> [Warning] Search connection failed: {e}")

            # ------------------ Call Local Structuring Model ------------------
            check_cancel()
            self.log(" -> Consulting local model for structured scriptwriting...")
            
            system_prompt = (
                "You are an expert executive producer. Generate a valid, single JSON object containing "
                "only a \"scenes\" key. Do not include introductory notes, conversational summaries, markdown boxes, "
                "or backticks. Respect these negative guidelines explicitly: DO NOT generate, draft, or describe images "
                "depicting any horned animals, sheep, rams, or related astrological animal carvings. Ensure all scenes "
                "focus entirely on alternative symbolic graphics like celestial stars, gold coins, scales, or cosmic fire.\n\n"
                "JSON Schema Target:\n"
                "{\n"
                "  \"scenes\": [\n"
                "    {\n"
                "      \"narration\": \"The vocal script narration text content goes here.\",\n"
                "      \"visual_prompt\": \"The detailed landscape descriptive visual layout prompt goes here.\"\n"
                "    }\n"
                "  ]\n"
                "}\n"
            )

            user_message = (
                f"Topic concept: '{user_prompt}'.\n"
                f"Video Aspect Ratio constraint: {layout_selection}.\n\n"
                f"Contextual Real-time Data:\n"
                f"--- SEARCH DATA ---\n"
                f"{search_context if search_context else 'No data found.'}\n"
                f"--- END CONTEXT ---\n"
            )

            raw_blueprint = ""
            try:
                import httpx
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(
                        "http://localhost:11434/api/chat",
                        json={
                            "model": "gemma4:12b",
                            "messages": [
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": user_message}
                            ],
                            "options": {"temperature": 0.3},
                            "stream": False
                        }
                    )
                    raw_blueprint = response.json()["message"]["content"].strip()
            except Exception as e:
                self.log(f"[Fatal Error] Local model server unreachable: {e}")
                return

            # Parse JSON blueprint safely
            json_match = re.search(r"\{.*\}", raw_blueprint, re.DOTALL)
            parsed_blueprint = {"scenes": []}
            if json_match:
                try:
                    parsed_blueprint = json.loads(json_match.group(0))
                except Exception as e:
                    self.log(f"[Error] Failed parsing response JSON. Raw dump: {raw_blueprint}")
                    return

            scenes = parsed_blueprint.get("scenes", [])
            if not scenes:
                self.log("[Fatal Error] No active scene timeline was written by the model.")
                return

            self.log(f" -> Blueprint constructed successfully: {len(scenes)} visual scenes generated.")

            # ------------------ Phase 2: Engine Synthetics ------------------
            audio_params = StdioServerParameters(command="python", args=[os.path.join(BASE_DIR, "servers", "audio_server.py")])
            video_params = StdioServerParameters(command="python", args=[os.path.join(BASE_DIR, "servers", "video_server.py")])
            compiler_params = StdioServerParameters(command="python", args=[os.path.join(BASE_DIR, "servers", "compiler_server.py")])

            final_timeline_data = []

            # Invoke Audio Engine
            self.log("\n🎙️ Generating Voiceover Narrations (Phase 2a/3)...")
            async with stdio_client(audio_params) as (r, w), ClientSession(r, w) as session:
                await session.initialize()
                for idx, scene in enumerate(scenes):
                    check_cancel()
                    text = scene.get("narration") or scene.get("script") or ""
                    self.log(f" -> Scene {idx+1}: Processing voice track...")
                    res = await session.call_tool("generate_audio_segment", arguments={"text": text, "scene_idx": idx, "voice": voice_id})
                    final_timeline_data.append({
                        "audio": res.content[0].text.strip(),
                        "visual": ""
                    })

            # Invoke Video Engine
            self.log("\n🎨 Generating Photographic Visuals & Motion (Phase 2b/3)...")
            async with stdio_client(video_params) as (r, w), ClientSession(r, w) as session:
                await session.initialize()
                for idx, scene in enumerate(scenes):
                    check_cancel()
                    prompt = scene.get("visual_prompt") or ""
                    self.log(f" -> Scene {idx+1}: Synthesizing base frames...")
                    img_res = await session.call_tool("generate_base_image", arguments={"prompt": prompt, "scene_idx": idx, "video_type": layout_selection})
                    image_path = img_res.content[0].text.strip()
                    
                    self.log(f" -> Scene {idx+1}: Rendering fluid SVD motion sequences...")
                    video_res = await session.call_tool("animate_scene_image", arguments={"image_path": image_path, "scene_idx": idx, "video_type": layout_selection})
                    final_timeline_data[idx]["visual"] = video_res.content[0].text.strip()

            # Phase 3: Assembly Stitching
            check_cancel()
            self.log("\n🎬 Stitching Timelines & Crossfades (Phase 3/3)...")
            async with stdio_client(compiler_params) as (r, w), ClientSession(r, w) as session:
                await session.initialize()
                output_path = os.path.join(BASE_DIR, "output", "final_output.mp4")
                compile_res = await session.call_tool("assemble_final_video", arguments={"scenes_data_json": json.dumps(final_timeline_data), "output_path": output_path})
                self.log(f"\n🎉 SUCCESS: Video rendered perfectly -> {compile_res.content[0].text.strip()}")

        try:
            self.current_task = self.loop.create_task(execute_mcp_pipeline())
            self.loop.run_until_complete(self.current_task)
        except asyncio.CancelledError:
            self.log("\n🛑 GENERATION ABORTED: The execution pipeline was safely halted by the user.")
        except Exception as e:
            self.log(f"[Fatal Error] Thread pipeline failed: {e}")
        finally:
            self.current_task = None
            self.loop = None
            self.after(0, lambda: self.generate_btn.configure(text="🚀 GENERATE CINEMATIC VIDEO", fg_color="#6366f1"))

if __name__ == "__main__":
    app = VideoAgentApp()
    app.mainloop()