#!/usr/bin/env python3
r"""
BỘ XÂY DỰNG TIMELINE SƯ PHẠM VÀ HÒA ÂM MASTER V3 — 4 GIỌNG ĐỌC CHUẨN MỸ
- Tuân thủ 100% nguyên tắc ZERO SPEECH OVERLAP (Không chồng thoại).
- Khoảng lặng nhận thức (Cognitive Processing Pause) 1200ms - 1500ms cho các câu hỏi tương tác.
- Tần suất lặp lại từ khóa chuẩn Nation & Webb (Ball: 7x, Red: 8x, Blue: 6x, Roll: 6x).
- SFX đồng bộ mili-giây: Boing, Bump, Whoosh, Ting Chime, Applause.
- BGM vui tươi mầm non (-22 dB) + Chuẩn hóa phát thanh EBU R128 (-14.0 LUFS).
"""

import json
import os
import subprocess
from pathlib import Path
import soundfile as sf
import numpy as np

AUDIO_DIR = Path("/root/scratch/red_w06_audio_v3/raw")
SFX_DIR = Path("/root/preschool-animation-factory/res/sfx")
BGM_FILE = Path("/root/preschool-animation-factory/res/bgm/Carefree.mp3")
SCRATCH_DIR = Path("/root/scratch/red_w06_audio_v3")

OUT_MASTER_WAV = SCRATCH_DIR / "master_v3_temp.wav"
OUT_MASTER_MP3 = SCRATCH_DIR / "master_v3_broadcast.mp3"
OUT_MANIFEST = SCRATCH_DIR / "perfect_manifest_v3.json"

# Định nghĩa danh sách 32 câu thoại cùng phân vai và loại khoảng nghỉ
DIALOGUES = [
    # (id, filename, speaker, is_interaction_question)
    ("01_male_hello", "01_male_hello.mp3", "mr_david", False),
    ("02_female_ready", "02_female_ready.mp3", "ms_sarah", False),
    ("03_male_look", "03_male_look.mp3", "mr_david", False),
    ("04_boy_ball", "04_boy_ball.mp3", "leo_red", False),
    ("05_female_say_ball", "05_female_say_ball.mp3", "ms_sarah", True),   # Cognitive Pause
    ("06_girl_ball", "06_girl_ball.mp3", "mia_blue", False),
    ("07_male_card_ball", "07_male_card_ball.mp3", "mr_david", False),
    ("08_female_what_color", "08_female_what_color.mp3", "ms_sarah", True), # Cognitive Pause
    ("09_boy_im_red", "09_boy_im_red.mp3", "leo_red", False),
    ("10_male_red_apple", "10_male_red_apple.mp3", "mr_david", False),
    ("11_girl_red", "11_girl_red.mp3", "mia_blue", False),
    ("12_female_card_red", "12_female_card_red.mp3", "ms_sarah", False),
    ("13_male_someone_rolling", "13_male_someone_rolling.mp3", "mr_david", False),
    ("14_girl_im_blue", "14_girl_im_blue.mp3", "mia_blue", False),
    ("15_boy_hello_blue", "15_boy_hello_blue.mp3", "leo_red", False),
    ("16_female_red_and_blue", "16_female_red_and_blue.mp3", "ms_sarah", False),
    ("17_male_say_blue", "17_male_say_blue.mp3", "mr_david", True),       # Cognitive Pause
    ("18_both_blue", "18_both_blue.mp3", "both_balls", False),
    ("19_female_what_can_do", "19_female_what_can_do.mp3", "ms_sarah", False),
    ("20_boy_watch_roll", "20_boy_watch_roll.mp3", "leo_red", False),
    ("21_girl_i_roll_too", "21_girl_i_roll_too.mp3", "mia_blue", False),
    ("22_male_say_roll", "22_male_say_roll.mp3", "mr_david", True),       # Cognitive Pause
    ("23_both_roll", "23_both_roll.mp3", "both_balls", False),
    ("24_female_flash_intro", "24_female_flash_intro.mp3", "ms_sarah", False),
    ("25_male_card_ball_flash", "25_male_card_ball_flash.mp3", "mr_david", False),
    ("26_female_card_red_flash", "26_female_card_red_flash.mp3", "ms_sarah", False),
    ("27_male_card_blue_flash", "27_male_card_blue_flash.mp3", "mr_david", False),
    ("28_female_card_roll_flash", "28_female_card_roll_flash.mp3", "ms_sarah", False),
    ("29_boy_we_did_it", "29_boy_we_did_it.mp3", "leo_red", False),
    ("30_girl_hooray", "30_girl_hooray.mp3", "mia_blue", False),
    ("31_female_praise", "31_female_praise.mp3", "ms_sarah", False),
    ("32_male_goodbye", "32_male_goodbye.mp3", "mr_david", False)
]

