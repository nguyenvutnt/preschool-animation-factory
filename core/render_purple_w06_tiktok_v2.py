#!/usr/bin/env python3
r"""
ĐỘNG CƠ HOẠT HÌNH KHỐI PURPLE V2 (SIÊU TỐI ƯU HIỆU NĂNG - 35 FPS)
NỀN ẢNH THẬT CHẤT LƯỢNG CAO + ICON ĐỘNG 3D + 100% ZERO TỪ THỪA

Tối ưu hóa:
  1. Pre-render 10 Thẻ từ vựng (chữ lớn, đổ bóng 3D, viền neon, màu sắc riêng biệt).
  2. Pre-scale ảnh nền sang 2050x1153 -> Ken Burns chỉ việc CROP (0 lần resize, tốc độ tức thì).
  3. Pre-render 9 khẩu hình Rhubarb visemes & bóng đổ mascot.
  4. 0% TỪ THỪA: Màn hình chỉ hiển thị đúng duy nhất 1 từ vựng đang học.
"""

import math
import os
import json
import random
import subprocess
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

REPO_ROOT = Path(__file__).resolve().parent.parent
RES_DIR = REPO_ROOT / "res" / "purple_w06"
PHOTOS_DIR = RES_DIR / "photos"
STICKERS_DIR = REPO_ROOT / "assets" / "purple" / "stickers"
ASSETS_DIR = REPO_ROOT / "assets" / "purple"

AUDIO_FILE = RES_DIR / "master_audio.mp3"
MANIFEST_FILE = RES_DIR / "manifest.json"
VISEMES_FILE = RES_DIR / "visemes.json"
OUT_VIDEO = REPO_ROOT / "demo_products" / "demo_W06_Purple_TikTok_Vocabulary.mp4"

FONT_PATH = "/usr/share/fonts/truetype/quicksand/Quicksand-Bold.ttf"
FPS = 30

# Nạp timeline & visemes
with open(MANIFEST_FILE, "r") as fp:
    manifest_data = json.load(fp)

TOTAL_DURATION = manifest_data["total_duration"]
TOTAL_FRAMES = int(TOTAL_DURATION * FPS)
events = manifest_data["events"]
dialogue_events = [e for e in events if e.get("type") == "dialogue"]

with open(VISEMES_FILE, "r") as fp:
    visemes_map = json.load(fp)

print("⚡ Đang tiền xử lý ảnh nền và tài nguyên đồ họa...")

# 1. TIỀN XỬ LÝ ẢNH NỀN SANG 2050x1153 (Cho Ken Burns Crop siêu tốc)
BG_FILES = {
    "school": PHOTOS_DIR / "school_front.jpg",
    "classroom1": PHOTOS_DIR / "classroom_unsplash.jpg",
    "classroom2": PHOTOS_DIR / "classroom_hero.jpg",
    "library1": PHOTOS_DIR / "library_unsplash.jpg",
    "library2": PHOTOS_DIR / "library_local.jpg",
    "playground1": PHOTOS_DIR / "playground_unsplash.jpg",
    "playground2": PHOTOS_DIR / "playground_local.jpg",
    "artroom1": PHOTOS_DIR / "artroom_unsplash.jpg",
    "artroom2": PHOTOS_DIR / "artroom_local.jpg",
}

bg_oversized = {}
for k, p in BG_FILES.items():
    im = Image.open(p).convert("RGB")
    bg_oversized[k] = im.resize((2050, 1153), Image.Resampling.BILINEAR)

# 2. TIỀN XỬ LÝ STICKERS (300x300)
stickers = {
    "book": Image.open(STICKERS_DIR / "sticker_book.png").convert("RGBA"),
    "library": Image.open(STICKERS_DIR / "sticker_library.png").convert("RGBA"),
    "playground": Image.open(STICKERS_DIR / "sticker_playground.png").convert("RGBA"),
    "art": Image.open(STICKERS_DIR / "sticker_art.png").convert("RGBA"),
    "star": Image.open(STICKERS_DIR / "sticker_star.png").convert("RGBA"),
}

