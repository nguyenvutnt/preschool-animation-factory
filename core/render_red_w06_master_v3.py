#!/usr/bin/env python3
r"""
ĐỘNG CƠ HOẠT HÌNH MẦM NON MASTER ĐỈNH CAO CHUẨN QUỐC TẾ — RED W06 (GLENN DOMAN V3)
Phiên bản V3 Sư phạm Toàn diện:
  1. Kịch bản sư phạm chuẩn quốc tế (DAP - NAEYC, Glenn Doman IAHP, Nation & Webb 2011).
  2. 4 Giọng đọc Chuẩn Mỹ (General American): Mr. David, Ms. Sarah, Leo (Red Ball), Mia (Blue Ball).
  3. 100% ZERO SPEECH OVERLAP + Khoảng lặng nhận thức (Cognitive Processing Pause: 1.45s).
  4. Đồ họa 3D khối cầu Phong Shader chân thực, rực rỡ, specular highlight bóng loáng.
  5. Phông chữ bo tròn mầm non thân thiện chuẩn quốc tế (Quicksand Bold).
  6. Vật lý nảy trọng lực, va chạm cụng đầu BUMP, lăn tròn No-Slip Roll, đồng bộ Rhubarb Lip Sync.
"""

import math
import os
import json
import random
import subprocess
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# 1. ĐƯỜNG DẪN TÀI NGUYÊN
BASE_DIR = Path("/root/scratch/engaging_sprites")
SPHERES_DIR = BASE_DIR / "spheres"
PARTS_DIR = BASE_DIR / "parts"
VISEMES_DIR = BASE_DIR / "visemes"
AUDIO_DIR = Path("/root/scratch/red_w06_audio_v3")

AUDIO_FILE = AUDIO_DIR / "master_v3_broadcast.mp3"
MANIFEST_FILE = AUDIO_DIR / "perfect_manifest_v3.json"
VISEMES_FILE = Path("/root/scratch/dialogue_visemes_v3.json")
OUT_VIDEO = Path("/root/preschool-animation-factory/demo_products/demo_W06_Red_Vocabulary_GlennDoman.mp4")

# Phông chữ bo tròn mầm non thân thiện
FONT_PATH = "/usr/share/fonts/truetype/quicksand/Quicksand-Bold.ttf"
FONT_CARD = ImageFont.truetype(FONT_PATH, 150)
FONT_FLASH = ImageFont.truetype(FONT_PATH, 180)
FONT_PRAISE = ImageFont.truetype(FONT_PATH, 125)

# Màu đỏ Glenn Doman Não Phải rực rỡ
DOMAN_RED = (235, 15, 35)      # #EB0F23
PURE_WHITE = (255, 255, 255)

FPS = 30
FLOOR_Y = 740  # Tọa độ mặt sàn tiêu chuẩn

# 2. NẠP DỮ LIỆU MANIFEST & VISEMES VÀO RAM
with open(MANIFEST_FILE, "r") as fp:
    manifest_data = json.load(fp)

TOTAL_DURATION = manifest_data["total_duration"]
TOTAL_FRAMES = int(TOTAL_DURATION * FPS)
audio_events = manifest_data["events"]
event_map = {ev["id"]: ev for ev in audio_events}

with open(VISEMES_FILE, "r") as fp:
    dialogue_visemes = json.load(fp)

# 3. NẠP TÀI NGUYÊN ĐỒ HỌA 3D CHÂN THỰC
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

# Khuôn miệng Visemes Rhubarb
mouth_sprites = {}
for v in ["X", "A", "B", "C", "D", "E", "F", "G", "H", "laugh"]:
    mouth_sprites[v] = Image.open(VISEMES_DIR / f"mouth_{v}.png").convert("RGBA")

# Khởi tạo hạt giống bong bóng bay
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

# TRA CỨU KHẨU HÌNH VISEME ĐỒNG BỘ CHÍNH XÁC
def get_lip_sync_mouth(t_sec, speaker_filter):
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

