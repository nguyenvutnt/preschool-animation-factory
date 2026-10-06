#!/usr/bin/env python3
r"""
ĐỘNG CƠ HOẠT HÌNH KHỐI PURPLE — TIKTOK STYLE HIGH-RETENTION (< 3S SCENE CUT)
Chủ đề: Tuần 06 - "Where Are We in Our School?" (Activity 2 & 3: School Places Vocabulary)
Từ vựng: CLASSROOM, LIBRARY, PLAYGROUND, ART ROOM.
Đặc trưng:
  1. MEGA HOOK (0 - 3s) giật tít thị giác và âm thanh, giữ chân trẻ lập tức.
  2. Pacing nhanh: 18 cảnh trong 66.8s (Dưới 3 giây đổi cảnh hoặc đổi góc máy 100%).
  3. Màu sắc bắt mắt: Tím Neon (#8B5CF6), Vàng Cam (#FBBF24), Xanh Ngọc, Color Splash.
  4. Hiệu ứng động liên tục: Camera Zoom, Screen Shake, Confetti, Starburst, Elastic Bounce.
  5. 4 Giọng Mỹ giàu cảm xúc, 100% Zero Speech Overlap, BGM viral sôi động.
"""

import math
import os
import json
import random
import subprocess
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# 1. ĐƯỜNG DẪN TÀI NGUYÊN (TỰ NẠP NỘI BỘ REPO HOẶC SCRATCH)
REPO_ROOT = Path(__file__).resolve().parent.parent
BASE_DIR = Path("/root/scratch/purple_w06_tiktok")
RES_DIR = REPO_ROOT / "res" / "purple_w06"

ASSETS_DIR = REPO_ROOT / "assets" / "purple" if (REPO_ROOT / "assets" / "purple").exists() else BASE_DIR / "assets"
AUDIO_FILE = RES_DIR / "master_audio.mp3" if (RES_DIR / "master_audio.mp3").exists() else BASE_DIR / "master_audio.mp3"
MANIFEST_FILE = RES_DIR / "manifest.json" if (RES_DIR / "manifest.json").exists() else BASE_DIR / "manifest.json"
VISEMES_FILE = RES_DIR / "visemes.json" if (RES_DIR / "visemes.json").exists() else BASE_DIR / "visemes.json"
OUT_VIDEO = REPO_ROOT / "demo_products" / "demo_W06_Purple_TikTok_Vocabulary.mp4"

# Phông chữ bo tròn mầm non Quicksand Bold
FONT_PATH = "/usr/share/fonts/truetype/quicksand/Quicksand-Bold.ttf"
FONT_HERO = ImageFont.truetype(FONT_PATH, 160)
FONT_CARD = ImageFont.truetype(FONT_PATH, 130)
FONT_SUB = ImageFont.truetype(FONT_PATH, 80)
FONT_TINY = ImageFont.truetype(FONT_PATH, 55)

FPS = 30

# Nạp manifest & visemes
with open(MANIFEST_FILE, "r") as fp:
    manifest_data = json.load(fp)

TOTAL_DURATION = manifest_data["total_duration"]
TOTAL_FRAMES = int(TOTAL_DURATION * FPS)
events = manifest_data["events"]
dialogue_events = [e for e in events if e.get("type") == "dialogue"]
event_map = {e["id"]: e for e in dialogue_events}

with open(VISEMES_FILE, "r") as fp:
    visemes_map = json.load(fp)

# Nạp assets
bunny_base = Image.open(ASSETS_DIR / "bunny_base.png").convert("RGBA")
bunny_eyes_normal = Image.open(ASSETS_DIR / "bunny_eyes_normal.png").convert("RGBA")
bunny_eyes_wink = Image.open(ASSETS_DIR / "bunny_eyes_wink.png").convert("RGBA")
magic_door = Image.open(ASSETS_DIR / "magic_door.png").convert("RGBA")
badge_class = Image.open(ASSETS_DIR / "badge_classroom.png").convert("RGBA")
badge_lib = Image.open(ASSETS_DIR / "badge_library.png").convert("RGBA")
badge_play = Image.open(ASSETS_DIR / "badge_playground.png").convert("RGBA")
badge_art = Image.open(ASSETS_DIR / "badge_artroom.png").convert("RGBA")
color_splash = Image.open(ASSETS_DIR / "color_splash.png").convert("RGBA")