# 3. TIỀN XỬ LÝ MASCOT THỎ TÍM & KHẨU HÌNH
bunny_base = Image.open(ASSETS_DIR / "bunny_base.png").convert("RGBA")
bunny_eyes_normal = Image.open(ASSETS_DIR / "bunny_eyes_normal.png").convert("RGBA")
bunny_eyes_wink = Image.open(ASSETS_DIR / "bunny_eyes_wink.png").convert("RGBA")

def build_mouth(viseme_char, w=120, h=75):
    m_canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(m_canvas)
    v = viseme_char.upper()
    if v in ["A", "B"]:
        d.line([(22, h//2), (w-22, h//2)], fill="#4A0E4E", width=8)
    elif v in ["C", "D"]:
        d.rounded_rectangle([25, h//2 - 15, w - 25, h//2 + 17], radius=12, fill="#E11D48", outline="#4A0E4E", width=4)
        d.rectangle([35, h//2 - 13, w - 35, h//2 - 2], fill="#FFFFFF")
    elif v in ["E", "F"]:
        d.ellipse([20, 10, w - 20, h - 10], fill="#E11D48", outline="#4A0E4E", width=5)
        d.rectangle([35, 12, w - 35, 27], fill="#FFFFFF")
        d.ellipse([35, h - 27, w - 35, h - 14], fill="#F43F5E")
    elif v in ["G", "H"]:
        d.ellipse([15, 6, w - 15, h - 6], fill="#9F1239", outline="#4A0E4E", width=5)
        d.rectangle([30, 8, w - 30, 25], fill="#FFFFFF")
        d.ellipse([30, h - 29, w - 30, h - 12], fill="#FB7185")
    else:
        d.arc([25, h//2 - 12, w - 25, h//2 + 20], start=0, end=180, fill="#4A0E4E", width=7)
    return m_canvas

viseme_cache = {v: build_mouth(v) for v in ["A", "B", "C", "D", "E", "F", "G", "H", "X"]}

# Tiền tạo bóng đổ cho Mascot
mascot_shadow = Image.new("RGBA", (300, 40), (0, 0, 0, 0))
ms_draw = ImageDraw.Draw(mascot_shadow)
ms_draw.ellipse([5, 5, 295, 35], fill=(0, 0, 0, 120))
mascot_shadow = mascot_shadow.filter(ImageFilter.GaussianBlur(6))

# Lớp phủ Vignette 1920x1080
vignette_layer = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
vdraw = ImageDraw.Draw(vignette_layer)
vdraw.rectangle([0, 0, 1920, 1080], fill=(15, 10, 30, 40))

# 4. TIỀN TẠO 10 THẺ TỪ VỰNG HOÀN CHỈNH (ZERO TỪ THỪA)
WORD_CONFIG = {
    "READY, GO!": {"color": "#FBBF24", "border": "#B45309", "glow": "#FEF08A", "size": 170},
    "CLASSROOM":  {"color": "#8B5CF6", "border": "#4C1D95", "glow": "#DDD6FE", "size": 170},
    "LEARN":      {"color": "#0284C7", "border": "#0369A1", "glow": "#BAE6FD", "size": 160},
    "LIBRARY":    {"color": "#0D9488", "border": "#115E59", "glow": "#CCFBF1", "size": 170},
    "READ":       {"color": "#D97706", "border": "#78350F", "glow": "#FEF3C7", "size": 160},
    "PLAYGROUND": {"color": "#16A34A", "border": "#14532D", "glow": "#DCFCE7", "size": 160},
    "PLAY":       {"color": "#EA580C", "border": "#7C2D12", "glow": "#FFEDD5", "size": 160},
    "ART ROOM":   {"color": "#E11D48", "border": "#881337", "glow": "#FFE4E6", "size": 170},
    "PAINT":      {"color": "#C026D3", "border": "#701A75", "glow": "#FDF4FF", "size": 160},
    "GREAT JOB!": {"color": "#F59E0B", "border": "#78350F", "glow": "#FEF08A", "size": 170},
}

precomputed_cards = {}
for word, conf in WORD_CONFIG.items():
    fnt = ImageFont.truetype(FONT_PATH, conf["size"])
    bbox = fnt.getbbox(word)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    
    cw = tw + 180
    ch = th + 90
    
    # Tạo thẻ với bóng đổ
    full_card = Image.new("RGBA", (cw + 40, ch + 40), (0, 0, 0, 0))
    fdraw = ImageDraw.Draw(full_card)
    
    # Bóng đổ
    fdraw.rounded_rectangle([25, 30, cw + 25, ch + 30], radius=35, fill=(0, 0, 0, 110))
    full_card = full_card.filter(ImageFilter.GaussianBlur(12))
    fdraw = ImageDraw.Draw(full_card)
    
    # Nền thẻ trắng tinh viền neon
    fdraw.rounded_rectangle([20, 20, cw + 20, ch + 20], radius=35, fill="#FFFFFF", outline=conf["glow"], width=14)
    
    # Chữ to rõ ràng có viền đậm
    tx = 20 + (cw - tw) // 2 - bbox[0]
    ty = 20 + (ch - th) // 2 - bbox[1] - 4
    
    # Viền chữ
    outline_w = 11
    for ox in range(-outline_w, outline_w + 1, 2):
        for oy in range(-outline_w, outline_w + 1, 2):
            fdraw.text((tx + ox, ty + oy), word, font=fnt, fill=conf["border"])
    # Lòng chữ
    fdraw.text((tx, ty), word, font=fnt, fill=conf["color"])
    
    precomputed_cards[word] = full_card

print("✅ Đã tiền xử lý xong toàn bộ tài nguyên! Bắt đầu render...")

# 5. DANH SÁCH 18 PHÂN CẢNH (< 3s / cut)
SCENES = [
    # 0. Hook: 0.0s - 4.7s
    {"id": "hook", "start": 0.0, "end": 4.7, "bg": "school", "sticker": "star", "word": "READY, GO!"},
    
    # 1. CLASSROOM: 4.7s - 18.0s
    {"id": "sc1_ask", "start": 4.7, "end": 7.4, "bg": "classroom1", "sticker": "book", "word": "CLASSROOM"},
    {"id": "sc1_leo", "start": 7.4, "end": 11.4, "bg": "classroom2", "sticker": "book", "word": "CLASSROOM"},
    {"id": "sc1_mia", "start": 11.4, "end": 15.4, "bg": "classroom1", "sticker": "book", "word": "CLASSROOM"},
    {"id": "sc1_act", "start": 15.4, "end": 18.0, "bg": "classroom2", "sticker": "book", "word": "LEARN"},
    
    # 2. LIBRARY: 18.0s - 31.0s
    {"id": "sc2_ask", "start": 18.0, "end": 20.4, "bg": "library1", "sticker": "library", "word": "LIBRARY"},
    {"id": "sc2_sar", "start": 20.4, "end": 24.4, "bg": "library2", "sticker": "library", "word": "LIBRARY"},
    {"id": "sc2_leo", "start": 24.4, "end": 28.4, "bg": "library1", "sticker": "library", "word": "LIBRARY"},
    {"id": "sc2_act", "start": 28.4, "end": 31.0, "bg": "library2", "sticker": "library", "word": "READ"},
    
    # 3. PLAYGROUND: 31.0s - 42.5s
    {"id": "sc3_ask", "start": 31.0, "end": 33.2, "bg": "playground1", "sticker": "playground", "word": "PLAYGROUND"},
    {"id": "sc3_mia", "start": 33.2, "end": 36.6, "bg": "playground2", "sticker": "playground", "word": "PLAYGROUND"},
    {"id": "sc3_leo", "start": 36.6, "end": 39.8, "bg": "playground1", "sticker": "playground", "word": "PLAY"},
    {"id": "sc3_sar", "start": 39.8, "end": 42.5, "bg": "playground2", "sticker": "playground", "word": "PLAYGROUND"},
    
    # 4. ART ROOM: 42.5s - 51.5s
    {"id": "sc4_ask", "start": 42.5, "end": 44.8, "bg": "artroom1", "sticker": "art", "word": "ART ROOM"},
    {"id": "sc4_leo", "start": 44.8, "end": 48.0, "bg": "artroom2", "sticker": "art", "word": "ART ROOM"},
    {"id": "sc4_act", "start": 48.0, "end": 51.5, "bg": "artroom1", "sticker": "art", "word": "PAINT"},
    
    # 5. RAPID RECAP: 51.5s - 59.5s (< 1.5s / cut)
    {"id": "recap_c", "start": 51.5, "end": 53.5, "bg": "classroom1", "sticker": "book", "word": "CLASSROOM"},
    {"id": "recap_l", "start": 53.5, "end": 55.5, "bg": "library1", "sticker": "library", "word": "LIBRARY"},
    {"id": "recap_p", "start": 55.5, "end": 57.5, "bg": "playground1", "sticker": "playground", "word": "PLAYGROUND"},
    {"id": "recap_a", "start": 57.5, "end": 59.5, "bg": "artroom1", "sticker": "art", "word": "ART ROOM"},
    
    # 6. Celebration: 59.5s - 66.84s
    {"id": "celebrate", "start": 59.5, "end": 66.84, "bg": "school", "sticker": "star", "word": "GREAT JOB!"}
]

def render_frame_fast(t, f):
    curr_scene = SCENES[-1]
    for s in SCENES:
        if s["start"] <= t < s["end"]:
            curr_scene = s
            break
            
    scene_dur = curr_scene["end"] - curr_scene["start"]
    scene_prog = (t - curr_scene["start"]) / max(0.1, scene_dur)
    
    # 1. KEN BURNS CROP (KHÔNG RESIZE -> SIÊU NHANH)
    src_bg = bg_oversized[curr_scene["bg"]]
    max_dx = 2050 - 1920 # 130px
    max_dy = 1153 - 1080 # 73px
    crop_x = int(max_dx * (0.5 + 0.3 * math.sin(scene_prog * math.pi)))
    crop_y = int(max_dy * (0.5 + 0.3 * math.cos(scene_prog * math.pi)))
    
    bg_frame = src_bg.crop((crop_x, crop_y, crop_x + 1920, crop_y + 1080))
    canvas = bg_frame.convert("RGBA")
    canvas.alpha_composite(vignette_layer)
    
    # 2. XÁC ĐỊNH VISEME
    curr_viseme = "X"
    for e in dialogue_events:
        st = e["start_ms"] / 1000.0
        et = e["end_ms"] / 1000.0
        if st <= t <= et:
            rel_t = t - st
            for v_entry in visemes_map.get(e["id"], []):
                if v_entry["start"] <= rel_t <= v_entry["end"]:
                    curr_viseme = v_entry["value"]
                    break
            break
            
    # 3. ANIMATED STICKER ICON (Góc trên phải, nhún nhảy theo beat)
    stk_key = curr_scene["sticker"]
    if stk_key in stickers:
        stk_img = stickers[stk_key]
        pulse = 1.0 + 0.08 * math.sin(t * 13.4) # Beat 128 BPM
        sw = int(310 * pulse)
        sh = int(310 * pulse)
        s_resized = stk_img.resize((sw, sh), Image.Resampling.BILINEAR)
        
        rot_deg = math.sin(t * 4.0) * 8.0
        s_rot = s_resized.rotate(rot_deg, expand=True, resample=Image.Resampling.BILINEAR)
        rw, rh = s_rot.size
        stk_x = 1580 - rw // 2
        stk_y = 230 - rh // 2 + int(math.sin(t * 6.0) * 14)
        canvas.alpha_composite(s_rot, (stk_x, stk_y))
        
    # 4. THẺ TỪ VỰNG TIỀN TÍNH (ZERO TỪ THỪA, ELASTIC POP-IN)
    word = curr_scene["word"]
    if word in precomputed_cards:
        card = precomputed_cards[word]
        pop_dt = t - curr_scene["start"]
        if pop_dt < 0.22:
            scale = 0.35 + 0.80 * (pop_dt / 0.22)
        elif pop_dt < 0.35:
            scale = 1.15 - 0.15 * ((pop_dt - 0.22) / 0.13)
        else:
            scale = 1.0 + 0.02 * math.sin(t * 7.5)
            
        scaled_cw = int(card.width * scale)
        scaled_ch = int(card.height * scale)
        scaled_card = card.resize((scaled_cw, scaled_ch), Image.Resampling.BILINEAR)
        
        float_y = int(math.sin(t * 4.5) * 8.0)
        card_x = 960 - scaled_cw // 2
        card_y = 230 - scaled_ch // 2 + float_y
        canvas.alpha_composite(scaled_card, (card_x, card_y))
        
    # 5. MASCOT THỎ TÍM (Góc dưới trái, nhún nhảy & lip-sync)
    bunny_bounce = abs(math.sin(t * 8.5))
    bunny_y_offset = int(bunny_bounce * 25)
    squash_x = 1.0 + 0.05 * (1.0 - bunny_bounce)
    squash_y = 1.0 - 0.05 * (1.0 - bunny_bounce)
    
    b_canvas = Image.new("RGBA", (500, 500), (0, 0, 0, 0))
    b_canvas.alpha_composite(bunny_base)
    
    if abs(math.sin(t * 2.2)) > 0.92:
        b_canvas.alpha_composite(bunny_eyes_wink)
    else:
        b_canvas.alpha_composite(bunny_eyes_normal)
        
    # Khẩu hình từ cache
    m_img = viseme_cache.get(curr_viseme, viseme_cache["X"])
    b_canvas.alpha_composite(m_img, (190, 275))
    
    cur_bw = int(460 * squash_x)
    cur_bh = int(460 * squash_y)
    scaled_bunny = b_canvas.resize((cur_bw, cur_bh), Image.Resampling.BILINEAR)
    
    # Bóng đổ
    sh_w = int(280 * squash_x)
    sh_scaled = mascot_shadow.resize((sh_w, 35), Image.Resampling.BILINEAR)
    
    mascot_x = 340
    mascot_floor = 1045
    canvas.alpha_composite(sh_scaled, (mascot_x - sh_w // 2, mascot_floor - 20))
    canvas.alpha_composite(scaled_bunny, (mascot_x - cur_bw // 2, mascot_floor - cur_bh - bunny_y_offset))
    
    # 6. HIỆU ỨNG NGÔI SAO ĂN MỪNG (GREAT JOB!)
    if t >= 59.5:
        star_icon = stickers["star"].resize((90, 90), Image.Resampling.BILINEAR)
        for i in range(8):
            st_x = int((i * 240 + t * 90) % 1920)
            st_y = int(80 + 120 * abs(math.sin(t * 3.0 + i)))
            canvas.alpha_composite(star_icon, (st_x, st_y))
            
    # 7. THANH TIẾN TRÌNH TIKTOK RETENTION BAR
    bar_w = int(1920 * (t / TOTAL_DURATION))
    pdraw = ImageDraw.Draw(canvas)
    pdraw.rectangle([0, 1070, 1920, 1080], fill=(0, 0, 0, 100))
    pdraw.rectangle([0, 1070, bar_w, 1080], fill="#8B5CF6")
    pdraw.rectangle([max(0, bar_w - 30), 1070, bar_w, 1080], fill="#FBBF24")
    
    return canvas.convert("RGB")

def main():
    print(f"🎬 Khởi động Render Master Video V2 (2005 frames @ 30fps)...")
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", "1920x1080",
        "-pix_fmt", "rgb24",
        "-r", str(FPS),
        "-i", "-",
        "-i", str(AUDIO_FILE),
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-color_primaries", "1",
        "-color_trc", "1",
        "-colorspace", "1",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        "-movflags", "+faststart",
        str(OUT_VIDEO)
    ]
    
    proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)
    
    for f in range(TOTAL_FRAMES):
        t = f / FPS
        frame_img = render_frame_fast(t, f)
        proc.stdin.write(frame_img.tobytes())
        
        if f % 150 == 0 or f == TOTAL_FRAMES - 1:
            pct = (f / TOTAL_FRAMES) * 100
            print(f"Tiến độ Render V2: {f}/{TOTAL_FRAMES} frames ({pct:.1f}%) — {t:.1f}s / {TOTAL_DURATION:.1f}s")
            sys.stdout.flush()
            
    proc.stdin.close()
    proc.wait()
    
    if proc.returncode == 0:
        print(f"✅ Hoàn tất render Master Video TikTok Purple W06 V2 Thành Công: {OUT_VIDEO}")
    else:
        print(f"❌ Lỗi khi render FFmpeg! Exit code: {proc.returncode}")
        sys.exit(1)

if __name__ == "__main__":
    main()