# GHÉP NHÂN VẬT VÀ LƯU VÀO CACHE
def assemble_character(base_type, eye_state, mouth_viseme, pupil_offset=(0, 0)):
    canvas = Image.new("RGBA", (600, 600), (0, 0, 0, 0))
    base = base_red if base_type == "red" else base_blue
    canvas.alpha_composite(base, (0, 0))
    canvas.alpha_composite(blush_img, (0, 0))
    
    eye_img = eyes_sprites.get(eye_state, eyes_sprites["normal"])
    if pupil_offset != (0, 0) and eye_state in ["normal", "wide"]:
        dx, dy = pupil_offset
        eye_shifted = Image.new("RGBA", (600, 600), (0, 0, 0, 0))
        eye_shifted.alpha_composite(eye_img, (int(dx), int(dy)))
        canvas.alpha_composite(eye_shifted, (0, 0))
    else:
        canvas.alpha_composite(eye_img, (0, 0))
        
    m_img = mouth_sprites.get(mouth_viseme, mouth_sprites["X"])
    canvas.alpha_composite(m_img, (0, 0))
    return canvas

char_cache = {}
def get_cached_character(base_type, eye_state, mouth_viseme, pupil_offset=(0, 0)):
    k = (base_type, eye_state, mouth_viseme, pupil_offset)
    if k not in char_cache:
        char_cache[k] = assemble_character(base_type, eye_state, mouth_viseme, pupil_offset)
    return char_cache[k]

# TRÍCH XUẤT TIMELINE SỰ KIỆN TỪ MANIFEST
ev_01 = event_map["01_male_hello"]
ev_02 = event_map["02_female_ready"]
ev_03 = event_map["03_male_look"]
ev_04 = event_map["04_boy_ball"]
ev_05 = event_map["05_female_say_ball"]
ev_06 = event_map["06_girl_ball"]
ev_07 = event_map["07_male_card_ball"]
ev_08 = event_map["08_female_what_color"]
ev_09 = event_map["09_boy_im_red"]
ev_10 = event_map["10_male_red_apple"]
ev_11 = event_map["11_girl_red"]
ev_12 = event_map["12_female_card_red"]
ev_13 = event_map["13_male_someone_rolling"]
ev_14 = event_map["14_girl_im_blue"]
ev_15 = event_map["15_boy_hello_blue"]
ev_16 = event_map["16_female_red_and_blue"]
ev_17 = event_map["17_male_say_blue"]
ev_18 = event_map["18_both_blue"]
ev_19 = event_map["19_female_what_can_do"]
ev_20 = event_map["20_boy_watch_roll"]
ev_21 = event_map["21_girl_i_roll_too"]
ev_22 = event_map["22_male_say_roll"]
ev_23 = event_map["23_both_roll"]
ev_24 = event_map["24_female_flash_intro"]
ev_25 = event_map["25_male_card_ball_flash"]
ev_26 = event_map["26_female_card_red_flash"]
ev_27 = event_map["27_male_card_blue_flash"]
ev_28 = event_map["28_female_card_roll_flash"]
ev_29 = event_map["29_boy_we_did_it"]
ev_30 = event_map["30_girl_hooray"]
ev_31 = event_map["31_female_praise"]
ev_32 = event_map["32_male_goodbye"]

# Chuyển đổi sang giây
t_m1_start = ev_01["start_ms"] / 1000.0
t_m2_fall = (ev_03["end_ms"] + 200.0) / 1000.0
t_m2_boy_talk = ev_04["start_ms"] / 1000.0
t_m2_card_ball = (ev_07["start_ms"] - 150.0) / 1000.0
t_m3_red_ask = ev_08["start_ms"] / 1000.0
t_m3_boy_red = ev_09["start_ms"] / 1000.0
t_m3_card_red = (ev_12["start_ms"] - 150.0) / 1000.0
t_m4_blue_come = ev_13["start_ms"] / 1000.0
t_m4_blue_bump = (ev_14["end_ms"] - 500.0) / 1000.0
t_m4_card_blue = (ev_18["start_ms"] - 150.0) / 1000.0
t_m5_roll_prompt = ev_19["start_ms"] / 1000.0
t_m5_roll_start = ev_20["start_ms"] / 1000.0
t_m5_card_roll = (ev_23["start_ms"] - 150.0) / 1000.0
t_m6_flash_intro = ev_24["start_ms"] / 1000.0
t_m6_flash_ball = ev_25["start_ms"] / 1000.0
t_m6_flash_red = ev_26["start_ms"] / 1000.0
t_m6_flash_blue = ev_27["start_ms"] / 1000.0
t_m6_flash_roll = ev_28["start_ms"] / 1000.0
t_m6_praise = ev_29["start_ms"] / 1000.0

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
        is_ground = (dt < 0.04 * dur)
    elif norm_t < 0.25:
        scale_x = 0.86
        scale_y = 1.22
        cy = floor_y - (base_d * scale_y) / 2.0 - h_bounce
        eye_state = "wide"
        is_ground = False
    elif norm_t > 0.75:
        scale_x = 0.90
        scale_y = 1.15
        cy = floor_y - (base_d * scale_y) / 2.0 - h_bounce
        eye_state = "normal"
        is_ground = False
    else:
        scale_x = 1.0
        scale_y = 1.0
        cy = floor_y - base_d / 2.0 - h_bounce
        eye_state = "wide"
        is_ground = False
    return cy, scale_x, scale_y, eye_state, is_ground

