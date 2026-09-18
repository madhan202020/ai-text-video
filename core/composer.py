import os
import time
import shutil
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional, Callable
import imageio
from imageio_ffmpeg import get_ffmpeg_exe
import numpy as np

from config import OUTPUT_DIR, RESOLUTIONS, ANIME_STYLES
from core.tts_engine import generate_speech
from core.visual_engine import generate_anime_image, render_scene_motion_clip
from core.audio_engine import mix_master_soundtrack, get_audio_duration_seconds
from core.audio_assets import generate_default_sfx, generate_default_bgm
from core.seo_generator import generate_youtube_seo_metadata

def render_full_faceless_video(
    storyboard: List[Dict[str, Any]],
    topic: str,
    style_name: str = "Shonen Action Anime",
    voice_name: str = "en-US-ChristopherNeural",
    resolution_preset: str = "9:16 (YouTube Shorts / TikTok / Reels)",
    bgm_name: str = "Chill Lofi Anime Beats",
    bgm_volume: float = -18.0,
    enable_subtitles: bool = True,
    enable_action_fx: bool = True,
    progress_callback: Optional[Callable[[float, str], None]] = None
) -> Dict[str, Any]:
    """
    Assembles the complete AI Anime Faceless Video:
    1. Generates voiceovers and calculates exact durations
    2. Generates high-res anime artwork for each scene
    3. Renders 2.5D camera motions with multi-layer action FX and subtitles
    4. Mixes ducked BGM and sound effects using high-fidelity numpy audio engine
    5. Muxes video & audio into a high-bitrate 1080p MP4 file
    6. Generates YouTube SEO Metadata
    """
    generate_default_sfx()
    generate_default_bgm()

    timestamp_id = int(time.time())
    project_dir = OUTPUT_DIR / f"project_{timestamp_id}"
    project_dir.mkdir(parents=True, exist_ok=True)
    
    res_info = RESOLUTIONS.get(resolution_preset, RESOLUTIONS["9:16 (YouTube Shorts / TikTok / Reels)"])
    target_w = res_info["width"]
    target_h = res_info["height"]
    is_vertical = (res_info["aspect"] == "9:16")
    
    total_scenes = len(storyboard)
    scene_clips = []
    scene_audios = []
    
    if progress_callback:
        progress_callback(0.05, f"Initializing project for '{topic}'...")

    # Phase 1: Process each scene (Voiceover + Visual Art + Motion Rendering)
    for idx, scene in enumerate(storyboard):
        scene_num = idx + 1
        narration = scene.get("narration", "").strip()
        visual_prompt = scene.get("visual_prompt", "").strip()
        motion_type = scene.get("motion", "Slow Zoom In (Intense Focus)")
        sfx_type = scene.get("sfx", "whoosh")
        
        step_base = 0.05 + (idx / total_scenes) * 0.70
        
        # 1. Voiceover Generation
        if progress_callback:
            progress_callback(step_base + 0.02, f"Scene {scene_num}/{total_scenes}: Synthesizing Neural Voiceover...")
            
        voice_file = project_dir / f"scene_{scene_num}_voice.mp3"
        tts_res = generate_speech(narration, voice=voice_name, output_path=str(voice_file))
        
        # Exact audio duration measurement
        voice_duration = get_audio_duration_seconds(str(voice_file))
        scene_total_duration = max(2.5, voice_duration + 0.35)
        
        scene_audios.append({
            "voice_path": str(voice_file),
            "duration": scene_total_duration,
            "sfx": sfx_type
        })
        
        # 2. Anime Artwork Generation
        if progress_callback:
            progress_callback(step_base + 0.10, f"Scene {scene_num}/{total_scenes}: Generating 1080p Anime Visual...")
            
        image_file = project_dir / f"scene_{scene_num}_art.jpg"
        generate_anime_image(
            prompt=visual_prompt,
            style_name=style_name,
            width=target_w,
            height=target_h,
            output_path=str(image_file),
            seed=timestamp_id + idx * 777
        )
        
        # 3. Dynamic Video Motion + Action FX + Single-pass Subtitles
        if progress_callback:
            progress_callback(step_base + 0.18, f"Scene {scene_num}/{total_scenes}: Rendering HD Camera Motion & Anime FX...")
            
        motion_file = project_dir / f"scene_{scene_num}_motion.mp4"
        sub_text = narration if enable_subtitles else None
        
        render_scene_motion_clip(
            image_path=str(image_file),
            duration=scene_total_duration,
            output_path=str(motion_file),
            motion_type=motion_type,
            subtitle_text=sub_text,
            target_size=(target_w, target_h),
            is_vertical=is_vertical,
            fps=24,
            enable_action_fx=enable_action_fx
        )
        scene_clips.append(str(motion_file))

    # Phase 2: Master Audio Mixing (Voiceover + BGM Ducking + SFX)
    if progress_callback:
        progress_callback(0.80, "Mixing High-Fidelity Master Audio (Crystal-Clear Voice + Ducked BGM)...")
        
    master_audio_file = project_dir / "master_soundtrack.mp3"
    mix_master_soundtrack(
        scene_audios=scene_audios,
        bgm_name=bgm_name,
        bgm_volume_db=bgm_volume,
        voice_volume_db=+2.0, # Crisp, prominent narrator
        output_path=str(master_audio_file)
    )

    # Phase 3: Fast Lossless Stitching & Audio Muxing
    if progress_callback:
        progress_callback(0.88, "Stitching Scenes & Muxing 1080p MP4...")
        
    final_video_file = project_dir / f"final_faceless_video_{timestamp_id}.mp4"
    _mux_final_video_fast(
        video_clips=scene_clips,
        audio_file=str(master_audio_file),
        output_file=str(final_video_file),
        target_size=(target_w, target_h),
        fps=24
    )

    # Phase 4: Generate SEO Metadata
    if progress_callback:
        progress_callback(0.96, "Generating Viral YouTube SEO Metadata...")
        
    seo_metadata = generate_youtube_seo_metadata(topic, style_name, storyboard)

    if progress_callback:
        progress_callback(1.0, "Complete! 1080p Video Ready for YouTube!")

    return {
        "video_path": str(final_video_file),
        "project_dir": str(project_dir),
        "seo_metadata": seo_metadata,
        "scene_count": len(storyboard)
    }


