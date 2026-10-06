#!/usr/bin/env python3
"""MODULE SINH PHỤ ĐỀ ASS ĐA THỂ LOẠI MẦM NON (MULTI-GENRE SUBTITLE GENERATOR).
Hỗ trợ định dạng typography riêng biệt cho 8 thể loại:
  - glenn_doman: Chữ đỏ to 130pt canh chính giữa màn hình (Alignment 5), não phải chụp hình tức thì.
  - vocabulary: Chữ đỏ 96pt canh giữa dải flashcard đáy (Alignment 2).
  - phonics: Chữ to rõ 100pt, phân biệt âm vần rõ ràng.
  - sight_words: Cỡ chữ 84pt, highlight từ khóa trong câu.
  - conversation: Phân biệt lượt nói bên Trái (Speaker A) và bên Phải (Speaker B).
  - rhyme: Dòng thơ trang nhã 80pt, nhịp điệu êm dịu.
  - story: Dải chữ đọc truyện Read-along 74pt thanh thoát.
  - song: Lời bài hát rộn ràng 88pt, nhịp nhàng theo giai điệu.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

def format_ass_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h}:{m:02d}:{s:05.2f}"

def tao_file_sub_ass(
    shots: List[Dict[str, Any]],
    out_ass: Path,
    genre: str = "vocabulary"
) -> Path:
    """Tạo file phụ đề ASS phù hợp chính xác với từng thể loại học liệu."""
    g = genre.lower().strip()

    header = """[Script Info]
Title: True English Multi-Genre Preschool Subtitles
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
PlayResX: 1920
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: DomanCenter,DejaVu Sans,130,&H001414DC,&H000000FF,&H00FFFFFF,&H60000000,-1,0,0,0,100,100,2,0,1,8,3,5,40,40,0,1
Style: VocabBottom,DejaVu Sans,96,&H001414DC,&H000000FF,&H00FFFFFF,&H40000000,-1,0,0,0,100,100,2,0,1,8,2,2,40,40,68,1
Style: PhonicsStyle,DejaVu Sans,100,&H001D3557,&H000000FF,&H00FFFFFF,&H40000000,-1,0,0,0,100,100,2,0,1,8,2,2,40,40,68,1
Style: SightWordStyle,DejaVu Sans,86,&H00141414,&H000000FF,&H00FFFFFF,&H40000000,-1,0,0,0,100,100,2,0,1,8,2,2,40,40,68,1
Style: SpeakerLeft,DejaVu Sans,86,&H008A2BE2,&H000000FF,&H00FFFFFF,&H40000000,-1,0,0,0,100,100,2,0,1,8,2,1,200,800,68,1
Style: SpeakerRight,DejaVu Sans,86,&H002E8B57,&H000000FF,&H00FFFFFF,&H40000000,-1,0,0,0,100,100,2,0,1,8,2,3,800,200,68,1
Style: RhymeStyle,DejaVu Sans,82,&H002C3E50,&H000000FF,&H00FFFFFF,&H40000000,-1,0,0,0,100,100,2,0,1,7,2,2,60,60,75,1
Style: StoryStyle,DejaVu Sans,76,&H001A252C,&H000000FF,&H00FFFFFF,&H40000000,-1,0,0,0,100,100,2,0,1,6,2,2,60,60,65,1
Style: SongStyle,DejaVu Sans,88,&H00D35400,&H000000FF,&H00FFFFFF,&H40000000,-1,0,0,0,100,100,2,0,1,8,2,2,40,40,68,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []
    current_time = 0.5

    # Chọn Style mặc định theo thể loại
    default_style = "VocabBottom"
    if g in ("glenn_doman", "glenndoman", "flashcard"):
        default_style = "DomanCenter"
    elif g in ("phonics", "nguam"):
        default_style = "PhonicsStyle"
    elif g in ("sight_words", "sightword", "signword"):
        default_style = "SightWordStyle"
    elif g in ("conversation", "giaotiep"):
        default_style = "SpeakerLeft"
    elif g in ("rhyme", "poem", "tho"):
        default_style = "RhymeStyle"
    elif g in ("story", "storybook", "truyen"):
        default_style = "StoryStyle"
    elif g in ("song", "movement", "baihat"):
        default_style = "SongStyle"

    for idx, it in enumerate(shots):
        dur = it.get("duration", 5.0)
        start_t = current_time
        end_t = current_time + dur - 0.2
        text = it.get("card_text", "")

        # Xử lý riêng cho Conversation (đổi lượt Left/Right)
        if g in ("conversation", "giaotiep"):
            speaker = it.get("speaker", "A")
            style = "SpeakerLeft" if speaker == "A" or idx % 2 == 0 else "SpeakerRight"
        else:
            style = default_style

        events.append(
            f"Dialogue: 0,{format_ass_time(start_t)},{format_ass_time(end_t)},{style},,0,0,0,,{text}"
        )
        current_time += dur

    out_ass.write_text(header + "\n".join(events), encoding="utf-8")
    return out_ass
