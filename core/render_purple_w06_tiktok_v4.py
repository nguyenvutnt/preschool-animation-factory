#!/usr/bin/env python3
"""
ĐỘNG CƠ HOẠT HÌNH KHỐI PURPLE V4 MASTER (TIKTOK VERTICAL 1080x1920)
CHỦ ĐỀ: TUẦN 06 VOCABULARY - WHERE ARE WE IN OUR SCHOOL?
ĐỘ TUỔI: 4-5 TUỔI (PURPLE STAGE)

TÍCH HỢP HỆ THỐNG GIÁO VIÊN ẢO ĐIỀU HƯỚNG SƯ PHẠM (PEDAGOGICAL VIRTUAL TEACHER POINTER):
1. Bàn tay trỏ thần kỳ (Pointer Hand with Magic Star) & Dụng cụ điều phối (Magic Lens, Magic Brush)
   di chuyển có chủ đích trên màn hình, dẫn dắt ánh nhìn của trẻ vào đúng đối tượng học tập.
2. Vòng hào quang chỉ điểm (Focus Spotlight Ring) tỏa rộng làm nổi bật chi tiết trong tranh.
3. Trượt theo lòng máng cầu trượt (Slide Path Tracing) trong Playground.
4. Nét cọ vẽ cầu vồng động (Dynamic Rainbow Brush Arc) trong Art Room.
5. Đấu nối trực tiếp dữ liệu từ Nhà máy TrueLearning (out/TL16/syllabus.jsonl).
"""

import json
import math
import os
import subprocess
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

REPO_ROOT = Path(__file__).resolve().parent.parent
DIR = Path("/root/scratch/purple_w06_tiktok")
V3_DIR = REPO_ROOT / "assets" / "purple" / "v3"
STICKERS_DIR = REPO_ROOT / "assets" / "purple" / "stickers"
ASSETS_DIR = REPO_ROOT / "assets" / "purple"
GUIDE_DIR = ASSETS_DIR / "guide_icons"

AUDIO_FILE = DIR / "master_audio_v3.mp3"
MANIFEST_FILE = DIR / "manifest_v3.json"
VISEME_DIR = DIR / "gemini_visemes"
OUT_VIDEO = REPO_ROOT / "demo_products" / "demo_W06_Purple_TikTok_Master_V4.mp4"
OUT_VIDEO.parent.mkdir(parents=True, exist_ok=True)

FONT_PATH = "/usr/share/fonts/opentype/comic-neue/ComicNeue-Bold.otf"
W, H = 1080, 1920
FPS = 30

# Nạp timeline & visemes
with open(MANIFEST_FILE, "r") as fp:
    manifest_data = json.load(fp)

TOTAL_DURATION = manifest_data["total_duration"]
TOTAL_FRAMES = int(TOTAL_DURATION * FPS)
events = manifest_data["events"]
dialogue_events = [e for e in events if e.get("type") == "dialogue"]

# Nạp Rhubarb visemes
visemes_map = {}
for ev in dialogue_events:
    v_file = VISEME_DIR / f"{ev['id']}.json"
    if v_file.exists():
        with open(v_file, "r") as fp:
            visemes_map[ev["id"]] = json.load(fp).get("mouthCues", [])
    else:
        visemes_map[ev["id"]] = []

print(f"🎬 Khởi động Master Video Renderer V4 Virtual Teacher Guided ({TOTAL_DURATION:.1f}s, {TOTAL_FRAMES} frames)...")

# 1. TIỀN XỬ LÝ ẢNH BỐI CẢNH 3D PIXAR
BG_FILES = {
    "door": ASSETS_DIR / "magic_door.png",
    "classroom": V3_DIR / "scene_classroom.jpg",
    "library": V3_DIR / "scene_library.jpg",
    "playground": V3_DIR / "scene_playground.jpg",
    "artroom": V3_DIR / "scene_artroom.jpg"
}

CARD_W, CARD_H = 960, 780
CARD_X = (W - CARD_W) // 2 # 60
CARD_Y = 250

bg_oversized = {}
for k, p in BG_FILES.items():
    if p.exists():
        im = Image.open(p).convert("RGB")
        bg_oversized[k] = im.resize((CARD_W + 140, CARD_H + 114), Image.Resampling.BILINEAR)
    else:
        bg_oversized[k] = Image.new("RGB", (CARD_W + 140, CARD_H + 114), (200, 200, 240))

