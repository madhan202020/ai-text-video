from typing import Dict, Any, List

def generate_youtube_seo_metadata(
    topic: str,
    style_name: str,
    storyboard: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Generates viral YouTube metadata (Titles, Description, Timestamps, Tags, Hashtags)
    to maximize CTR and view retention on YouTube Shorts & Longform.
    """
    clean_topic = topic.strip().title() if topic else "Legendary Anime Awakening"
    
    # Generate 5 high CTR Titles
    viral_titles = [
        f"HE WAS WEAK UNTIL THIS HAPPENED... 🔥 | {clean_topic}",
        f"The Forbidden Power of {clean_topic} Explained! ⚡",
        f"NO ONE EXPECTED HIM TO AWAKEN THIS... 😱 | Anime Story",
        f"When The God of {clean_topic} Returns To Mortal Realm! 👑",
        f"From Zero To The Strongest Sovereign: {clean_topic} 🗡️"
    ]
    
    # Generate Chapters / Story breakdown
    synopsis_lines = []
    for i, scene in enumerate(storyboard):
        narration = scene.get("narration", "")
        synopsis_lines.append(f"• Part {i+1}: {narration}")
        
    full_synopsis = "\n".join(synopsis_lines)
    
    description = f"""🎬 {clean_topic} - High Stakes Anime Story
Experience the breathtaking tale of {clean_topic} animated with cutting-edge AI cinematography.

📖 STORY CHAPTERS:
{full_synopsis}

✨ Animation Style: {style_name}
🔊 Voiceover: AI Neural Anime Narrator
🎵 Sound Design: Dynamic SFX & Cinematic Anime OST

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔔 Subscribe for daily epic anime stories, manhwa lore, and animated shorts!
👍 Drop a LIKE and comment your favorite scene below!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

#anime #animestory #shorts #animeedit #manhwa #isekai #sololeveling #epic #animation #facelesschannel
"""

    hashtags = [
        "#anime", "#shorts", "#animeedit", "#sololeveling", "#manhwa",
        "#animelore", "#animation", "#facelesschannel", "#otaku", "#viral"
    ]
    
    tags = [
        clean_topic, "anime recap", "anime storytelling", "anime shorts",
        "manhwa summary", "isekai story", "epic anime battle",
        "faceless youtube channel", "ai animation", "anime lore explained"
    ]
    
    thumbnail_prompt = f"epic masterpiece anime key visual of {clean_topic}, glowing eyes, intense battle aura, dramatic lighting, high contrast, cinematic anime movie poster style"
    
    return {
        "titles": viral_titles,
        "selected_title": viral_titles[0],
        "description": description,
        "hashtags": " ".join(hashtags),
        "tags": ", ".join(tags),
        "thumbnail_prompt": thumbnail_prompt
    }

