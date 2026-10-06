#!/usr/bin/env python3
r"""
Trích xuất 8 Snapshots thị giác V2 kiểm chứng:
  1. 1.5s  - READY, GO! (Cổng trường mầm non lộng lẫy + Thỏ Tím + Star Sticker)
  2. 7.5s  - CLASSROOM (Lớp học quốc tế thật Unsplash + Thẻ CLASSROOM Tím Neon + Sticker Sách)
  3. 16.0s - LEARN (Lớp học góc đồ chơi gỗ EYC + Thẻ LEARN Xanh Ngọc + Thỏ nói Learn)
  4. 24.0s - LIBRARY (Kệ sách thiếu nhi khổng lồ Unsplash + Thẻ LIBRARY Xanh Teal + Sticker Thư viện)
  5. 29.5s - READ (Góc đọc sách êm ái EYC + Thẻ READ Vàng Cam)
  6. 35.0s - PLAYGROUND (Sân chơi mầm non ngoài trời Unsplash + Thẻ PLAYGROUND Xanh Lá + Sticker Cầu trượt)
  7. 45.0s - ART ROOM (Phòng vẽ tranh màu nước nghệ thuật Unsplash + Thẻ ART ROOM Đỏ Hồng + Sticker Bảng màu)
  8. 61.0s - GREAT JOB! (Toà nhà trường học + Thẻ GREAT JOB! Vàng Kim + Mưa sao vàng)
"""

import subprocess
import json
from pathlib import Path

VIDEO_PATH = Path("/root/preschool-animation-factory/demo_products/demo_W06_Purple_TikTok_Vocabulary.mp4")
OUTPUT_DIR = Path("/srv/school-ai/var/video-cong-khai/purple-w06-tiktok")
SNAP_DIR = OUTPUT_DIR / "snapshots"
SNAP_DIR.mkdir(parents=True, exist_ok=True)

TIMESTAMPS = [
    (1.5, "01_hook_real_school.jpg", "Hook 1.5s: READY, GO! - Cổng trường mầm non quốc tế thật"),
    (7.5, "02_classroom_real.jpg", "Scene 7.5s: CLASSROOM - Lớp học mầm non thật Unsplash + Sticker Sách"),
    (16.0, "03_learn_real.jpg", "Action 16.0s: LEARN - Thẻ chữ LEARN rực rỡ + Thỏ Tím Lip-sync"),
    (24.0, "04_library_real.jpg", "Scene 24.0s: LIBRARY - Thư viện sách thiếu nhi khổng lồ"),
    (29.5, "05_read_real.jpg", "Action 29.5s: READ - Góc đọc sách êm ái + Thẻ READ nổi khối"),
    (35.0, "06_playground_real.jpg", "Scene 35.0s: PLAYGROUND - Sân chơi ngoài trời thật cỏ xanh nắng vàng"),
    (45.0, "07_artroom_real.jpg", "Scene 45.0s: ART ROOM - Phòng vẽ màu nước nghệ thuật sặc sỡ"),
    (61.0, "08_great_job_celebration.jpg", "Celebration 61.0s: GREAT JOB! - Đại tiệc mưa sao vàng rực rỡ")
]

for sec, fname, title in TIMESTAMPS:
    out_file = SNAP_DIR / fname
    cmd = [
        "ffmpeg", "-y", "-ss", str(sec),
        "-i", str(VIDEO_PATH),
        "-frames:v", "1",
        "-q:v", "2",
        str(out_file)
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if out_file.exists():
        print(f"✅ Snap [{sec:.1f}s]: {fname} — {title}")
    else:
        print(f"❌ Failed: {fname}")

# Sao chép sang docs/purple_w06_tiktok/snapshots/ trong repo
REPO_SNAP_DIR = Path("/root/preschool-animation-factory/docs/purple_w06_tiktok/snapshots")
REPO_SNAP_DIR.mkdir(parents=True, exist_ok=True)
subprocess.run(f"cp {SNAP_DIR}/*.jpg {REPO_SNAP_DIR}/", shell=True)
print("Synced snapshots to repo docs!")
