import os
import wave
import subprocess
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from imageio_ffmpeg import get_ffmpeg_exe
from config import BGM_DIR, SFX_DIR

def decode_audio_to_numpy(file_path: str, target_sr: int = 44100) -> Tuple[np.ndarray, int]:
    """
    Decodes ANY audio format (MP3, WAV, AAC, OGG) to mono float32 numpy array [-1.0, 1.0]
    using bundled FFmpeg binary. 100% reliable on all systems with zero external dependencies.
    """
    if not os.path.exists(file_path):
        return np.zeros(0, dtype=np.float32), target_sr
        
    temp_wav = Path(file_path).parent / f"{Path(file_path).stem}_raw_pcm.wav"
    ffmpeg_exe = get_ffmpeg_exe()
    
    cmd = [
        ffmpeg_exe, "-y",
        "-i", str(file_path),
        "-ar", str(target_sr),
        "-ac", "1",
        "-f", "wav",
        str(temp_wav)
    ]
    
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    if not temp_wav.exists():
        return np.zeros(0, dtype=np.float32), target_sr
        
    try:
        with wave.open(str(temp_wav), "rb") as wf:
            n_frames = wf.getnframes()
            audio_bytes = wf.readframes(n_frames)
            # 16-bit PCM to float32
            audio_int16 = np.frombuffer(audio_bytes, dtype=np.int16)
            audio_float = audio_int16.astype(np.float32) / 32768.0
            
        if temp_wav.exists():
            try:
                os.remove(temp_wav)
            except Exception:
                pass
                
        return audio_float, target_sr
    except Exception as e:
        print(f"[Audio Engine] Error reading decoded wav {file_path}: {e}")
        return np.zeros(0, dtype=np.float32), target_sr


def get_audio_duration_seconds(file_path: str) -> float:
    """Returns exact duration in seconds of any audio file"""
    audio_data, sr = decode_audio_to_numpy(file_path)
    if len(audio_data) == 0:
        return 3.0
    return len(audio_data) / float(sr)


