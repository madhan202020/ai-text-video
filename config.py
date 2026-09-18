import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
FONTS_DIR = ASSETS_DIR / "fonts"
BGM_DIR = ASSETS_DIR / "bgm"
SFX_DIR = ASSETS_DIR / "sfx"
OUTPUT_DIR = BASE_DIR / "output"

# Ensure directories exist
for folder in [ASSETS_DIR, FONTS_DIR, BGM_DIR, SFX_DIR, OUTPUT_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

# Video Formats / Resolutions
RESOLUTIONS = {
    "9:16 (YouTube Shorts / TikTok / Reels)": {"width": 1080, "height": 1920, "aspect": "9:16"},
    "16:9 (YouTube Longform / Widescreen)": {"width": 1920, "height": 1080, "aspect": "16:9"},
    "1:1 (Square Feed)": {"width": 1080, "height": 1080, "aspect": "1:1"}
}

# Anime & Cartoon Styles with prompt boosters and negative prompts
ANIME_STYLES = {
    "Shonen Action Anime": {
        "prefix": "masterpiece, best quality, ultra detailed, modern 2D shonen anime style, dynamic lighting, sharp anime cel shading, vibrant colors, cinematic composition, anime key visual",
        "negative": "photorealistic, 3D, CGI, realistic photo, blurry, bad anatomy, deformed eyes, disfigured, extra limbs, low resolution, watermark, text"
    },
    "Studio Ghibli Aesthetic": {
        "prefix": "masterpiece, best quality, Studio Ghibli aesthetic, hand-drawn anime scenery, soft watercolor texture, nostalgic atmosphere, lush painted background, Miyazaki style, detailed sky",
        "negative": "photorealistic, harsh 3D, neon cyberpunk, low quality, blurry, distorted, digital 3d render"
    },
    "Dark Fantasy & Cyberpunk Anime": {
        "prefix": "masterpiece, best quality, dark fantasy anime, cyberpunk neon glow, dramatic cinematic anime lighting, atmospheric fog, intense shadows, highly detailed illustration, 8k wallpaper",
        "negative": "cute chibi, oversaturated flat cartoon, photorealistic, bad quality, blurry, low resolution"
    },
    "Cute 2D Chibi / Cartoon": {
        "prefix": "cute 2d cartoon anime, adorable chibi character style, bright cheerful colors, clean vector lines, playful storybook illustration, kawaii expression",
        "negative": "dark, horror, photorealistic, gritty, violent, blurry, bad art"
    },
    "Korean Webtoon / Manhwa": {
        "prefix": "masterpiece, best quality, modern Korean webtoon art style, manhwa digital illustration, sharp character features, glowing eyes, stylized manhwa lighting, dramatic webtoon panel",
        "negative": "photorealistic, western comic, blurry, deformed hands, low quality"
    },
    "Classic 90s Retro Anime": {
        "prefix": "masterpiece, 1990s retro anime aesthetic, vintage cel animation, grain texture, classic anime character design, nostalgic color palette, 90s anime screenshot",
        "negative": "modern 3D CGI, hyperrealistic, blurry, ugly, distorted"
    }
}

# Free Edge-TTS Voices
VOICE_PROFILES = {
    "Epic Anime Narrator (Male - Deep & Dramatic)": "en-US-ChristopherNeural",
    "Anime Storyteller (Male - Engaging & Energetic)": "en-US-GuyNeural",
    "Anime Heroine / Narrator (Female - Expressive)": "en-US-AriaNeural",
    "Cute Anime Girl (Female - Bright & Sweet)": "en-US-AnaNeural",
    "Wise Old Sensei / Mythic (Male - British Deep)": "en-GB-RyanNeural",
    "Japanese Anime Girl (Female - Subbed Style)": "ja-JP-NanamiNeural",
    "Japanese Anime Hero (Male - Shonen Subbed)": "ja-JP-KeitaNeural",
    "Hindi Storyteller (Male - Indian Voice)": "hi-IN-MadhurNeural",
    "Hindi Storyteller (Female - Indian Voice)": "hi-IN-SwaraNeural"
}

# Sound Effect (SFX) Preset Types
SFX_PRESETS = [
    "none",
    "whoosh",
    "sword_slash",
    "dramatic_boom",
    "thunder_strike",
    "magic_chime",
    "dragon_roar",
    "heartbeat_suspense",
    "laser_energy"
]

# BGM Mood Presets
BGM_MOODS = [
    "Epic Anime Battle",
    "Emotional & Wholesome (Ghibli vibe)",
    "Suspense & Dark Fantasy",
    "Chill Lofi Anime Beats",
    "Upbeat & Adventurous",
    "None"
]

# Camera Motion Options for 2.5D Anime Rendering
CAMERA_MOTIONS = [
    "Auto Dynamic (Smart Flow)",
    "Slow Zoom In (Intense Focus)",
    "Slow Zoom Out (Epic Reveal)",
    "Cinematic Pan Left-to-Right",
    "Cinematic Pan Right-to-Left",
    "Anime Action Shake & Pulse",
    "Subtle Float"
]

