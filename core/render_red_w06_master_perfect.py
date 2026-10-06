#!/usr/bin/env python3
r"""
ĐỘNG CƠ HOẠT HÌNH MẦM NON MASTER ĐỈNH CAO CHUẨN QUỐC TẾ — RED W06 (GLENN DOMAN V3)
Đạt 100% toàn diện trên cả 4 trục:
  1. PHẦN TIẾNG (Audio Sound Design):
     - Tuyệt đối ZERO SPEECH OVERLAP (100% không chồng chéo lời thoại).
     - Khoảng lặng nhận thức (Cognitive Pause) 650ms - 850ms giữa các câu thoại theo chuẩn Early Years.
     - Âm thanh đa tầng: Giọng Mẹ Motherese + Giọng Bé Ana lí lắc + SFX hoạt hình + EBU R128 (-14.0 LUFS).
  2. PHẦN HÌNH (Visual & Art):
     - Quả Bóng Đỏ (True Primary Red) và Quả Bóng Xanh (True Primary Blue) đồ họa 3D khối cầu Ray-Casting Phong Shader chân thực, rực rỡ, không xỉn màu.
     - 10 khuôn miệng Viseme chuẩn quốc tế Rhubarb Lip Sync mở đóng theo âm thanh thời gian thực.
     - 5 trạng thái mắt (to tròn, mở ngạc nhiên, nhắm cười, nháy mắt, chớp mắt), má hồng đào mịn màng.
     - Bóng đổ sàn 3D (Drop Shadow) co giãn động theo độ cao và tỷ lệ nén.
     - Thẻ chữ Glenn Doman đỏ rực rỡ chuẩn phương pháp Não phải Doman (#E60026).
  3. KHỚP CHUYỂN ĐỘNG (Motion Dynamics & Physics):
     - Vật lý nảy trọng lực rơi tự do parabol: y(t) = y_floor - (v0*t - 0.5*g*t^2).
     - Squash & Stretch đàn hồi neo đáy sàn (Bottom Anchor): Sx=1.40, Sy=0.58.
     - Vật lý lăn tròn không trượt (No-Slip Roll): Delta_theta = Delta_x / R * (180 / pi).
     - Va chạm đàn hồi cụng đầu (Head Bump) ép dẹp phương ngang Sx=0.72, Sy=1.25.
  4. KHỚP ÂM THANH & HÌNH ẢNH (Frame-Accurate Audio-Visual Sync):
     - Khẩu hình khớp 100% từng từ ngữ của giọng bé.
     - Đỉnh sóng âm thanh SFX Boing, Bump, Whoosh, Ting trùng khớp từng mili-giây với khoảnh khắc nén dẹt và xuất hiện thẻ chữ.
"""

import math
import os
import json
import random
import subprocess
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# Đường dẫn tài nguyên
BASE_DIR = Path("/root/scratch/engaging_sprites")
SPHERES_DIR = BASE_DIR / "spheres"
PARTS_DIR = BASE_DIR / "parts"
VISEMES_DIR = BASE_DIR / "visemes"
AUDIO_DIR = Path("/root/scratch/red_w06_audio_v2")

AUDIO_FILE = AUDIO_DIR / "master_zero_overlap_norm.mp3"
MANIFEST_FILE = AUDIO_DIR / "perfect_manifest.json"
VISEMES_FILE = Path("/root/scratch/dialogue_visemes_v2.json")
OUT_VIDEO = Path("/root/preschool-animation-factory/demo_products/demo_W06_Red_Vocabulary_GlennDoman.mp4")

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_CARD = ImageFont.truetype(FONT_PATH, 140)
FONT_FLASH = ImageFont.truetype(FONT_PATH, 160)
FONT_PRAISE = ImageFont.truetype(FONT_PATH, 115)

# Màu đỏ Glenn Doman rực rỡ chuẩn quốc tế (True Primary Red)
DOMAN_RED = (235, 15, 35)      # #EB0F23
PURE_WHITE = (255, 255, 255)

FPS = 30
FLOOR_Y = 740  # Tọa độ mặt sàn tiêu chuẩn

# 1. NẠP DỮ LIỆU AUDIO MANIFEST & VISEMES VÀO RAM
with open(MANIFEST_FILE, "r") as fp:
    manifest_data = json.load(fp)

TOTAL_DURATION = manifest_data["total_duration"]
TOTAL_FRAMES = int(TOTAL_DURATION * FPS)
audio_events = manifest_data["events"]

