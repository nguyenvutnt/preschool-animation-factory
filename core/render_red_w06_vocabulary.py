#!/usr/bin/env python3
"""ĐỘNG CƠ DỰNG CLIP TỪ VỰNG CHUẨN GLENN DOMAN CHO KHỐI RED (6–12 THÁNG) — TUẦN 6.
Quy chuẩn sư phạm:
  - Khối RED: 6 – 12 tháng tuổi.
  - Tuần 6 (W06): Chủ đề "A Familiar Ball".
  - Đúng 4 từ vựng trọng tâm: BALL, RED, BLUE, ROLL.
  - Chuẩn Glenn Doman: Nền trắng tinh khiết #FFFFFF 100%, không cảnh nền gây nhiễu, vật thể cô lập.
  - Thẻ từ Glenn Doman: Chữ đỏ rực rỡ #D63031, DejaVu Sans Bold 140pt - 160pt.
  - Hoạt hình sống động (Dynamic Physics): Bóng nảy tưng tưng (boing), bóng lăn xoay tròn (roll),
    phóng to thu nhỏ (pulse), không một giây nào bị tĩnh chết!
  - Thời lượng chuẩn: 94.0 giây (> 1 phút).
  - Âm thanh: Giọng US Motherese chuẩn phát thanh EBU R128 (-14 LUFS) + BGM thiếu nhi -25dB + SFX đa giác quan.
"""
from __future__ import annotations

import math
import subprocess
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Đường dẫn tài nguyên
RES_BALL_REAL = Path("/root/scratch/ball_real_transparent.png")
RES_BALL_RED = Path("/root/scratch/bong_do_transparent.png")
RES_BALL_BLUE = Path("/root/scratch/bong_xanh_duong_transparent.png")
AUDIO_FILE = Path("/root/scratch/red_w06_audio/master_audio_norm.mp3")
OUT_VIDEO = Path("/root/preschool-animation-factory/demo_products/demo_W06_Red_Vocabulary_GlennDoman.mp4")

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_CARD = ImageFont.truetype(FONT_PATH, 140)
FONT_FLASH = ImageFont.truetype(FONT_PATH, 160)
FONT_PRAISE = ImageFont.truetype(FONT_PATH, 120)

DOMAN_RED = (214, 48, 49)  # #D63031
PURE_WHITE = (255, 255, 255)

FPS = 30
TOTAL_DURATION = 94.0
TOTAL_FRAMES = int(TOTAL_DURATION * FPS)

def load_assets():
    ball_real = Image.open(RES_BALL_REAL).convert("RGBA")
    ball_red = Image.open(RES_BALL_RED).convert("RGBA")
    ball_blue = Image.open(RES_BALL_BLUE).convert("RGBA")
    return ball_real, ball_red, ball_blue

def draw_shadow(draw, cx, ground_y, current_y, base_w=340, base_h=55):
    """Vẽ bóng đổ vật lý mềm mại dưới chân quả bóng."""
    dist = max(0, ground_y - current_y)
    # Càng lên cao bóng càng to và mờ
    factor = 1.0 / (1.0 + dist / 300.0)
    w = base_w * (1.2 - 0.2 * factor)
    h = base_h * (1.2 - 0.2 * factor)
    alpha = int(140 * factor)
    if alpha > 10:
        box = [cx - w/2, ground_y + 120 - h/2, cx + w/2, ground_y + 120 + h/2]
        draw.ellipse(box, fill=(230, 230, 230))

def draw_centered_text(draw, text, font, cx, cy, color=DOMAN_RED, scale=1.0):
    """Vẽ thẻ chữ Glenn Doman căn giữa hoàn hảo với hiệu ứng phóng to nếu có."""
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    
    if abs(scale - 1.0) > 0.02:
        # Render text to temp image to scale smoothly
        pad = 40
        txt_img = Image.new("RGBA", (tw + pad * 2, th + pad * 2), (255, 255, 255, 0))
        t_draw = ImageDraw.Draw(txt_img)
        t_draw.text((pad - bbox[0], pad - bbox[1]), text, font=font, fill=color)
        new_w = max(10, int(txt_img.width * scale))
        new_h = max(10, int(txt_img.height * scale))
        resized = txt_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        return resized, (int(cx - new_w / 2), int(cy - new_h / 2))
    else:
        x = cx - tw / 2 - bbox[0]
        y = cy - th / 2 - bbox[1]
        draw.text((x, y), text, font=font, fill=color)
        return None, None

