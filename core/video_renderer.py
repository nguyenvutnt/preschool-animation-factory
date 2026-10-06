#!/usr/bin/env python3
"""MODULE ĐIỀU PHỐI DÂY CHUYỀN SẢN XUẤT VIDEO MẦM NON ĐA THỂ LOẠI.
Hỗ trợ toàn diện 8 thể loại:
  1. glenn_doman (Flashcard tráo thẻ nhanh não phải, không BGM hoặc gõ phách tĩnh)
  2. vocabulary (Từ vựng trực quan Cambridge Pre-A1)
  3. phonics (Ngữ âm Oxford Phonics)
  4. sight_words (Từ nhận diện tức thì Dolch/Fry)
  5. conversation (Giao tiếp tình huống đối thoại 2 nhân vật)
  6. rhyme (Thơ vần điệu)
  7. story (Truyện tranh kể chuyện Read-Along)
  8. song (Bài hát & vận động TPR)

Kết nối: Multi-Genre Visual Composer + Voice Engine + Audio Master + Multi-Genre Subtitle ASS + FFmpeg Rec.709 CFR 25fps + QC Validator.
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
from typing import Any, Dict, List, Optional

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
RES_BGM = ROOT_DIR / "res" / "bgm"

from core.visual_composer import compose_stage_by_genre
from core.voice_engine import sinh_giong_doc
from core.audio_master import master_audio_ebu_r128
from core.subtitle_generator import tao_file_sub_ass
from core.qc_validator import kiem_dinh_video

def render_clip_hoan_chinh(
    clip_id: str,
    shots: List[Dict[str, Any]],
    out_dir: Path,
    genre: str = "vocabulary",
    bgm_name: Optional[str] = None,
    subject_image_path: Optional[Path] = None
) -> Dict[str, Any]:
    """Sản xuất 1 clip video mầm non đa thể loại đạt chuẩn xuất bản quốc tế."""
    work_dir = out_dir / f"_work_{clip_id}"
    work_dir.mkdir(parents=True, exist_ok=True)
    t_start = time.time()
    g = genre.lower().strip()

    # 1. Quản lý BGM theo đặc thù từng thể loại
    bgm_file = None
    if g in ("glenn_doman", "glenndoman", "flashcard"):
        # Glenn Doman tuyệt đối không để nhạc nền làm phân tán chú ý não phải
        bgm_file = None
    elif bgm_name:
        bgm_file = RES_BGM / bgm_name
    else:
        bgm_list = list(RES_BGM.glob("*.mp3"))
        if bgm_list:
            bgm_file = random.choice(bgm_list)

    # 2. Sinh Audio cho từng shot & Concat
    speech_parts = []
    total_duration = 0.5 # Lead silence
    for idx, s in enumerate(shots):
        spk_file = work_dir / f"speech_{idx:02d}.mp3"
        # Chọn giọng đọc và tốc độ theo thể loại hoặc phân vai
        voice = "oxford_teacher"
        if g in ("conversation", "giaotiep"):
            speaker = s.get("speaker", "A")
            voice = "oxford_teacher" if (speaker == "A" or idx % 2 == 0) else "cartoon_child"
        elif g in ("story", "truyen"):
            voice = "oxford_teacher"
        elif g in ("song", "movement"):
            voice = "cartoon_child"

        rate = s.get("rate", "-16%")
        if g in ("glenn_doman", "flashcard"):
            rate = "-5%" # Đọc dứt khoát 1s/từ
        elif g in ("story", "truyen"):
            rate = "-18%" # Giọng kể chuyện thong thả

        sinh_giong_doc(s["speech"], spk_file, voice_type=voice, rate=rate)
        speech_parts.append(spk_file)
        dur = s.get("duration", 5.0 if g != "glenn_doman" else 1.0)
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
        # Ép chuẩn loudnorm độc lập cho giọng đọc
        subprocess.run([
            'ffmpeg', '-y', '-i', str(full_speech),
            '-af', 'loudnorm=I=-14.0:TP=-1.0:LRA=7.0',
            '-c:a', 'aac', '-b:a', '192k', str(master_audio)
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    # 4. Tạo Sân khấu Visual theo thể loại & Subtitle ASS
    stage_img = work_dir / "stage.png"
    compose_stage_by_genre(genre, stage_img, subject_image_path=subject_image_path)

    ass_sub = work_dir / "subtitles.ass"
    tao_file_sub_ass(shots, ass_sub, genre=genre)

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
    qc_data["genre"] = genre
    qc_data["render_time_seconds"] = round(t_render, 2)
    qc_data["bgm_used"] = bgm_file.name if bgm_file else "None (Clean Vocal Policy)"

    # Dọn dẹp file tạm _work để giữ ổ cứng thông thoáng
    shutil.rmtree(work_dir, ignore_errors=True)
    return qc_data

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Render video mầm non đa thể loại")
    parser.add_argument("--demo", action="store_true", help="Chạy demo 1 clip mẫu")
    parser.add_argument("--genre", default="vocabulary", choices=[
        "glenn_doman", "vocabulary", "phonics", "sight_words", "conversation", "rhyme", "story", "song"
    ], help="Thể loại clip học liệu")
    args = parser.parse_args()

    out_dir = ROOT_DIR / "out_demo"
    out_dir.mkdir(parents=True, exist_ok=True)

    from core.llm_engine import tao_kich_ban_clip_theo_the_loai
    kb = tao_kich_ban_clip_theo_the_loai(args.genre, "Apple")
    clip_id = f"demo_{args.genre}_{int(time.time())}"
    print(f"Khởi chạy render clip thể loại: {args.genre.upper()}...")
    res = render_clip_hoan_chinh(clip_id, kb["shots"], out_dir, genre=args.genre)
    print(json.dumps(res, indent=2))