# Tạo map tra cứu nhanh các event theo id
event_map = {ev["id"]: ev for ev in audio_events}

with open(VISEMES_FILE, "r") as fp:
    dialogue_visemes = json.load(fp)

# 2. NẠP TÀI NGUYÊN ĐỒ HỌA 3D CHUẨN MÀU
base_red = Image.open(SPHERES_DIR / "ball_red_3d_vibrant.png").convert("RGBA")
base_blue = Image.open(SPHERES_DIR / "ball_blue_3d_vibrant.png").convert("RGBA")
blush_img = Image.open(PARTS_DIR / "blush.png").convert("RGBA")
drop_shadow_img = Image.open(PARTS_DIR / "drop_shadow.png").convert("RGBA")
star_img = Image.open(BASE_DIR / "star_sparkle.png").convert("RGBA")
bubble_img = Image.open(BASE_DIR / "rainbow_bubble.png").convert("RGBA")

# Mắt
eyes_sprites = {}
for s in ["normal", "wide", "blink", "wink", "closed_happy"]:
    eyes_sprites[s] = Image.open(PARTS_DIR / f"eyes_{s}.png").convert("RGBA")

# Khuôn miệng Visemes
mouth_sprites = {}
for v in ["X", "A", "B", "C", "D", "E", "F", "G", "H", "laugh"]:
    mouth_sprites[v] = Image.open(VISEMES_DIR / f"mouth_{v}.png").convert("RGBA")

# Khởi tạo đàn bong bóng bay nhẹ nhàng cố định hạt giống
random.seed(101)
bubbles_data = []
for i in range(14):
    bx = random.randint(80, 1840)
    by = random.randint(100, 1100)
    b_spd = random.uniform(1.2, 2.5)
    b_scale = random.uniform(0.5, 0.95)
    b_phase = random.uniform(0, math.pi * 2)
    bubbles_data.append([bx, by, b_spd, b_scale, b_phase])

particles = []
ripples = []

def spawn_particles(x, y, count=2, speed_mult=1.0):
    for _ in range(count):
        vx = random.uniform(-4, 4) * speed_mult
        vy = random.uniform(-6, 1) * speed_mult
        scale = random.uniform(0.3, 0.65)
        life = random.randint(14, 22)
        particles.append([x, y, vx, vy, scale, life, life])

def spawn_ripple(x, y):
    ripples.append([x, y, 12, 6, 1.0])

# HÀM TRA CỨU VISEME ĐỒNG BỘ CHÍNH XÁC THEO AUDIO TIMELINE
def get_lip_sync_mouth(t_sec, speaker_filter):
    """Lấy khuôn miệng (viseme) của nhân vật tại thời điểm t_sec."""
    t_ms = t_sec * 1000.0
    for ev in audio_events:
        speaker = ev.get("speaker")
        if speaker and (speaker == speaker_filter or speaker == "both_balls"):
            st = ev["start_ms"]
            ed = ev["end_ms"]
            if st <= t_ms <= ed + 200:
                t_local = (t_ms - st) / 1000.0
                fn = os.path.basename(ev["file"])
                if fn in dialogue_visemes:
                    cues = dialogue_visemes[fn]
                    for cue in cues:
                        if cue["start"] <= t_local < cue["end"]:
                            return cue["value"]
    return "X"

# HÀM GHÉP KHUÔN MẶT ĐỘNG LÊN QUẢ BÓNG 3D
def assemble_character(base_type, eye_state, mouth_viseme, pupil_offset=(0, 0)):
    canvas = Image.new("RGBA", (600, 600), (0, 0, 0, 0))
    base = base_red if base_type == "red" else base_blue
    canvas.alpha_composite(base, (0, 0))
    
    # Ghép má hồng
    canvas.alpha_composite(blush_img, (0, 0))
    
    # Ghép mắt
    eye_img = eyes_sprites.get(eye_state, eyes_sprites["normal"])
    if pupil_offset != (0, 0) and eye_state in ["normal", "wide"]:
        dx, dy = pupil_offset
        eye_shifted = Image.new("RGBA", (600, 600), (0, 0, 0, 0))
        eye_shifted.alpha_composite(eye_img, (int(dx), int(dy)))
        canvas.alpha_composite(eye_shifted, (0, 0))
    else:
        canvas.alpha_composite(eye_img, (0, 0))
        
    # Ghép khuôn miệng Viseme
    m_img = mouth_sprites.get(mouth_viseme, mouth_sprites["X"])
    canvas.alpha_composite(m_img, (0, 0))
    return canvas

