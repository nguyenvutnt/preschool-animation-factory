#!/usr/bin/env python3
"""ĐỘNG CƠ DỰNG CLIP TỪ VỰNG HOẠT HÌNH ĐỈNH CAO CHUẨN GLENN DOMAN — RED W06 (6–12 THÁNG).

Đặc điểm sư phạm & nghệ thuật vượt bậc:
  1. Chuẩn Khối RED (6–12 tháng): Nền trắng tinh khiết #FFFFFF 100%, không rối mắt.
  2. Thẻ chữ Glenn Doman màu đỏ rực rỡ #D63031, cỡ lớn 140pt - 160pt DejaVu Sans Bold.
  3. Đúng 4 từ vựng mục tiêu tuần 6: BALL, RED, BLUE, ROLL.
  4. ĐỘNG HOẠT HÌNH SINH ĐỘNG (Lively Characters with Kawaii Faces):
     - Bóng Đỏ và Bóng Xanh là các "BẠN BÓNG" có mắt to tròn long lanh, má hồng phúng phính, miệng cười toe toét.
     - Mắt chớp chớp tự nhiên, nháy mắt tinh nghịch, mắt mở to ngạc nhiên khi bay vút lên!
     - Hiệu ứng Squash & Stretch đàn hồi cực mạnh như thạch rau câu khi chạm đất.
     - Vòng sóng nảy (Shockwave ripples) bừng nở dưới đất mỗi khi chạm sàn.
     - Vệt sao vàng lấp lánh (Sparkle Star Trail) bay theo quỹ đạo bóng.
     - Bong bóng cầu vồng trong suốt (Rainbow Bubbles) bay lơ lửng nhẹ nhàng.
     - Trò chơi Ú ÒA (Peek-a-boo) kích thích trực tiếp phản xạ nhận thức của trẻ 6-12 tháng.
  5. ÂM THANH MẸ - BÉ TƯƠNG TÁC (Motherese & Baby Giggle):
     - Giọng Mẹ dịu dàng ấm áp (Jenny) + Giọng Bé gái lí lắc cười khúc khích (Ana).
     - Hiệu ứng âm thanh hoạt hình phong phú: Boing lò xo, Slide whistle, Bump, Whoosh, Ting chuông, Vỗ tay hoan hô rộn rã.
     - Chuẩn phát thanh quốc tế EBU R128 (-14 LUFS).
  6. Thời lượng chuẩn: 95.0 giây (> 1 phút).
"""
import math
import os
import random
import subprocess
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Đường dẫn tài nguyên
SPRITE_DIR = Path("/root/scratch/engaging_sprites")
AUDIO_FILE = Path("/root/scratch/red_w06_engaging_audio/master_audio_norm.mp3")
OUT_VIDEO = Path("/root/preschool-animation-factory/demo_products/demo_W06_Red_Vocabulary_GlennDoman.mp4")

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_CARD = ImageFont.truetype(FONT_PATH, 140)
FONT_FLASH = ImageFont.truetype(FONT_PATH, 160)
FONT_PRAISE = ImageFont.truetype(FONT_PATH, 115)

DOMAN_RED = (214, 48, 49)  # #D63031
PURE_WHITE = (255, 255, 255)

FPS = 30
TOTAL_DURATION = 95.0
TOTAL_FRAMES = int(TOTAL_DURATION * FPS)

# Load sẵn sprites vào RAM
sprites = {
    "red_happy": Image.open(SPRITE_DIR / "ball_red_happy.png").convert("RGBA"),
    "red_blink": Image.open(SPRITE_DIR / "ball_red_blink.png").convert("RGBA"),
    "red_excited": Image.open(SPRITE_DIR / "ball_red_excited.png").convert("RGBA"),
    "red_wink": Image.open(SPRITE_DIR / "ball_red_wink.png").convert("RGBA"),
    "blue_happy": Image.open(SPRITE_DIR / "ball_blue_happy.png").convert("RGBA"),
    "blue_blink": Image.open(SPRITE_DIR / "ball_blue_blink.png").convert("RGBA"),
    "blue_excited": Image.open(SPRITE_DIR / "ball_blue_excited.png").convert("RGBA"),
    "star": Image.open(SPRITE_DIR / "star_sparkle.png").convert("RGBA"),
    "bubble": Image.open(SPRITE_DIR / "rainbow_bubble.png").convert("RGBA"),
}