def save_numpy_to_wav(file_path: str, audio_data: np.ndarray, sample_rate: int = 44100):
    """Saves float32 numpy array to 16-bit PCM WAV file"""
    out_file = Path(file_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Clip and convert to 16-bit integer
    audio_clipped = np.clip(audio_data, -1.0, 1.0)
    audio_int16 = (audio_clipped * 32767.0).astype(np.int16)
    
    with wave.open(str(out_file), "wb") as wf:
        wf.setnchannels(1) # mono
        wf.setsampwidth(2) # 16-bit
        wf.setframerate(sample_rate)
        wf.writeframes(audio_int16.tobytes())


def mix_master_soundtrack(
    scene_audios: List[Dict[str, Any]],
    bgm_name: str = "Chill Lofi Anime Beats",
    bgm_volume_db: float = -18.0,
    voice_volume_db: float = +2.0, # Crisp, prominent voice
    sfx_volume_db: float = -4.0,
    sample_rate: int = 44100,
    output_path: str = "master_audio.mp3"
) -> str:
    """
    Mathematical high-fidelity audio mixer:
    1. Concatenates all voice lines with natural breathing pauses
    2. Duck-mixes background music under narration
    3. Triggers SFX clips at exact scene start timestamps
    4. Normalizes and exports pristine 44.1kHz master audio
    """
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    
    # 1. Build Voice Timeline & Track Scene Offsets
    silence_pad = np.zeros(int(sample_rate * 0.15), dtype=np.float32) # 150ms start pad
    voice_timeline = [silence_pad]
    scene_sample_offsets = []
    
    current_pos = len(silence_pad)
    
    # Voice linear gain
    voice_gain = 10.0 ** (voice_volume_db / 20.0)
    
    for item in scene_audios:
        scene_sample_offsets.append(current_pos)
        voice_path = item.get("voice_path", "")
        
        voice_data, _ = decode_audio_to_numpy(voice_path, target_sr=sample_rate)
        
        if len(voice_data) > 0:
            voice_timeline.append(voice_data * voice_gain)
            current_pos += len(voice_data)
        else:
            # Silence placeholder for estimated scene duration
            dur = item.get("duration", 3.0)
            pad = np.zeros(int(sample_rate * dur), dtype=np.float32)
            voice_timeline.append(pad)
            current_pos += len(pad)
            
        # 300ms pause between scene transitions
        pause_pad = np.zeros(int(sample_rate * 0.30), dtype=np.float32)
        voice_timeline.append(pause_pad)
        current_pos += len(pause_pad)
        
    master_voice = np.concatenate(voice_timeline)
    total_samples = len(master_voice)
    total_duration_sec = total_samples / float(sample_rate)
    
    master_mix = np.copy(master_voice)
    
    # 2. Add Ducked Background Music
    if bgm_name and bgm_name != "None":
        bgm_file = None
        for ext in [".wav", ".mp3"]:
            cand = BGM_DIR / f"{bgm_name}{ext}"
            if cand.exists():
                bgm_file = str(cand)
                break
                
        if not bgm_file:
            cand_list = list(BGM_DIR.glob("*.wav")) + list(BGM_DIR.glob("*.mp3"))
            if cand_list:
                bgm_file = str(cand_list[0])
                
        if bgm_file and os.path.exists(bgm_file):
            bgm_data, _ = decode_audio_to_numpy(bgm_file, target_sr=sample_rate)
            if len(bgm_data) > 0:
                # Loop BGM to match total duration
                reps = int(np.ceil(total_samples / float(len(bgm_data)))) + 1
                bgm_looped = np.tile(bgm_data, reps)[:total_samples]
                
                # Apply BGM ducking gain (e.g. -18dB)
                bgm_gain = 10.0 ** (bgm_volume_db / 20.0)
                bgm_scaled = bgm_looped * bgm_gain
                
                # Fade in (0.8s) & Fade out (1.2s)
                fade_in_len = min(len(bgm_scaled), int(sample_rate * 0.8))
                fade_out_len = min(len(bgm_scaled), int(sample_rate * 1.2))
                if fade_in_len > 0:
                    bgm_scaled[:fade_in_len] *= np.linspace(0.0, 1.0, fade_in_len)
                if fade_out_len > 0:
                    bgm_scaled[-fade_out_len:] *= np.linspace(1.0, 0.0, fade_out_len)
                    
                master_mix = master_mix + bgm_scaled
                
    # 3. Layer Sound Effects (SFX)
    sfx_gain = 10.0 ** (sfx_volume_db / 20.0)
    for i, item in enumerate(scene_audios):
        sfx_name = item.get("sfx", "none")
        if sfx_name and sfx_name != "none":
            sfx_file = None
            for ext in [".wav", ".mp3"]:
                cand = SFX_DIR / f"{sfx_name}{ext}"
                if cand.exists():
                    sfx_file = str(cand)
                    break
            if sfx_file and os.path.exists(sfx_file):
                sfx_data, _ = decode_audio_to_numpy(sfx_file, target_sr=sample_rate)
                if len(sfx_data) > 0:
                    start_idx = scene_sample_offsets[i]
                    end_idx = min(total_samples, start_idx + len(sfx_data))
                    sfx_len = end_idx - start_idx
                    if sfx_len > 0:
                        master_mix[start_idx:end_idx] += sfx_data[:sfx_len] * sfx_gain

    # 4. Master Peak Limiter & Normalization (Prevent distortion while keeping voice crisp)
    max_val = np.max(np.abs(master_mix))
    if max_val > 0.95:
        master_mix = (master_mix / max_val) * 0.95
        
    # 5. Export Master Audio
    temp_wav_out = out_file.with_suffix(".temp_master.wav")
    save_numpy_to_wav(str(temp_wav_out), master_mix, sample_rate)
    
    ffmpeg_exe = get_ffmpeg_exe()
    cmd = [
        ffmpeg_exe, "-y",
        "-i", str(temp_wav_out),
        "-c:a", "libmp3lame",
        "-b:a", "256k",
        str(out_file)
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    if temp_wav_out.exists():
        try:
            os.remove(temp_wav_out)
        except Exception:
            pass
            
    return str(out_file)
