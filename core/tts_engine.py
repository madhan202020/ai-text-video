import asyncio
import os
import edge_tts
from pathlib import Path
from typing import Dict, Any, List

async def generate_speech_async(
    text: str,
    voice: str = "en-US-ChristopherNeural",
    output_path: str = "output_speech.mp3",
    rate: str = "+5%",
    pitch: str = "+0Hz"
) -> Dict[str, Any]:
    """
    Generates high-quality neural voiceover using Edge-TTS (100% Free).
    Collects timing and boundary information.
    """
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    
    communicate = edge_tts.Communicate(
        text=text,
        voice=voice,
        rate=rate,
        pitch=pitch
    )
    
    word_timestamps = []
    
    # Save audio stream and capture word boundaries
    with open(out_file, "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                # offset & duration are in 100-nanosecond units (ticks)
                start_sec = chunk["offset"] / 10_000_000.0
                duration_sec = chunk["duration"] / 10_000_000.0
                word = chunk["text"]
                word_timestamps.append({
                    "word": word,
                    "start": start_sec,
                    "end": start_sec + duration_sec
                })

    return {
        "audio_path": str(out_file),
        "text": text,
        "word_timestamps": word_timestamps
    }


def generate_speech(
    text: str,
    voice: str = "en-US-ChristopherNeural",
    output_path: str = "output_speech.mp3",
    rate: str = "+5%",
    pitch: str = "+0Hz"
) -> Dict[str, Any]:
    """Synchronous wrapper for generate_speech_async"""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If inside an existing async loop (e.g. Gradio/Jupyter)
            import nest_asyncio
            nest_asyncio.apply()
            return loop.run_until_complete(
                generate_speech_async(text, voice, output_path, rate, pitch)
            )
        else:
            return loop.run_until_complete(
                generate_speech_async(text, voice, output_path, rate, pitch)
            )
    except Exception:
        return asyncio.run(
            generate_speech_async(text, voice, output_path, rate, pitch)
        )

