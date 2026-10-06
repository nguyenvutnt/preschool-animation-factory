#!/usr/bin/env python3
"""MODULE ĐIỀU PHỐI DÂY CHUYỀN SẢN XUẤT VIDEO MẦM NON HOÀN CHỈNH.
Kết nối: Visual Composer + Voice Engine + Audio Master + Subtitle ASS + FFmpeg Rec.709 CFR 25fps + QC Validator.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import shutil
import subprocess
import time
import sys
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
RES_BGM = ROOT_DIR / "res" / "bgm"

from core.visual_composer import render_stage_image
from core.voice_engine import sinh_giong_doc
from core.audio_master import master_audio_ebu_r128
from core.subtitle_generator import tao_file_sub_ass
from core.qc_validator import kiem_dinh_video

def render_clip_hoan_chinh(
    clip_id: str,
    shots: List[Dict[str, Any]],
    out_dir: Path,
    bgm_name: Optional[str] = None,
    subject_image_path: Optional[Path] = None
) -> Dict[str, Any]:
    """Sản xuất 1 clip video mầm non đạt chuẩn xuất bản quốc tế."""
    work_dir = out_dir / f"_work_{clip_id}"
    work_dir.mkdir(parents=True, exist_ok=True)
    t_start = time.time()

    # 1. Chọn BGM ngẫu nhiên nếu không chỉ định
    if not bgm_name:
        bgm_list = list(RES_BGM.glob("*.mp3"))
        bgm_file = random.choice(bgm_list) if bgm_list else None
    else:
        bgm_file = RES_BGM / bgm_name

    # 2. Sinh Audio cho từng shot & Concat
    speech_parts = []
    total_duration = 0.5 # Lead silence
    for idx, s in enumerate(shots):
        spk_file = work_dir / f"speech_{idx:02d}.mp3"
        sinh_giong_doc(s["speech"], spk_file)
        speech_parts.append(spk_file)
        dur = s.get("duration", 5.0)
        total_duration += dur

    # Concat speech files
    concat_txt = work_dir / "concat_speech.txt"
    lead_silence = work_dir / "lead_silence.mp3"
    subprocess.run([
        'ffmpeg', '-y', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo',
        '-t', '0.5', str(lead_silence)
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    with open(concat_txt, "w", encoding="utf-8") as f:
        f.write(f"file '{lead_silence}'\n")
        for p in speech_parts:
            f.write(f"file '{p}'\n")

    full_speech = work_dir / "full_speech.mp3"
    subprocess.run([
        'ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', str(concat_txt),
        '-c:a', 'libmp3lame', '-b:a', '192k', str(full_speech)
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    # 3. Master Audio với EBU R128 & Sidechain Ducking
    master_audio = work_dir / "master_audio.aac"
    if bgm_file and bgm_file.exists():
        master_audio_ebu_r128(full_speech, bgm_file, master_audio)
    else:
        # Nếu không có BGM, chỉ ép chuẩn loudnorm
        subprocess.run([
            'ffmpeg', '-y', '-i', str(full_speech),
            '-af', 'loudnorm=I=-14.0:TP=-1.0:LRA=7.0',
            '-c:a', 'aac', '-b:a', '192k', str(master_audio)
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    # 4. Tạo Sân khấu Visual & Subtitle ASS
    stage_img = work_dir / "stage.png"
    render_stage_image(stage_img, subject_image_path=subject_image_path)

    ass_sub = work_dir / "subtitles.ass"
    tao_file_sub_ass(shots, ass_sub)

    # 5. Render Video H.264 Rec.709 CFR 25fps Siêu tốc
    out_video = out_dir / f"{clip_id}.mp4"
    render_cmd = [
        'ffmpeg', '-y',
        '-loop', '1', '-i', str(stage_img),
        '-i', str(master_audio),
        '-t', str(total_duration),
        '-vf', f"ass={ass_sub},format=yuv420p",
        '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20',
        '-x264-params', 'colorprim=bt709:transfer=bt709:colormatrix=bt709:keyint=50:min-keyint=50:no-scenecut=1',
        '-c:a', 'copy',
        '-movflags', '+faststart',
        '-shortest',
        str(out_video)
    ]
    subprocess.run(render_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    t_render = time.time() - t_start

    # 6. Kiểm định chất lượng tự động (Auto QC Gate)
    qc_data = kiem_dinh_video(out_video)
    qc_data["render_time_seconds"] = round(t_render, 2)
    qc_data["bgm_used"] = bgm_file.name if bgm_file else "None"

    # Dọn dẹp file tạm _work để giữ ổ cứng thông thoáng
    shutil.rmtree(work_dir, ignore_errors=True)
    return qc_data

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--demo", action="store_true", help="Chạy demo 1 clip mẫu")
    args = parser.parse_args()

    demo_shots = [
        {"card_text": "HELLO SUN /sʌn/", "speech": "Hello warm sun! Good morning.", "duration": 4.5},
        {"card_text": "THE SUN IS YELLOW", "speech": "Look! The sun is bright and yellow.", "duration": 4.5},
        {"card_text": "CAN YOU SAY SUN?", "speech": "Can you say sun? Let's say it!", "duration": 5.0},
        {"card_text": "GREAT JOB! /sʌn/", "speech": "Sun! Wonderful job, little friends.", "duration": 4.5}
    ]
    out_dir = ROOT_DIR / "out_demo"
    out_dir.mkdir(parents=True, exist_ok=True)
    print("Khởi chạy demo render 1 clip đạt chuẩn xuất bản...")
    res = render_clip_hoan_chinh("demo_sun_clip", demo_shots, out_dir)
    print(json.dumps(res, indent=2))
