import json
import re
import urllib.parse
import urllib.request
import requests
from typing import List, Dict, Any

DEFAULT_TEMPLATES = {
    "Shadow Monarch Awakening (Shonen / Manhwa)": [
        {
            "narration": "They called him the weakest hunter in the world... until he walked through the forbidden dungeon gate.",
            "visual_prompt": "weak injured anime boy standing alone before a giant glowing purple ancient dungeon portal, dark atmospheric cavern",
            "motion": "Slow Zoom In (Intense Focus)",
            "sfx": "whoosh"
        },
        {
            "narration": "A glowing holographic system appeared before his eyes: [You have been chosen as the Shadow Sovereign].",
            "visual_prompt": "glowing blue and purple holographic system screen floating in front of shock anime character face, neon runes, glowing eyes",
            "motion": "Anime Action Shake & Pulse",
            "sfx": "magic_chime"
        },
        {
            "narration": "From the shadows beneath his feet, an army of spectral knights arose, bowing to their new king.",
            "visual_prompt": "army of glowing purple shadow knights rising from the ground, glowing dark energy, epic anime army formation",
            "motion": "Slow Zoom Out (Epic Reveal)",
            "sfx": "dramatic_boom"
        },
        {
            "narration": "His eyes flared with unstoppable power. The hunter had become the absolute ruler.",
            "visual_prompt": "badass anime boy with glowing purple eyes and dark aura smiling in victory, cinematic masterpiece key visual",
            "motion": "Cinematic Pan Left-to-Right",
            "sfx": "thunder_strike"
        }
    ],
    "The Whispering Spirit Shrine (Ghibli Aesthetic)": [
        {
            "narration": "Deep inside the misty mountains of Kyoto lies a hidden shrine forgotten by modern time.",
            "visual_prompt": "ancient Japanese Shinto shrine in lush green mossy forest with soft sunlight rays and floating glowing dust particles, Studio Ghibli style",
            "motion": "Slow Zoom In (Intense Focus)",
            "sfx": "whoosh"
        },
        {
            "narration": "Every midnight, the spirit lantern flickers, and gentle forest spirits gather around the pond.",
            "visual_prompt": "cute glowing forest spirits floating around a stone lantern and water lilies in serene pond at night, soft watercolor anime style",
            "motion": "Subtle Float",
            "sfx": "magic_chime"
        },
        {
            "narration": "A lone traveler bowed respectfully, and the ancient guardian spirit granted them a blessing of courage.",
            "visual_prompt": "young anime girl in traditional travel kimono bowing respectfully to a majestic giant white glowing spirit wolf, magical atmosphere",
            "motion": "Cinematic Pan Right-to-Left",
            "sfx": "none"
        },
        {
            "narration": "Some say whoever finds this shrine will never walk alone in darkness again.",
            "visual_prompt": "panoramic scenic view of lush enchanted forest with cherry blossoms blowing in the wind at sunrise, breathtaking Ghibli anime landscape",
            "motion": "Slow Zoom Out (Epic Reveal)",
            "sfx": "magic_chime"
        }
    ],
    "Cyberpunk Neo-Tokyo Outlaw": [
        {
            "narration": "In the year 2099, the neon lights of Neo-Tokyo hide the world's most dangerous secret.",
            "visual_prompt": "cyberpunk anime city skyline at night with rain, massive neon holographic billboards, flying vehicles, dark alley reflections",
            "motion": "Cinematic Pan Left-to-Right",
            "sfx": "whoosh"
        },
        {
            "narration": "Ren, a rogue cyber-ninja, infiltrated the Megacorp tower to recover the forbidden memory chip.",
            "visual_prompt": "cyberpunk anime ninja crouching on top of skyscraper rooftop in rain, glowing cyan cybernetic mask and dual energy blades",
            "motion": "Slow Zoom In (Intense Focus)",
            "sfx": "laser_energy"
        },
        {
            "narration": "Red alarm sirens flared as robotic enforcers surrounded the sector.",
            "visual_prompt": "futuristic combat androids with glowing red eyes aiming laser rifles down a futuristic corridor, intense anime action scene",
            "motion": "Anime Action Shake & Pulse",
            "sfx": "dramatic_boom"
        },
        {
            "narration": "With one swift slash of his plasma blade, he disappeared into the electric night.",
            "visual_prompt": "cyber ninja leaping through broken glass window into the rainy night sky, dynamic action pose, neon city backdrop",
            "motion": "Slow Zoom Out (Epic Reveal)",
            "sfx": "sword_slash"
        }
    ]
}


