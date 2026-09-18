import os
import json
import shutil
import gradio as gr
from pathlib import Path
from typing import Dict, Any, List

from config import (
    ANIME_STYLES,
    VOICE_PROFILES,
    RESOLUTIONS,
    BGM_MOODS,
    SFX_PRESETS,
    CAMERA_MOTIONS,
    BGM_DIR,
    SFX_DIR,
    OUTPUT_DIR
)
from core.script_generator import generate_story_script, DEFAULT_TEMPLATES
from core.tts_engine import generate_speech
from core.visual_engine import generate_anime_image, render_scene_motion_clip, generate_hf_video_clip
from core.composer import render_full_faceless_video
from core.audio_assets import generate_default_sfx, generate_default_bgm

# Initialize procedural default audio
generate_default_sfx()
generate_default_bgm()

# Get dynamic list of available BGMs and SFX
def get_available_bgms():
    bgms = ["None"]
    for f in list(BGM_DIR.glob("*.wav")) + list(BGM_DIR.glob("*.mp3")):
        if f.stem not in bgms:
            bgms.append(f.stem)
    return bgms

def get_available_sfx():
    sfxs = ["none"]
    for f in list(SFX_DIR.glob("*.wav")) + list(SFX_DIR.glob("*.mp3")):
        if f.stem not in sfxs:
            sfxs.append(f.stem)
    return sfxs

# --- Tab 1: 1-Click Faceless Video Maker ---
def one_click_generate_video(
    topic: str,
    style_name: str,
    voice_name: str,
    resolution: str,
    num_scenes: int,
    bgm_mood: str,
    bgm_volume: float,
    enable_subs: bool,
    enable_fx: bool,
    progress=gr.Progress(track_tqdm=True)
):
    if not topic or not topic.strip():
        return None, "⚠️ Please enter a topic or select an idea preset!", ""
        
    def update_progress(p_val: float, desc: str):
        progress(p_val, desc=desc)

    try:
        progress(0.02, desc="Generating Storyboard & Scene Breakdown...")
        storyboard = generate_story_script(
            topic=topic,
            style_name=style_name,
            num_scenes=int(num_scenes),
            video_format=resolution
        )
        
        voice_id = VOICE_PROFILES.get(voice_name, "en-US-ChristopherNeural")
        
        result = render_full_faceless_video(
            storyboard=storyboard,
            topic=topic,
            style_name=style_name,
            voice_name=voice_id,
            resolution_preset=resolution,
            bgm_name=bgm_mood,
            bgm_volume=float(bgm_volume),
            enable_subtitles=enable_subs,
            enable_action_fx=enable_fx,
            progress_callback=update_progress
        )
        
        video_path = result["video_path"]
        seo = result["seo_metadata"]
        
        seo_text = f"""### 🏷️ YouTube Viral Titles:
1. **{seo['titles'][0]}**
2. {seo['titles'][1]}
3. {seo['titles'][2]}

---
### 📝 Video Description:
```
{seo['description']}
```

---
### 🏷️ Hashtags & Tags:
**Hashtags**: `{seo['hashtags']}`
**Tags**: `{seo['tags']}`
"""
        status_msg = f"✅ 1080p Video created successfully! ({len(storyboard)} scenes rendered in {resolution} with crystal-clear voice and dynamic anime effects)"
        return video_path, status_msg, seo_text
        
    except Exception as e:
        import traceback
        err_msg = f"❌ Error: {str(e)}\n{traceback.format_exc()}"
        print(err_msg)
        return None, f"Error generating video: {str(e)}", ""


# --- Tab 2: Storyboard Generation & Custom Scene Rendering ---
def create_storyboard_ui(topic: str, style_name: str, num_scenes: int):
    scenes = generate_story_script(topic=topic, style_name=style_name, num_scenes=int(num_scenes))
    return json.dumps(scenes, indent=2), f"✅ Generated {len(scenes)} scenes! You can customize the JSON below before rendering."


