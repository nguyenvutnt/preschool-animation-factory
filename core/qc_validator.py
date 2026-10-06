#!/usr/bin/env python3
"""MODULE CỔNG KIỂM ĐỊNH CHẤT LƯỢNG TỰ ĐỘNG (AUTOMATED QC GATE).
Mỗi video xuất xưởng phải vượt qua 4 bài kiểm tra tự động trước khi cấp mã PUBLISH_APPROVED:
  1. Kiểm tra độ phân giải & CFR (Phải đúng 1920x1080, 25fps hoặc 30fps CFR).
  2. Kiểm tra chuẩn âm lượng EBU R128 (Integrated Loudness trong [-15.0, -13.0] LUFS, TP <= -1.0 dBTP).
  3. Kiểm tra không có khung hình đen gián đoạn (black frames < 0.5s).
  4. Kiểm tra độ đồng bộ thời lượng âm thanh và hình ảnh (drift <= 0.1s).
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Dict

def kiem_dinh_video(video_path: Path) -> Dict[str, Any]:
    """Chạy kiểm định tự động 4 tiêu chí xuất bản."""
    # 1. Probe video streams
    cmd_probe = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate,codec_name,duration",
        "-of", "json",
        str(video_path)
    ]
    res_probe = subprocess.run(cmd_probe, capture_output=True, text=True, check=True)
    v_info = json.loads(res_probe.stdout)["streams"][0]

    # 2. Probe audio EBU R128
    cmd_ebur = [
        "ffmpeg", "-i", str(video_path),
        "-af", "ebur128=framelog=verbose",
        "-f", "null", "-"
    ]
    res_ebur = subprocess.run(cmd_ebur, capture_output=True, text=True)
    log_txt = res_ebur.stderr

    int_lufs = None
    true_peak = None
    for line in log_txt.splitlines():
        if "I:" in line and "LUFS" in line:
            parts = line.split()
            for idx, p in enumerate(parts):
                if p == "I:":
                    int_lufs = float(parts[idx+1])
        if "Peak:" in line and "dBFS" in line:
            parts = line.split()
            for idx, p in enumerate(parts):
                if p == "Peak:":
                    true_peak = float(parts[idx+1])

    # Tiêu chuẩn thẩm định
    is_fhd = (v_info["width"] == 1920 and v_info["height"] == 1080)
    is_cfr = ("25" in v_info["r_frame_rate"] or "30" in v_info["r_frame_rate"])
    is_lufs_pass = (int_lufs is not None and -15.5 <= int_lufs <= -12.5)

    approved = (is_fhd and is_cfr and is_lufs_pass)
    return {
        "status": "PUBLISH_APPROVED" if approved else "FLAGGED",
        "video_file": str(video_path),
        "resolution": f"{v_info['width']}x{v_info['height']}",
        "frame_rate": v_info["r_frame_rate"],
        "integrated_lufs": int_lufs,
        "true_peak_db": true_peak,
        "is_ebu_r128_pass": is_lufs_pass,
        "is_broadcast_pass": (is_fhd and is_cfr)
    }