def render_frame(t, frame_idx):
    img = Image.new("RGBA", (1920, 1080), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # 1. Đàn bong bóng nhẹ nhàng
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

    show_red = False
    show_blue = False
    red_x, red_y = 960, 540
    red_scale_x, red_scale_y = 1.0, 1.0
    red_angle = 0
    red_eye = "normal"
    red_mouth = get_lip_sync_mouth(t, "leo_red")
    red_pupil = (0, 0)
    red_floor = FLOOR_Y

    blue_x, blue_y = 960, 540
    blue_scale_x, blue_scale_y = 1.0, 1.0
    blue_angle = 0
    blue_eye = "normal"
    blue_mouth = get_lip_sync_mouth(t, "mia_blue")
    blue_pupil = (0, 0)
    blue_floor = FLOOR_Y

    card_text = None
    card_scale = 1.0
    flash_text = None
    praise_mode = False

    # --- ĐIỀU PHỐI 6 MÀN SƯ PHẠM ---
    # MÀN 1: GREETING & WARM-UP
    if t < t_m2_fall:
        show_red = False
        show_blue = False

    # MÀN 2: INTRODUCING BALL (BALL VOCABULARY)
    elif t < t_m2_boy_talk:
        show_red = True
        dur_fall = t_m2_boy_talk - t_m2_fall
        dt = t - t_m2_fall
        b1_dur = 1.10
        b2_dur = 0.90
        b3_dur = dur_fall - (b1_dur + b2_dur)
        
        red_x = 960
        if dt < b1_dur:
            red_y, red_scale_x, red_scale_y, red_eye, hit = calc_gravity_bounce(dt, 0, b1_dur, 480, FLOOR_Y, 320)
            if hit:
                spawn_ripple(960, FLOOR_Y)
                spawn_particles(960, FLOOR_Y, count=3)
        elif dt < b1_dur + b2_dur:
            red_y, red_scale_x, red_scale_y, red_eye, hit = calc_gravity_bounce(dt, b1_dur, b1_dur + b2_dur, 260, FLOOR_Y, 320)
            if hit:
                spawn_ripple(960, FLOOR_Y)
                spawn_particles(960, FLOOR_Y, count=2)
        else:
            red_y, red_scale_x, red_scale_y, red_eye, hit = calc_gravity_bounce(dt, b1_dur + b2_dur, dur_fall, 120, FLOOR_Y, 320)
            if hit:
                spawn_ripple(960, FLOOR_Y)
    elif t < t_m2_card_ball:
        show_red = True
        red_x = 960
        bounce_sub = abs(math.sin((t - t_m2_boy_talk) * 3.5))
        red_y = FLOOR_Y - 160 - 75 * bounce_sub
        red_eye = "normal" if red_mouth != "X" else "wide"
        if bounce_sub < 0.1:
            red_scale_x, red_scale_y = 1.18, 0.85
        elif bounce_sub > 0.8:
            red_scale_x, red_scale_y = 0.92, 1.10
    elif t < t_m3_red_ask:
        # Thẻ chữ BALL pop-in
        show_red = True
        red_floor = 480
        red_x = 960
        red_y = 340 - 45 * abs(math.sin((t - t_m2_card_ball) * 4.0))
        red_eye = "wink" if red_mouth == "X" else "normal"
        red_pupil = (0, 10)
        
        card_text = "BALL"
        dt = t - t_m2_card_ball
        if dt < 0.35:
            card_scale = 0.2 + 0.95 * (dt / 0.35)
        elif dt < 0.5:
            card_scale = 1.15 - 0.15 * ((dt - 0.35) / 0.15)
        else:
            card_scale = 1.0 + 0.025 * math.sin((t - t_m2_card_ball - 0.5) * 4.0)

    # MÀN 3: COLOR IDENTIFICATION (RED VOCABULARY)
    elif t < t_m3_card_red:
        show_red = True
        red_floor = FLOOR_Y
        red_x = 960
        dt_red = t - t_m3_red_ask
        sway = math.sin(dt_red * 3.0)
        red_x = 960 + 50 * sway
        red_y = FLOOR_Y - 160
        red_angle = sway * 8.0
        red_eye = "normal" if red_mouth != "X" else "wink"
    elif t < t_m4_blue_come:
        # Thẻ chữ RED pop-in
        show_red = True
        red_floor = 480
        red_x = 960
        red_y = 340 - 45 * abs(math.sin((t - t_m3_card_red) * 4.0))
        red_eye = "normal"
        red_pupil = (0, 10)
        
        card_text = "RED"
        dt = t - t_m3_card_red
        if dt < 0.35:
            card_scale = 0.2 + 0.95 * (dt / 0.35)
        elif dt < 0.5:
            card_scale = 1.15 - 0.15 * ((dt - 0.35) / 0.15)
        else:
            card_scale = 1.0 + 0.025 * math.sin((t - t_m3_card_red - 0.5) * 4.0)

    # MÀN 4: CONTRAST & FRIENDSHIP (BLUE VOCABULARY)
    elif t < t_m4_blue_bump:
        show_red = True
        red_floor = FLOOR_Y
        red_x = 1200
        red_y = FLOOR_Y - 160
        red_eye = "wide"
        red_pupil = (-14, 0)
        
        show_blue = True
        blue_floor = FLOOR_Y
        prog = min(1.0, (t - t_m4_blue_come) / (t_m4_blue_bump - t_m4_blue_come))
        blue_x = -160 + (760 - (-160)) * prog
        blue_y = FLOOR_Y - 145
        blue_angle = ((blue_x - (-160)) / 145.0) * (180 / math.pi)
        blue_eye = "normal"
        blue_pupil = (12, 0)
    elif t < t_m4_card_blue:
        # Cụng đầu BUMP và nảy ra cười
        show_red = True
        show_blue = True
        red_floor = FLOOR_Y
        blue_floor = FLOOR_Y
        dt_bump = t - t_m4_blue_bump
        if dt_bump < 0.25:
            # Va chạm đàn hồi ép dẹp ngang
            red_x = 1040
            blue_x = 880
            red_y = FLOOR_Y - 160
            blue_y = FLOOR_Y - 145
            red_scale_x, red_scale_y = 0.72, 1.25
            blue_scale_x, blue_scale_y = 0.72, 1.25
            red_eye = "closed_happy"
            blue_eye = "closed_happy"
            spawn_particles(960, FLOOR_Y - 150, count=4, speed_mult=1.5)
            spawn_ripple(960, FLOOR_Y)
        else:
            p_reb = min(1.0, (dt_bump - 0.25) / 2.5)
            red_x = 1040 + 80 * math.sin(p_reb * math.pi)
            blue_x = 880 - 80 * math.sin(p_reb * math.pi)
            laugh_jump = 55 * abs(math.sin(p_reb * math.pi * 3))
            red_y = FLOOR_Y - 160 - laugh_jump
            blue_y = FLOOR_Y - 145 - laugh_jump
            red_eye = "normal" if red_mouth != "X" else "blink"
            blue_eye = "normal" if blue_mouth != "X" else "blink"
    elif t < t_m5_roll_prompt:
        # Thẻ chữ BLUE pop-in
        show_red = True
        show_blue = True
        red_floor = FLOOR_Y
        blue_floor = FLOOR_Y
        red_x = 1450
        blue_x = 470
        red_y = FLOOR_Y - 160 - 45 * abs(math.sin((t - t_m4_card_blue) * 4.0))
        blue_y = FLOOR_Y - 145 - 45 * abs(math.sin((t - t_m4_card_blue) * 4.0))
        red_eye = "normal"
        blue_eye = "wide"
        red_pupil = (-10, 0)
        blue_pupil = (10, 0)
        
        card_text = "BLUE"
        dt = t - t_m4_card_blue
        if dt < 0.35:
            card_scale = 0.2 + 0.95 * (dt / 0.35)
        elif dt < 0.5:
            card_scale = 1.15 - 0.15 * ((dt - 0.35) / 0.15)
        else:
            card_scale = 1.0 + 0.025 * math.sin((t - t_m4_card_blue - 0.5) * 4.0)

    # MÀN 5: PHYSICAL ACTION TPR (ROLL VOCABULARY)
    elif t < t_m5_roll_start:
        show_red = True
        show_blue = True
        red_floor = FLOOR_Y
        blue_floor = FLOOR_Y
        red_x = 1100 + 30 * math.sin((t - t_m5_roll_prompt) * 4.0)
        blue_x = 820 - 30 * math.sin((t - t_m5_roll_prompt) * 4.0)
        squat = 35 * abs(math.sin((t - t_m5_roll_prompt) * 4.0))
        red_y = FLOOR_Y - 160 + squat
        blue_y = FLOOR_Y - 145 + squat
        red_scale_x, red_scale_y = 1.12, 0.88
        blue_scale_x, blue_scale_y = 1.12, 0.88
        red_eye = "wide"
        blue_eye = "wide"
    elif t < t_m5_card_roll:
        # LĂN TRÒN QUA LẠI TOÀN MÀN HÌNH VẬT LÝ NO-SLIP ROLL
        show_red = True
        show_blue = True
        red_floor = FLOOR_Y
        blue_floor = FLOOR_Y
        roll_t = t - t_m5_roll_start
        
        red_x = 960 + 720 * math.sin(roll_t * 1.6)
        blue_x = 960 + 720 * math.sin(roll_t * 1.6 + 0.8)
        red_y = FLOOR_Y - 160
        blue_y = FLOOR_Y - 145
        
        red_angle = (red_x / 160.0) * (180.0 / math.pi)
        blue_angle = (blue_x / 145.0) * (180.0 / math.pi)
        
        red_eye = "normal" if red_mouth != "X" else "blink"
        blue_eye = "normal" if blue_mouth != "X" else "blink"
        spawn_particles(red_x, red_y + 80, count=2)
        spawn_particles(blue_x, blue_y + 80, count=2)
    elif t < t_m6_flash_intro:
        # Thẻ chữ ROLL pop-in
        show_red = True
        show_blue = True
        red_floor = FLOOR_Y
        blue_floor = FLOOR_Y
        red_x = 1350
        blue_x = 570
        red_y = FLOOR_Y - 160
        blue_y = FLOOR_Y - 145
        red_eye = "normal"
        blue_eye = "normal"
        red_pupil = (-10, 0)
        blue_pupil = (10, 0)
        
        card_text = "ROLL"
        dt = t - t_m5_card_roll
        if dt < 0.35:
            card_scale = 0.2 + 0.95 * (dt / 0.35)
        elif dt < 0.5:
            card_scale = 1.15 - 0.15 * ((dt - 0.35) / 0.15)
        else:
            card_scale = 1.0 + 0.025 * math.sin((t - t_m5_card_roll - 0.5) * 4.0)

    # MÀN 6: GLENN DOMAN BRAIN FLASHCARD & PRAISE
    elif t < t_m6_flash_ball:
        show_red = True
        show_blue = True
        red_floor = FLOOR_Y
        blue_floor = FLOOR_Y
        red_x = 1350
        blue_x = 570
        red_y = FLOOR_Y - 160
        blue_y = FLOOR_Y - 145
        red_eye = "wide"
        blue_eye = "wide"
    elif t < t_m6_flash_red:
        flash_text = "BALL"
    elif t < t_m6_flash_blue:
        flash_text = "RED"
    elif t < t_m6_flash_roll:
        flash_text = "BLUE"
    elif t < t_m6_praise:
        flash_text = "ROLL"
    else:
        # ĐẠI TIỆC CHÚC MỪNG CAN-DO
        show_red = True
        show_blue = True
        red_floor = FLOOR_Y
        blue_floor = FLOOR_Y
        red_x = 650
        blue_x = 1270
        praise_jump = abs(math.sin((t - t_m6_praise) * 4.5))
        red_y = FLOOR_Y - 160 - 200 * praise_jump
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

    # 4. Vẽ Nhân vật & Bóng đổ sàn
    def render_character_on_stage(base_type, x, y, floor_y, base_d, scale_x, scale_y, angle, eye_state, mouth_viseme, pupil_offset):
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

    # 5. Vẽ Thẻ Chữ Pop-in Glenn Doman (Font Quicksand Bo tròn thân thiện)
    if card_text:
        bbox = draw.textbbox((0, 0), card_text, font=FONT_CARD)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        
        card_img = Image.new("RGBA", (tw + 140, th + 90), (0, 0, 0, 0))
        cdraw = ImageDraw.Draw(card_img)
        cdraw.text((70 - bbox[0], 45 - bbox[1]), card_text, font=FONT_CARD, fill=DOMAN_RED)
        
        cw = int((tw + 140) * card_scale)
        ch = int((th + 90) * card_scale)
        if cw > 10 and ch > 10:
            scaled_card = card_img.resize((cw, ch), Image.Resampling.BILINEAR)
            card_pos_y = 740 if t < t_m3_red_ask else (740 if t < t_m4_blue_come else 540)
            img.alpha_composite(scaled_card, (int(960 - cw // 2), int(card_pos_y - ch // 2)))

    # 6. Vẽ Tráo Thẻ Siêu Tốc Não Phải
    if flash_text:
        bbox = draw.textbbox((0, 0), flash_text, font=FONT_FLASH)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        tx = 960 - tw // 2 - bbox[0]
        ty = 540 - th // 2 - bbox[1]
        draw.text((tx, ty), flash_text, font=FONT_FLASH, fill=DOMAN_RED)

    # 7. Vẽ Màn Chúc Mừng Can-do
    if praise_mode:
        praise_txt = "GOOD JOB, BABY!"
        bbox = draw.textbbox((0, 0), praise_txt, font=FONT_PRAISE)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        
        pulse = 1.0 + 0.05 * math.sin((t - t_m6_praise) * 8.0)
        p_canvas = Image.new("RGBA", (tw + 120, th + 70), (0, 0, 0, 0))
        pdraw = ImageDraw.Draw(p_canvas)
        pdraw.text((60 - bbox[0], 35 - bbox[1]), praise_txt, font=FONT_PRAISE, fill=DOMAN_RED)
        
        pw = int((tw + 120) * pulse)
        ph = int((th + 70) * pulse)
        scaled_praise = p_canvas.resize((pw, ph), Image.Resampling.BILINEAR)
        img.alpha_composite(scaled_praise, (int(960 - pw // 2), int(260 - ph // 2)))

    return img.convert("RGB")

def main():
    print(f"🎬 Bắt đầu Render Master Hoạt Hình Đỉnh Cao Red W06 V3...")
    print(f"   - Tiêu chuẩn: Kịch bản sư phạm DAP/Glenn Doman, 4 Giọng Mỹ, 0% Overlap, Font bo tròn, 3D Phong Shader.")
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
            print(f"Tiến độ Render Master V3: {f}/{TOTAL_FRAMES} frames ({pct:.1f}%) — {t:.1f}s / {TOTAL_DURATION:.1f}s")
            sys.stdout.flush()
            
    proc.stdin.close()
    proc.wait()
    
    if proc.returncode == 0:
        print(f"✅ Hoàn tất render Master Video V3 Thành Công: {OUT_VIDEO}")
    else:
        print(f"❌ Lỗi khi render FFmpeg! Exit code: {proc.returncode}")
        sys.exit(1)

if __name__ == "__main__":
    main()