def render_custom_storyboard(
    storyboard_json: str,
    topic: str,
    style_name: str,
    voice_name: str,
    resolution: str,
    bgm_mood: str,
    bgm_volume: float,
    enable_subs: bool,
    enable_fx: bool,
    progress=gr.Progress(track_tqdm=True)
):
    try:
        storyboard = json.loads(storyboard_json)
        if not isinstance(storyboard, list) or len(storyboard) == 0:
            return None, "⚠️ Invalid storyboard JSON. Must be a list of scene objects.", ""
    except Exception as e:
        return None, f"⚠️ JSON Parse Error: {str(e)}", ""

    def update_progress(p_val: float, desc: str):
        progress(p_val, desc=desc)

    voice_id = VOICE_PROFILES.get(voice_name, "en-US-ChristopherNeural")
    
    result = render_full_faceless_video(
        storyboard=storyboard,
        topic=topic or "Custom Anime Story",
        style_name=style_name,
        voice_name=voice_id,
        resolution_preset=resolution,
        bgm_name=bgm_mood,
        bgm_volume=float(bgm_volume),
        enable_subtitles=enable_subs,
        enable_action_fx=enable_fx,
        progress_callback=update_progress
    )
    
    video_path = result["video_path"]
    seo = result["seo_metadata"]
    seo_text = f"**Selected Title**: {seo['titles'][0]}\n\n**Description**:\n{seo['description']}"
    return video_path, "✅ Custom Storyboard Rendered Successfully!", seo_text


# --- Tab 3: Single Prompt Video Lab ---
def single_prompt_video_lab(prompt: str, style_name: str, motion_type: str, resolution: str, video_mode: str):
    if not prompt.strip():
        return None, "Please enter a prompt!"
        
    res_info = RESOLUTIONS.get(resolution, RESOLUTIONS["9:16 (YouTube Shorts / TikTok / Reels)"])
    target_w = res_info["width"]
    target_h = res_info["height"]
    
    out_video = OUTPUT_DIR / f"lab_clip_{int(time.time())}.mp4"
    
    if "Cloud AI Video Model" in video_mode:
        res = generate_hf_video_clip(prompt=prompt, style_name=style_name, output_path=str(out_video))
        if res and os.path.exists(res):
            return str(out_video), "Generated via Cloud AI Video Model (AnimateDiff)!"
            
    out_img = OUTPUT_DIR / f"lab_art_{int(time.time())}.jpg"
    generate_anime_image(
        prompt=prompt,
        style_name=style_name,
        width=target_w,
        height=target_h,
        output_path=str(out_img)
    )
    
    render_scene_motion_clip(
        image_path=str(out_img),
        duration=4.5,
        output_path=str(out_video),
        motion_type=motion_type,
        target_size=(target_w, target_h),
        fps=24,
        enable_action_fx=True
    )
    
    return str(out_video), f"Generated 1080p Anime FX Video for '{prompt}'"


# --- Tab 4: Free Neural TTS & Audio Studio ---
def tts_studio_preview(text: str, voice_name: str, speed_rate: str):
    if not text.strip():
        return None, "Please enter text to speak!"
    voice_id = VOICE_PROFILES.get(voice_name, "en-US-ChristopherNeural")
    out_audio = OUTPUT_DIR / "tts_preview.mp3"
    generate_speech(text=text, voice=voice_id, output_path=str(out_audio), rate=speed_rate)
    return str(out_audio), f"Voiceover synthesized with {voice_name}"

def preview_bgm_track(bgm_name: str):
    if not bgm_name or bgm_name == "None":
        return None
    for ext in [".wav", ".mp3"]:
        p = BGM_DIR / f"{bgm_name}{ext}"
        if p.exists():
            return str(p)
    return None

def preview_sfx_track(sfx_name: str):
    if not sfx_name or sfx_name == "none":
        return None
    for ext in [".wav", ".mp3"]:
        p = SFX_DIR / f"{sfx_name}{ext}"
        if p.exists():
            return str(p)
    return None

def upload_custom_audio(file_obj, category: str):
    if file_obj is None:
        return "⚠️ No file selected."
    src_path = Path(file_obj.name)
    target_folder = BGM_DIR if category == "Background Music (BGM)" else SFX_DIR
    target_path = target_folder / src_path.name
    shutil.copyfile(src_path, target_path)
    return f"✅ Uploaded '{src_path.name}' to {category} library successfully!"


