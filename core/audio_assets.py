import os
import math
import wave
import numpy as np
from pathlib import Path
from config import SFX_DIR, BGM_DIR

def apply_reverb(audio: np.ndarray, sample_rate: int = 44100, delay_ms: float = 80, decay: float = 0.35, passes: int = 4) -> np.ndarray:
    """Applies multi-tap stereo reverb to float32 audio"""
    out = np.copy(audio)
    for p in range(1, passes + 1):
        d_samples = int(sample_rate * (delay_ms * p / 1000.0))
        if d_samples < len(out):
            gain = decay ** p
            out[d_samples:] += audio[:-d_samples] * gain
    return np.clip(out, -1.0, 1.0)


def generate_default_sfx(force: bool = False):
    """
    Generates studio-grade, high-impact anime sound effects (WAV):
    - whoosh (cinematic air slice + sub drop)
    - sword_slash (metallic katana unsheath + blade clash)
    - dramatic_boom (massive 808 Hollywood sub-bass impact)
    - thunder_strike (lightning crack + rolling rumble)
    - magic_chime (crystalline anime sparkle chime tree)
    - laser_energy (sci-fi energy beam blast)
    - dragon_roar (guttural monster roar & sub bass)
    - heartbeat_suspense (cinematic heart thud tension)
    """
    sample_rate = 44100
    
    # 1. Cinematic Whoosh / Air Slice
    whoosh_path = SFX_DIR / "whoosh.wav"
    if not whoosh_path.exists() or force:
        dur = 0.75
        t = np.linspace(0, dur, int(sample_rate * dur), False)
        # Noise sweep with resonant pitch drop
        noise = np.random.uniform(-1, 1, len(t))
        env = (np.sin(np.pi * t / dur) ** 2)
        sweep_freq = 900.0 * np.exp(-3.5 * t) + 120.0
        phase = 2 * np.pi * np.cumsum(sweep_freq) / sample_rate
        sub_tone = np.sin(phase) * 0.5
        whoosh_wave = (noise * 0.45 + sub_tone) * env
        whoosh_wave = apply_reverb(whoosh_wave, sample_rate, delay_ms=45, decay=0.3)
        _save_wav(whoosh_path, whoosh_wave, sample_rate)

    # 2. Anime Katana Sword Slash
    slash_path = SFX_DIR / "sword_slash.wav"
    if not slash_path.exists() or force:
        dur = 0.65
        t = np.linspace(0, dur, int(sample_rate * dur), False)
        # Multi-frequency metallic blade clash (harmonics at 1800, 2900, 4400, 6200 Hz)
        metal = (
            0.4 * np.sin(2 * np.pi * 1850 * t) +
            0.3 * np.sin(2 * np.pi * 2920 * t) +
            0.2 * np.sin(2 * np.pi * 4400 * t) +
            0.15 * np.sin(2 * np.pi * 6180 * t)
        ) * np.exp(-14 * t)
        whip = np.random.uniform(-0.6, 0.6, len(t)) * (np.sin(np.pi * t / dur) ** 4)
        slash_wave = np.clip(metal * 0.75 + whip * 0.5, -1, 1)
        slash_wave = apply_reverb(slash_wave, sample_rate, delay_ms=30, decay=0.25)
        _save_wav(slash_path, slash_wave, sample_rate)

    # 3. Dramatic 808 Sub Boom / Impact
    boom_path = SFX_DIR / "dramatic_boom.wav"
    if not boom_path.exists() or force:
        dur = 2.4
        t = np.linspace(0, dur, int(sample_rate * dur), False)
        # Sub pitch dive from 140Hz down to 35Hz
        sub_freq = 110.0 * np.exp(-3.2 * t) + 38.0
        phase = 2 * np.pi * np.cumsum(sub_freq) / sample_rate
        sub = np.sin(phase) * np.exp(-1.4 * t)
        # Punch transient
        transient = np.random.uniform(-0.7, 0.7, len(t)) * np.exp(-25 * t)
        boom_wave = np.clip(sub * 0.85 + transient * 0.45, -1, 1)
        boom_wave = apply_reverb(boom_wave, sample_rate, delay_ms=80, decay=0.45)
        _save_wav(boom_path, boom_wave, sample_rate)

    # 4. Thunder Strike & Lightning Crack
    thunder_path = SFX_DIR / "thunder_strike.wav"
    if not thunder_path.exists() or force:
        dur = 2.8
        t = np.linspace(0, dur, int(sample_rate * dur), False)
        crack = np.random.uniform(-1, 1, len(t)) * np.exp(-16 * t)
        rumble = np.sin(2 * np.pi * (55 + 18 * np.sin(2 * np.pi * 3.5 * t)) * t) * np.exp(-1.1 * t)
        thunder_wave = np.clip(crack * 0.85 + rumble * 0.65, -1, 1)
        thunder_wave = apply_reverb(thunder_wave, sample_rate, delay_ms=110, decay=0.55, passes=5)
        _save_wav(thunder_path, thunder_wave, sample_rate)

    # 5. Magic Crystalline Chime
    chime_path = SFX_DIR / "magic_chime.wav"
    if not chime_path.exists() or force:
        dur = 2.0
        t = np.linspace(0, dur, int(sample_rate * dur), False)
        chime_wave = np.zeros_like(t)
        # Pentatonic shimmering bells (E6, G6, A6, B6, D7, E7)
        freqs = [1318.51, 1567.98, 1760.00, 1975.53, 2349.32, 2637.02]
        for i, f in enumerate(freqs):
            delay = i * 0.075
            idx = int(delay * sample_rate)
            if idx < len(t):
                seg_t = t[idx:] - delay
                bell = (np.sin(2 * np.pi * f * seg_t) + 0.4 * np.sin(2 * np.pi * f * 2.76 * seg_t)) * np.exp(-3.2 * seg_t)
                chime_wave[idx:] += bell * 0.22
        chime_wave = apply_reverb(chime_wave, sample_rate, delay_ms=90, decay=0.4)
        _save_wav(chime_path, chime_wave, sample_rate)

    # 6. Laser Energy Blast
    laser_path = SFX_DIR / "laser_energy.wav"
    if not laser_path.exists() or force:
        dur = 0.85
        t = np.linspace(0, dur, int(sample_rate * dur), False)
        # FM synthesis laser chirp
        mod = np.sin(2 * np.pi * 80 * t) * 400.0
        freq = (2800 * np.exp(-7.5 * t) + 180) + mod
        phase = 2 * np.pi * np.cumsum(freq) / sample_rate
        laser_wave = np.sin(phase) * np.exp(-2.8 * t)
        laser_wave = apply_reverb(laser_wave, sample_rate, delay_ms=40, decay=0.3)
        _save_wav(laser_path, laser_wave, sample_rate)

    # 7. Dragon Roar / Monster Growl
    roar_path = SFX_DIR / "dragon_roar.wav"
    if not roar_path.exists() or force:
        dur = 2.2
        t = np.linspace(0, dur, int(sample_rate * dur), False)
        growl_freq = 65 + 25 * np.sin(2 * np.pi * 14 * t)
        phase = 2 * np.pi * np.cumsum(growl_freq) / sample_rate
        saw = (2 * (phase / (2 * np.pi) % 1) - 1)
        noise = np.random.uniform(-0.5, 0.5, len(t))
        env = (np.sin(np.pi * t / dur) ** 1.5) * np.exp(-0.8 * t)
        roar_wave = np.clip((saw * 0.6 + noise * 0.4) * env, -1, 1)
        roar_wave = apply_reverb(roar_wave, sample_rate, delay_ms=80, decay=0.45)
        _save_wav(roar_path, roar_wave, sample_rate)

    # 8. Heartbeat Suspense Tension
    heart_path = SFX_DIR / "heartbeat_suspense.wav"
    if not heart_path.exists() or force:
        dur = 1.6
        t = np.linspace(0, dur, int(sample_rate * dur), False)
        heart_wave = np.zeros_like(t)
        for offset in [0.0, 0.28]:
            idx = int(offset * sample_rate)
            if idx < len(t):
                seg_t = t[idx:] - offset
                thump = np.sin(2 * np.pi * 50 * seg_t) * np.exp(-14 * seg_t)
                heart_wave[idx:] += thump * 0.85
        _save_wav(heart_path, heart_wave, sample_rate)


