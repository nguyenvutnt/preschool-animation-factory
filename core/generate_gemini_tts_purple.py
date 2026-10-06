#!/usr/bin/env python3
"""
Tạo toàn bộ 18 câu thoại cho Khối Purple - Tuần 06 Vocabulary
Sử dụng Google Gemini 2.5 Flash TTS (gemini-2.5-flash-preview-tts)
với các giọng diễn xuất hoạt hình Mỹ chất lượng cao:
- Ms. Sarah: Aoede (giáo viên mầm non nữ, Motherese ấm áp, nốt cao thấp nảy nhót)
- Mr. David: Fenrir (thầy giáo mầm non nam, hào hứng, năng lượng)
- Leo Bunny: Puck (chú thỏ 4 tuổi, lém lỉnh, vui nhộn, giọng cao hoạt hình)
- Mia Kid: Kore (bé gái 4 tuổi, ngọt ngào, trong sáng, hồn nhiên)
"""

import base64
import json
import time
import urllib.request
import wave
from pathlib import Path

KEY_FILE = Path("/srv/school-ai/var/eyc-kids/khoa-google.txt")
OUT_DIR = Path("/root/scratch/purple_w06_tiktok/gemini_audio")
OUT_DIR.mkdir(parents=True, exist_ok=True)

MODEL = "gemini-2.5-flash-preview-tts"

LINES = [
    {
        "id": "01_sarah_hook",
        "voice": "Aoede",
        "speaker": "ms_sarah",
        "prompt": "Say cheerfully with exaggerated Motherese intonation and high-low pitch melody as a loving American female kindergarten teacher talking to 4-year-old children: Look! Where are we in our school? Let's explore together!"
    },
    {
        "id": "02_david_door1",
        "voice": "Fenrir",
        "speaker": "mr_david",
        "prompt": "Say warmly and enthusiastically as a friendly American male preschool teacher: Door number one! Open sesame! Whoosh!"
    },
    {
        "id": "03_leo_classroom",
        "voice": "Puck",
        "speaker": "leo_bunny",
        "prompt": "Say excitedly in a cute, bouncy 4-year-old cartoon boy voice: Yay! It's our classroom! Where we learn!"
    },
    {
        "id": "04_mia_say_classroom",
        "voice": "Kore",
        "speaker": "mia_kid",
        "prompt": "Say sweetly and clearly in a happy, adorable 4-year-old little girl voice: Classroom! We learn here! Say it: Classroom!"
    },
    {
        "id": "05_david_door2",
        "voice": "Fenrir",
        "speaker": "mr_david",
        "prompt": "Say with playful mystery and excitement as an American preschool teacher: Great job! Now, magic door number two! Ready? Whoosh!"
    },
    {
        "id": "06_sarah_library",
        "voice": "Aoede",
        "speaker": "ms_sarah",
        "prompt": "Say with a gentle, joyful whisper-to-normal warm American kindergarten teacher voice: Quiet whisper... It's the library! So many wonderful books!"
    },
    {
        "id": "07_leo_read_library",
        "voice": "Puck",
        "speaker": "leo_bunny",
        "prompt": "Say in a happy, curious 4-year-old cartoon voice: I love storybooks! In the library, we read!"
    },
    {
        "id": "08_both_library",
        "voice": "Kore",
        "speaker": "mia_kid",
        "prompt": "Say enthusiastically as a cute 4-year-old girl inviting friends: Read in the library! Can you say: Library!"
    },
    {
        "id": "09_david_whoosh",
        "voice": "Fenrir",
        "speaker": "mr_david",
        "prompt": "Say with high energy and an upbeat tone as an American teacher: Awesome! Door number three is opening! Let's go outside!"
    },
    {
        "id": "10_mia_playground",
        "voice": "Kore",
        "speaker": "mia_kid",
        "prompt": "Say with pure delight and giggles as a 4-year-old cartoon girl: Look at the big slide! We are at the playground!"
    },
    {
        "id": "11_leo_play",
        "voice": "Puck",
        "speaker": "leo_bunny",
        "prompt": "Say cheerfully and jumping with joy as an energetic 4-year-old: Playground! We play together! Weee!"
    },
    {
        "id": "12_sarah_yes_playground",
        "voice": "Aoede",
        "speaker": "ms_sarah",
        "prompt": "Say proudly with big teacher smile and warm affirmation: Yes! At the playground, we play! Say: Playground!"
    },
    {
        "id": "13_david_door4",
        "voice": "Fenrir",
        "speaker": "mr_david",
        "prompt": "Say with colorful enthusiasm as a male teacher: One more magic door! Door number four! Wow!"
    },
    {
        "id": "14_leo_artroom",
        "voice": "Puck",
        "speaker": "leo_bunny",
        "prompt": "Say in awe and excitement as a 4-year-old cartoon boy: Rainbow colors everywhere! It's the art room!"
    },
    {
        "id": "15_mia_paint",
        "voice": "Kore",
        "speaker": "mia_kid",
        "prompt": "Say happily and playfully as an excited 4-year-old girl: Art room! We paint bright pictures! Paint! Paint! Paint!"
    },
    {
        "id": "16_fast_recap",
        "voice": "Aoede",
        "speaker": "ms_sarah",
        "prompt": "Say rhythmically, upbeat, and enthusiastically like a fun catchy chant for preschoolers: Classroom! Library! Playground! Art room! Super stars!"
    },
    {
        "id": "17_both_yay",
        "voice": "Puck",
        "speaker": "leo_bunny",
        "prompt": "Say with maximum joy and cheer as a happy cartoon character: We know our school places! Hip hip hooray!"
    },
    {
        "id": "18_teachers_bye",
        "voice": "Fenrir",
        "speaker": "mr_david",
        "prompt": "Say warmly with a big waving goodbye tone: You are fantastic! See you next time, bye bye!"
    }
]