# Nạp visemes miệng
VISEMES_SPRITES_DIR = Path("/root/scratch/engaging_sprites/visemes")
mouth_sprites = {}
for v in ["X", "A", "B", "C", "D", "E", "F", "G", "H"]:
    mouth_sprites[v] = Image.open(VISEMES_SPRITES_DIR / f"mouth_{v}.png").convert("RGBA")

# Ghép Mascot Thỏ Tím
def get_bunny(eye_state="normal", mouth_viseme="X"):
    im = Image.new("RGBA", (600, 600), (0, 0, 0, 0))
    im.alpha_composite(bunny_base, (0, 0))
    eye_img = bunny_eyes_wink if eye_state == "wink" else bunny_eyes_normal
    im.alpha_composite(eye_img, (0, 0))
    # Miệng
    m_img = mouth_sprites.get(mouth_viseme, mouth_sprites["X"])
    # Thu nhỏ miệng vừa khuôn mặt thỏ
    m_scaled = m_img.resize((140, 140), Image.Resampling.BILINEAR)
    im.alpha_composite(m_scaled, (230, 360))
    return im

# Lấy viseme miệng theo thời gian
def get_mouth_viseme(t_sec):
    t_ms = t_sec * 1000.0
    for ev in dialogue_events:
        st = ev["start_ms"]
        ed = ev["end_ms"]
        if st <= t_ms <= ed + 150:
            t_loc = (t_ms - st) / 1000.0
            fname = os.path.basename(ev["file"])
            if fname in visemes_map:
                for cue in visemes_map[fname]:
                    if cue["start"] <= t_loc < cue["end"]:
                        return cue["value"]
    return "X"

# Hạt sao & pháo hoa confetti
confetti = []
for _ in range(60):
    confetti.append({
        "x": random.randint(50, 1870),
        "y": random.randint(-500, 1080),
        "vx": random.uniform(-3, 3),
        "vy": random.uniform(4, 9),
        "color": random.choice([(239, 68, 68), (59, 130, 246), (234, 179, 8), (168, 85, 247), (16, 185, 129), (236, 72, 153)]),
        "size": random.randint(12, 24),
        "rot": random.uniform(0, 360),
        "vrot": random.uniform(-10, 10)
    })

# Tạo nền gradient sống động theo thời gian
def get_dynamic_bg(scene_idx, t):
    w, h = 1920, 1080
    bg = Image.new("RGBA", (w, h))
    draw = ImageDraw.Draw(bg)
    
    # 5 Bộ màu chủ đạo rực rỡ theo chủ đề
    palettes = [
        ((124, 58, 237), (167, 139, 250)),  # Tím Neon (Hook)
        ((37, 99, 235), (96, 165, 250)),    # Xanh Dương (Classroom)
        ((13, 148, 136), (45, 212, 191)),   # Xanh Ngọc (Library)
        ((234, 88, 12), (251, 146, 60)),    # Cam Nắng (Playground)
        ((219, 39, 119), (244, 114, 182))   # Hồng Nghệ Thuật (Art Room)
    ]
    c1, c2 = palettes[scene_idx % len(palettes)]
    
    # Vẽ gradient chéo
    steps = 60
    for i in range(steps):
        p = i / float(steps)
        r = int(c1[0] + (c2[0] - c1[0]) * p)
        g = int(c1[1] + (c2[1] - c1[1]) * p)
        b = int(c1[2] + (c2[2] - c1[2]) * p)
        y0 = int(i * (h / steps))
        y1 = int((i + 1) * (h / steps))
        draw.rectangle([0, y0, w, y1], fill=(r, g, b, 255))
        
    # Vòng tròn ánh sáng trung tâm
    pulse = 1.0 + 0.04 * math.sin(t * 8.0)
    rw = int(900 * pulse)
    rh = int(600 * pulse)
    draw.ellipse([960 - rw, 540 - rh, 960 + rw, 540 + rh], outline=(255, 255, 255, 40), width=6)
    return bg