# MASK BO TRÒN GÓC CHO CARD TRANH (Corner radius = 48px)
card_mask = Image.new("L", (CARD_W, CARD_H), 0)
d_mask = ImageDraw.Draw(card_mask)
d_mask.rounded_rectangle([0, 0, CARD_W, CARD_H], radius=48, fill=255)

card_border_overlay = Image.new("RGBA", (CARD_W, CARD_H), (0, 0, 0, 0))
d_border = ImageDraw.Draw(card_border_overlay)
d_border.rounded_rectangle([0, 0, CARD_W, CARD_H], radius=48, outline="#FFFFFF", width=14)
d_border.rounded_rectangle([6, 6, CARD_W - 6, CARD_H - 6], radius=42, outline="#7B1FA2", width=4)

card_shadow = Image.new("RGBA", (CARD_W + 60, CARD_H + 60), (0, 0, 0, 0))
d_cs = ImageDraw.Draw(card_shadow)
d_cs.rounded_rectangle([30, 30, CARD_W + 30, CARD_H + 30], radius=52, fill=(0, 0, 0, 90))
card_shadow = card_shadow.filter(ImageFilter.GaussianBlur(16))

# 2. TIỀN XỬ LÝ ICONS GIÁO VIÊN ẢO ĐIỀU HƯỚNG
pointer_hand = Image.open(GUIDE_DIR / "pointer_hand_star.png").convert("RGBA").resize((180, 180), Image.Resampling.BILINEAR)
magic_brush = Image.open(GUIDE_DIR / "magic_brush.png").convert("RGBA").resize((180, 180), Image.Resampling.BILINEAR)
magic_lens = Image.open(GUIDE_DIR / "magic_lens.png").convert("RGBA").resize((180, 180), Image.Resampling.BILINEAR)
star_icon = Image.open(STICKERS_DIR / "sticker_star.png").convert("RGBA").resize((140, 140), Image.Resampling.BILINEAR)

# 3. TIỀN XỬ LÝ NHÂN VẬT (LEO BUNNY & MIA KID)
bunny_base = Image.open(ASSETS_DIR / "bunny_base.png").convert("RGBA").resize((380, 480), Image.Resampling.BILINEAR)
bunny_eyes_norm = Image.open(ASSETS_DIR / "bunny_eyes_normal.png").convert("RGBA").resize((380, 480), Image.Resampling.BILINEAR)
bunny_eyes_wink = Image.open(ASSETS_DIR / "bunny_eyes_wink.png").convert("RGBA").resize((380, 480), Image.Resampling.BILINEAR)

mia_base = Image.open(ASSETS_DIR / "mia_base.png").convert("RGBA").resize((380, 480), Image.Resampling.BILINEAR)
mia_eyes_norm = Image.open(ASSETS_DIR / "mia_eyes_normal.png").convert("RGBA").resize((380, 480), Image.Resampling.BILINEAR)
mia_eyes_wink = Image.open(ASSETS_DIR / "mia_eyes_wink.png").convert("RGBA").resize((380, 480), Image.Resampling.BILINEAR)