def render_frame(frame_idx: int, ball_real, ball_red, ball_blue) -> Image.Image:
    t = frame_idx / float(FPS)
    canvas = Image.new("RGBA", (1920, 1080), PURE_WHITE)
    draw = ImageDraw.Draw(canvas)
    
    # -------------------------------------------------------------
    # 1. SCENE 1: INTRO (0.0s - 8.0s)
    # -------------------------------------------------------------
    if t < 8.0:
        # Quả bóng nhỏ chào bé ở trên
        small_ball = ball_red.resize((260, 260), Image.Resampling.LANCZOS)
        angle = 8.0 * math.sin(2 * math.pi * t * 1.5)
        rot_ball = small_ball.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
        bx = 960 - rot_ball.width // 2
        by = 280 - rot_ball.height // 2
        canvas.alpha_composite(rot_ball, (bx, by))
        
        # Chữ "LOOK!" ở giữa
        scale = 1.0 + 0.05 * math.sin(2 * math.pi * t * 1.2)
        txt_overlay, pos = draw_centered_text(draw, "LOOK!", FONT_FLASH, 960, 680, DOMAN_RED, scale=scale)
        if txt_overlay:
            canvas.alpha_composite(txt_overlay, pos)

    # -------------------------------------------------------------
    # 2. SCENE 2: TỪ VỰNG 1 — BALL (8.0s - 26.5s)
    # -------------------------------------------------------------
    elif t < 26.5:
        st = t - 8.0
        ground_y = 420
        ball_sz = 440
        
        # Bouncing physics
        if st < 0.8:
            # Drop from top
            progress = st / 0.8
            cy = -200 + (ground_y - (-200)) * (progress ** 2)
            squish_x, squish_y = 0.95, 1.08
        elif st < 1.4:
            # Bounce 1 (up to 180 and down)
            prog = (st - 0.8) / 0.6
            cy = ground_y - 240 * math.sin(math.pi * prog)
            squish_x, squish_y = 1.0, 1.0
        elif st < 1.9:
            # Bounce 2 (up to 300 and down)
            prog = (st - 1.4) / 0.5
            cy = ground_y - 120 * math.sin(math.pi * prog)
            squish_x, squish_y = 1.0, 1.0
        elif st < 2.3:
            # Bounce 3 (small settling)
            prog = (st - 1.9) / 0.4
            cy = ground_y - 40 * math.sin(math.pi * prog)
            squish_x, squish_y = 1.0, 1.0
        else:
            # Idle breathing pulse
            cy = ground_y
            squish_x = 1.0 + 0.03 * math.sin(2 * math.pi * (st - 2.3) * 1.0)
            squish_y = 1.0 + 0.03 * math.sin(2 * math.pi * (st - 2.3) * 1.0)
            
        # At 19.5s (st = 11.5s): joyful hop!
        if 11.0 <= st <= 13.0:
            hop_prog = (st - 11.0) / 2.0
            cy -= 160 * math.sin(math.pi * hop_prog)
            
        draw_shadow(draw, 960, ground_y, cy, base_w=360)
        
        # Render ball sprite
        bw = int(ball_sz * squish_x)
        bh = int(ball_sz * squish_y)
        scaled_b = ball_real.resize((bw, bh), Image.Resampling.LANCZOS)
        bx = int(960 - bw / 2)
        by = int(cy - bh / 2)
        canvas.alpha_composite(scaled_b, (bx, by))
        
        # Glenn Doman Card: BALL
        if st >= 4.0:
            # Card pop in
            card_scale = min(1.0, (st - 4.0) * 3.5)
            if card_scale < 1.0:
                card_scale = 1.0 + 0.15 * math.sin(math.pi * card_scale)
            txt_overlay, pos = draw_centered_text(draw, "BALL", FONT_CARD, 960, 840, DOMAN_RED, scale=card_scale)
            if txt_overlay:
                canvas.alpha_composite(txt_overlay, pos)

    # -------------------------------------------------------------
    # 3. SCENE 3: TỪ VỰNG 2 — RED (26.5s - 44.5s)
    # -------------------------------------------------------------
    elif t < 44.5:
        st = t - 26.5
        ground_y = 420
        ball_sz = 460
        
        # Pop zoom in
        if st < 0.6:
            prog = st / 0.6
            scale = 0.2 + 0.8 * prog + 0.12 * math.sin(math.pi * prog)
            cx = 960
            cy = ground_y
        else:
            # Rhythmic sway and bounce
            scale = 1.0
            sway_prog = (st - 0.6) * 1.0
            cx = 960 + 90 * math.sin(2 * math.pi * sway_prog * 0.5)
            cy = ground_y - 45 * abs(math.sin(2 * math.pi * sway_prog * 1.0))
            
        # At 38.0s (st = 11.5s): 3 pulses for "Red, red, red!"
        if 11.0 <= st <= 14.5:
            pulse_prog = (st - 11.0) * 1.0
            scale = 1.0 + 0.12 * abs(math.sin(math.pi * pulse_prog * 1.5))
            
        draw_shadow(draw, cx, ground_y, cy, base_w=380)
        
        bw = max(10, int(ball_sz * scale))
        bh = max(10, int(ball_sz * scale))
        scaled_b = ball_red.resize((bw, bh), Image.Resampling.LANCZOS)
        bx = int(cx - bw / 2)
        by = int(cy - bh / 2)
        canvas.alpha_composite(scaled_b, (bx, by))
        
        # Glenn Doman Card: RED
        if st >= 3.5:
            card_scale = min(1.0, (st - 3.5) * 3.5)
            if card_scale < 1.0:
                card_scale = 1.0 + 0.15 * math.sin(math.pi * card_scale)
            txt_overlay, pos = draw_centered_text(draw, "RED", FONT_CARD, 960, 840, DOMAN_RED, scale=card_scale)
            if txt_overlay:
                canvas.alpha_composite(txt_overlay, pos)

    # -------------------------------------------------------------
    # 4. SCENE 4: TỪ VỰNG 3 — BLUE (44.5s - 62.5s)
    # -------------------------------------------------------------
    elif t < 62.5:
        st = t - 44.5
        ground_y = 420
        
        # Red ball slides to left
        red_x = 960 - min(360, st * 280)
        red_y = ground_y
        draw_shadow(draw, red_x, ground_y, red_y, base_w=320)
        scaled_red = ball_red.resize((400, 400), Image.Resampling.LANCZOS)
        canvas.alpha_composite(scaled_red, (int(red_x - 200), int(red_y - 200)))
        
        # Blue ball rolls in from right
        if st < 1.0:
            blue_x = 2200
            blue_y = ground_y
            blue_rot = 0
        elif st < 3.2:
            prog = (st - 1.0) / 2.2
            # Easing out
            ease = 1.0 - (1.0 - prog) ** 2
            blue_x = 2200 - (2200 - 1320) * ease
            blue_y = ground_y
            blue_rot = -ease * 720
        else:
            blue_x = 1320
            # Playful hops between both balls
            hop_time = st - 3.2
            blue_y = ground_y - 70 * abs(math.sin(2 * math.pi * hop_time * 0.8))
            blue_rot = 0
            
        draw_shadow(draw, blue_x, ground_y, blue_y, base_w=320)
        scaled_blue = ball_blue.resize((400, 400), Image.Resampling.LANCZOS)
        if abs(blue_rot) > 1:
            scaled_blue = scaled_blue.rotate(blue_rot, resample=Image.Resampling.BICUBIC, expand=True)
        canvas.alpha_composite(scaled_blue, (int(blue_x - scaled_blue.width / 2), int(blue_y - scaled_blue.height / 2)))
        
        # Glenn Doman Card: BLUE
        if st >= 4.0:
            card_scale = min(1.0, (st - 4.0) * 3.5)
            if card_scale < 1.0:
                card_scale = 1.0 + 0.15 * math.sin(math.pi * card_scale)
            txt_overlay, pos = draw_centered_text(draw, "BLUE", FONT_CARD, 960, 840, DOMAN_RED, scale=card_scale)
            if txt_overlay:
                canvas.alpha_composite(txt_overlay, pos)

    # -------------------------------------------------------------
    # 5. SCENE 5: TỪ VỰNG 4 — ROLL (62.5s - 80.5s)
    # -------------------------------------------------------------
    elif t < 80.5:
        st = t - 62.5
        ground_y = 420
        
        if st < 4.5:
            # Phase 1: Fast cross-screen roll
            prog = st / 4.5
            red_x = 250 + 1420 * prog
            red_rot = -(prog * 1440)
            blue_x = 50 + 1420 * prog
            blue_rot = -(prog * 1440)
        elif st < 10.0:
            # Phase 2: Gentle circular roll together around center
            prog = (st - 4.5) / 5.5
            ang = 2 * math.pi * prog * 1.5
            red_x = 960 + 260 * math.cos(ang)
            red_y = ground_y + 90 * math.sin(ang)
            red_rot = -(ang * 180 / math.pi)
            blue_x = 960 + 260 * math.cos(ang + math.pi)
            blue_y = ground_y + 90 * math.sin(ang + math.pi)
            blue_rot = -(ang * 180 / math.pi)
        else:
            # Phase 3: Roll to center and stop!
            prog = min(1.0, (st - 10.0) / 3.0)
            ease = 1.0 - (1.0 - prog) ** 3
            red_x = 350 + (820 - 350) * ease
            red_y = ground_y
            red_rot = -(ease * 720)
            blue_x = 1570 - (1570 - 1100) * ease
            blue_y = ground_y
            blue_rot = (ease * 720)
            
        draw_shadow(draw, red_x, ground_y, ground_y, base_w=300)
        draw_shadow(draw, blue_x, ground_y, ground_y, base_w=300)
        
        r_ball = ball_red.resize((380, 380), Image.Resampling.LANCZOS).rotate(red_rot, resample=Image.Resampling.BICUBIC, expand=True)
        b_ball = ball_blue.resize((380, 380), Image.Resampling.LANCZOS).rotate(blue_rot, resample=Image.Resampling.BICUBIC, expand=True)
        
        canvas.alpha_composite(r_ball, (int(red_x - r_ball.width / 2), int(ground_y - r_ball.height / 2)))
        canvas.alpha_composite(b_ball, (int(blue_x - b_ball.width / 2), int(ground_y - b_ball.height / 2)))
        
        # Glenn Doman Card: ROLL
        if st >= 4.0:
            card_scale = min(1.0, (st - 4.0) * 3.5)
            if card_scale < 1.0:
                card_scale = 1.0 + 0.15 * math.sin(math.pi * card_scale)
            txt_overlay, pos = draw_centered_text(draw, "ROLL", FONT_CARD, 960, 840, DOMAN_RED, scale=card_scale)
            if txt_overlay:
                canvas.alpha_composite(txt_overlay, pos)

    # -------------------------------------------------------------
    # 6. SCENE 6: GLENN DOMAN SPEED FLASHCARDS & PRAISE (80.5s - 94.0s)
    # -------------------------------------------------------------
    else:
        st = t - 80.5
        
        # Speed flashcards: 1.5s per card
        if st < 2.0:
            # Card 1: BALL
            pulse = 1.0 + 0.06 * math.sin(math.pi * (st / 2.0))
            txt_overlay, pos = draw_centered_text(draw, "BALL", FONT_FLASH, 960, 520, DOMAN_RED, scale=pulse)
            if txt_overlay:
                canvas.alpha_composite(txt_overlay, pos)
        elif st < 4.0:
            # Card 2: RED
            sub_st = st - 2.0
            pulse = 1.0 + 0.06 * math.sin(math.pi * (sub_st / 2.0))
            txt_overlay, pos = draw_centered_text(draw, "RED", FONT_FLASH, 960, 520, DOMAN_RED, scale=pulse)
            if txt_overlay:
                canvas.alpha_composite(txt_overlay, pos)
        elif st < 6.0:
            # Card 3: BLUE
            sub_st = st - 4.0
            pulse = 1.0 + 0.06 * math.sin(math.pi * (sub_st / 2.0))
            txt_overlay, pos = draw_centered_text(draw, "BLUE", FONT_FLASH, 960, 520, DOMAN_RED, scale=pulse)
            if txt_overlay:
                canvas.alpha_composite(txt_overlay, pos)
        elif st < 8.0:
            # Card 4: ROLL
            sub_st = st - 6.0
            pulse = 1.0 + 0.06 * math.sin(math.pi * (sub_st / 2.0))
            txt_overlay, pos = draw_centered_text(draw, "ROLL", FONT_FLASH, 960, 520, DOMAN_RED, scale=pulse)
            if txt_overlay:
                canvas.alpha_composite(txt_overlay, pos)
        else:
            # Praise finale: Good job, baby!
            praise_st = st - 8.0
            ground_y = 360
            bounce_y = ground_y - 60 * abs(math.sin(2 * math.pi * praise_st * 1.5))
            
            draw_shadow(draw, 800, ground_y, bounce_y, base_w=280)
            draw_shadow(draw, 1120, ground_y, bounce_y, base_w=280)
            
            r_ball = ball_red.resize((340, 340), Image.Resampling.LANCZOS)
            b_ball = ball_blue.resize((340, 340), Image.Resampling.LANCZOS)
            canvas.alpha_composite(r_ball, (int(800 - 170), int(bounce_y - 170)))
            canvas.alpha_composite(b_ball, (int(1120 - 170), int(bounce_y - 170)))
            
            praise_scale = 1.0 + 0.04 * math.sin(2 * math.pi * praise_st * 1.2)
            txt_overlay, pos = draw_centered_text(draw, "GOOD JOB, BABY!", FONT_PRAISE, 960, 750, DOMAN_RED, scale=praise_scale)
            if txt_overlay:
                canvas.alpha_composite(txt_overlay, pos)
                
    return canvas.convert("RGB")