def _mux_final_video_fast(
    video_clips: List[str],
    audio_file: str,
    output_file: str,
    target_size: Tuple[int, int],
    fps: int = 24
):
    """Fast, high-bitrate video concatenation and audio muxing using imageio_ffmpeg"""
    ffmpeg_exe = get_ffmpeg_exe()
    parent_dir = Path(output_file).parent
    
    # Create FFmpeg concat list file
    concat_list_file = parent_dir / "concat_list.txt"
    with open(concat_list_file, "w", encoding="utf-8") as f:
        for clip in video_clips:
            clean_path = str(Path(clip).resolve()).replace("\\", "/")
            f.write(f"file '{clean_path}'\n")
            
    concat_temp = parent_dir / "concat_temp.mp4"
    
    # 1. Lossless video concat
    cmd_concat = [
        ffmpeg_exe, "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_list_file),
        "-c", "copy",
        str(concat_temp)
    ]
    subprocess.run(cmd_concat, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # 2. Mux audio and video with high quality AAC 256k
    cmd_mux = [
        ffmpeg_exe, "-y",
        "-i", str(concat_temp),
        "-i", str(audio_file),
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "256k",
        "-shortest",
        str(output_file)
    ]
    subprocess.run(cmd_mux, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    if not os.path.exists(output_file) or os.path.getsize(output_file) == 0:
        if os.path.exists(concat_temp):
            shutil.copy(str(concat_temp), output_file)
            
    # Cleanup intermediate files
    for tmp in [concat_temp, concat_list_file]:
        if tmp.exists():
            try:
                os.remove(tmp)
            except Exception:
                pass
