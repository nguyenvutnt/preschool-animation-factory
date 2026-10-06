#!/usr/bin/env python3
"""
Hoàn thiện 6 câu thoại còn lại của kịch bản Khối Purple Tuần 6
bằng Edge TTS (Neural Voices chuẩn Mỹ với pitch/rate hoạt hình tự nhiên):
- 13_david_door4: en-US-ChristopherNeural
- 14_leo_artroom: en-US-AnaNeural (+18Hz)
- 15_mia_paint: en-US-AnaNeural (+28Hz)
- 16_fast_recap: en-US-JennyNeural (+15% rate)
- 17_both_yay: en-US-AnaNeural (+22Hz)
- 18_teachers_bye: en-US-ChristopherNeural
"""

import asyncio
import subprocess
from pathlib import Path
import edge_tts

OUT_DIR = Path("/root/scratch/purple_w06_tiktok/gemini_audio")
OUT_DIR.mkdir(parents=True, exist_ok=True)

REMAINING_LINES = [
    {
        "id": "13_david_door4",
        "voice": "en-US-ChristopherNeural",
        "pitch": "+4Hz",
        "rate": "+5%",
        "text": "One more magic door! Door number four! Wow!"
    },
    {
        "id": "14_leo_artroom",
        "voice": "en-US-AnaNeural",
        "pitch": "+18Hz",
        "rate": "+10%",
        "text": "Rainbow colors everywhere! It's the art room!"
    },
    {
        "id": "15_mia_paint",
        "voice": "en-US-AnaNeural",
        "pitch": "+26Hz",
        "rate": "+8%",
        "text": "Art room! We paint bright pictures! Paint! Paint! Paint!"
    },
    {
        "id": "16_fast_recap",
        "voice": "en-US-JennyNeural",
        "pitch": "+6Hz",
        "rate": "+14%",
        "text": "Classroom! Library! Playground! Art room! Super stars!"
    },
    {
        "id": "17_both_yay",
        "voice": "en-US-AnaNeural",
        "pitch": "+20Hz",
        "rate": "+10%",
        "text": "We know our school places! Hip hip hooray!"
    },
    {
        "id": "18_teachers_bye",
        "voice": "en-US-ChristopherNeural",
        "pitch": "+3Hz",
        "rate": "+2%",
        "text": "You are fantastic! See you next time, bye bye!"
    }
]

async def generate_line(item):
    out_mp3 = OUT_DIR / f"{item['id']}.mp3"
    out_wav = OUT_DIR / f"{item['id']}.wav"
    
    communicate = edge_tts.Communicate(
        text=item["text"],
        voice=item["voice"],
        pitch=item["pitch"],
        rate=item["rate"]
    )
    await communicate.save(str(out_mp3))
    
    # Tạo luôn file WAV 24000Hz phục vụ Rhubarb Lip-sync
    subprocess.run([
        "ffmpeg", "-y", "-i", str(out_mp3),
        "-ar", "24000", "-ac", "1",
        str(out_wav)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    print(f"✅ Generated {item['id']} -> {out_mp3.name} & {out_wav.name}")

async def main():
    print(f"🎤 Generating remaining {len(REMAINING_LINES)} voice lines...")
    for item in REMAINING_LINES:
        await generate_line(item)
    print("🎉 ALL 18 VOICE LINES READY!")

if __name__ == "__main__":
    asyncio.run(main())
