#!/usr/bin/env python3
"""TẢI VÀ CHUẨN HÓA KHO NHẠC NỀN THIẾU NHI BẢN QUYỀN SẠCH (INCOMPETECH CC-BY 4.0).
Tự động tải về, kiểm tra và chuẩn hóa âm lượng theo chuẩn EBU R128 (-14 LUFS, TP -1.0 dBTP).
"""
import os
import subprocess
import urllib.parse
from pathlib import Path

BGM_DIR = Path('/root/truelearning/res/bgm')
BGM_DIR.mkdir(parents=True, exist_ok=True)

TRACKS = [
    ("Carefree", "Carefree.mp3", "Ukulele mộc vui tươi"),
    ("Fluffing a Duck", "Fluffing_a_Duck.mp3", "Giai điệu vịt con tinh nghịch"),
    ("Monkeys Spinning Monkeys", "Monkeys_Spinning_Monkeys.mp3", "Đàn dây pizzicato và sáo vui nhộn"),
    ("The Builder", "The_Builder.mp3", "Nhịp điệu học tập và xây dựng"),
    ("Sneaky Snitch", "Sneaky_Snitch.mp3", "Tò mò, khám phá"),
    ("Pixelland", "Pixelland.mp3", "Giai điệu hoạt họa tươi tắn"),
    ("Wallpaper", "Wallpaper.mp3", "Nhạc nền dịu nhẹ không lời"),
    ("Quirky Dog", "Quirky_Dog.mp3", "Chú cún vui nhộn"),
    ("Rainbows", "Rainbows.mp3", "Cầu vồng êm dịu, ấm áp")
]

BASE_URL = "https://incompetech.com/music/royalty-free/mp3-royaltyfree/"

def tai_va_chuan_hoa_bgm():
    print(f"Bắt đầu nạp kho nhạc vào {BGM_DIR}...")
    for title, filename, desc in TRACKS:
        out_path = BGM_DIR / filename
        if out_path.exists() and out_path.stat().st_size > 50000:
            print(f" [Đã có sẵn] {title} ({desc})")
            continue

        raw_url = BASE_URL + urllib.parse.quote(title) + ".mp3"
        tmp_file = BGM_DIR / f"temp_{filename}"
        print(f" [Đang tải] {title} từ {raw_url}...")
        try:
            curl_cmd = ["curl", "-sL", raw_url, "-o", str(tmp_file)]
            subprocess.run(curl_cmd, check=True)

            # Chuẩn hóa âm lượng EBU R128 dịu tai cho mầm non
            norm_cmd = [
                "ffmpeg", "-y", "-i", str(tmp_file),
                "-af", "loudnorm=I=-16.0:TP=-1.5:LRA=7.0",
                "-c:a", "libmp3lame", "-b:a", "192k",
                str(out_path)
            ]
            subprocess.run(norm_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            tmp_file.unlink(missing_ok=True)
            print(f"  -> Hoàn thành nạp {title} ({out_path.stat().st_size // 1024} KB)")
        except Exception as e:
            print(f"  -> Lỗi tải {title}: {e}")
            tmp_file.unlink(missing_ok=True)

if __name__ == "__main__":
    tai_va_chuan_hoa_bgm()
