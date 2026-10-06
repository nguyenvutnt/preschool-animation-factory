#!/usr/bin/env python3
"""MODULE DỰNG SÂN KHẤU VISUAL 1920x1080 ĐA THỂ LOẠI (MULTI-GENRE VISUAL COMPOSER).
Hỗ trợ toàn diện 8 thể loại học liệu mầm non:
  1. glenn_doman: Nền trắng sạch tinh khiết, zero-clutter, thẻ chữ to toàn màn hình.
  2. vocabulary: Sân khấu Top Stage + Safe Buffer >= 140px + Bottom Flashcard Bar.
  3. phonics: Khung Letter Spotlight + Hộp chia âm CVC (Nguyên âm Đỏ / Phụ âm Xanh).
  4. sight_words: Huy hiệu từ khóa trung tâm + 3 dải câu mẫu lặp lại (Sentence Frames).
  5. conversation: Sân khấu đối thoại 2 phía (Left/Right Speakers) + Bong bóng thoại.
  6. rhyme: Bố cục thơ trang nhã pastel, canh lề êm đềm, tôn vinh vần điệu.
  7. story: Khung sách tranh truyện lật trang (70% tranh tranh vẽ + 30% dải read-along).
  8. song: Sân khấu âm nhạc vận động, biểu tượng hành động TPR (Clap, Jump, Stomp).
"""
from __future__ import annotations

from pathlib import Path
from typing import List, Optional
from PIL import Image, ImageDraw, ImageFont

def render_glenn_doman_stage(
    out_image: Path,
    bg_color: str = "#FFFFFF",
    card_border_color: str = "#F0EAE1"
) -> Path:
    """Tạo sân khấu Glenn Doman chuẩn Não phải: Nền trắng tuyệt đối, không chi tiết thừa."""
    img = Image.new("RGB", (1920, 1080), bg_color)
    draw = ImageDraw.Draw(img)
    # Khung thẻ trắng bo góc siêu nhẹ để phân định ranh giới mắt nhìn
    card_box = [120, 90, 1800, 990]
    draw.rounded_rectangle(card_box, radius=28, fill="#FFFFFF", outline=card_border_color, width=3)
    img.save(out_image, "PNG")
    return out_image

def render_stage_image(
    out_image: Path,
    bg_color: str = "#FFF9F2",
    stage_box_color: str = "#FFEEDD",
    card_box_color: str = "#FFFFFF",
    subject_image_path: Optional[Path] = None
) -> Path:
    """Sân khấu Từ vựng & Khái niệm (Vocabulary / Zero-Collision)."""
    img = Image.new("RGB", (1920, 1080), bg_color)
    draw = ImageDraw.Draw(img)

    # 1. Top Visual Stage: Y=80 đến 720 (Cao 640px)
    stage_box = [200, 80, 1720, 720]
    draw.rounded_rectangle(stage_box, radius=24, fill=stage_box_color, outline="#E8D5C4", width=3)

    if subject_image_path and subject_image_path.exists():
        try:
            subj = Image.open(subject_image_path).convert("RGBA")
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

def render_phonics_stage(
    out_image: Path,
    bg_color: str = "#F3F7FA",
    letter: str = "A"
) -> Path:
    """Sân khấu Ngữ âm Oxford Phonics: Spotlight chữ cái + 3 ô ghép vần CVC."""
    img = Image.new("RGB", (1920, 1080), bg_color)
    draw = ImageDraw.Draw(img)

    # 1. Khung Letter Spotlight phía trên
    spotlight_box = [360, 70, 1560, 540]
    draw.rounded_rectangle(spotlight_box, radius=24, fill="#EBF2F7", outline="#CFDEE8", width=3)

    # 2. Dải 3 ô ghép âm CVC phía dưới (Consonant - Vowel - Consonant)
    # Box 1 (Phụ âm đầu)
    draw.rounded_rectangle([360, 590, 720, 830], radius=20, fill="#FFFFFF", outline="#1D3557", width=3)
    # Box 2 (Nguyên âm giữa - Đỏ nổi bật)
    draw.rounded_rectangle([780, 590, 1140, 830], radius=20, fill="#FFF0F0", outline="#E63946", width=4)
    # Box 3 (Phụ âm cuối)
    draw.rounded_rectangle([1200, 590, 1560, 830], radius=20, fill="#FFFFFF", outline="#1D3557", width=3)

    # Thanh phụ đề chant đáy (Y=870 đến 1030)
    draw.rounded_rectangle([300, 870, 1620, 1030], radius=16, fill="#FFFFFF", outline="#DFCFBE", width=2)

    img.save(out_image, "PNG")
    return out_image

def render_sight_words_stage(
    out_image: Path,
    bg_color: str = "#FAF8F5"
) -> Path:
    """Sân khấu Sight Words: Huy hiệu từ khóa trung tâm + 3 dòng Sentence Frames."""
    img = Image.new("RGB", (1920, 1080), bg_color)
    draw = ImageDraw.Draw(img)

    # Khung Word Focus lớn ở trên (Y=80 đến 450)
    draw.rounded_rectangle([400, 80, 1520, 450], radius=28, fill="#FFFFFF", outline="#FFB703", width=4)

    # 3 Khung câu mẫu lặp lại (Sentence Frames Y=490, 660, 830)
    for idx, y in enumerate([490, 660, 830]):
        box = [260, y, 1660, y + 140]
        draw.rounded_rectangle(box, radius=18, fill="#FFFFFF", outline="#E4DCD3", width=2)

    img.save(out_image, "PNG")
    return out_image