def main():
    print(f"Khởi động render video Glenn Doman Red W06: {TOTAL_FRAMES} frames ({TOTAL_DURATION}s @ {FPS}fps)...")
    ball_real, ball_red, ball_blue = load_assets()
    OUT_VIDEO.parent.mkdir(parents=True, exist_ok=True)
    
    # Khởi động pipe FFmpeg
    cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", "1920x1080",
        "-pix_fmt", "rgb24",
        "-r", str(FPS),
        "-i", "-",  # đọc từ STDIN
        "-i", str(AUDIO_FILE),
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "19",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        "-movflags", "+faststart",
        str(OUT_VIDEO)
    ]
    
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    
    for f in range(TOTAL_FRAMES):
        img = render_frame(f, ball_real, ball_red, ball_blue)
        proc.stdin.write(img.tobytes())
        if f % 150 == 0:
            percent = (f / TOTAL_FRAMES) * 100.0
            cur_sec = f / float(FPS)
            print(f"Tiến độ: {f}/{TOTAL_FRAMES} frames ({percent:.1f}%) — {cur_sec:.1f}s / {TOTAL_DURATION}s")
            
    proc.stdin.close()
    proc.wait()
    
    if proc.returncode == 0:
        print(f"✅ Hoàn tất render Master Glenn Doman Red W06: {OUT_VIDEO}")
    else:
        print(f"❌ Lỗi render FFmpeg: Exit code {proc.returncode}")
        sys.exit(1)

if __name__ == "__main__":
    main()