def generate_default_bgm(force: bool = False):
    """
    Generates rich, multi-instrument anime OST background tracks (WAV):
    - Epic Anime Battle (Driving brass chords, sub-bass 808s, rhythmic pulse)
    - Emotional & Wholesome (Ghibli vibe - Lush warm piano & strings)
    - Suspense & Dark Fantasy (Dissonant drones & tension pulse)
    - Chill Lofi Anime Beats (Warm Rhodes piano chords & vinyl beat)
    - Cyberpunk Neo-Tokyo Darksynth (Retro 80s synthwave arpeggio)
    """
    sample_rate = 44100
    
    # 1. Epic Anime Battle (D Minor Shonen Battle OST)
    epic_path = BGM_DIR / "Epic Anime Battle.wav"
    if not epic_path.exists() or force:
        duration = 32.0 # 32s loopable
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # 130 BPM tempo
        bpm = 130.0
        beat_len = 60.0 / bpm
        
        # Chords: Dm - Bb - C - Am
        chord_prog = [
            [146.83, 220.00, 293.66, 349.23], # Dm
            [116.54, 174.61, 233.08, 293.66], # Bb
            [130.81, 196.00, 261.63, 329.63], # C
            [110.00, 164.81, 220.00, 261.63]  # Am
        ]
        
        bgm_wave = np.zeros_like(t)
        chord_dur = duration / len(chord_prog) # 8s each
        
        for c_idx, chord in enumerate(chord_prog):
            s_idx = int(c_idx * chord_dur * sample_rate)
            e_idx = int((c_idx + 1) * chord_dur * sample_rate)
            seg_t = t[s_idx:e_idx] - (c_idx * chord_dur)
            
            # Brass & Strings Staccato (16th notes pulse)
            for freq in chord:
                brass_pulse = (np.sin(2 * np.pi * freq * seg_t) + 0.3 * np.sin(2 * np.pi * freq * 2 * seg_t)) * (np.sin(2 * np.pi * (bpm/60.0 * 2) * seg_t) ** 4)
                bgm_wave[s_idx:e_idx] += brass_pulse * 0.08
                
        # Driving 808 Sub-Bass line (D2 - Bb1 - C2 - A1)
        bass_notes = [73.42, 58.27, 65.41, 55.00]
        for c_idx, b_freq in enumerate(bass_notes):
            s_idx = int(c_idx * chord_dur * sample_rate)
            e_idx = int((c_idx + 1) * chord_dur * sample_rate)
            seg_t = t[s_idx:e_idx] - (c_idx * chord_dur)
            bass_wave = np.sin(2 * np.pi * b_freq * seg_t) * (0.7 + 0.3 * np.sin(2 * np.pi * (bpm/60.0 * 4) * seg_t) ** 2)
            bgm_wave[s_idx:e_idx] += bass_wave * 0.18
            
        # Percussion: Driving Kick on every beat + Snare on 2 and 4
        kick_env = (np.sin(2 * np.pi * (bpm/60.0) * t) ** 18) * 0.22
        kick_sound = kick_env * np.sin(2 * np.pi * 55 * t)
        
        snare_env = (np.sin(2 * np.pi * (bpm/120.0) * t + np.pi/2) ** 24) * 0.14
        snare_sound = snare_env * np.random.uniform(-1, 1, len(t))
        
        bgm_wave = np.clip((bgm_wave + kick_sound + snare_sound) * 0.85, -1, 1)
        bgm_wave = apply_reverb(bgm_wave, sample_rate, delay_ms=75, decay=0.25)
        _save_wav(epic_path, bgm_wave, sample_rate)

    # 2. Emotional & Wholesome (Studio Ghibli Nostalgia)
    ghibli_path = BGM_DIR / "Emotional & Wholesome (Ghibli vibe).wav"
    if not ghibli_path.exists() or force:
        duration = 32.0
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # Major 7th Piano Progression (Fmaj7 - Em7 - Dm7 - Cmaj7)
        chords = [
            [174.61, 261.63, 329.63, 392.00, 523.25], # Fmaj7
            [164.81, 246.94, 329.63, 392.00, 493.88], # Em7
            [146.83, 220.00, 261.63, 349.23, 440.00], # Dm7
            [130.81, 196.00, 261.63, 329.63, 392.00]  # Cmaj7
        ]
        
        bgm_wave = np.zeros_like(t)
        chord_dur = duration / len(chords)
        
        for c_idx, chord in enumerate(chords):
            s_idx = int(c_idx * chord_dur * sample_rate)
            e_idx = int((c_idx + 1) * chord_dur * sample_rate)
            seg_t = t[s_idx:e_idx] - (c_idx * chord_dur)
            for f in chord:
                # Warm piano tone with gentle harmonic decay
                tone = (np.sin(2 * np.pi * f * seg_t) + 0.25 * np.sin(2 * np.pi * f * 2 * seg_t)) * np.exp(-0.45 * (seg_t % 2.0))
                bgm_wave[s_idx:e_idx] += tone * 0.08
                
        # Pentatonic music box arpeggio on top
        melody_notes = [523.25, 659.25, 783.99, 1046.50, 1318.51, 1046.50, 783.99, 659.25]
        for m_idx in range(int(duration * 2)):
            note = melody_notes[m_idx % len(melody_notes)]
            s_t = m_idx * 0.5
            idx = int(s_t * sample_rate)
            if idx < len(t):
                seg_t = t[idx:] - s_t
                bell = np.sin(2 * np.pi * note * seg_t) * np.exp(-4.5 * seg_t)
                bgm_wave[idx:] += bell * 0.06
                
        bgm_wave = np.clip(bgm_wave * 0.85, -1, 1)
        bgm_wave = apply_reverb(bgm_wave, sample_rate, delay_ms=110, decay=0.4)
        _save_wav(ghibli_path, bgm_wave, sample_rate)

    # 3. Chill Lofi Anime Beats
    lofi_path = BGM_DIR / "Chill Lofi Anime Beats.wav"
    if not lofi_path.exists() or force:
        duration = 32.0
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # Cm9 - Fm9 - Bb13 - Ebmaj9
        chords = [
            [261.63, 311.13, 392.00, 466.16, 587.33],
            [349.23, 415.30, 523.25, 622.25, 783.99],
            [233.08, 293.66, 349.23, 440.00, 523.25],
            [311.13, 392.00, 466.16, 587.33, 698.46]
        ]
        
        bgm_wave = np.zeros_like(t)
        chord_dur = duration / len(chords)
        
        for c_idx, chord in enumerate(chords):
            s_idx = int(c_idx * chord_dur * sample_rate)
            e_idx = int((c_idx + 1) * chord_dur * sample_rate)
            seg_t = t[s_idx:e_idx] - (c_idx * chord_dur)
            for f in chord:
                # Rhodes electric piano warm chorused tone
                rhodes = np.sin(2 * np.pi * f * seg_t + 0.1 * np.sin(2 * np.pi * 2 * seg_t)) * np.exp(-0.35 * (seg_t % 2.0))
                bgm_wave[s_idx:e_idx] += rhodes * 0.08
                
        # Lofi Vinyl Crackle + Boom Bap Kick & Snare (85 BPM)
        lofi_bpm = 85.0
        kick = (np.sin(2 * np.pi * (lofi_bpm/60.0) * t) ** 14) * 0.18 * np.sin(2 * np.pi * 50 * t)
        snare = (np.sin(2 * np.pi * (lofi_bpm/120.0) * t + np.pi/2) ** 20) * 0.09 * np.random.uniform(-1, 1, len(t))
        vinyl = np.random.uniform(-0.02, 0.02, len(t))
        
        bgm_wave = np.clip((bgm_wave + kick + snare + vinyl) * 0.85, -1, 1)
        bgm_wave = apply_reverb(bgm_wave, sample_rate, delay_ms=65, decay=0.25)
        _save_wav(lofi_path, bgm_wave, sample_rate)

    # 4. Suspense & Dark Fantasy
    suspense_path = BGM_DIR / "Suspense & Dark Fantasy.wav"
    if not suspense_path.exists() or force:
        duration = 32.0
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        # Low beating D-minor drone + sub-bass pulse
        drone = 0.28 * (np.sin(2 * np.pi * 55 * t) + 0.6 * np.sin(2 * np.pi * 58.27 * t))
        pulse = 0.18 * np.sin(2 * np.pi * 110 * t) * (np.sin(2 * np.pi * 0.8 * t) ** 6)
        high_string = 0.06 * np.sin(2 * np.pi * 1174.66 * t) * (np.sin(2 * np.pi * 0.2 * t) ** 2)
        suspense_wave = np.clip((drone + pulse + high_string) * 0.85, -1, 1)
        suspense_wave = apply_reverb(suspense_wave, sample_rate, delay_ms=130, decay=0.5)
        _save_wav(suspense_path, suspense_wave, sample_rate)

    # 5. Upbeat & Adventurous (Shonen Opening Style)
    upbeat_path = BGM_DIR / "Upbeat & Adventurous.wav"
    if not upbeat_path.exists() or force:
        duration = 32.0
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        bpm = 140.0
        chords = [
            [261.63, 329.63, 392.00, 523.25], # C
            [196.00, 246.94, 293.66, 392.00], # G
            [220.00, 261.63, 329.63, 440.00], # Am
            [174.61, 220.00, 261.63, 349.23]  # F
        ]
        bgm_wave = np.zeros_like(t)
        chord_dur = duration / len(chords)
        for c_idx, chord in enumerate(chords):
            s_idx = int(c_idx * chord_dur * sample_rate)
            e_idx = int((c_idx + 1) * chord_dur * sample_rate)
            seg_t = t[s_idx:e_idx] - (c_idx * chord_dur)
            for f in chord:
                synth = (np.sin(2 * np.pi * f * seg_t) + 0.3 * np.sin(2 * np.pi * f * 2 * seg_t)) * (np.sin(2 * np.pi * (bpm/60.0 * 2) * seg_t) ** 2)
                bgm_wave[s_idx:e_idx] += synth * 0.08
                
        kick = (np.sin(2 * np.pi * (bpm/60.0) * t) ** 16) * 0.20 * np.sin(2 * np.pi * 60 * t)
        bgm_wave = np.clip((bgm_wave + kick) * 0.85, -1, 1)
        bgm_wave = apply_reverb(bgm_wave, sample_rate, delay_ms=60, decay=0.25)
        _save_wav(upbeat_path, bgm_wave, sample_rate)


def _save_wav(filepath: Path, audio_data: np.ndarray, sample_rate: int):
    """Saves float numpy array [-1.0, 1.0] to 16-bit PCM WAV file"""
    audio_int16 = (np.clip(audio_data, -1.0, 1.0) * 32767.0).astype(np.int16)
    with wave.open(str(filepath), 'wb') as wf:
        wf.setnchannels(1) # mono
        wf.setsampwidth(2) # 16 bit
        wf.setframerate(sample_rate)
        wf.writeframes(audio_int16.tobytes())