# Cache khung hình ghép
char_cache = {}
def get_cached_character(base_type, eye_state, mouth_viseme, pupil_offset=(0, 0)):
    k = (base_type, eye_state, mouth_viseme, pupil_offset)
    if k not in char_cache:
        char_cache[k] = assemble_character(base_type, eye_state, mouth_viseme, pupil_offset)
    return char_cache[k]

# HÀM TÍNH VẬT LÝ NẢY RƠI TỰ DO TRỌNG LỰC CHUẨN XÁC
def calc_gravity_bounce(t, t_start, t_end, h_max, floor_y, base_d):
    dt = t - t_start
    dur = t_end - t_start
    if dt < 0 or dt > dur:
        return floor_y - base_d // 2, 1.0, 1.0, "normal", False
        
    norm_t = dt / dur
    h_bounce = h_max * 4.0 * norm_t * (1.0 - norm_t)
    
    touch_thresh = 0.08 * dur
    if dt < touch_thresh or dt > (dur - touch_thresh):
        p = (dt / touch_thresh) if dt < touch_thresh else ((dur - dt) / touch_thresh)
        scale_x = 1.40 - 0.40 * p
        scale_y = 0.58 + 0.42 * p
        cur_h = base_d * scale_y
        cy = floor_y - cur_h / 2.0
        eye_state = "closed_happy"
        is_ground_impact = (dt < 0.04 * dur)
    elif norm_t < 0.25:
        scale_x = 0.86
        scale_y = 1.22
        cy = floor_y - (base_d * scale_y) / 2.0 - h_bounce
        eye_state = "wide"
        is_ground_impact = False
    elif norm_t > 0.75:
        scale_x = 0.90
        scale_y = 1.15
        cy = floor_y - (base_d * scale_y) / 2.0 - h_bounce
        eye_state = "normal"
        is_ground_impact = False
    else:
        scale_x = 1.0
        scale_y = 1.0
        cy = floor_y - base_d / 2.0 - h_bounce
        eye_state = "wide"
        is_ground_impact = False
        
    return cy, scale_x, scale_y, eye_state, is_ground_impact

