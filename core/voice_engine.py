#!/usr/bin/env python3
"""MODULE SINH GIỌNG ĐỌC MẦM NON CHUẨN OXFORD / CAMBRIDGE (EDGE-TTS).
Tốc độ phát âm được kiểm soát nghiêm ngặt: 85 - 105 WPM (rate="-16%").
Giọng chuẩn:
  - en-GB-SoniaNeural: Giọng cô giáo Anh - Anh ngọt ngào, rõ âm đuôi.
  - en-US-AnaNeural: Giọng hoạt hình trẻ thơ trong trẻo, dễ thương.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

VOICE_PROFILES = {
    "oxford_teacher": "en-GB-SoniaNeural",
    "cartoon_child": "en-US-AnaNeural",
    "american_friendly": "en-US-EmmaMultilingualNeural",
    "gentle_guide": "en-GB-MaisieNeural"
}

def sinh_giong_doc(
    text: str,
    out_file: Path,
    voice_type: str = "oxford_teacher",
    rate: str = "-16%",
    volume: str = "+0%"
) -> Path:
    """Sinh file âm thanh WAV/MP3 từ văn bản bằng edge-tts CLI (0 VNĐ)."""
    voice = VOICE_PROFILES.get(voice_type, "en-GB-SoniaNeural")
    cmd = [
        "edge-tts",
        f"--voice={voice}",
        f"--rate={rate}",
        f"--volume={volume}",
        f"--text={text}",
        f"--write-media={out_file}"
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    return out_file

if __name__ == "__main__":
    test_out = Path("/tmp/test_voice.mp3")
    sinh_giong_doc("Hello little friends! Welcome to our happy class.", test_out)
    print(f"Generated test voice at: {test_out} ({test_out.stat().st_size} bytes)")
