#!/usr/bin/env python3
"""
Trích xuất khẩu hình (Mouth Visemes) bằng Rhubarb Lip Sync
cho toàn bộ 18 câu thoại Gemini TTS của Khối Purple Tuần 6.
"""

import json
import subprocess
from pathlib import Path

AUDIO_DIR = Path("/root/scratch/purple_w06_tiktok/gemini_audio")
VISEME_DIR = Path("/root/scratch/purple_w06_tiktok/gemini_visemes")
VISEME_DIR.mkdir(parents=True, exist_ok=True)

def process_file(wav_file: Path):
    out_json = VISEME_DIR / f"{wav_file.stem}.json"
    cmd = [
        "rhubarb",
        "-f", "json",
        "-o", str(out_json),
        str(wav_file)
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"👄 Visemes generated for {wav_file.name} -> {out_json.name}")

def main():
    wav_files = sorted(list(AUDIO_DIR.glob("*.wav")))
    print(f"🔍 Found {len(wav_files)} WAV files in {AUDIO_DIR}")
    for wf in wav_files:
        process_file(wf)
    print("🎉 ALL VISEMES GENERATED SUCCESSFULLY!")

if __name__ == "__main__":
    main()