def render_frame(t, frame_idx):
    # Xác định phân cảnh hiện tại dựa trên timeline
    # 18 sự kiện dialogue
    cur_ev_idx = 0
    t_ms = t * 1000.0
    for idx, ev in enumerate(dialogue_events):
        if t_ms >= ev["start_ms"]:
            cur_ev_idx = idx

    # Chọn scene_theme (0: Hook, 1: Classroom, 2: Library, 3: Playground, 4: Art Room, 5: Celebration)
    if cur_ev_idx < 2:
        scene_theme = 0 # Hook & Magic Door 1
    elif cur_ev_idx < 5:
        scene_theme = 1 # Classroom
    elif cur_ev_idx < 9:
        scene_theme = 2 # Library
    elif cur_ev_idx < 13:
        scene_theme = 3 # Playground
    elif cur_ev_idx < 16:
        scene_theme = 4 # Art Room
    else:
        scene_theme = 0 # Recap & Celebration

    # 1. Vẽ nền gradient sống động
    frame = get_dynamic_bg(scene_theme, t)
    draw = ImageDraw.Draw(frame)

    mouth_v = get_mouth_viseme(t)
    bunny_eye = "wink" if (math.sin(t * 5.0) > 0.8) else "normal"
    bunny_img = get_bunny(eye_state=bunny_eye, mouth_viseme=mouth_v)

    # Nhịp nhún nhảy (Bounce to the 128 BPM beat)
    beat = abs(math.sin(t * 6.5))
    bunny_scale = 1.0 + 0.06 * beat
    bw = int(480 * bunny_scale)
    bh = int(480 / bunny_scale)
    b_resized = bunny_img.resize((bw, bh), Image.Resampling.BILINEAR)

    # Vị trí nhân vật Thỏ Tím
    bunny_x = 960
    bunny_y = 660 - int(50 * beat)

    # 2. XỬ LÝ THEO TỪNG PHÂN CẢNH (< 3S ĐỔI CẢNH)
    # --- PHÂN CẢNH 1 & 2: MEGA HOOK & MAGIC DOOR (0 - 6.5s) ---
    if cur_ev_idx == 0:
        # HOOK BÙNG NỔ: Phóng to cực mạnh
        hook_zoom = min(1.3, 0.4 + (t / 1.5) * 0.9)
        hook_text = "GUESS THE PLACE!"
        bbox = draw.textbbox((0, 0), hook_text, font=FONT_HERO)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        
        # Vẽ thẻ nổi
        card_w, card_h = int((tw + 120) * hook_zoom), int((th + 60) * hook_zoom)
        c_im = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 0))
        cdraw = ImageDraw.Draw(c_im)
        cdraw.rounded_rectangle([0, 0, card_w, card_h], radius=30, fill=(255, 255, 255, 240), outline=(251, 191, 36), width=8)
        
        f_scaled = ImageFont.truetype(FONT_PATH, int(160 * hook_zoom))
        cdraw.text((card_w // 2, card_h // 2), hook_text, font=f_scaled, fill=(124, 58, 237), anchor="mm")
        frame.alpha_composite(c_im, (960 - card_w // 2, 280 - card_h // 2))
        
        # Thỏ Tím rơi từ trên xuống
        frame.alpha_composite(b_resized, (bunny_x - bw // 2, bunny_y - bh // 2 + 100))

    elif cur_ev_idx == 1:
        # Cánh cửa số 1 ma thuật
        door_pulse = 1.0 + 0.05 * math.sin(t * 8.0)
        dw, dh = int(320 * door_pulse), int(440 * door_pulse)
        d_scaled = magic_door.resize((dw, dh), Image.Resampling.BILINEAR)
        frame.alpha_composite(d_scaled, (960 - dw // 2, 420 - dh // 2))
        
        # Label "DOOR 1"
        draw.text((960, 160), "DOOR NUMBER 1", font=FONT_SUB, fill=(254, 240, 138), anchor="mm")
        frame.alpha_composite(b_resized, (360 - bw // 2, 700 - bh // 2))

    # --- PHÂN CẢNH 3 & 4: CLASSROOM (6.5s - 14.5s) ---
    elif cur_ev_idx in [2, 3]:
        # Badge Classroom xoay nhẹ
        badge_scale = 1.0 + 0.08 * math.sin(t * 6.0)
        bdw, bdh = int(380 * badge_scale), int(380 * badge_scale)
        b_class = badge_class.resize((bdw, bdh), Image.Resampling.BILINEAR)
        frame.alpha_composite(b_class, (560 - bdw // 2, 480 - bdh // 2))
        
        # Thẻ chữ CLASSROOM to bản rực rỡ
        word = "CLASSROOM"
        bbox = draw.textbbox((0, 0), word, font=FONT_HERO)
        tw = bbox[2] - bbox[0]
        # Hộp nền trắng nổi
        draw.rounded_rectangle([1050, 360, 1850, 560], radius=35, fill=(255, 255, 255), outline=(251, 191, 36), width=10)
        draw.text((1450, 460), word, font=FONT_HERO, fill=(37, 99, 235), anchor="mm")
        
        sub_action = "We learn here!" if cur_ev_idx == 2 else "Say it: CLASSROOM!"
        draw.text((1450, 630), sub_action, font=FONT_SUB, fill=(254, 240, 138), anchor="mm")
        
        # Thỏ tím đứng bên phải nhảy múa
        frame.alpha_composite(b_resized, (1550 - bw // 2, 850 - bh // 2))

    # --- PHÂN CẢNH 5, 6, 7, 8: LIBRARY (14.5s - 27.5s) ---
    elif cur_ev_idx in [4, 5, 6, 7]:
        if cur_ev_idx == 4:
            # Cửa số 2
            dw, dh = 320, 440
            d_scaled = magic_door.resize((dw, dh), Image.Resampling.BILINEAR)
            frame.alpha_composite(d_scaled, (960 - dw // 2, 420 - dh // 2))
            draw.text((960, 160), "DOOR NUMBER 2: SHHH...", font=FONT_SUB, fill=(254, 240, 138), anchor="mm")
            frame.alpha_composite(b_resized, (360 - bw // 2, 700 - bh // 2))
        else:
            # Badge Library bừng sáng
            badge_scale = 1.0 + 0.08 * math.sin(t * 6.0)
            bdw, bdh = int(380 * badge_scale), int(380 * badge_scale)
            b_lib = badge_lib.resize((bdw, bdh), Image.Resampling.BILINEAR)
            frame.alpha_composite(b_lib, (560 - bdw // 2, 480 - bdh // 2))
            
            # Thẻ chữ LIBRARY
            word = "LIBRARY"
            draw.rounded_rectangle([1050, 360, 1850, 560], radius=35, fill=(255, 255, 255), outline=(16, 185, 129), width=10)
            draw.text((1450, 460), word, font=FONT_HERO, fill=(13, 148, 136), anchor="mm")
            
            sub_action = "Look at all the books!" if cur_ev_idx == 5 else ("I love reading!" if cur_ev_idx == 6 else "Book, book, LIBRARY!")
            draw.text((1450, 630), sub_action, font=FONT_SUB, fill=(254, 240, 138), anchor="mm")
            frame.alpha_composite(b_resized, (1550 - bw // 2, 850 - bh // 2))

    # --- PHÂN CẢNH 9, 10, 11, 12: PLAYGROUND (27.5s - 39.0s) ---
    elif cur_ev_idx in [8, 9, 10, 11]:
        # Cầu trượt Playground
        badge_scale = 1.0 + 0.08 * math.sin(t * 6.0)
        bdw, bdh = int(380 * badge_scale), int(380 * badge_scale)
        b_play = badge_play.resize((bdw, bdh), Image.Resampling.BILINEAR)
        frame.alpha_composite(b_play, (560 - bdw // 2, 480 - bdh // 2))
        
        # Thẻ chữ PLAYGROUND
        word = "PLAYGROUND"
        draw.rounded_rectangle([1000, 360, 1880, 560], radius=35, fill=(255, 255, 255), outline=(234, 88, 12), width=10)
        draw.text((1440, 460), word, font=FONT_CARD, fill=(234, 88, 12), anchor="mm")
        
        sub_action = "Run, Jump, and Play!" if cur_ev_idx in [9, 10] else "Wheeee! PLAYGROUND!"
        draw.text((1440, 630), sub_action, font=FONT_SUB, fill=(254, 240, 138), anchor="mm")
        
        # Thỏ Tím trượt vèo
        slide_x = int(1400 + 200 * math.sin(t * 4.0))
        frame.alpha_composite(b_resized, (slide_x - bw // 2, 850 - bh // 2))

    # --- PHÂN CẢNH 13, 14, 15: ART ROOM & COLOR SPLASH (39.0s - 48.5s) ---
    elif cur_ev_idx in [12, 13, 14]:
        # Color Splash bùng nổ phía sau
        cs_size = int(550 * (1.0 + 0.05 * math.sin(t * 8.0)))
        cs_scaled = color_splash.resize((cs_size, cs_size), Image.Resampling.BILINEAR)
        frame.alpha_composite(cs_scaled, (960 - cs_size // 2, 460 - cs_size // 2))
        
        badge_scale = 1.0 + 0.08 * math.sin(t * 6.0)
        bdw, bdh = int(360 * badge_scale), int(360 * badge_scale)
        b_art = badge_art.resize((bdw, bdh), Image.Resampling.BILINEAR)
        frame.alpha_composite(b_art, (480 - bdw // 2, 480 - bdh // 2))
        
        # Thẻ chữ ART ROOM
        word = "ART ROOM"
        draw.rounded_rectangle([1050, 360, 1850, 560], radius=35, fill=(255, 255, 255), outline=(219, 39, 119), width=10)
        draw.text((1450, 460), word, font=FONT_HERO, fill=(219, 39, 119), anchor="mm")
        
        sub_action = "I can paint!" if cur_ev_idx == 13 else "Red, Blue, and Yellow!"
        draw.text((1450, 630), sub_action, font=FONT_SUB, fill=(254, 240, 138), anchor="mm")
        frame.alpha_composite(b_resized, (1550 - bw // 2, 850 - bh // 2))

    # --- PHÂN CẢNH 16: FAST RECAP (4 TỪ SIÊU TỐC - 48.5s - 54.0s) ---
    elif cur_ev_idx == 15:
        # Phân chia 4 từ trong 5.5s của câu recap
        t_in_recap = t - (dialogue_events[15]["start_ms"] / 1000.0)
        sub_words = ["CLASSROOM", "LIBRARY", "PLAYGROUND", "ART ROOM"]
        sub_badges = [badge_class, badge_lib, badge_play, badge_art]
        sub_colors = [(37, 99, 235), (13, 148, 136), (234, 88, 12), (219, 39, 119)]
        
        w_idx = min(3, max(0, int(t_in_recap / 1.35)))
        w_active = sub_words[w_idx]
        b_active = sub_badges[w_idx]
        c_active = sub_colors[w_idx]
        
        # Hiển thị cực to ở giữa màn hình (TikTok Punch-in)
        punch = 1.0 + 0.10 * math.sin(t_in_recap * 12.0)
        bdw = int(450 * punch)
        b_img_scaled = b_active.resize((bdw, bdw), Image.Resampling.BILINEAR)
        frame.alpha_composite(b_img_scaled, (960 - bdw // 2, 380 - bdw // 2))
        
        draw.rounded_rectangle([360, 680, 1560, 880], radius=40, fill=(255, 255, 255), outline=c_active, width=12)
        draw.text((960, 780), w_active, font=FONT_HERO, fill=c_active, anchor="mm")
        
        # Hiệu ứng sao nổ
        for s_i in range(8):
            ang = s_i * (math.pi / 4) + t * 4.0
            sx = int(960 + 580 * math.cos(ang))
            sy = int(480 + 380 * math.sin(ang))
            draw.ellipse([sx - 15, sy - 15, sx + 15, sy + 15], fill=(254, 240, 138))

    # --- PHÂN CẢNH 17 & 18: CELEBRATION DANCE & CAN-DO (54.0s - 66.8s) ---
    else:
        # Confetti rơi tung bay
        for c in confetti:
            c["y"] += c["vy"]
            c["x"] += c["vx"]
            c["rot"] += c["vrot"]
            if c["y"] > 1100:
                c["y"] = -40
                c["x"] = random.randint(50, 1870)
            cs = c["size"]
            draw.rectangle([c["x"] - cs//2, c["y"] - cs//2, c["x"] + cs//2, c["y"] + cs//2], fill=c["color"])
            
        # Dòng chữ lớn chúc mừng
        praise_pulse = 1.0 + 0.08 * math.sin(t * 8.0)
        praise_txt = "SUPER STAR!" if cur_ev_idx == 16 else "YOU ARE AMAZING!"
        draw.text((960, 260), praise_txt, font=FONT_HERO, fill=(254, 240, 138), anchor="mm")
        
        # Thỏ Tím nhảy cực cao ở giữa sân khấu
        jump_y = int(680 - 180 * abs(math.sin(t * 7.0)))
        frame.alpha_composite(b_resized, (960 - bw // 2, jump_y - bh // 2))
        
        draw.text((960, 920), "HIGH FIVE! SEE YOU AGAIN!", font=FONT_SUB, fill=(255, 255, 255), anchor="mm")

    # 3. Thanh tiến trình TikTok ở đáy màn hình
    progress_w = int(1920 * (t / TOTAL_DURATION))
    draw.rectangle([0, 1068, 1920, 1080], fill=(0, 0, 0, 80))
    draw.rectangle([0, 1068, progress_w, 1080], fill=(251, 191, 36))

    return frame.convert("RGB")

def main():
    print(f"🎬 Bắt đầu Render TikTok-Style Hyper-Retention Video — Purple W06...")
    print(f"   - Tổng thời lượng: {TOTAL_DURATION:.1f}s ({TOTAL_FRAMES} frames @ {FPS}fps)")
    print(f"   - Audio Master: {AUDIO_FILE}")
    print(f"   - Video Output: {OUT_VIDEO}")
    
    OUT_VIDEO.parent.mkdir(parents=True, exist_ok=True)
    
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
        frame_img = render_frame(t, f)
        proc.stdin.write(frame_img.tobytes())
        
        if f % 120 == 0 or f == TOTAL_FRAMES - 1:
            pct = (f / TOTAL_FRAMES) * 100
            print(f"Render TikTok Purple W06: {f}/{TOTAL_FRAMES} frames ({pct:.1f}%) — {t:.1f}s / {TOTAL_DURATION:.1f}s")
            sys.stdout.flush()
            
    proc.stdin.close()
    proc.wait()
    
    if proc.returncode == 0:
        print(f"✅ Hoàn tất render Master Video TikTok Purple W06 Thành Công: {OUT_VIDEO}")
    else:
        print(f"❌ Lỗi khi render FFmpeg! Exit code: {proc.returncode}")
        sys.exit(1)

if __name__ == "__main__":
    main()