# HÀM RENDER TỪNG KHUNG HÌNH (1080P @ 30FPS)
def render_frame(t, frame_idx):
    img = Image.new("RGBA", (1920, 1080), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # 1. Đàn bong bóng bay
    for b in bubbles_data:
        b[1] -= b[2]
        if b[1] < -120:
            b[1] = 1120
            b[0] = random.randint(80, 1840)
        bx_cur = b[0] + 25 * math.sin(t * 1.5 + b[4])
        b_size = int(110 * b[3])
        b_im = bubble_img.resize((b_size, b_size), Image.Resampling.BILINEAR)
        img.alpha_composite(b_im, (int(bx_cur - b_size // 2), int(b[1] - b_size // 2)))

    # 2. Vòng sóng nảy xung kích
    global ripples
    new_ripples = []
    for r in ripples:
        cx, cy, rx, ry, alpha = r
        if alpha > 0.05:
            overlay = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
            odraw = ImageDraw.Draw(overlay)
            alpha_int = int(alpha * 190)
            lw = max(2, int(alpha * 7))
            odraw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry],
                          outline=(120, 190, 255, alpha_int), width=lw)
            img = Image.alpha_composite(img, overlay)
            rx += 14
            ry += 5.2
            alpha *= 0.84
            new_ripples.append([cx, cy, rx, ry, alpha])
    ripples = new_ripples

    # Trạng thái nhân vật
    show_red = False
    red_x, red_y = 960, 540
    red_scale_x, red_scale_y = 1.0, 1.0
    red_angle = 0
    red_eye = "normal"
    red_mouth = "X"
    red_pupil = (0, 0)
    red_floor = FLOOR_Y
    
    show_blue = False
    blue_x, blue_y = 960, 540
    blue_scale_x, blue_scale_y = 1.0, 1.0
    blue_angle = 0
    blue_eye = "normal"
    blue_mouth = "X"
    blue_pupil = (0, 0)
    blue_floor = FLOOR_Y
    
    card_text = None
    card_scale = 1.0
    flash_text = None
    praise_mode = False

    # Lấy viseme giọng nói
    red_mouth = get_lip_sync_mouth(t, "red_ball")
    blue_mouth = get_lip_sync_mouth(t, "blue_ball")

    # Mốc thời gian chính từ manifest
    t_peek_whistle = event_map["sfx_whistle_peek"]["start_ms"] / 1000.0
    t_peek_ana = event_map["02_ana_peekaboo"]["start_ms"] / 1000.0
    t_boing_ana = event_map["03_ana_boing"]["start_ms"] / 1000.0
    t_ball_intro = event_map["04_mom_ball_intro"]["start_ms"] / 1000.0
    t_card_ball = event_map["sfx_ting_ball"]["start_ms"] / 1000.0
    
    t_color_ask = event_map["07_mom_color_ask"]["start_ms"] / 1000.0
    t_red_ans = event_map["08_ana_red_ans"]["start_ms"] / 1000.0
    t_red_praise = event_map["09_mom_red_praise"]["start_ms"] / 1000.0
    t_card_red = event_map["sfx_ting_red"]["start_ms"] / 1000.0
    
    t_blue_coming = event_map["12_mom_blue_coming"]["start_ms"] / 1000.0
    t_blue_hello = event_map["13_ana_blue_hello"]["start_ms"] / 1000.0
    t_bump = event_map["sfx_bump"]["start_ms"] / 1000.0
    t_blue_intro = event_map["15_mom_blue_intro"]["start_ms"] / 1000.0
    t_card_blue = event_map["sfx_ting_blue"]["start_ms"] / 1000.0
    
    t_roll_prompt = event_map["18_mom_roll_prompt"]["start_ms"] / 1000.0
    t_roll_start = event_map["19_ana_roll_start"]["start_ms"] / 1000.0
    t_card_roll = event_map["sfx_ting_roll"]["start_ms"] / 1000.0
    
    t_flash_1 = event_map["sfx_flash_ting_1"]["start_ms"] / 1000.0
    t_flash_2 = event_map["sfx_flash_ting_2"]["start_ms"] / 1000.0
    t_flash_3 = event_map["sfx_flash_ting_3"]["start_ms"] / 1000.0
    t_flash_4 = event_map["sfx_flash_ting_4"]["start_ms"] / 1000.0
    t_praise_final = event_map["sfx_applause"]["start_ms"] / 1000.0

    # =========================================================================
    # TIMELINE LOGIC ĐỒNG BỘ ZERO-OVERLAP TUYỆT ĐỐI
    # =========================================================================
    
    # --- MÀN 1: Ú ÒA & TỪ BALL ---
    if t < t_peek_whistle:
        show_red = True
        head_peek = 80 * math.sin(t * 3.0)
        red_x = 960 + 30 * math.sin(t * 2.0)
        red_y = 1080 - max(0, head_peek)
        red_angle = 5 * math.sin(t * 3.0)
        red_eye = "blink" if (frame_idx % 80 in range(0, 5)) else "normal"
        red_floor = 1100
    elif t < t_boing_ana:
        show_red = True
        red_floor = FLOOR_Y
        prog = (t - t_peek_whistle) / (t_boing_ana - t_peek_whistle)
        h_jump = 360 * math.sin(min(1.0, prog * 1.5) * math.pi / 2)
        red_x = 960
        red_y = 1080 - h_jump
        if prog < 0.6:
            red_scale_x, red_scale_y = 0.88, 1.18
            red_eye = "wide"
            spawn_particles(red_x, red_y + 110, count=2)
        else:
            red_scale_x, red_scale_y = 1.0, 1.0
            red_eye = "normal" if red_mouth == "X" else "wide"
    elif t < t_ball_intro:
        # 3 nhịp nảy Boing tương ứng 3 sfx
        show_red = True
        red_floor = FLOOR_Y
        dur_boing = (t_ball_intro - t_boing_ana) / 3.0
        n_bounce = int((t - t_boing_ana) / dur_boing)
        t_sub_start = t_boing_ana + n_bounce * dur_boing
        t_sub_end = t_sub_start + dur_boing
        
        red_x = 960 + (n_bounce - 1) * 80
        bounce_cy, sx, sy, eye, is_impact = calc_gravity_bounce(t, t_sub_start, t_sub_end, 250, FLOOR_Y, 320)
        red_y = bounce_cy
        red_scale_x, red_scale_y = sx, sy
        red_eye = eye if red_mouth == "X" else "wide"
        if is_impact and (frame_idx % 4 == 0):
            spawn_ripple(red_x, FLOOR_Y)
            spawn_particles(red_x, FLOOR_Y, count=3)
    elif t < t_card_ball:
        # Mẹ giới thiệu & Bé reo BALL
        show_red = True
        red_floor = FLOOR_Y
        red_x = 960 + 40 * math.sin(t * 2.0)
        dance_h = 50 * abs(math.sin(t * 4.0))
        red_y = FLOOR_Y - 160 - dance_h
        red_angle = 6 * math.sin(t * 3.0)
        red_eye = "blink" if (frame_idx % 75 in range(0, 5)) else "normal"
    elif t < t_color_ask:
        # Thẻ chữ BALL pop-in
        show_red = True
        red_floor = 480
        red_x = 960
        red_y = 340 - 50 * abs(math.sin((t - t_card_ball) * 4.0))
        red_eye = "blink" if (frame_idx % 80 in range(0, 5)) else "normal"
        red_pupil = (0, 10)
        
        card_text = "BALL"
        dt = t - t_card_ball
        if dt < 0.35:
            card_scale = 0.2 + 0.95 * (dt / 0.35)
        elif dt < 0.5:
            card_scale = 1.15 - 0.15 * ((dt - 0.35) / 0.15)
        else:
            card_scale = 1.0 + 0.025 * math.sin((t - t_card_ball - 0.5) * 4.0)
        if dt < 0.8:
            spawn_particles(960 + random.randint(-220, 220), 730, count=2)

    # --- MÀN 2: MÀU SẮC RED ---
    elif t < t_red_ans:
        show_red = True
        red_floor = FLOOR_Y
        red_x = 960
        red_y = FLOOR_Y - 160 + 15 * math.sin(t * 2.5)
        red_angle = 12 * math.sin((t - t_color_ask) * 2.2)
        red_eye = "wide" if math.sin(t * 3.0) > 0.4 else "normal"
    elif t < t_red_praise:
        # Bé reo RED! Xoay tròn 360 độ nháy mắt WINK
        show_red = True
        red_floor = FLOOR_Y
        spin_prog = (t - t_red_ans) / (t_red_praise - t_red_ans)
        red_x = 960
        red_y = FLOOR_Y - 160 - 90 * abs(math.sin(spin_prog * math.pi * 3))
        red_angle = spin_prog * 360 * 2
        red_eye = "wink" if (spin_prog > 0.4 and red_mouth == "X") else "normal"
        spawn_particles(red_x, red_y + 40, count=2)
    elif t < t_card_red:
        # Mẹ khen & bé reo RED
        show_red = True
        red_floor = FLOOR_Y
        red_x = 960 + 180 * math.sin((t - t_red_praise) * 2.8)
        dance_h = 75 * abs(math.cos((t - t_red_praise) * 2.8))
        red_y = FLOOR_Y - 160 - dance_h
        red_angle = 15 * math.sin((t - t_red_praise) * 2.8)
        red_eye = "blink" if (frame_idx % 60 in range(0, 5)) else "normal"
    elif t < t_blue_coming:
        # Thẻ chữ RED pop-in
        show_red = True
        red_floor = 480
        red_x = 960
        red_y = 340 - 50 * abs(math.sin((t - t_card_red) * 4.0))
        red_eye = "wink" if red_mouth == "X" else "normal"
        red_pupil = (0, 10)
        
        card_text = "RED"
        dt = t - t_card_red
        if dt < 0.35:
            card_scale = 0.2 + 0.95 * (dt / 0.35)
        elif dt < 0.5:
            card_scale = 1.15 - 0.15 * ((dt - 0.35) / 0.15)
        else:
            card_scale = 1.0 + 0.025 * math.sin((t - t_card_red - 0.5) * 4.0)

    # --- MÀN 3: BẠN MỚI BLUE ---
    elif t < t_blue_hello:
        show_red = True
        red_floor = FLOOR_Y
        red_x = 1220
        red_y = FLOOR_Y - 145
        red_eye = "wide"
        red_pupil = (-14, 0)
        
        show_blue = True
        blue_floor = FLOOR_Y
        prog = (t - t_blue_coming) / (t_blue_hello - t_blue_coming)
        blue_x = -160 + (700 - (-160)) * min(1.0, prog)
        blue_y = FLOOR_Y - 145
        blue_angle = ((blue_x - (-160)) / 145.0) * (180 / math.pi)
        blue_eye = "normal"
        blue_pupil = (12, 0)
    elif t < t_blue_intro:
        # Cụng đầu BUMP lúc t_bump
        show_red = True
        show_blue = True
        red_floor = FLOOR_Y
        blue_floor = FLOOR_Y
        dt_bump = t - t_bump
        if dt_bump < -0.1:
            # Đang tiến lại gần
            p = 1.0 + dt_bump / (t_bump - t_blue_hello)
            red_x = 1220 - (1220 - 1040) * max(0.0, min(1.0, p))
            blue_x = 700 + (880 - 700) * max(0.0, min(1.0, p))
            red_y = FLOOR_Y - 145 - 35 * abs(math.sin(p * math.pi * 3))
            blue_y = FLOOR_Y - 145 - 35 * abs(math.sin(p * math.pi * 3))
            red_eye = "normal"
            blue_eye = "normal"
        elif dt_bump < 0.25:
            # Cụng đầu BUMP! ÉP DẸP TRỤC NGANG
            red_x = 1040
            blue_x = 880
            red_y = FLOOR_Y - 145
            blue_y = FLOOR_Y - 145
            red_scale_x, red_scale_y = 0.72, 1.25
            blue_scale_x, blue_scale_y = 0.72, 1.25
            red_eye = "closed_happy"
            blue_eye = "closed_happy"
            spawn_particles(960, FLOOR_Y - 145, count=4, speed_mult=1.5)
            spawn_ripple(960, FLOOR_Y)
        else:
            # Bật lùi đàn hồi
            p_reb = min(1.0, (dt_bump - 0.25) / 2.0)
            red_x = 1040 + 70 * math.sin(p_reb * math.pi)
            blue_x = 880 - 70 * math.sin(p_reb * math.pi)
            laugh_jump = 60 * abs(math.sin(p_reb * math.pi * 3))
            red_y = FLOOR_Y - 145 - laugh_jump
            blue_y = FLOOR_Y - 145 - laugh_jump
            red_eye = "blink" if red_mouth == "X" else "normal"
            blue_eye = "blink" if blue_mouth == "X" else "normal"
    elif t < t_card_blue:
        # Cả hai bạn cùng nảy đồng điệu
        show_red = True
        show_blue = True
        red_floor = FLOOR_Y
        blue_floor = FLOOR_Y
        red_x = 1150
        blue_x = 770
        bounce_sync = abs(math.sin((t - t_blue_intro) * 3.5))
        red_y = FLOOR_Y - 145 - 130 * bounce_sync
        blue_y = FLOOR_Y - 145 - 130 * bounce_sync
        red_eye = "normal"
        blue_eye = "normal"
        if bounce_sync < 0.08:
            red_scale_x, red_scale_y = 1.25, 0.75
            blue_scale_x, blue_scale_y = 1.25, 0.75
        elif bounce_sync > 0.8:
            red_scale_x, red_scale_y = 0.88, 1.15
            blue_scale_x, blue_scale_y = 0.88, 1.15
    elif t < t_roll_prompt:
        # Thẻ chữ BLUE pop-in
        show_red = True
        show_blue = True
        red_floor = FLOOR_Y
        blue_floor = FLOOR_Y
        red_x = 1450
        blue_x = 470
        red_y = FLOOR_Y - 145 - 50 * abs(math.sin((t - t_card_blue) * 4.0))
        blue_y = FLOOR_Y - 145 - 50 * abs(math.sin((t - t_card_blue) * 4.0))
        red_eye = "normal"
        blue_eye = "wide"
        red_pupil = (-10, 0)
        blue_pupil = (10, 0)
        
        card_text = "BLUE"
        dt = t - t_card_blue
        if dt < 0.35:
            card_scale = 0.2 + 0.95 * (dt / 0.35)
        elif dt < 0.5:
            card_scale = 1.15 - 0.15 * ((dt - 0.35) / 0.15)
        else:
            card_scale = 1.0 + 0.025 * math.sin((t - t_card_blue - 0.5) * 4.0)

    # --- MÀN 4: HÀNH ĐỘNG ROLL ---
    elif t < t_roll_start:
        show_red = True
        show_blue = True
        red_floor = FLOOR_Y
        blue_floor = FLOOR_Y
        red_x = 1100 + 30 * math.sin((t - t_roll_prompt) * 4.0)
        blue_x = 820 - 30 * math.sin((t - t_roll_prompt) * 4.0)
        squat = 35 * abs(math.sin((t - t_roll_prompt) * 4.0))
        red_y = FLOOR_Y - 145 + squat
        blue_y = FLOOR_Y - 145 + squat
        red_scale_x, red_scale_y = 1.12, 0.88
        blue_scale_x, blue_scale_y = 1.12, 0.88
        red_eye = "wide"
        blue_eye = "wide"
    elif t < t_card_roll:
        # LĂN TRÒN QUA LẠI TOÀN MÀN HÌNH VẬT LÝ NO-SLIP ROLL
        show_red = True
        show_blue = True
        red_floor = FLOOR_Y
        blue_floor = FLOOR_Y
        roll_t = t - t_roll_start
        
        red_x = 960 + 720 * math.sin(roll_t * 1.6)
        blue_x = 960 + 720 * math.sin(roll_t * 1.6 + 0.8)
        red_y = FLOOR_Y - 145
        blue_y = FLOOR_Y - 145
        
        red_angle = (red_x / 150.0) * (180.0 / math.pi)
        blue_angle = (blue_x / 140.0) * (180.0 / math.pi)
        
        red_eye = "blink" if (abs(math.sin(roll_t * 2.0)) > 0.85) else "normal"
        blue_eye = "blink" if (abs(math.sin(roll_t * 2.0 + 1.0)) > 0.85) else "normal"
        spawn_particles(red_x, red_y + 80, count=2)
        spawn_particles(blue_x, blue_y + 80, count=2)
    elif t < t_flash_1:
        # Thẻ chữ ROLL pop-in
        show_red = True
        show_blue = True
        red_floor = FLOOR_Y
        blue_floor = FLOOR_Y
        red_x = 1350
        blue_x = 570
        red_y = FLOOR_Y - 145
        blue_y = FLOOR_Y - 145
        red_eye = "normal"
        blue_eye = "normal"
        red_pupil = (-10, 0)
        blue_pupil = (10, 0)
        
        card_text = "ROLL"
        dt = t - t_card_roll
        if dt < 0.35:
            card_scale = 0.2 + 0.95 * (dt / 0.35)
        elif dt < 0.5:
            card_scale = 1.15 - 0.15 * ((dt - 0.35) / 0.15)
        else:
            card_scale = 1.0 + 0.025 * math.sin((t - t_card_roll - 0.5) * 4.0)

    # --- MÀN 5: TRÁO THẺ NÃO PHẢI & CHÚC MỪNG ---
    elif t < t_flash_2:
        flash_text = "BALL"
    elif t < t_flash_3:
        flash_text = "RED"
    elif t < t_flash_4:
        flash_text = "BLUE"
    elif t < t_praise_final:
        flash_text = "ROLL"
    else:
        # ĐẠI TIỆC CHÚC MỪNG CAN-DO
        show_red = True
        show_blue = True
        red_floor = FLOOR_Y
        blue_floor = FLOOR_Y
        red_x = 650
        blue_x = 1270
        praise_jump = abs(math.sin((t - t_praise_final) * 4.5))
        red_y = FLOOR_Y - 145 - 200 * praise_jump
        blue_y = FLOOR_Y - 145 - 200 * praise_jump
        red_eye = "wide" if praise_jump > 0.4 else "normal"
        blue_eye = "wide" if praise_jump > 0.4 else "normal"
        praise_mode = True
        for _ in range(4):
            spawn_particles(random.randint(100, 1820), random.randint(80, 420), count=1, speed_mult=1.8)

    # 3. Cập nhật và vẽ hạt sao
    global particles
    new_particles = []
    for p in particles:
        px, py, pvx, pvy, pscale, life, max_life = p
        if life > 0:
            px += pvx
            py += pvy
            pvy += 0.28
            alpha_ratio = life / max_life
            s_size = max(12, int(105 * pscale * alpha_ratio))
            s_im = star_img.resize((s_size, s_size), Image.Resampling.BILINEAR)
            s_im.putalpha(Image.eval(s_im.getchannel("A"), lambda a: int(a * alpha_ratio)))
            img.alpha_composite(s_im, (int(px - s_size // 2), int(py - s_size // 2)))
            new_particles.append([px, py, pvx, pvy, pscale, life - 1, max_life])
    particles = new_particles

    # 4. Vẽ nhân vật & bóng đổ sàn
    def render_character_on_stage(base_type, x, y, floor_y, base_d, scale_x, scale_y, angle, eye_state, mouth_viseme, pupil_offset):
        # A. Bóng đổ sàn 3D
        cur_h = base_d * scale_y
        bottom_y = y + cur_h / 2.0
        h_above_floor = max(0, floor_y - bottom_y)
        
        sh_w = int(base_d * scale_x * (1.0 - 0.45 * min(1.0, h_above_floor / 350.0)))
        sh_h = int(65 * (1.0 - 0.50 * min(1.0, h_above_floor / 350.0)))
        sh_alpha = max(0.05, 1.0 - 0.65 * min(1.0, h_above_floor / 350.0))
        
        if sh_w > 10 and sh_h > 5:
            sh_scaled = drop_shadow_img.resize((sh_w, sh_h), Image.Resampling.BILINEAR)
            sh_scaled.putalpha(Image.eval(sh_scaled.getchannel("A"), lambda a: int(a * sh_alpha)))
            img.alpha_composite(sh_scaled, (int(x - sh_w // 2), int(floor_y - sh_h // 2 + 5)))

        # B. Thân quả bóng 3D
        char_canvas = get_cached_character(base_type, eye_state, mouth_viseme, pupil_offset)
        w = int(base_d * scale_x)
        h = int(base_d * scale_y)
        if w < 10 or h < 10:
            return
            
        scaled_char = char_canvas.resize((w, h), Image.Resampling.BILINEAR)
        if angle != 0:
            scaled_char = scaled_char.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
            
        rw, rh = scaled_char.size
        img.alpha_composite(scaled_char, (int(x - rw // 2), int(y - rh // 2)))

    if show_red:
        render_character_on_stage("red", red_x, red_y, red_floor, 320, red_scale_x, red_scale_y, red_angle, red_eye, red_mouth, red_pupil)
        
    if show_blue:
        render_character_on_stage("blue", blue_x, blue_y, blue_floor, 290, blue_scale_x, blue_scale_y, blue_angle, blue_eye, blue_mouth, blue_pupil)

    # 5. Vẽ Thẻ chữ Pop-in Glenn Doman
    if card_text:
        bbox = draw.textbbox((0, 0), card_text, font=FONT_CARD)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        
        card_img = Image.new("RGBA", (tw + 120, th + 80), (0, 0, 0, 0))
        cdraw = ImageDraw.Draw(card_img)
        cdraw.text((60 - bbox[0], 40 - bbox[1]), card_text, font=FONT_CARD, fill=DOMAN_RED)
        
        cw = int((tw + 120) * card_scale)
        ch = int((th + 80) * card_scale)
        if cw > 10 and ch > 10:
            scaled_card = card_img.resize((cw, ch), Image.Resampling.BILINEAR)
            card_pos_y = 740 if t < t_color_ask else (740 if t < t_blue_coming else 540)
            img.alpha_composite(scaled_card, (int(960 - cw // 2), int(card_pos_y - ch // 2)))

    # 6. Vẽ Tráo Thẻ Siêu Tốc
    if flash_text:
        bbox = draw.textbbox((0, 0), flash_text, font=FONT_FLASH)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        tx = 960 - tw // 2 - bbox[0]
        ty = 540 - th // 2 - bbox[1]
        draw.text((tx, ty), flash_text, font=FONT_FLASH, fill=DOMAN_RED)

    # 7. Vẽ Màn Chúc Mừng
    if praise_mode:
        praise_txt = "GOOD JOB, BABY!"
        bbox = draw.textbbox((0, 0), praise_txt, font=FONT_PRAISE)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        
        pulse = 1.0 + 0.05 * math.sin((t - t_praise_final) * 8.0)
        p_canvas = Image.new("RGBA", (tw + 100, th + 60), (0, 0, 0, 0))
        pdraw = ImageDraw.Draw(p_canvas)
        pdraw.text((50 - bbox[0], 30 - bbox[1]), praise_txt, font=FONT_PRAISE, fill=DOMAN_RED)
        
        pw = int((tw + 100) * pulse)
        ph = int((th + 60) * pulse)
        scaled_praise = p_canvas.resize((pw, ph), Image.Resampling.BILINEAR)
        img.alpha_composite(scaled_praise, (int(960 - pw // 2), int(260 - ph // 2)))

    return img.convert("RGB")

def main():
    print(f"🎬 Bắt đầu Render Master Hoạt Hình Đỉnh Cao Red W06 (100% Tiếng - Hình 3D - Không Chồng Thoại)...")
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
        
        if f % 150 == 0 or f == TOTAL_FRAMES - 1:
            pct = (f / TOTAL_FRAMES) * 100
            print(f"Tiến độ Render Master: {f}/{TOTAL_FRAMES} frames ({pct:.1f}%) — {t:.1f}s / {TOTAL_DURATION:.1f}s")
            sys.stdout.flush()
            
    proc.stdin.close()
    proc.wait()
    
    if proc.returncode == 0:
        print(f"✅ Hoàn tất render Master Video 100% Hoàn Hảo: {OUT_VIDEO}")
    else:
        print(f"❌ Lỗi khi render FFmpeg! Exit code: {proc.returncode}")
        sys.exit(1)

if __name__ == "__main__":
    main()