def get_audio_duration_ms(file_path):
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(file_path)]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    return float(res.stdout.strip()) * 1000.0

def main():
    print("🚀 Bắt đầu tính toán Timeline sư phạm tuần tự (Zero Speech Overlap V3)...")
    
    events = []
    current_time_ms = 1000.0  # Mở đầu 1.0s cho BGM du dương
    
    for item in DIALOGUES:
        ev_id, filename, speaker, is_interaction = item
        fpath = AUDIO_DIR / filename
        dur_ms = get_audio_duration_ms(fpath)
        
        start_ms = current_time_ms
        end_ms = start_ms + dur_ms
        
        events.append({
            "id": ev_id,
            "file": str(fpath),
            "speaker": speaker,
            "start_ms": start_ms,
            "end_ms": end_ms,
            "duration_ms": dur_ms,
            "type": "dialogue"
        })
        
        # Tính khoảng nghỉ tiếp theo
        if is_interaction:
            pause = 1450.0  # Khoảng lặng nhận thức (Cognitive Processing Pause)
        elif ev_id in ["24_female_flash_intro"]:
            pause = 800.0
        elif ev_id in ["25_male_card_ball_flash", "26_female_card_red_flash", "27_male_card_blue_flash", "28_female_card_roll_flash"]:
            pause = 450.0   # Nhịp điệu dứt khoát của tráo thẻ Glenn Doman (mỗi thẻ ~1.0-1.1s)
        else:
            pause = 750.0   # Khoảng nghỉ đàm thoại tự nhiên mầm non
            
        current_time_ms = end_ms + pause
        
    total_duration_ms = current_time_ms + 1500.0 # Thêm 1.5s outro
    total_duration_sec = total_duration_ms / 1000.0
    
    print(f"📊 Timeline chi tiết: {len(events)} câu thoại | Tổng thời lượng: {total_duration_sec:.2f} giây")
    
    # KIỂM ĐỊNH TỰ ĐỘNG CHỐNG CHỒNG THOẠI
    overlaps = []
    for i in range(len(events) - 1):
        gap = events[i+1]["start_ms"] - events[i]["end_ms"]
        if gap < 0:
            overlaps.append((events[i]["id"], events[i+1]["id"], abs(gap)))
            
    if overlaps:
        print(f"❌ PHÁT HIỆN {len(overlaps)} ĐIỂM CHỒNG THOẠI:")
        for o in overlaps:
            print(f"   - {o[0]} đè lên {o[1]}: {o[2]:.1f}ms")
        raise RuntimeError("Trượt kiểm định Zero Speech Overlap!")
    else:
        print("✅ 100% ZERO SPEECH OVERLAP — Không có bất kỳ điểm chồng thoại nào!")

    # THÊM HIỆU ỨNG ÂM THANH SFX VÀO MANIFEST
    sfx_events = []
    
    # 1. Boing lúc bóng đỏ nảy xuống (trước câu 04)
    t_boing_start = 7500.0
    for b_idx in range(3):
        sfx_events.append({
            "id": f"sfx_boing_{b_idx+1}",
            "file": "/root/scratch/sfx_boing_spring.wav",
            "start_ms": t_boing_start + b_idx * 1100.0,
            "type": "sfx"
        })
        
    # 2. Ting Chime lúc thẻ BALL pop-in (ngay trước câu 07)
    ev_07 = next(e for e in events if e["id"] == "07_male_card_ball")
    sfx_events.append({
        "id": "sfx_ting_ball",
        "file": str(SFX_DIR / "sfx_stop_ting.mp3"),
        "start_ms": ev_07["start_ms"] - 150.0,
        "type": "sfx"
    })
    
    # 3. Ting Chime lúc thẻ RED pop-in (ngay trước câu 12)
    ev_12 = next(e for e in events if e["id"] == "12_female_card_red")
    sfx_events.append({
        "id": "sfx_ting_red",
        "file": str(SFX_DIR / "sfx_stop_ting.mp3"),
        "start_ms": ev_12["start_ms"] - 150.0,
        "type": "sfx"
    })
    
    # 4. Whoosh lúc bóng xanh xuất hiện (giữa câu 13 và 14)
    ev_13 = next(e for e in events if e["id"] == "13_male_someone_rolling")
    sfx_events.append({
        "id": "sfx_whoosh_blue",
        "file": "/root/scratch/sfx_whoosh.wav",
        "start_ms": ev_13["end_ms"] + 200.0,
        "type": "sfx"
    })
    
    # 5. Bump Boing lúc hai quả bóng cụng đầu (câu 14)
    ev_14 = next(e for e in events if e["id"] == "14_girl_im_blue")
    sfx_events.append({
        "id": "sfx_bump_balls",
        "file": "/root/scratch/sfx_boing_spring.wav",
        "start_ms": ev_14["end_ms"] - 500.0,
        "type": "sfx"
    })
    
    # 6. Ting Chime lúc thẻ BLUE pop-in (câu 18)
    ev_18 = next(e for e in events if e["id"] == "18_both_blue")
    sfx_events.append({
        "id": "sfx_ting_blue",
        "file": str(SFX_DIR / "sfx_stop_ting.mp3"),
        "start_ms": ev_18["start_ms"] - 150.0,
        "type": "sfx"
    })
    
    # 7. Ting Chime lúc thẻ ROLL pop-in (câu 23)
    ev_23 = next(e for e in events if e["id"] == "23_both_roll")
    sfx_events.append({
        "id": "sfx_ting_roll",
        "file": str(SFX_DIR / "sfx_stop_ting.mp3"),
        "start_ms": ev_23["start_ms"] - 150.0,
        "type": "sfx"
    })
    
    # 8. Ting Chimes trong màn tráo thẻ Glenn Doman (câu 25, 26, 27, 28)
    for card_id in ["25_male_card_ball_flash", "26_female_card_red_flash", "27_male_card_blue_flash", "28_female_card_roll_flash"]:
        ev_c = next(e for e in events if e["id"] == card_id)
        sfx_events.append({
            "id": f"sfx_ting_{card_id}",
            "file": str(SFX_DIR / "sfx_stop_ting.mp3"),
            "start_ms": ev_c["start_ms"] - 100.0,
            "type": "sfx"
        })
        
    # 9. Tiếng vỗ tay hân hoan chúc mừng (câu 31)
    ev_31 = next(e for e in events if e["id"] == "31_female_praise")
    sfx_events.append({
        "id": "sfx_applause_final",
        "file": str(SFX_DIR / "sfx_applause.mp3"),
        "start_ms": ev_31["start_ms"],
        "type": "sfx"
    })
    
    all_audio_events = events + sfx_events
    manifest = {
        "version": "3.0_pedagogical_zero_overlap",
        "total_duration": total_duration_sec,
        "events": all_audio_events
    }
    
    with open(OUT_MANIFEST, "w") as fp:
        json.dump(manifest, fp, indent=2)
        
    print(f"💾 Đã lưu Manifest V3: {OUT_MANIFEST}")
    
    # HÒA ÂM ĐA KÊNH BẰNG FFMPEG COMPLEX FILTER
    print("🎛️ Đang hòa âm đa kênh (32 Voice lines + 12 SFX + BGM) và chuẩn hóa EBU R128...")
    
    # Xây dựng lệnh FFmpeg
    inputs = []
    filter_complex = []
    
    # Input 0: BGM
    inputs.extend(["-i", str(BGM_FILE)])
    
    # Các input thoại và SFX
    for idx, ev in enumerate(all_audio_events):
        inputs.extend(["-i", ev["file"]])
        
    # Tạo filter graph
    # 1. BGM lặp lại nếu cần và chỉnh volume -22dB
    filter_complex.append(f"[0:a]aloop=loop=-1:size=2e+09,atrim=0:{total_duration_sec},volume=0.08,afade=t=out:st={total_duration_sec-3.0}:d=3.0[bgm];")
    
    delayed_labels = ["[bgm]"]
    for idx, ev in enumerate(all_audio_events):
        delay_ms = int(ev["start_ms"])
        inp_idx = idx + 1
        vol = "1.0"
        if "sfx" in ev["type"]:
            vol = "0.75" if "applause" in ev["id"] else "0.85"
            
        filter_complex.append(f"[{inp_idx}:a]adelay={delay_ms}|{delay_ms},volume={vol}[a{idx}];")
        delayed_labels.append(f"[a{idx}]")
        
    # Mix tất cả các stream lại
    mix_inputs = "".join(delayed_labels)
    total_streams = len(delayed_labels)
    filter_complex.append(f"{mix_inputs}amix=inputs={total_streams}:dropout_transition=0:normalize=0[mixed];")
    
    # Chuẩn hóa EBU R128 Broadcast (-14.0 LUFS)
    filter_complex.append("[mixed]loudnorm=I=-14:LRA=11:TP=-1.5[out]")
    
    cmd_ffmpeg = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", "".join(filter_complex),
        "-map", "[out]",
        "-c:a", "libmp3lame",
        "-b:a", "192k",
        str(OUT_MASTER_MP3)
    ]
    
    res = subprocess.run(cmd_ffmpeg, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode == 0:
        print(f"🎉 Hòa âm thành công Master Broadcast Audio: {OUT_MASTER_MP3}")
        print(f"   Thời lượng audio: {total_duration_sec:.1f}s")
    else:
        print("❌ Lỗi FFmpeg khi hòa âm!")
        print(res.stderr[-1000:])
        raise RuntimeError("Hòa âm thất bại!")

if __name__ == "__main__":
    main()