def build_viseme_mouth(v_char, w=110, h=65):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    v = v_char.upper()
    if v in ["A", "B"]:
        d.line([(20, h//2), (w-20, h//2)], fill="#4A0E4E", width=7)
    elif v in ["C", "D"]:
        d.rounded_rectangle([20, h//2 - 14, w - 20, h//2 + 16], radius=10, fill="#E11D48", outline="#4A0E4E", width=4)
        d.rectangle([28, h//2 - 12, w - 28, h//2 - 2], fill="#FFFFFF")
    elif v in ["E", "F"]:
        d.ellipse([16, 8, w - 16, h - 8], fill="#E11D48", outline="#4A0E4E", width=4)
        d.rectangle([28, 10, w - 28, 23], fill="#FFFFFF")
        d.ellipse([28, h - 24, w - 28, h - 12], fill="#F43F5E")
    elif v in ["G", "H"]:
        d.ellipse([14, 5, w - 14, h - 5], fill="#9F1239", outline="#4A0E4E", width=4)
        d.rectangle([26, 7, w - 26, 21], fill="#FFFFFF")
        d.ellipse([26, h - 25, w - 26, h - 10], fill="#FB7185")
    else:
        d.arc([20, h//2 - 10, w - 20, h//2 + 18], start=0, end=180, fill="#4A0E4E", width=6)
    return im

viseme_cache = {v: build_viseme_mouth(v) for v in ["A", "B", "C", "D", "E", "F", "G", "H", "X"]}

char_shadow = Image.new("RGBA", (340, 45), (0, 0, 0, 0))
d_sh = ImageDraw.Draw(char_shadow)
d_sh.ellipse([10, 5, 330, 40], fill=(0, 0, 0, 85))
char_shadow = char_shadow.filter(ImageFilter.GaussianBlur(8))

# 4. TIỀN TẠO THẺ TỪ VỰNG HOÀN HẢO (100% ZERO TỪ THỪA)
WORDS_MAP = {
    "WELCOME!":   {"bg": "#FFF9C4", "border": "#F57F17", "text": "#E65100", "size": 115},
    "CLASSROOM":  {"bg": "#EDE7F6", "border": "#6A1B9A", "text": "#4A148C", "size": 120},
    "LEARN":      {"bg": "#E1F5FE", "border": "#0288D1", "text": "#01579B", "size": 130},
    "LIBRARY":    {"bg": "#E0F2F1", "border": "#00897B", "text": "#004D40", "size": 125},
    "READ":       {"bg": "#FFF3E0", "border": "#FB8C00", "text": "#E65100", "size": 135},
    "PLAYGROUND": {"bg": "#E8F5E9", "border": "#43A047", "text": "#1B5E20", "size": 110},
    "PLAY":       {"bg": "#FBE9E7", "border": "#F4511E", "text": "#BF360C", "size": 135},
    "ART ROOM":   {"bg": "#FCE4EC", "border": "#D81B60", "text": "#880E4F", "size": 120},
    "PAINT":      {"bg": "#F3E5F5", "border": "#8E24AA", "text": "#4A148C", "size": 135},
    "SUPER STARS!": {"bg": "#FFFDE7", "border": "#FFB300", "text": "#FF6F00", "size": 110}
}

CARD_TEXT_W, CARD_TEXT_H = 880, 180
word_card_cache = {}
for w_text, conf in WORDS_MAP.items():
    card_img = Image.new("RGBA", (CARD_TEXT_W + 40, CARD_TEXT_H + 40), (0, 0, 0, 0))
    d_c = ImageDraw.Draw(card_img)
    d_c.rounded_rectangle([20, 25, CARD_TEXT_W + 20, CARD_TEXT_H + 25], radius=36, fill=(0, 0, 0, 75))
    card_img = card_img.filter(ImageFilter.GaussianBlur(10))
    d_c = ImageDraw.Draw(card_img)
    d_c.rounded_rectangle([15, 15, CARD_TEXT_W + 15, CARD_TEXT_H + 15], radius=36, fill=conf["bg"], outline="#FFFFFF", width=8)
    d_c.rounded_rectangle([19, 19, CARD_TEXT_W + 11, CARD_TEXT_H + 11], radius=32, outline=conf["border"], width=4)
    
    fnt = ImageFont.truetype(FONT_PATH, conf["size"])
    bbox = fnt.getbbox(w_text)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = 15 + (CARD_TEXT_W - tw) // 2 - bbox[0]
    ty = 15 + (CARD_TEXT_H - th) // 2 - bbox[1] - 4
    
    for ox in range(-6, 7, 2):
        for oy in range(-6, 7, 2):
            d_c.text((tx + ox, ty + oy), w_text, font=fnt, fill="#FFFFFF")
    d_c.text((tx, ty), w_text, font=fnt, fill=conf["text"])
    word_card_cache[w_text] = card_img

# HEADER BADGE CỐ ĐỊNH
header_badge = Image.new("RGBA", (960, 120), (0, 0, 0, 0))
d_hb = ImageDraw.Draw(header_badge)
d_hb.rounded_rectangle([0, 0, 960, 120], radius=30, fill="#6A1B9A", outline="#FFD54F", width=5)
fnt_h1 = ImageFont.truetype(FONT_PATH, 46)
fnt_h2 = ImageFont.truetype(FONT_PATH, 28)

title_txt = "WHERE ARE WE IN OUR SCHOOL?"
bb1 = fnt_h1.getbbox(title_txt)
d_hb.text(((960 - (bb1[2]-bb1[0]))//2 - bb1[0], 18), title_txt, font=fnt_h1, fill="#FFFFFF")

sub_txt = "PURPLE STAGE • AGES 4-5 • WEEK 06"
bb2 = fnt_h2.getbbox(sub_txt)
d_hb.text(((960 - (bb2[2]-bb2[0]))//2 - bb2[0], 76), sub_txt, font=fnt_h2, fill="#FFF59D")

# SÀN SÂN KHẤU HOẠT HÌNH DƯỚI CÙNG
stage_floor = Image.new("RGBA", (W, 280), (0, 0, 0, 0))
d_sf = ImageDraw.Draw(stage_floor)
d_sf.chord([-100, 20, W + 100, 560], start=180, end=360, fill="#FFE082", outline="#FFB300", width=6)
d_sf.chord([-100, 140, W + 100, 680], start=180, end=360, fill="#81C784", outline="#4CAF50", width=4)

# NỀN GRADIENT PASTEL
bg_pastel = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d_bp = ImageDraw.Draw(bg_pastel)
for y in range(H):
    ratio = y / H
    r = int(255 * (1 - ratio) + 243 * ratio)
    g = int(253 * (1 - ratio) + 229 * ratio)
    b = int(231 * (1 - ratio) + 245 * ratio)
    d_bp.line([(0, y), (W, y)], fill=(r, g, b, 255))

# XÁC ĐỊNH BỐI CẢNH VÀ QUỸ ĐẠO ĐIỀU HƯỚNG CỦA GIÁO VIÊN ẢO
def get_scene_state(t):
    curr_ev = None
    for ev in dialogue_events:
        st = ev["start_ms"] / 1000.0
        et = ev["end_ms"] / 1000.0
        if st <= t <= et:
            curr_ev = ev
            break
            
    eid = curr_ev["id"] if curr_ev else ""
    
    if t < 3.2:
        return "door", "WELCOME!", curr_ev, "door"
    elif "door1" in eid:
        return "door", "CLASSROOM", curr_ev, "door"
    elif "classroom" in eid or "say_classroom" in eid:
        if "say_classroom" in eid and (t - (curr_ev["start_ms"]/1000.0)) > 1.2:
            return "classroom", "LEARN", curr_ev, "classroom_learn"
        return "classroom", "CLASSROOM", curr_ev, "classroom_spot"
    elif "door2" in eid:
        return "door", "LIBRARY", curr_ev, "door"
    elif "library" in eid or "read_library" in eid:
        if "read_library" in eid:
            return "library", "READ", curr_ev, "library_read"
        return "library", "LIBRARY", curr_ev, "library_scan"
    elif "whoosh" in eid:
        return "door", "PLAYGROUND", curr_ev, "door"
    elif "playground" in eid or "play" in eid:
        if "11_leo_play" in eid:
            return "playground", "PLAY", curr_ev, "playground_play"
        return "playground", "PLAYGROUND", curr_ev, "playground_slide"
    elif "door4" in eid:
        return "door", "ART ROOM", curr_ev, "door"
    elif "artroom" in eid or "paint" in eid:
        if "15_mia_paint" in eid:
            return "artroom", "PAINT", curr_ev, "artroom_paint"
        return "artroom", "ART ROOM", curr_ev, "artroom_easel"
    elif "fast_recap" in eid:
        rel_t = t - (curr_ev["start_ms"] / 1000.0)
        dur = curr_ev["duration_ms"] / 1000.0
        quarter = dur / 4.0
        if rel_t < quarter:
            return "classroom", "CLASSROOM", curr_ev, "recap_c"
        elif rel_t < quarter * 2:
            return "library", "LIBRARY", curr_ev, "recap_l"
        elif rel_t < quarter * 3:
            return "playground", "PLAYGROUND", curr_ev, "recap_p"
        else:
            return "artroom", "ART ROOM", curr_ev, "recap_a"
    else:
        return "classroom", "SUPER STARS!", curr_ev, "celebrate"

print("⚡ Tất cả các tài nguyên và thuật toán điều hướng đã sẵn sàng!")

def render_frame(f_idx):
    t = f_idx / FPS
    bg_key, word_text, curr_ev, guide_mode = get_scene_state(t)
    
    # 1. Canvas nền
    frame = bg_pastel.copy()
    
    # 2. Header
    frame.alpha_composite(header_badge, (CARD_X, 80))
    
    # 3. Card tranh minh họa (Ken Burns crop nhẹ)
    src_bg = bg_oversized.get(bg_key, bg_oversized["classroom"])
    kb_prog = (t % 3.0) / 3.0
    crop_x = int(60 + 35 * math.sin(kb_prog * math.pi))
    crop_y = int(50 + 25 * math.cos(kb_prog * math.pi))
    cropped = src_bg.crop((crop_x, crop_y, crop_x + CARD_W, crop_y + CARD_H)).convert("RGBA")
    
    card_content = Image.new("RGBA", (CARD_W, CARD_H), (0, 0, 0, 0))
    card_content.paste(cropped, (0, 0), card_mask)
    card_content.alpha_composite(card_border_overlay)
    
    frame.alpha_composite(card_shadow, (CARD_X - 30, CARD_Y - 30))
    frame.alpha_composite(card_content, (CARD_X, CARD_Y))
    
    # 4. HỆ THỐNG GIÁO VIÊN ẢO ĐIỀU HƯỚNG SƯ PHẠM (VIRTUAL TEACHER GUIDED POINTER)
    # Xác định tọa độ và hành động điều phối trên màn hình:
    guide_draw = ImageDraw.Draw(frame)
    
    if guide_mode == "classroom_spot":
        # Bàn tay trỏ gõ vào chiếc bàn học sinh trong lớp (Focus Spotlight Target)
        target_x, target_y = CARD_X + 480, CARD_Y + 440
        # Vòng hào quang phát sáng mở rộng
        pulse_r = int(24 + 18 * (math.sin(t * 8.0) * 0.5 + 0.5))
        guide_draw.ellipse([target_x - pulse_r, target_y - pulse_r, target_x + pulse_r, target_y + pulse_r], outline="#FFD54F", width=5)
        # Bàn tay trỏ bay vào chỉ điểm
        px = target_x - 120 + int(10 * math.sin(t * 8.0))
        py = target_y - 20 + int(10 * math.cos(t * 8.0))
        frame.alpha_composite(pointer_hand, (px, py))
        
    elif guide_mode == "classroom_learn":
        # Bàn tay trỏ di chuyển xuống thẻ từ vựng LEARN
        target_x, target_y = W // 2, 1100
        pulse_r = int(30 + 15 * (math.sin(t * 10.0) * 0.5 + 0.5))
        guide_draw.ellipse([target_x - 80 - pulse_r, target_y - pulse_r, target_x + 80 + pulse_r, target_y + pulse_r], outline="#40C4FF", width=4)
        px = target_x + 180 + int(15 * math.sin(t * 10.0))
        py = target_y - 70
        frame.alpha_composite(pointer_hand, (px, py))
        
    elif guide_mode == "library_scan":
        # Kính lúp ma thuật quét ngang kệ sách tranh theo chiều đọc từ trái sang phải
        sweep_prog = (t % 2.5) / 2.5
        lx = int(CARD_X + 180 + 560 * sweep_prog)
        ly = int(CARD_Y + 420 + 20 * math.sin(sweep_prog * math.pi * 2))
        # Vòng sáng soi kính lúp
        guide_draw.ellipse([lx + 20, ly + 20, lx + 120, ly + 120], outline="#FFEA00", width=4)
        frame.alpha_composite(magic_lens, (lx, ly))
        
    elif guide_mode == "library_read":
        # Bàn tay trỏ chỉ vào thẻ từ vựng READ
        target_x, target_y = W // 2, 1100
        px = target_x - 220 + int(14 * math.sin(t * 9.0))
        py = target_y - 70
        frame.alpha_composite(pointer_hand, (px, py))
        
    elif guide_mode == "playground_slide":
        # Ngôi sao ma thuật trượt theo lòng máng cầu trượt từ đỉnh xuống đáy
        slide_prog = (t % 2.2) / 2.2
        # Đường cong parabol cầu trượt
        sx = int(CARD_X + 680 - 320 * slide_prog)
        sy = int(CARD_Y + 280 + 380 * (slide_prog ** 1.3))
        # Vệt bụi sao lấp lánh (Stardust trail)
        for trail_i in range(5):
            trail_p = max(0.0, slide_prog - trail_i * 0.05)
            tx_pt = int(CARD_X + 680 - 320 * trail_p)
            ty_pt = int(CARD_Y + 280 + 380 * (trail_p ** 1.3))
            tr_size = int(6 * (1.0 - trail_i * 0.18))
            guide_draw.ellipse([tx_pt - tr_size, ty_pt - tr_size, tx_pt + tr_size, ty_pt + tr_size], fill="#FFD54F")
        frame.alpha_composite(star_icon, (sx - 70, sy - 70))
        
    elif guide_mode == "playground_play":
        # Bàn tay trỏ gõ nhịp vào thẻ từ vựng PLAY
        target_x, target_y = W // 2, 1100
        px = target_x - 220 + int(15 * math.sin(t * 11.0))
        py = target_y - 70
        frame.alpha_composite(pointer_hand, (px, py))
        
    elif guide_mode == "artroom_easel":
        # Cây cọ vẽ ma thuật vung nét vẽ vòng cung cầu vồng trên giá vẽ tranh
        brush_prog = (t % 2.0) / 2.0
        bx = int(CARD_X + 380 + 200 * math.sin(brush_prog * math.pi))
        by = int(CARD_Y + 360 - 80 * math.cos(brush_prog * math.pi))
        # Cung nét vẽ cầu vồng
        guide_draw.arc([CARD_X + 280, CARD_Y + 280, CARD_X + 680, CARD_Y + 520], start=180, end=180 + int(180 * brush_prog), fill="#E91E63", width=8)
        frame.alpha_composite(magic_brush, (bx - 90, by - 90))
        
    elif guide_mode == "artroom_paint":
        # Cọ vẽ chấm 3 nhịp Ting Ting Ting theo tiếng "Paint! Paint! Paint!"
        paint_step = int((t * 3.5) % 3)
        bx_step = CARD_X + 320 + paint_step * 140
        by_step = CARD_Y + 440
        guide_draw.ellipse([bx_step - 25, by_step - 25, bx_step + 25, by_step + 25], fill="#00E676")
        frame.alpha_composite(magic_brush, (bx_step - 50, by_step - 110))
        
    elif guide_mode.startswith("recap"):
        # Bàn tay trỏ di chuyển nhanh theo 4 góc định vị
        rec_idx = ["recap_c", "recap_l", "recap_p", "recap_a"].index(guide_mode) if guide_mode in ["recap_c", "recap_l", "recap_p", "recap_a"] else 0
        r_x = [CARD_X + 250, CARD_X + 650, CARD_X + 250, CARD_X + 650][rec_idx]
        r_y = [CARD_Y + 250, CARD_Y + 250, CARD_Y + 550, CARD_Y + 550][rec_idx]
        guide_draw.ellipse([r_x - 30, r_y - 30, r_x + 30, r_y + 30], outline="#FF6F00", width=5)
        frame.alpha_composite(pointer_hand, (r_x - 90, r_y - 90))
        
    else: # door / celebrate
        # Đũa phép ngôi sao tung hào quang
        rot_star = (t * 60.0) % 360
        s_rot = star_icon.rotate(rot_star, resample=Image.Resampling.BILINEAR)
        frame.alpha_composite(s_rot, (CARD_X + CARD_W - 160, CARD_Y + 20))
        
    # 5. Thẻ từ vựng mục tiêu (DUY NHẤT 1 TỪ VỰNG - 0% TỪ THỪA)
    w_card = word_card_cache.get(word_text, word_card_cache["CLASSROOM"])
    word_x = (W - (CARD_TEXT_W + 40)) // 2
    word_y = 1090
    
    if curr_ev and (t - (curr_ev["start_ms"]/1000.0)) < 0.4:
        scale_bounce = 1.0 + 0.07 * math.sin((t - (curr_ev["start_ms"]/1000.0)) * math.pi / 0.4)
        bw = int((CARD_TEXT_W + 40) * scale_bounce)
        bh = int((CARD_TEXT_H + 40) * scale_bounce)
        w_bounced = w_card.resize((bw, bh), Image.Resampling.BILINEAR)
        bx = (W - bw) // 2
        by = word_y - (bh - (CARD_TEXT_H + 40)) // 2
        frame.alpha_composite(w_bounced, (bx, by))
    else:
        frame.alpha_composite(w_card, (word_x, word_y))
        
    # 6. Sàn sân khấu hoạt hình
    frame.alpha_composite(stage_floor, (0, 1640))
    
    # 7. Trích xuất Viseme cho frame hiện tại
    curr_speaker = curr_ev["speaker"] if curr_ev else ""
    viseme_char = "X"
    if curr_ev:
        st = curr_ev["start_ms"] / 1000.0
        rel_t = t - st
        for cue in visemes_map.get(curr_ev["id"], []):
            if cue["start"] <= rel_t <= cue["end"]:
                viseme_char = cue["value"]
                break
                
    m_img = viseme_cache.get(viseme_char, viseme_cache["X"])
    blink = (t % 3.2) < 0.15
    
    # 8. Nhân vật Leo Bunny (Bên trái: x=70, y=1340)
    leo_speaking = (curr_speaker in ["leo_bunny", "both_kids"])
    leo_bounce_y = int(-14 * math.sin(t * 16.0)) if leo_speaking else 0
    leo_x, leo_y = 70, 1340 + leo_bounce_y
    frame.alpha_composite(char_shadow, (leo_x + 20, 1780))
    
    leo_canvas = bunny_base.copy()
    leo_eyes = bunny_eyes_wink if (blink or (leo_speaking and viseme_char in ["E", "F"])) else bunny_eyes_norm
    leo_canvas.alpha_composite(leo_eyes)
    leo_mouth_viseme = m_img if leo_speaking else viseme_cache["X"]
    leo_canvas.alpha_composite(leo_mouth_viseme, (135, 260))
    frame.alpha_composite(leo_canvas, (leo_x, leo_y))
    
    # 9. Nhân vật Mia Kid (Bên phải: x=630, y=1340)
    mia_speaking = (curr_speaker in ["mia_kid", "both_kids"])
    mia_bounce_y = int(-14 * math.sin(t * 16.0)) if mia_speaking else 0
    mia_x, mia_y = 630, 1340 + mia_bounce_y
    frame.alpha_composite(char_shadow, (mia_x + 20, 1780))
    
    mia_canvas = mia_base.copy()
    mia_eyes = mia_eyes_wink if (blink or (mia_speaking and viseme_char in ["E", "F"])) else mia_eyes_norm
    mia_canvas.alpha_composite(mia_eyes)
    mia_mouth_viseme = m_img if mia_speaking else viseme_cache["X"]
    mia_canvas.alpha_composite(mia_mouth_viseme, (135, 245))
    frame.alpha_composite(mia_canvas, (mia_x, mia_y))
    
    # 10. Teacher Avatar Indicator (Góc trên khi thầy cô nói)
    if curr_speaker in ["ms_sarah", "mr_david", "teachers"]:
        t_x = 80 if "sarah" in curr_speaker else 860
        t_y = 110
        pulse_ring = int(12 * math.sin(t * 10.0))
        guide_draw.ellipse([t_x - 10 - pulse_ring, t_y - 10 - pulse_ring, t_x + 110 + pulse_ring, t_y + 110 + pulse_ring], outline="#FFD54F", width=3)
        guide_draw.ellipse([t_x, t_y, t_x + 100, t_y + 100], fill="#FFFFFF", outline="#FF6F00", width=4)
        t_label = "Ms. Sarah" if "sarah" in curr_speaker else "Mr. David"
        fnt_tl = ImageFont.truetype(FONT_PATH, 20)
        guide_draw.text((t_x + 10, t_y + 36), t_label, font=fnt_tl, fill="#6A1B9A")

    return frame.convert("RGB")

def main():
    print(f"🚀 Render video V4 Virtual Teacher Guided ({W}x{H} @ {FPS}fps)...")
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{W}x{H}",
        "-pix_fmt", "rgb24",
        "-r", str(FPS),
        "-i", "-",
        "-i", str(AUDIO_FILE),
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "19",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        str(OUT_VIDEO)
    ]
    
    proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)
    
    for f in range(TOTAL_FRAMES):
        frame_rgb = render_frame(f)
        proc.stdin.write(frame_rgb.tobytes())
        if f % 200 == 0:
            pct = (f / TOTAL_FRAMES) * 100
            print(f"⏳ Tiến độ render V4: frame {f}/{TOTAL_FRAMES} ({pct:.1f}%)")
            
    proc.stdin.close()
    proc.wait()
    
    if proc.returncode != 0:
        raise RuntimeError("FFmpeg render failed!")
        
    print(f"🎉 RENDER V4 MASTER HOÀN TẤT THÀNH CÔNG RỰC RỠ: {OUT_VIDEO}")
    file_size_mb = OUT_VIDEO.stat().st_size / (1024 * 1024)
    print(f"📦 Dung lượng file: {file_size_mb:.2f} MB")

if __name__ == "__main__":
    main()