# --- Build Gradio App Interface ---
custom_css = """
body { background-color: #0b0e14; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
.gradio-container { max-width: 1200px !important; margin: auto; }
.hero-header { background: linear-gradient(135deg, #181924 0%, #2b1d3d 50%, #4a1942 100%); padding: 25px; border-radius: 12px; color: white; margin-bottom: 20px; border: 1px solid #ff336644; }
.hero-header h1 { font-size: 2.2rem; margin: 0; font-weight: 800; color: #ff3366; text-shadow: 0 0 10px rgba(255, 51, 102, 0.4); }
.hero-header p { margin-top: 8px; font-size: 1.05rem; opacity: 0.9; }
.generate-btn { background: linear-gradient(90deg, #FF416C 0%, #FF4B2B 100%) !important; color: white !important; font-size: 1.15rem !important; font-weight: bold !important; border: none !important; border-radius: 8px !important; padding: 12px !important; box-shadow: 0 4px 15px rgba(255, 65, 108, 0.4); }
"""

with gr.Blocks(title="Anime AI Faceless Studio (100% Free)", css=custom_css, theme=gr.themes.Soft(primary_hue="red", secondary_hue="slate")) as demo:
    
    gr.HTML(
        """
        <div class="hero-header">
            <h1>🎬 Anime & Cartoon AI Video Studio (100% Free)</h1>
            <p>1080p Full HD Video • Crystal-Clear Neural Voiceover • Studio Anime OST & SFX • Dynamic Energy & Speedlines • Viral Subtitles</p>
        </div>
        """
    )
    
    with gr.Tabs():
        # TAB 1: 1-Click Generator
        with gr.Tab("🚀 1-Click Faceless Video Maker"):
            with gr.Row():
                with gr.Column(scale=5):
                    topic_input = gr.Textbox(
                        label="💡 Topic / Story Idea",
                        placeholder="e.g. Weak hunter awakens forbidden dragon sovereign powers in dark dungeon",
                        lines=2
                    )
                    
                    gr.Markdown("**✨ Quick Idea Presets (Click to load):**")
                    with gr.Row():
                        btn_preset1 = gr.Button("⚔️ Shadow Monarch", size="sm")
                        btn_preset2 = gr.Button("🌿 Spirit Shrine", size="sm")
                        btn_preset3 = gr.Button("🏙️ Cyberpunk Ninja", size="sm")
                    
                    btn_preset1.click(lambda: "Shadow Monarch Awakening (Shonen / Manhwa)", outputs=topic_input)
                    btn_preset2.click(lambda: "The Whispering Spirit Shrine (Ghibli Aesthetic)", outputs=topic_input)
                    btn_preset3.click(lambda: "Cyberpunk Neo-Tokyo Outlaw", outputs=topic_input)
                    
                    with gr.Row():
                        style_dropdown = gr.Dropdown(
                            label="🎨 Anime & Art Style",
                            choices=list(ANIME_STYLES.keys()),
                            value="Shonen Action Anime"
                        )
                        voice_dropdown = gr.Dropdown(
                            label="🎙️ Neural Voiceover (Free)",
                            choices=list(VOICE_PROFILES.keys()),
                            value="Epic Anime Narrator (Male - Deep & Dramatic)"
                        )
                        
                    with gr.Row():
                        format_dropdown = gr.Dropdown(
                            label="📐 Video Format / Aspect Ratio",
                            choices=list(RESOLUTIONS.keys()),
                            value="9:16 (YouTube Shorts / TikTok / Reels)"
                        )
                        scenes_slider = gr.Slider(
                            minimum=2, maximum=6, step=1, value=4,
                            label="🔢 Number of Scenes"
                        )
                        
                    with gr.Row():
                        bgm_dropdown = gr.Dropdown(
                            label="🎵 Background Music (Anime OST)",
                            choices=get_available_bgms(),
                            value="Epic Anime Battle"
                        )
                        bgm_vol_slider = gr.Slider(
                            minimum=-30.0, maximum=-5.0, step=1.0, value=-18.0,
                            label="🔊 BGM Ducking Volume (dB)"
                        )
                    
                    with gr.Row():
                        subs_checkbox = gr.Checkbox(
                            label="✨ Animated Karaoke Subtitles",
                            value=True
                        )
                        fx_checkbox = gr.Checkbox(
                            label="⚡ Dynamic Anime Particles & Speedlines FX",
                            value=True
                        )
                        
                    gen_btn = gr.Button("🚀 Generate 100% Free Faceless Video", variant="primary", elem_classes=["generate-btn"])
                    
                with gr.Column(scale=5):
                    status_box = gr.Textbox(label="Status", interactive=False)
                    video_output = gr.Video(label="🎬 Generated 1080p Video", autoplay=True)
                    seo_box = gr.Markdown(label="📈 YouTube SEO Metadata")

            gen_btn.click(
                fn=one_click_generate_video,
                inputs=[
                    topic_input, style_dropdown, voice_dropdown, format_dropdown,
                    scenes_slider, bgm_dropdown, bgm_vol_slider, subs_checkbox, fx_checkbox
                ],
                outputs=[video_output, status_box, seo_box]
            )

        # TAB 2: Storyboard & Scene Director
        with gr.Tab("🎬 Storyboard & Scene Director"):
            gr.Markdown("### 🛠️ Step-by-Step Scene Storyboard Editor")
            with gr.Row():
                with gr.Column(scale=5):
                    custom_topic = gr.Textbox(label="Story Topic", placeholder="Enter topic...")
                    custom_style = gr.Dropdown(label="Style", choices=list(ANIME_STYLES.keys()), value="Shonen Action Anime")
                    custom_scenes_cnt = gr.Slider(minimum=2, maximum=6, value=4, step=1, label="Scenes Count")
                    btn_make_storyboard = gr.Button("🤖 Generate Storyboard JSON")
                    
                    storyboard_editor = gr.Code(
                        label="Edit Storyboard JSON (Narration, Visual Prompts, Motion, SFX)",
                        language="json",
                        lines=16
                    )
                    
                    btn_render_custom = gr.Button("🎬 Render Full Custom Video", variant="primary")
                    
                with gr.Column(scale=5):
                    custom_voice = gr.Dropdown(label="Voice", choices=list(VOICE_PROFILES.keys()), value="Anime Storyteller (Male - Engaging & Energetic)")
                    custom_res = gr.Dropdown(label="Resolution", choices=list(RESOLUTIONS.keys()), value="9:16 (YouTube Shorts / TikTok / Reels)")
                    custom_bgm = gr.Dropdown(label="BGM", choices=get_available_bgms(), value="Epic Anime Battle")
                    custom_bgm_vol = gr.Slider(minimum=-30.0, maximum=-5.0, value=-18.0, label="BGM Volume")
                    with gr.Row():
                        custom_subs = gr.Checkbox(label="Enable Subtitles", value=True)
                        custom_fx = gr.Checkbox(label="Enable Anime FX", value=True)
                    
                    custom_status = gr.Textbox(label="Status", interactive=False)
                    custom_video_out = gr.Video(label="Custom Rendered Video")
                    custom_seo_out = gr.Markdown()

            btn_make_storyboard.click(
                fn=create_storyboard_ui,
                inputs=[custom_topic, custom_style, custom_scenes_cnt],
                outputs=[storyboard_editor, custom_status]
            )
            
            btn_render_custom.click(
                fn=render_custom_storyboard,
                inputs=[
                    storyboard_editor, custom_topic, custom_style,
                    custom_voice, custom_res, custom_bgm, custom_bgm_vol, custom_subs, custom_fx
                ],
                outputs=[custom_video_out, custom_status, custom_seo_out]
            )

        # TAB 3: Single Prompt Video Lab
        with gr.Tab("🎨 Prompt-to-Anime Video Lab"):
            gr.Markdown("### Test prompt video generation with choice of Engine")
            with gr.Row():
                with gr.Column():
                    lab_prompt = gr.Textbox(
                        label="Anime Visual Prompt",
                        placeholder="e.g. samurai with glowing blue katana standing under sakura tree in rain",
                        lines=3
                    )
                    lab_style = gr.Dropdown(label="Style", choices=list(ANIME_STYLES.keys()), value="Shonen Action Anime")
                    lab_engine = gr.Radio(
                        label="Video Engine",
                        choices=["🌟 Dynamic Anime FX Video (1080p HD - Recommended)", "🚀 Cloud AI Video Model (AnimateDiff)"],
                        value="🌟 Dynamic Anime FX Video (1080p HD - Recommended)"
                    )
                    lab_motion = gr.Dropdown(label="Camera Motion", choices=CAMERA_MOTIONS, value="Slow Zoom In (Intense Focus)")
                    lab_res = gr.Dropdown(label="Format", choices=list(RESOLUTIONS.keys()), value="9:16 (YouTube Shorts / TikTok / Reels)")
                    lab_btn = gr.Button("Generate Video Clip", variant="primary")
                with gr.Column():
                    lab_status = gr.Textbox(label="Status", interactive=False)
                    lab_video = gr.Video(label="Generated Clip")
                    
            lab_btn.click(
                fn=single_prompt_video_lab,
                inputs=[lab_prompt, lab_style, lab_motion, lab_res, lab_engine],
                outputs=[lab_video, lab_status]
            )

        # TAB 4: Free Neural TTS & Audio Studio
        with gr.Tab("🎙️ Audio & Sound Design Studio"):
            gr.Markdown("### 🔊 Preview, Test & Upload Custom Music & Sound Effects")
            with gr.Row():
                with gr.Column(scale=5):
                    gr.Markdown("#### 🎙️ Test Neural Voiceover")
                    tts_text = gr.Textbox(label="Speech Text", placeholder="Enter script line to narrate...", lines=2)
                    tts_voice = gr.Dropdown(label="Voice Profile", choices=list(VOICE_PROFILES.keys()), value="Epic Anime Narrator (Male - Deep & Dramatic)")
                    tts_speed = gr.Dropdown(label="Speed Rate", choices=["-10%", "+0%", "+5%", "+10%", "+15%", "+20%"], value="+5%")
                    tts_btn = gr.Button("Synthesize Speech", variant="secondary")
                    tts_audio = gr.Audio(label="Synthesized Voice Preview")
                    
                with gr.Column(scale=5):
                    gr.Markdown("#### 🎵 Preview Background Music (OST)")
                    bgm_preview_select = gr.Dropdown(label="Select BGM Track", choices=get_available_bgms(), value="Epic Anime Battle")
                    bgm_player = gr.Audio(label="BGM Audio Player")
                    bgm_preview_select.change(fn=preview_bgm_track, inputs=bgm_preview_select, outputs=bgm_player)
                    
                    gr.Markdown("#### 💥 Preview Sound Effects (SFX)")
                    sfx_preview_select = gr.Dropdown(label="Select SFX", choices=get_available_sfx(), value="sword_slash")
                    sfx_player = gr.Audio(label="SFX Audio Player")
                    sfx_preview_select.change(fn=preview_sfx_track, inputs=sfx_preview_select, outputs=sfx_player)

            gr.Markdown("---")
            gr.Markdown("#### 📤 Upload Your Own Custom Music / Sound Effects")
            with gr.Row():
                upload_file = gr.File(label="Upload MP3 / WAV Audio File", file_types=[".mp3", ".wav"])
                upload_type = gr.Radio(label="Audio Category", choices=["Background Music (BGM)", "Sound Effect (SFX)"], value="Background Music (BGM)")
                btn_upload = gr.Button("📥 Save to Studio Library")
                upload_status = gr.Textbox(label="Upload Status", interactive=False)
                
            btn_upload.click(
                fn=upload_custom_audio,
                inputs=[upload_file, upload_type],
                outputs=upload_status
            )
            
            tts_btn.click(
                fn=tts_studio_preview,
                inputs=[tts_text, tts_voice, tts_speed],
                outputs=[tts_audio, status_box]
            )

        # TAB 5: YouTube Faceless Growth Guide
        with gr.Tab("📈 Faceless Channel Blueprint"):
            gr.Markdown(
                """
                ## 🚀 How to Scale a 100% Free Faceless Anime YouTube Channel
                
                ### 1. Niche & Content Formulas that Go Viral:
                - **Manhwa & Anime Awakening Stories**: "The weakest F-rank hunter enters the forbidden dungeon..." (High curiosity retention).
                - **Dark Anime Lore & Mysteries**: "The horrifying truth behind the Cursed Spirit King..."
                - **What-If Scenarios & Recaps**: Fast-paced 45-second animated summaries with bold subtitles.
                
                ### 2. High-Retention YouTube Shorts Formula (Hook, Story, Climax):
                - **0-3 Seconds (The Hook)**: Bold claim or shocking visual + Sound Effect (Whoosh / Boom).
                - **3-20 Seconds (The Escalation)**: Fast pacing, dramatic narrator, dynamic camera zoom/pan every 3-4 seconds.
                - **20-40 Seconds (The Climax)**: Action shake, sound effects, peak visual.
                - **40-45 Seconds (The Payoff / Loop)**: Satisfying conclusion or seamless loop back to the hook.
                
                ### 3. Monetization Strategy:
                - **YouTube AdSense & Shorts Fund**
                - **Affiliate Marketing**: Anime figures, gaming gear, manga subscription links in pinned comments.
                - **Patreon / Discord Community**: Early access to longform stories and high-res wallpapers.
                """
            )

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860, inbrowser=False)
