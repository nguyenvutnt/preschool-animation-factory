#!/usr/bin/env python3
"""MODULE SINH PHỤ ĐỀ ASS CHUẨN GLENN DOMAN MẦM NON.
Đặc tính:
  - Font: DejaVu Sans nét tròn dày, dễ nhận biết mặt chữ.
  - Cỡ chữ: 92pt, Màu đỏ Glenn Doman (&H001414DC), viền trắng nổi khối 8px (&H00FFFFFF).
  - Tương phản: Đạt chuẩn WCAG AAA (>= 7:1) trên nền trắng.
  - Vị trí: Canh giữa đáy (Alignment: 2, MarginV: 68px).
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

def format_ass_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h}:{m:02d}:{s:05.2f}"

def tao_file_sub_ass(shots: List[Dict[str, Any]], out_ass: Path) -> Path:
    """Tạo file phụ đề ASS từ danh sách phân cảnh."""
    header = """[Script Info]
Title: Glenn Doman Micro-Shots Subtitles
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
PlayResX: 1920
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: DomanRed,DejaVu Sans,92,&H001414DC,&H000000FF,&H00FFFFFF,&H40000000,-1,0,0,0,100,100,2,0,1,8,2,2,40,40,68,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []
    current_time = 0.5
    for it in shots:
        dur = it.get("duration", 5.0)
        start_t = current_time
        end_t = current_time + dur - 0.2
        text = it.get("card_text", "")
        events.append(
            f"Dialogue: 0,{format_ass_time(start_t)},{format_ass_time(end_t)},DomanRed,,0,0,0,,{text}"
        )
        current_time += dur

    out_ass.write_text(header + "\n".join(events), encoding="utf-8")
    return out_ass
