import os
import random
import time
import math
import urllib.parse
import urllib.request
import requests
import numpy as np
from PIL import Image, ImageEnhance, ImageDraw, ImageFilter
from pathlib import Path
from typing import Optional, Tuple, List
import imageio
from config import ANIME_STYLES, RESOLUTIONS
from core.subtitle_engine import draw_karaoke_subtitle_pil

def generate_anime_image(
    prompt: str,
    style_name: str = "Shonen Action Anime",
    width: int = 1080,
    height: int = 1920,
    output_path: str = "scene.jpg",
    seed: Optional[int] = None
) -> str:
    """
    Generates a 100% free high-resolution anime illustration using Pollinations Flux/SDXL engine.
    Applies style keywords, quality boosters, and negative prompts.
    """
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    
    style_info = ANIME_STYLES.get(style_name, ANIME_STYLES["Shonen Action Anime"])
    full_prompt = f"{style_info['prefix']}, {prompt}"
    negative = style_info.get("negative", "photorealistic, blurry, bad anatomy, low quality")
    
    if seed is None:
        seed = random.randint(100000, 99999999)
        
    encoded_prompt = urllib.parse.quote(full_prompt)
    encoded_negative = urllib.parse.quote(negative)
    
    # Pollinations Flux-Anime with 1080p high resolution
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&seed={seed}&model=flux-anime&nologo=true&enhance=true&negative={encoded_negative}"
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            )
            with urllib.request.urlopen(req, timeout=35) as response:
                img_data = response.read()
                if len(img_data) > 1000:
                    with open(out_file, "wb") as f:
                        f.write(img_data)
                    return str(out_file)
        except Exception as e:
            print(f"[Visual Engine] Pollinations attempt {attempt+1} notice: {e}")
            time.sleep(1.5)
            
    # Fallback to turbo endpoint
    try:
        fallback_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&seed={seed}&model=turbo&nologo=true"
        req = urllib.request.Request(
            fallback_url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        with urllib.request.urlopen(req, timeout=25) as response:
            with open(out_file, "wb") as f:
                f.write(response.read())
            return str(out_file)
    except Exception as e:
        print(f"[Visual Engine] Fallback notice: {e}. Generating procedural keyframe.")
        _create_placeholder_image(out_file, width, height, prompt)
        return str(out_file)


def _create_placeholder_image(out_file: Path, width: int, height: int, prompt: str):
    """Procedural fallback image"""
    img = Image.new("RGB", (width, height), color=(20, 25, 45))
    draw = ImageDraw.Draw(img)
    draw.text((width // 4, height // 2), f"Anime Keyframe: {prompt[:30]}...", fill=(255, 255, 255))
    img.save(out_file)


def render_scene_motion_clip(
    image_path: str,
    duration: float,
    output_path: str,
    motion_type: str = "Slow Zoom In (Intense Focus)",
    subtitle_text: Optional[str] = None,
    target_size: Tuple[int, int] = (1080, 1920),
    is_vertical: bool = True,
    fps: int = 24,
    enable_action_fx: bool = True
) -> str:
    """
    Renders high-definition Dynamic Anime FX Video:
    - Kinetic Camera Motion (non-linear smooth zoom, pan, drift, impact shake)
    - Dynamic Floating Energy Particles & Embers moving across 3D space
    - Anime Action Speedlines during high intensity scenes
    - Single-pass high-contrast karaoke subtitle overlay
    - Crystal clear 1080p H.264 high-bitrate encoding
    """
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    
    target_w, target_h = target_size
    img = Image.open(image_path).convert("RGB")
    
    # Pre-scale image with 30% margin for sweeping camera motion
    margin_w = int(target_w * 1.30)
    margin_h = int(target_h * 1.30)
    base_img = img.resize((margin_w, margin_h), Image.Resampling.BILINEAR)
    
    total_frames = max(1, int(duration * fps))
    writer = imageio.get_writer(
        str(out_file),
        fps=fps,
        codec='libx264',
        quality=9, # High visual quality
        bitrate='8000k', # High 8Mbps bitrate for crispness
        pixelformat='yuv420p',
        macro_block_size=1
    )
    
    max_offset_x = margin_w - target_w
    max_offset_y = margin_h - target_h
    center_x = max_offset_x // 2
    center_y = max_offset_y // 2
    
    # Generate 35 persistent particle coordinates for floating anime aura
    np.random.seed(42)
    particles = []
    for _ in range(35):
        particles.append({
            "x": np.random.uniform(0, target_w),
            "y": np.random.uniform(0, target_h),
            "vx": np.random.uniform(-1.2, 1.2),
            "vy": np.random.uniform(-2.5, -0.8), # float upward
            "size": np.random.uniform(2, 6),
            "alpha": np.random.uniform(120, 240),
            "color": (255, 230, 150) if "Ghibli" in motion_type else (200, 180, 255)
        })
    
    is_action = ("Shake" in motion_type or "Action" in motion_type or "Sword" in motion_type)
    
    for i in range(total_frames):
        progress = i / max(1, total_frames - 1)
        smooth_t = (1.0 - np.cos(progress * np.pi)) / 2.0
        
        # 1. Camera Framing & Crop
        if "Slow Zoom In" in motion_type:
            scale = 1.0 + 0.22 * smooth_t
            cw = int(target_w / scale)
            ch = int(target_h / scale)
            x1 = center_x + (target_w - cw) // 2
            y1 = center_y + (target_h - ch) // 2
            frame_img = base_img.crop((x1, y1, x1+cw, y1+ch)).resize((target_w, target_h), Image.Resampling.BILINEAR)
            
        elif "Slow Zoom Out" in motion_type:
            scale = 1.22 - 0.22 * smooth_t
            cw = int(target_w / scale)
            ch = int(target_h / scale)
            x1 = center_x + (target_w - cw) // 2
            y1 = center_y + (target_h - ch) // 2
            frame_img = base_img.crop((x1, y1, x1+cw, y1+ch)).resize((target_w, target_h), Image.Resampling.BILINEAR)
            
        elif "Pan Left-to-Right" in motion_type:
            x1 = int(max_offset_x * smooth_t)
            y1 = center_y
            frame_img = base_img.crop((x1, y1, x1+target_w, y1+target_h))
            
        elif "Pan Right-to-Left" in motion_type:
            x1 = int(max_offset_x * (1.0 - smooth_t))
            y1 = center_y
            frame_img = base_img.crop((x1, y1, x1+target_w, y1+target_h))
            
        elif "Shake & Pulse" in motion_type or is_action:
            shake_amp = 10.0 * (1.0 - 0.6 * smooth_t)
            dx = int(shake_amp * np.sin(progress * 45))
            dy = int(shake_amp * np.cos(progress * 35))
            pulse_scale = 1.06 + 0.06 * np.sin(progress * 10)
            cw = int(target_w / pulse_scale)
            ch = int(target_h / pulse_scale)
            x1 = max(0, min(margin_w - cw, center_x + dx))
            y1 = max(0, min(margin_h - ch, center_y + dy))
            frame_img = base_img.crop((x1, y1, x1+cw, y1+ch)).resize((target_w, target_h), Image.Resampling.BILINEAR)
            
            # Initial flash on impact
            if i < int(fps * 0.18):
                frame_img = ImageEnhance.Brightness(frame_img).enhance(1.40)
                
        else: # Subtle Float / Auto Dynamic
            scale = 1.05 + 0.05 * np.sin(progress * np.pi)
            dx = int(14 * np.sin(progress * np.pi * 2))
            cw = int(target_w / scale)
            ch = int(target_h / scale)
            x1 = max(0, min(margin_w - cw, center_x + dx))
            y1 = center_y
            frame_img = base_img.crop((x1, y1, x1+cw, y1+ch)).resize((target_w, target_h), Image.Resampling.BILINEAR)

        # 2. Add Dynamic Multi-Layer Action FX
        if enable_action_fx:
            fx_layer = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
            fx_draw = ImageDraw.Draw(fx_layer)
            
            # (A) Floating Anime Aura Particles
            for p in particles:
                p["x"] = (p["x"] + p["vx"]) % target_w
                p["y"] = (p["y"] + p["vy"]) % target_h
                r = p["size"]
                alpha = int(p["alpha"] * (0.6 + 0.4 * np.sin(progress * 6 + p["x"])))
                fx_draw.ellipse(
                    [p["x"] - r, p["y"] - r, p["x"] + r, p["y"] + r],
                    fill=(*p["color"], alpha)
                )
                
            # (B) Anime Action Speed Lines (Burst on action scenes)
            if is_action and (i % 6 < 4):
                cx, cy = target_w // 2, target_h // 2
                for angle_deg in range(0, 360, 20):
                    rad = math.radians(angle_deg + (i * 7) % 360)
                    start_dist = target_w * 0.40
                    end_dist = target_w * 0.75
                    x_start = cx + start_dist * math.cos(rad)
                    y_start = cy + start_dist * math.sin(rad)
                    x_end = cx + end_dist * math.cos(rad)
                    y_end = cy + end_dist * math.sin(rad)
                    fx_draw.line(
                        [(x_start, y_start), (x_end, y_end)],
                        fill=(255, 255, 255, 110),
                        width=int(np.random.uniform(2, 5))
                    )
                    
            # Composite FX
            frame_img = Image.alpha_composite(frame_img.convert("RGBA"), fx_layer).convert("RGB")

        # 3. Overlay Subtitles in Single Pass
        if subtitle_text and subtitle_text.strip():
            frame_img = draw_karaoke_subtitle_pil(
                img=frame_img,
                text=subtitle_text,
                is_vertical=is_vertical
            )
            
        writer.append_data(np.asarray(frame_img))
        
    writer.close()
    return str(out_file)


def generate_hf_video_clip(
    prompt: str,
    style_name: str = "Shonen Action Anime",
    output_path: str = "hf_anime.mp4"
) -> Optional[str]:
    """
    Generates a direct AI neural video clip via free public Hugging Face Spaces (AnimateDiff / Wan).
    """
    from gradio_client import Client
    try:
        style_info = ANIME_STYLES.get(style_name, ANIME_STYLES["Shonen Action Anime"])
        full_prompt = f"{style_info['prefix']}, {prompt}"
        negative = style_info.get("negative", "photorealistic, blurry, deformed")
        
        client = Client("KingNish/Animate-Diff-Lightning")
        result = client.predict(
            prompt=full_prompt,
            negative_prompt=negative,
            api_name="/generate"
        )
        if result and os.path.exists(result):
            import shutil
            shutil.copy(result, output_path)
            return output_path
    except Exception as e:
        print(f"[Visual Engine] Cloud Video generator notice: {e}")
    return None