# Khởi tạo đàn bong bóng bay lơ lửng ngẫu nhiên cố định hạt giống (reproducible seed)
random.seed(42)
bubbles_data = []
for i in range(12):
    bx = random.randint(80, 1840)
    by = random.randint(100, 1100)
    b_spd = random.uniform(1.2, 2.8)
    b_scale = random.uniform(0.5, 0.95)
    b_phase = random.uniform(0, math.pi * 2)
    bubbles_data.append([bx, by, b_spd, b_scale, b_phase])

# Danh sách hạt sao lấp lánh động
particles = []
# Danh sách vòng sóng nảy
ripples = []

def spawn_particles(x, y, count=2):
    for _ in range(count):
        vx = random.uniform(-4, 4)
        vy = random.uniform(-5, 1)
        scale = random.uniform(0.3, 0.6)
        life = random.randint(12, 20)
        particles.append([x, y, vx, vy, scale, life, life])

def spawn_ripple(x, y):
    ripples.append([x, y, 10, 6, 1.0])  # cx, cy, rx, ry, alpha

def render_frame(t, frame_idx):
    # Tạo nền trắng tinh khiết
    img = Image.new("RGBA", (1920, 1080), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # 1. Cập nhật và vẽ đàn bong bóng bay lơ lửng
    for b in bubbles_data:
        b[1] -= b[2] # Bay lên trên
        if b[1] < -120:
            b[1] = 1120
            b[0] = random.randint(80, 1840)
        bx_cur = b[0] + 25 * math.sin(t * 1.5 + b[4])
        b_size = int(120 * b[3])
        b_im = sprites["bubble"].resize((b_size, b_size), Image.Resampling.BILINEAR)
        img.alpha_composite(b_im, (int(bx_cur - b_size // 2), int(b[1] - b_size // 2)))

    # 2. Cập nhật và vẽ vòng sóng nảy dưới sàn
    global ripples
    new_ripples = []
    for r in ripples:
        cx, cy, rx, ry, alpha = r
        if alpha > 0.05:
            # Vẽ elip sóng
            overlay = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
            odraw = ImageDraw.Draw(overlay)
            alpha_int = int(alpha * 180)
            lw = max(2, int(alpha * 6))
            odraw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry],
                          outline=(100, 180, 255, alpha_int), width=lw)
            img = Image.alpha_composite(img, overlay)
            # Tăng bán kính, giảm alpha
            rx += 12
            ry += 4.5
            alpha *= 0.85
            new_ripples.append([cx, cy, rx, ry, alpha])
    ripples = new_ripples

    # Trạng thái nhân vật
    # Red ball
    show_red = False
    red_x, red_y = 960, 540
    red_scale_x, red_scale_y = 1.0, 1.0
    red_angle = 0
    red_expr = "happy"
    
    # Blue ball
    show_blue = False
    blue_x, blue_y = 960, 540
    blue_scale_x, blue_scale_y = 1.0, 1.0
    blue_angle = 0
    blue_expr = "happy"
    
    # Text card
    card_text = None
    card_scale = 1.0
    
    # Flashcard mode
    flash_text = None
    
    # Praise mode
    praise_mode = False

    # Logic kịch bản theo thời gian t (giây)
    # =========================================================================
    # MÀN 1: PEEK-A-BOO & TỪ VỰNG BALL (0.0s - 25.5s)
    # =========================================================================
    if t < 4.5:
        # 0 - 4.5s: Ú òa! Lấp ló ở mép dưới màn hình
        show_red = True
        head_peek = 80 * math.sin(t * 3.0)
        red_x = 960 + 30 * math.sin(t * 2.0)
        red_y = 1100 - max(0, head_peek)
        red_expr = "happy"
        red_angle = 5 * math.sin(t * 3.0)
        if frame_idx % 80 in range(0, 5):
            red_expr = "blink"
    elif t < 7.0:
        # 4.5s - 7.0s: Bật nhảy vút lên giữa màn hình "PEEK-A-BOO! HEHEHE!"
        show_red = True
        prog = (t - 4.5) / 2.5
        # Nhảy hình parabol vút lên cao rồi đáp nhẹ giữa màn hình
        h = math.sin(prog * math.pi)
        red_x = 960
        red_y = 1100 - (1100 - 480) * math.sin(min(1.0, prog * 1.5) * math.pi / 2)
        red_expr = "excited"
        red_scale_x = 0.85
        red_scale_y = 1.2
        spawn_particles(red_x, red_y + 100, count=3)
    elif t < 10.5:
        # 7.0s - 10.5s: Nảy 3 nhịp siêu đàn hồi boing boing boing
        show_red = True
        local_t = (t - 7.0) % 1.0  # Chu kỳ 1 giây / nhịp
        bounce_h = math.sin(local_t * math.pi)
        red_x = 960 + 80 * math.sin((t - 7.0) * math.pi * 0.7)
        ground_y = 700
        red_y = ground_y - 280 * bounce_h
        
        # Squash & Stretch
        if bounce_h < 0.08:
            red_scale_x = 1.35
            red_scale_y = 0.65
            red_expr = "blink"
            if local_t < 0.15 and frame_idx % 30 == 0:
                spawn_ripple(red_x, ground_y + 80)
        elif bounce_h > 0.8:
            red_scale_x = 0.9
            red_scale_y = 1.15
            red_expr = "excited"
        else:
            red_scale_x = 1.0
            red_scale_y = 1.0
            red_expr = "happy"
        spawn_particles(red_x, red_y + 60, count=2)
    elif t < 17.5:
        # 11.0s - 17.5s: Mẹ giới thiệu "Look! It's a BALL!". Bóng nảy nhịp nhàng đung đưa
        show_red = True
        red_x = 960 + 40 * math.sin(t * 1.8)
        red_y = 520 - 70 * abs(math.sin(t * 3.5))
        red_angle = 6 * math.sin(t * 2.0)
        red_expr = "happy"
        if frame_idx % 75 in range(0, 5):
            red_expr = "blink"
        spawn_particles(red_x, red_y + 100, count=1)
    elif t < 25.5:
        # 17.5s - 25.5s: Thẻ chữ BALL pop-in, bóng đỏ nảy vui vẻ phía trên thẻ chữ
        show_red = True
        red_x = 960
        red_y = 350 - 50 * abs(math.sin((t - 17.5) * 4.0))
        red_expr = "happy"
        if frame_idx % 80 in range(0, 5):
            red_expr = "blink"
        
        card_text = "BALL"
        # Pop-in đàn hồi
        dt = t - 17.5
        if dt < 0.35:
            card_scale = 0.2 + 0.9 * (dt / 0.35)
        elif dt < 0.5:
            card_scale = 1.1 - 0.1 * ((dt - 0.35) / 0.15)
        else:
            card_scale = 1.0 + 0.03 * math.sin((t - 18.0) * 4.0)
            
        spawn_particles(red_x + random.randint(-180, 180), 750, count=1)

    # =========================================================================
    # MÀN 2: MÀU SẮC RED (25.5s - 45.0s)
    # =========================================================================
    elif t < 29.5:
        # 25.5s - 29.5s: Mẹ hỏi màu sắc. Bóng đỏ tiến ra trung tâm, nghiêng đầu tò mò
        show_red = True
        red_x = 960
        red_y = 540 + 20 * math.sin(t * 2.5)
        red_angle = 12 * math.sin((t - 25.5) * 2.0)
        red_expr = "excited" if math.sin(t * 3.0) > 0.5 else "happy"
        if frame_idx % 70 in range(0, 5):
            red_expr = "blink"
    elif t < 33.5:
        # 29.5s - 33.5s: Bé reo "It's RED!". Bóng đỏ xoay 360 độ, nháy mắt wink!
        show_red = True
        spin_t = (t - 29.5) / 4.0
        red_x = 960
        red_y = 500 - 80 * abs(math.sin(spin_t * math.pi * 3))
        red_angle = spin_t * 360 * 2
        red_expr = "wink" if (t - 29.5) > 2.0 else "happy"
        spawn_particles(red_x, red_y, count=3)
    elif t < 39.5:
        # 33.5s - 39.5s: Điệu nhảy vui tươi "RED! Bright RED!"
        show_red = True
        red_x = 960 + 160 * math.sin((t - 33.5) * 2.8)
        red_y = 540 - 70 * abs(math.cos((t - 33.5) * 2.8))
        red_angle = 15 * math.sin((t - 33.5) * 2.8)
        red_expr = "happy"
        if frame_idx % 60 in range(0, 5):
            red_expr = "blink"
        spawn_particles(red_x, red_y + 110, count=2)
    elif t < 45.0:
        # 39.5s - 45.0s: Thẻ chữ RED pop-in, bóng đỏ nảy phía trên
        show_red = True
        red_x = 960
        red_y = 350 - 50 * abs(math.sin((t - 39.5) * 4.0))
        red_expr = "wink"
        
        card_text = "RED"
        dt = t - 39.5
        if dt < 0.35:
            card_scale = 0.2 + 0.9 * (dt / 0.35)
        elif dt < 0.5:
            card_scale = 1.1 - 0.1 * ((dt - 0.35) / 0.15)
        else:
            card_scale = 1.0 + 0.03 * math.sin((t - 40.0) * 4.0)
        spawn_particles(red_x + random.randint(-160, 160), 750, count=1)

    # =========================================================================
    # MÀN 3: BẠN MỚI BLUE (45.0s - 65.5s)
    # =========================================================================
    elif t < 49.5:
        # 45.0s - 49.5s: Mẹ gọi bạn mới. Bóng xanh từ bên trái lăn vào
        show_red = True
        red_x = 1200
        red_y = 550
        red_expr = "excited"
        red_angle = -10
        
        show_blue = True
        prog = (t - 45.0) / 4.5
        blue_x = -150 + (720 - (-150)) * min(1.0, prog)
        blue_y = 550 - 40 * abs(math.sin(prog * math.pi * 4))
        blue_angle = prog * 360 * 2
        blue_expr = "happy"
        spawn_particles(blue_x, blue_y + 90, count=2)
    elif t < 55.0:
        # 49.5s - 55.0s: Hai bạn bóng nhảy lại gần, cụng đầu BUMP! rồi cười khúc khích
        show_red = True
        show_blue = True
        dt = t - 49.5
        if dt < 2.5:
            # Tiến lại gần chạm nhau ở 960
            red_x = 1200 - (1200 - 1080) * (dt / 2.5)
            blue_x = 720 + (840 - 720) * (dt / 2.5)
            red_y = 540 - 60 * abs(math.sin(dt * 4.0))
            blue_y = 540 - 60 * abs(math.sin(dt * 4.0))
            red_expr = "happy"
            blue_expr = "happy"
        else:
            # Cụng đầu nhẹ rồi lùi ra cười
            red_x = 1080 + 40 * math.sin((dt - 2.5) * 3.0)
            blue_x = 840 - 40 * math.sin((dt - 2.5) * 3.0)
            red_y = 540 - 70 * abs(math.sin((dt - 2.5) * 5.0))
            blue_y = 540 - 70 * abs(math.sin((dt - 2.5) * 5.0))
            red_expr = "blink"
            blue_expr = "blink"
            spawn_particles(960, 520, count=3)
    elif t < 61.5:
        # 55.0s - 61.5s: Mẹ & bé reo "BLUE! Two happy balls!". Cả hai cùng nảy đồng điệu
        show_red = True
        show_blue = True
        red_x = 1150
        blue_x = 770
        bounce_sync = abs(math.sin((t - 55.0) * 3.5))
        red_y = 550 - 120 * bounce_sync
        blue_y = 550 - 120 * bounce_sync
        red_expr = "happy"
        blue_expr = "happy"
        if frame_idx % 65 in range(0, 5):
            blue_expr = "blink"
        spawn_particles(red_x, red_y + 90, count=1)
        spawn_particles(blue_x, blue_y + 90, count=1)
    elif t < 65.5:
        # 61.5s - 65.5s: Thẻ chữ BLUE pop-in, hai bóng nảy hai bên thẻ chữ
        show_red = True
        show_blue = True
        red_x = 1450
        blue_x = 470
        red_y = 540 - 60 * abs(math.sin((t - 61.5) * 4.0))
        blue_y = 540 - 60 * abs(math.sin((t - 61.5) * 4.0))
        red_expr = "happy"
        blue_expr = "excited"
        
        card_text = "BLUE"
        dt = t - 61.5
        if dt < 0.35:
            card_scale = 0.2 + 0.9 * (dt / 0.35)
        elif dt < 0.5:
            card_scale = 1.1 - 0.1 * ((dt - 0.35) / 0.15)
        else:
            card_scale = 1.0 + 0.03 * math.sin((t - 62.0) * 4.0)
        spawn_particles(960 + random.randint(-180, 180), 650, count=1)

    # =========================================================================
    # MÀN 4: HÀNH ĐỘNG ROLL (65.5s - 83.5s)
    # =========================================================================
    elif t < 69.0:
        # 65.5s - 69.0s: Chuẩn bị lăn "Can you roll?". Nhún nhảy lấy đà
        show_red = True
        show_blue = True
        red_x = 1100 + 30 * math.sin((t - 65.5) * 4.0)
        blue_x = 820 - 30 * math.sin((t - 65.5) * 4.0)
        red_y = 600 - 40 * abs(math.sin((t - 65.5) * 4.0))
        blue_y = 600 - 40 * abs(math.sin((t - 65.5) * 4.0))
        red_angle = 15 * math.sin((t - 65.5) * 4.0)
        blue_angle = -15 * math.sin((t - 65.5) * 4.0)
        red_expr = "excited"
        blue_expr = "excited"
    elif t < 81.0:
        # 69.0s - 81.0s: Lăn tròn qua lại khắp màn hình! ROLL ROLL ROLL!
        show_red = True
        show_blue = True
        roll_t = t - 69.0
        # Di chuyển ngang theo sin biên độ cực rộng (toàn màn hình 200 -> 1720)
        red_x = 960 + 720 * math.sin(roll_t * 1.6)
        blue_x = 960 + 720 * math.sin(roll_t * 1.6 + 0.7)
        ground_roll = 650
        red_y = ground_roll
        blue_y = ground_roll
        red_angle = (red_x / 300) * 360
        blue_angle = (blue_x / 280) * 360
        red_expr = "blink" if abs(math.sin(roll_t * 2.0)) > 0.8 else "happy"
        blue_expr = "blink" if abs(math.sin(roll_t * 2.0 + 1.0)) > 0.8 else "happy"
        spawn_particles(red_x, red_y + 80, count=2)
        spawn_particles(blue_x, blue_y + 80, count=2)
    elif t < 83.5:
        # 81.0s - 83.5s: Phanh dừng lại giữa màn hình, thẻ ROLL pop-in
        show_red = True
        show_blue = True
        red_x = 1350
        blue_x = 570
        red_y = 540
        blue_y = 540
        red_expr = "happy"
        blue_expr = "happy"
        
        card_text = "ROLL"
        dt = t - 81.0
        if dt < 0.35:
            card_scale = 0.2 + 0.9 * (dt / 0.35)
        elif dt < 0.5:
            card_scale = 1.1 - 0.1 * ((dt - 0.35) / 0.15)
        else:
            card_scale = 1.0 + 0.03 * math.sin((t - 81.5) * 4.0)
        spawn_particles(960 + random.randint(-180, 180), 650, count=1)

    # =========================================================================
    # MÀN 5: TRÁO THẺ NÃO PHẢI SIÊU TỐC & ĐẠI TIỆC CHÚC MỪNG (83.5s - 95.0s)
    # =========================================================================
    elif t < 85.5:
        # 83.5s - 85.5s: Thẻ BALL cực đại
        flash_text = "BALL"
    elif t < 87.0:
        # 85.5s - 87.0s: Thẻ RED cực đại
        flash_text = "RED"
    elif t < 88.5:
        # 87.0s - 88.5s: Thẻ BLUE cực đại
        flash_text = "BLUE"
    elif t < 90.0:
        # 88.5s - 90.0s: Thẻ ROLL cực đại
        flash_text = "ROLL"
    else:
        # 90.0s - 95.0s: ĐẠI TIỆC CHÚC MỪNG! Hai bạn bóng nhảy cẫng lên ăn mừng!
        show_red = True
        show_blue = True
        red_x = 650
        blue_x = 1270
        praise_jump = abs(math.sin((t - 90.0) * 4.5))
        red_y = 620 - 180 * praise_jump
        blue_y = 620 - 180 * praise_jump
        red_expr = "excited" if praise_jump > 0.4 else "happy"
        blue_expr = "excited" if praise_jump > 0.4 else "happy"
        praise_mode = True
        # Mưa sao vàng và confetti
        for _ in range(3):
            spawn_particles(random.randint(100, 1820), random.randint(100, 400), count=1)

    # 3. Cập nhật và vẽ hạt sao lấp lánh (Particles)
    global particles
    new_particles = []
    for p in particles:
        px, py, pvx, pvy, pscale, life, max_life = p
        if life > 0:
            px += pvx
            py += pvy
            pvy += 0.25 # Trọng lực nhẹ
            alpha_ratio = life / max_life
            s_size = max(10, int(100 * pscale * alpha_ratio))
            s_im = sprites["star"].resize((s_size, s_size), Image.Resampling.BILINEAR)
            
            # Gán alpha mờ dần
            s_im.putalpha(Image.eval(s_im.getchannel("A"), lambda a: int(a * alpha_ratio)))
            img.alpha_composite(s_im, (int(px - s_size // 2), int(py - s_size // 2)))
            new_particles.append([px, py, pvx, pvy, pscale, life - 1, max_life])
    particles = new_particles

    # 4. Vẽ các nhân vật bóng lên khung hình
    def draw_ball(sprite_key, x, y, base_size, scale_x, scale_y, angle):
        sp = sprites[sprite_key]
        w = int(base_size * scale_x)
        h = int(base_size * scale_y)
        if w < 10 or h < 10:
            return
        resized = sp.resize((w, h), Image.Resampling.BILINEAR)
        if angle != 0:
            resized = resized.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
        rx, ry = resized.size
        img.alpha_composite(resized, (int(x - rx // 2), int(y - ry // 2)))

    if show_red:
        draw_ball(f"red_{red_expr}", red_x, red_y, 320, red_scale_x, red_scale_y, red_angle)
    if show_blue:
        draw_ball(f"blue_{blue_expr}", blue_x, blue_y, 290, blue_scale_x, blue_scale_y, blue_angle)

    # 5. Vẽ Thẻ chữ Glenn Doman (Pop-in Card)
    if card_text:
        # Hộp thẻ chữ với font FONT_CARD (140pt)
        bbox = draw.textbbox((0, 0), card_text, font=FONT_CARD)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        
        # Tạo canvas riêng cho chữ để scale đàn hồi
        card_img = Image.new("RGBA", (tw + 120, th + 80), (0, 0, 0, 0))
        cdraw = ImageDraw.Draw(card_img)
        # Vẽ chữ đỏ Glenn Doman
        cdraw.text((60 - bbox[0], 40 - bbox[1]), card_text, font=FONT_CARD, fill=DOMAN_RED)
        
        cw = int((tw + 120) * card_scale)
        ch = int((th + 80) * card_scale)
        if cw > 10 and ch > 10:
            scaled_card = card_img.resize((cw, ch), Image.Resampling.BILINEAR)
            card_pos_y = 740 if t < 26 else (740 if t < 46 else (540 if t < 66 else 540))
            img.alpha_composite(scaled_card, (int(960 - cw // 2), int(card_pos_y - ch // 2)))

    # 6. Vẽ Tráo Thẻ Não Phải Siêu Tốc (Flashcard Mode)
    if flash_text:
        bbox = draw.textbbox((0, 0), flash_text, font=FONT_FLASH)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        tx = 960 - tw // 2 - bbox[0]
        ty = 540 - th // 2 - bbox[1]
        draw.text((tx, ty), flash_text, font=FONT_FLASH, fill=DOMAN_RED)

    # 7. Vẽ Màn Chúc Mừng (Praise Mode)
    if praise_mode:
        praise_txt = "GOOD JOB, BABY!"
        bbox = draw.textbbox((0, 0), praise_txt, font=FONT_PRAISE)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        tx = 960 - tw // 2 - bbox[0]
        ty = 260 - th // 2 - bbox[1]
        
        # Nhấp nháy hào quang vàng và chữ đỏ rực rỡ
        pulse = 1.0 + 0.05 * math.sin((t - 90.0) * 8.0)
        p_canvas = Image.new("RGBA", (tw + 100, th + 60), (0, 0, 0, 0))
        pdraw = ImageDraw.Draw(p_canvas)
        pdraw.text((50 - bbox[0], 30 - bbox[1]), praise_txt, font=FONT_PRAISE, fill=DOMAN_RED)
        
        pw = int((tw + 100) * pulse)
        ph = int((th + 60) * pulse)
        scaled_praise = p_canvas.resize((pw, ph), Image.Resampling.BILINEAR)
        img.alpha_composite(scaled_praise, (int(960 - pw // 2), int(260 - ph // 2)))

    return img.convert("RGB")

def main():
    print(f"🎬 Bắt đầu render Master Hoạt Hình Đỉnh Cao Red W06...")
    print(f"   - Tổng thời lượng: {TOTAL_DURATION}s ({TOTAL_FRAMES} frames @ {FPS}fps)")
    print(f"   - Audio Master: {AUDIO_FILE}")
    print(f"   - Video Output: {OUT_VIDEO}")
    
    OUT_VIDEO.parent.mkdir(parents=True, exist_ok=True)
    
    # FFmpeg command nhận stdin rawvideo
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", "1920x1080",
        "-pix_fmt", "rgb24",
        "-r", str(FPS),
        "-i", "-",  # Nhận từ stdin
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
        
        if f % 150 == 0:
            pct = (f / TOTAL_FRAMES) * 100
            print(f"Tiến độ: {f}/{TOTAL_FRAMES} frames ({pct:.1f}%) — {t:.1f}s / {TOTAL_DURATION}s")
            sys.stdout.flush()
            
    proc.stdin.close()
    proc.wait()
    
    if proc.returncode == 0:
        print(f"✅ Hoàn tất render Master Hoạt Hình Red W06: {OUT_VIDEO}")
    else:
        print(f"❌ Lỗi khi render FFmpeg! Exit code: {proc.returncode}")
        sys.exit(1)

if __name__ == "__main__":
    main()