def generate_story_script(
    topic: str,
    style_name: str = "Shonen Action Anime",
    num_scenes: int = 4,
    video_format: str = "9:16 (YouTube Shorts / TikTok / Reels)",
    custom_api_key: str = ""
) -> List[Dict[str, Any]]:
    """
    Generates a structured YouTube faceless storyboard (scenes with narration, visual prompts, motion, SFX).
    Uses 100% Free AI endpoints (Pollinations Text LLM) with graceful offline template fallback.
    """
    if not topic or not topic.strip():
        # Pick default
        return list(DEFAULT_TEMPLATES.values())[0]

    # Check if matching template directly
    for template_name, scenes in DEFAULT_TEMPLATES.items():
        if topic.lower() in template_name.lower():
            return scenes

    prompt_instruction = f"""
You are a viral YouTube Shorts and Anime Director specializing in high-retention faceless anime videos.
Create a captivating {num_scenes}-scene anime story for the topic: "{topic}".
Style: {style_name}.
Target Format: {video_format}.

Respond ONLY with a valid JSON array of {num_scenes} objects. No markdown ticks, no preamble, no explanations.
Each JSON object must have these exact keys:
1. "narration": One punchy, engaging sentence to be spoken by voiceover (hook the viewer, build tension, or provide satisfying climax).
2. "visual_prompt": A detailed 2D anime image prompt describing the subject, action, lighting, and environment without any artist names or watermarks.
3. "motion": Pick one from ["Slow Zoom In (Intense Focus)", "Slow Zoom Out (Epic Reveal)", "Cinematic Pan Left-to-Right", "Cinematic Pan Right-to-Left", "Anime Action Shake & Pulse", "Subtle Float"].
4. "sfx": Pick one from ["whoosh", "sword_slash", "dramatic_boom", "thunder_strike", "magic_chime", "laser_energy", "none"].

Example JSON output:
[
  {{
    "narration": "Deep within the cursed abyss, a lone warrior awakened a dormant power.",
    "visual_prompt": "young anime warrior with glowing aura standing in dark crystalline cavern, dramatic lighting, intense focus",
    "motion": "Slow Zoom In (Intense Focus)",
    "sfx": "whoosh"
  }}
]
"""

    # Try Free Pollinations AI text endpoint
    try:
        url = "https://text.pollinations.ai/"
        payload = {
            "messages": [
                {"role": "system", "content": "You are a specialized JSON-only generator for YouTube anime video storyboards."},
                {"role": "user", "content": prompt_instruction}
            ],
            "model": "openai",
            "jsonMode": True
        }
        
        headers = {"Content-Type": "application/json"}
        resp = requests.post(url, json=payload, headers=headers, timeout=15)
        
        if resp.status_code == 200:
            raw_text = resp.text.strip()
            # Clean possible markdown wrapping
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.startswith("```"):
                raw_text = raw_text[3:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]
            raw_text = raw_text.strip()
            
            # Find json array
            match = re.search(r'\[.*\]', raw_text, re.DOTALL)
            if match:
                parsed = json.loads(match.group(0))
                if isinstance(parsed, list) and len(parsed) > 0:
                    return parsed[:num_scenes]
    except Exception as e:
        print(f"[Script Generator] Free online LLM notice: {e}, using smart dynamic synthesizer...")

    # Dynamic fallback generator based on topic
    return _synthesize_dynamic_script(topic, style_name, num_scenes)


def _synthesize_dynamic_script(topic: str, style_name: str, num_scenes: int) -> List[Dict[str, Any]]:
    """Synthesizes structured anime scenes tailored to the user's topic dynamically"""
    clean_topic = topic.strip()
    
    scenes = [
        {
            "narration": f"In a world where destiny is forged in battle, the legend of {clean_topic} began.",
            "visual_prompt": f"dramatic anime scene of {clean_topic}, epic atmospheric landscape, cinematic anime key visual, stunning lighting",
            "motion": "Slow Zoom In (Intense Focus)",
            "sfx": "whoosh"
        },
        {
            "narration": "An ancient power surged through the atmosphere, altering the fate of all who witnessed it.",
            "visual_prompt": f"anime character channeling mystical glowing energy related to {clean_topic}, glowing eyes, swirling particles",
            "motion": "Anime Action Shake & Pulse",
            "sfx": "magic_chime"
        },
        {
            "narration": "When darkness threatened to engulf everything, a decisive strike shattered the barrier.",
            "visual_prompt": f"dynamic anime battle clash, explosive vibrant energy waves, intense motion, detailed anime art",
            "motion": "Cinematic Pan Left-to-Right",
            "sfx": "dramatic_boom"
        },
        {
            "narration": f"And from the remnants of the clash, the true power of {clean_topic} was revealed forever.",
            "visual_prompt": f"triumphant anime hero standing atop a hill overlooking a breathtaking world at sunrise, masterpiece anime scenery",
            "motion": "Slow Zoom Out (Epic Reveal)",
            "sfx": "thunder_strike"
        }
    ]
    return scenes[:num_scenes]

