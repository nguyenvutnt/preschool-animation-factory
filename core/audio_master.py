#!/usr/bin/env python3
"""MODULE HÒA ÂM CHUẨN PHÁT THANH TRUYỀN HÌNH QUỐC TẾ (EBU R128).
Quy chuẩn:
  - Integrated Loudness: -14.0 LUFS (+/- 0.5 LU)
  - True Peak: <= -1.0 dBTP
  - Loudness Range: <= 7.0 LU
  - Tự động Sidechain Compression Ducking: Ép nhỏ nhạc nền BGM (-14dB) khi có tiếng đọc.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

def master_audio_ebu_r128(
    speech_path: Path,
    bgm_path: Path,
    out_master: Path,
    target_lufs: float = -14.0,
    true_peak: float = -1.0,
    bgm_base_vol: float = 0.22
) -> Path:
    """Hòa âm giọng đọc và nhạc nền bằng FFmpeg với Sidechain Ducking và chuẩn EBU R128."""
    mix_cmd = [
        'ffmpeg', '-y',
        '-i', str(speech_path),
        '-stream_loop', '-1', '-i', str(bgm_path),
        '-filter_complex',
        f'[1:a]volume={bgm_base_vol}[bgm];'
        f'[bgm][0:a]sidechaincompress=threshold=0.08:ratio=4:attack=50:release=300[ducked];'
        f'[0:a][ducked]amix=inputs=2:duration=first:dropout_transition=2[mixed];'
        f'[mixed]loudnorm=I={target_lufs}:TP={true_peak}:LRA=7.0:dual_mono=false[master]',
        '-map', '[master]',
        '-c:a', 'aac', '-b:a', '192k',
        str(out_master)
    ]
    subprocess.run(mix_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    return out_master