def pcm_to_wav(pcm_bytes: bytes, wav_path: Path, sample_rate: int = 24000):
    with wave.open(str(wav_path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sample_rate)
        w.writeframes(pcm_bytes)

def generate_voice(key: str, item: dict) -> Path:
    out_wav = OUT_DIR / f"{item['id']}.wav"
    out_mp3 = OUT_DIR / f"{item['id']}.mp3"
    
    if out_mp3.exists() and out_mp3.stat().st_size > 1000:
        print(f"⏩ [Skip] {item['id']} already exists ({out_mp3.stat().st_size} bytes)")
        return out_mp3

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={key}"
    body = {
        "contents": [{"parts": [{"text": item["prompt"]}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {
                "voiceConfig": {
                    "prebuiltVoiceConfig": {
                        "voiceName": item["voice"]
                    }
                }
            }
        }
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"}
    )
    
    for attempt in range(10):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                res = json.loads(r.read())
            parts = res["candidates"][0]["content"]["parts"]
            for p in parts:
                if "inlineData" in p:
                    pcm = base64.b64decode(p["inlineData"]["data"])
                    pcm_to_wav(pcm, out_wav)
                    # Chuyển đổi sang MP3 chất lượng cao bằng ffmpeg
                    import subprocess
                    subprocess.run(
                        ["ffmpeg", "-y", "-i", str(out_wav), "-b:a", "192k", str(out_mp3)],
                        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                    )
                    print(f"✅ Generated {item['id']} ({item['voice']}) -> {out_mp3.name} ({out_mp3.stat().st_size} bytes)")
                    return out_mp3
            raise RuntimeError(f"No inlineData in response: {res}")
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 503) and attempt < 9:
                wait_sec = 20 if e.code == 429 else 5
                print(f"⚠️ HTTP {e.code} on {item['id']} (attempt {attempt+1}/10). Retrying in {wait_sec}s...")
                time.sleep(wait_sec)
                continue
            raise

def main():
    if not KEY_FILE.exists():
        print(f"❌ Key file not found: {KEY_FILE}")
        return 1
    key = KEY_FILE.read_text().strip()
    
    print(f"🚀 Starting Gemini 2.5 Flash TTS for {len(LINES)} lines...")
    for idx, item in enumerate(LINES, 1):
        print(f"[{idx}/{len(LINES)}] {item['id']} ({item['voice']})...")
        generate_voice(key, item)
        # Giữ khoảng nghỉ nhẹ để tránh rate-limit
        time.sleep(2.0)
        
    print("\n🎉 ALL 18 GEMINI TTS VOICES GENERATED SUCCESSFULLY!")
    return 0

if __name__ == "__main__":
    main()
