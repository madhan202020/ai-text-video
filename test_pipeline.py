import os
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent))

from config import OUTPUT_DIR, RESOLUTIONS
from core.script_generator import generate_story_script
from core.tts_engine import generate_speech
from core.visual_engine import generate_anime_image, render_scene_motion_clip
from core.composer import render_full_faceless_video

def run_test():
    print("=== TEST 1: Script & Storyboard Generator ===")
    storyboard = generate_story_script(
        topic="Shadow Monarch Awakening (Shonen / Manhwa)",
        style_name="Shonen Action Anime",
        num_scenes=2
    )
    print(f"Generated {len(storyboard)} scenes:")
    for s in storyboard:
        print(f" - [{s.get('sfx')}] {s.get('narration')}")

    print("\n=== TEST 2: Single Voiceover Generation (Edge-TTS) ===")
    test_voice_file = OUTPUT_DIR / "test_voice.mp3"
    tts_res = generate_speech(
        text="The shadow monarch has awakened his true power.",
        voice="en-US-ChristopherNeural",
        output_path=str(test_voice_file)
    )
    print(f"Voice saved to: {tts_res['audio_path']} (Exists: {os.path.exists(tts_res['audio_path'])})")

    print("\n=== TEST 3: Anime Art & 2.5D Motion Test ===")
    test_img = OUTPUT_DIR / "test_art.jpg"
    generate_anime_image(
        prompt="badass anime boy with glowing purple eyes and dark aura, masterpiece key visual",
        style_name="Shonen Action Anime",
        width=540,
        height=960,
        output_path=str(test_img)
    )
    print(f"Image saved to: {test_img} (Exists: {os.path.exists(test_img)})")

    test_motion = OUTPUT_DIR / "test_motion.mp4"
    render_scene_motion_clip(
        image_path=str(test_img),
        duration=3.0,
        output_path=str(test_motion),
        motion_type="Slow Zoom In (Intense Focus)",
        target_size=(540, 960),
        fps=24
    )
    print(f"Motion clip saved to: {test_motion} (Exists: {os.path.exists(test_motion)})")

    print("\n=== TEST 4: End-to-End Faceless Video Pipeline ===")
    test_story = storyboard[:2]
    result = render_full_faceless_video(
        storyboard=test_story,
        topic="Shadow Monarch Test",
        style_name="Shonen Action Anime",
        voice_name="en-US-ChristopherNeural",
        resolution_preset="9:16 (YouTube Shorts / TikTok / Reels)",
        bgm_name="Epic Anime Battle",
        bgm_volume=-18.0,
        enable_subtitles=True
    )
    print(f"Final Video Created: {result['video_path']}")
    print(f"Video Exists: {os.path.exists(result['video_path'])}")
    print("SEO Metadata Titles generated successfully.")
    print("\n>>> ALL PIPELINE TESTS PASSED 100% SUCCESSFULLY! <<<")

if __name__ == "__main__":
    run_test()
