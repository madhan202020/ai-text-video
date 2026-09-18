import os
import functools
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from typing import List, Dict, Any, Tuple
from config import FONTS_DIR

@functools.lru_cache(maxsize=32)
def get_subtitle_font(font_size: int = 48) -> ImageFont.FreeTypeFont:
    """Gets and caches a bold font for subtitles, with fallback to standard system fonts"""
    for font_file in FONTS_DIR.glob("*.ttf"):
        try:
            return ImageFont.truetype(str(font_file), font_size)
        except Exception:
            pass
            
    system_fonts = [
        "C:\\Windows\\Fonts\\impact.ttf",
        "C:\\Windows\\Fonts\\arialbd.ttf",
        "C:\\Windows\\Fonts\\segoeuib.ttf",
        "C:\\Windows\\Fonts\\tahomabd.ttf"
    ]
    for sf in system_fonts:
        if os.path.exists(sf):
            try:
                return ImageFont.truetype(sf, font_size)
            except Exception:
                pass
                
    return ImageFont.load_default()


def draw_karaoke_subtitle_pil(
    img: Image.Image,
    text: str,
    is_vertical: bool = True,
    text_color: str = "#FFFFFF",
    stroke_color: str = "#000000",
    stroke_width: int = 5
) -> Image.Image:
    """
    Renders anime styled subtitle directly on PIL Image using cached fonts.
    Blazing fast, zero array conversions.
    """
    if not text or not text.strip():
        return img

    w, h = img.size
    draw = ImageDraw.Draw(img)
    
    base_font_size = int(h * 0.042) if is_vertical else int(h * 0.052)
    font = get_subtitle_font(base_font_size)
    
    # Text wrapping
    words = text.strip().split()
    lines = []
    current_line = []
    max_chars_per_line = 24 if is_vertical else 40
    
    for word in words:
        if sum(len(w) for w in current_line) + len(current_line) + len(word) <= max_chars_per_line:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]
    if current_line:
        lines.append(" ".join(current_line))
        
    line_spacing = int(base_font_size * 1.25)
    total_text_h = len(lines) * line_spacing
    
    if is_vertical:
        start_y = int(h * 0.70) - (total_text_h // 2)
    else:
        start_y = int(h * 0.80) - (total_text_h // 2)
        
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        text_w = bbox[2] - bbox[0]
        text_x = (w - text_w) // 2
        text_y = start_y + (i * line_spacing)
        
        # Shadow
        draw.text(
            (text_x + 3, text_y + 3),
            line,
            font=font,
            fill="#000000"
        )
        
        # Stroke / Border
        draw.text(
            (text_x, text_y),
            line,
            font=font,
            fill=text_color,
            stroke_width=stroke_width,
            stroke_fill=stroke_color
        )
        
    return img


def draw_karaoke_subtitle_frame(
    frame_rgb: np.ndarray,
    text: str,
    target_size: Tuple[int, int] = (1080, 1920),
    is_vertical: bool = True,
    text_color: str = "#FFFFFF",
    stroke_color: str = "#000000",
    stroke_width: int = 5
) -> np.ndarray:
    """Numpy array wrapper around draw_karaoke_subtitle_pil"""
    if not text or not text.strip():
        return frame_rgb
    img = Image.fromarray(frame_rgb)
    img = draw_karaoke_subtitle_pil(img, text, is_vertical, text_color, stroke_color, stroke_width)
    return np.asarray(img)
