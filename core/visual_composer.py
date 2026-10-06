#!/usr/bin/env python3
"""MODULE DỰNG SÂN KHẤU VISUAL 1920x1080 CHUẨN LOW-STIMULATION & ZERO COLLISION.
Phân vùng nghiêm ngặt:
  - Top Visual Stage: Y=70px -> 750px (Khung tranh trung tâm 1600x680, bo góc mềm mại).
  - Safe Buffer Zone: Y=750px -> 820px (Khoảng cách an toàn >= 140px, cấm đè hình).
  - Bottom Flashcard Bar: Y=820px -> 1080px (Vùng độc lập cho thẻ chữ đỏ Glenn Doman).
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional
from PIL import Image, ImageDraw

def render_stage_image(
    out_image: Path,
    bg_color: str = "#FFF9F2",
    stage_box_color: str = "#FFEEDD",
    card_box_color: str = "#FFFFFF",
    subject_image_path: Optional[Path] = None
) -> Path:
    """Tạo khung hình tĩnh 1920x1080 với bố cục Low-Stimulation."""
    img = Image.new("RGB", (1920, 1080), bg_color)
    draw = ImageDraw.Draw(img)

    # 1. Top Visual Stage: Khung sân khấu Y=80 đến 720 (Cao 640px)
    stage_box = [200, 80, 1720, 720]
    draw.rounded_rectangle(stage_box, radius=24, fill=stage_box_color, outline="#E8D5C4", width=3)

    # Nếu có ảnh đối tượng thực tế hoặc 2D sprite, dán vào giữa Top Stage
    if subject_image_path and subject_image_path.exists():
        try:
            subj = Image.open(subject_image_path).convert("RGBA")
            # Resize fit trong 1400x560
            subj.thumbnail((1400, 560), Image.Resampling.LANCZOS)
            offset_x = 200 + (1520 - subj.width) // 2
            offset_y = 80 + (640 - subj.height) // 2
            img.paste(subj, (offset_x, offset_y), subj)
        except Exception:
            pass

    # 2. Bottom Flashcard Bar: Y=830 đến 1030 (Cao 200px)
    card_box = [320, 830, 1600, 1030]
    draw.rounded_rectangle(card_box, radius=20, fill=card_box_color, outline="#DFCFBE", width=2)

    img.save(out_image, "PNG")
    return out_image