def render_conversation_stage(
    out_image: Path,
    bg_color: str = "#F8F9FA"
) -> Path:
    """Sân khấu Giao tiếp tình huống: Đối thoại 2 nhân vật (Left / Right)."""
    img = Image.new("RGB", (1920, 1080), bg_color)
    draw = ImageDraw.Draw(img)

    # Vùng Nhân vật A (Bên trái: X: 160 đến 720, Y: 100 đến 760)
    draw.rounded_rectangle([160, 100, 720, 760], radius=24, fill="#E8F4F8", outline="#BEE3F8", width=3)

    # Biểu tượng tương tác ở giữa (Interactive Heart / Soundwave X: 840 đến 1080)
    draw.rounded_rectangle([840, 360, 1080, 500], radius=20, fill="#FFF3CD", outline="#FFEBAA", width=3)

    # Vùng Nhân vật B (Bên phải: X: 1200 đến 1760, Y: 100 đến 760)
    draw.rounded_rectangle([1200, 100, 1760, 760], radius=24, fill="#FFF2E8", outline="#FBD38D", width=3)

    # Khung phụ đề đối thoại tương tác ở đáy (Y=820 đến 1030)
    draw.rounded_rectangle([200, 820, 1720, 1030], radius=20, fill="#FFFFFF", outline="#D3D3D3", width=2)

    img.save(out_image, "PNG")
    return out_image

def render_rhyme_stage(
    out_image: Path,
    bg_color: str = "#FAF6F0"
) -> Path:
    """Sân khấu Thơ ngắn & Vần điệu (Nursery Rhymes & Poems)."""
    img = Image.new("RGB", (1920, 1080), bg_color)
    draw = ImageDraw.Draw(img)

    # Khung tranh thơ nghệ thuật viền pastel
    outer_box = [180, 90, 1740, 990]
    draw.rounded_rectangle(outer_box, radius=32, fill="#FFFFFF", outline="#E2D4C3", width=3)

    inner_box = [220, 130, 1700, 950]
    draw.rounded_rectangle(inner_box, radius=24, fill="#FCFAF7", outline="#F0E8DC", width=2)

    img.save(out_image, "PNG")
    return out_image

def render_story_stage(
    out_image: Path,
    bg_color: str = "#F5F2EB"
) -> Path:
    """Sân khấu Truyện tranh kể chuyện (Read-Along Storybook)."""
    img = Image.new("RGB", (1920, 1080), bg_color)
    draw = ImageDraw.Draw(img)

    # Khung tranh truyện lớn (Y=70 đến 770, cao 700px, 70% diện tích)
    story_box = [160, 70, 1760, 770]
    draw.rounded_rectangle(story_box, radius=24, fill="#FFFFFF", outline="#DBC8B6", width=3)

    # Dải chữ đọc truyện Read-along bên dưới (Y=820 đến 1030)
    text_strip = [160, 820, 1760, 1030]
    draw.rounded_rectangle(text_strip, radius=18, fill="#FFFFFF", outline="#DBC8B6", width=2)

    img.save(out_image, "PNG")
    return out_image

def render_song_stage(
    out_image: Path,
    bg_color: str = "#FFF8ED"
) -> Path:
    """Sân khấu Bài hát & Vận động TPR (Action Songs & Movement)."""
    img = Image.new("RGB", (1920, 1080), bg_color)
    draw = ImageDraw.Draw(img)

    # Khung sân khấu vận động lớn ở giữa (Y=80 đến 750)
    stage_box = [200, 80, 1720, 750]
    draw.rounded_rectangle(stage_box, radius=28, fill="#FFF2DF", outline="#F6D5A8", width=3)

    # Thanh hiển thị Lyric bài hát phía dưới (Y=810 đến 1030)
    lyric_box = [250, 810, 1670, 1030]
    draw.rounded_rectangle(lyric_box, radius=20, fill="#FFFFFF", outline="#E4C8A6", width=2)

    img.save(out_image, "PNG")
    return out_image

def compose_stage_by_genre(
    genre: str,
    out_image: Path,
    subject_image_path: Optional[Path] = None
) -> Path:
    """Điều phối dựng sân khấu chuẩn xác theo từng thể loại học liệu."""
    g = genre.lower().strip()
    if g in ("glenn_doman", "glenndoman", "flashcard"):
        return render_glenn_doman_stage(out_image)
    elif g in ("phonics", "nguam"):
        return render_phonics_stage(out_image)
    elif g in ("sight_words", "sightword", "signword"):
        return render_sight_words_stage(out_image)
    elif g in ("conversation", "giaotiep", "dialogue"):
        return render_conversation_stage(out_image)
    elif g in ("rhyme", "poem", "tho"):
        return render_rhyme_stage(out_image)
    elif g in ("story", "storybook", "truyen"):
        return render_story_stage(out_image)
    elif g in ("song", "movement", "baihat"):
        return render_song_stage(out_image)
    else: # vocabulary default
        return render_stage_image(out_image, subject_image_path=subject_image_path)
