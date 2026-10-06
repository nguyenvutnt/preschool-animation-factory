#!/usr/bin/env python3
r"""
TẠO TÀI NGUYÊN ĐỒ HỌA HOẠT HÌNH KHỐI PURPLE SIÊU BẮT MẮT
1. Mascot Thỏ Tím (Purple Bunny - Pip): Thân tròn tím mộng mơ, tai thỏ nhún nhảy, má hồng đào.
2. 4 Biểu tượng địa điểm mầm non (Classroom, Library, Playground, Art Room).
3. Cánh cửa ma thuật 3D, Cầu vồng trượt, Color Splash và Confetti pháo hoa.
"""

import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

ASSETS_DIR = Path("/root/scratch/purple_w06_tiktok/assets")
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

# 1. TẠO MASCOT THỎ TÍM (PURPLE BUNNY - 600x600 RGBA)
def create_purple_bunny():
    img = Image.new("RGBA", (600, 600), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Tai thỏ bên trái
    draw.ellipse([170, 40, 250, 260], fill=(167, 139, 250), outline=(139, 92, 246), width=6)
    draw.ellipse([190, 70, 230, 230], fill=(244, 114, 182)) # Lòng tai hồng
    
    # Tai thỏ bên phải
    draw.ellipse([350, 40, 430, 260], fill=(167, 139, 250), outline=(139, 92, 246), width=6)
    draw.ellipse([370, 70, 410, 230], fill=(244, 114, 182))
    
    # Đầu thỏ tròn trịa (Phong Shader Ray-Casting 3D nhẹ)
    cx, cy, r = 300, 340, 180
    for y in range(cy - r, cy + r):
        for x in range(cx - r, cx + r):
            dx = (x - cx) / float(r)
            dy = (y - cy) / float(r)
            dist2 = dx*dx + dy*dy
            if dist2 <= 1.0:
                dz = math.sqrt(1.0 - dist2)
                # Đèn từ góc trên trái
                lx, ly, lz = -0.4, -0.6, 0.7
                l_len = math.sqrt(lx*lx + ly*ly + lz*lz)
                lx, ly, lz = lx/l_len, ly/l_len, lz/l_len
                diff = max(0.0, dx*lx + dy*ly + dz*lz)
                
                # Specular
                rx = 2 * diff * dx - lx
                ry = 2 * diff * dy - ly
                rz = 2 * diff * dz - lz
                spec = max(0.0, rz) ** 14
                
                # Base Purple color: #A78BFA -> #7C3AED
                cr = int(140 * (0.55 + 0.45 * diff) + 255 * 0.4 * spec)
                cg = int(100 * (0.55 + 0.45 * diff) + 255 * 0.4 * spec)
                cb = int(245 * (0.55 + 0.45 * diff) + 255 * 0.4 * spec)
                cr = min(255, max(0, cr))
                cg = min(255, max(0, cg))
                cb = min(255, max(0, cb))
                img.putpixel((x, y), (cr, cg, cb, 255))
                
    # Vẽ lại draw sau pixel manipulation
    draw = ImageDraw.Draw(img)
    # Má hồng đào
    draw.ellipse([180, 360, 240, 400], fill=(251, 113, 133, 160))
    draw.ellipse([360, 360, 420, 400], fill=(251, 113, 133, 160))
    
    # Nơ cổ màu vàng nghệ rực rỡ
    draw.polygon([(260, 490), (220, 460), (220, 520)], fill=(251, 191, 36), outline=(217, 119, 6), width=3)
    draw.polygon([(340, 490), (380, 460), (380, 520)], fill=(251, 191, 36), outline=(217, 119, 6), width=3)
    draw.ellipse([285, 475, 315, 505], fill=(245, 158, 11))
    
    img.save(ASSETS_DIR / "bunny_base.png")
    print("Created bunny_base.png")

# 2. TẠO CÁC MẮT VÀ MIỆNG CHO THỎ
def create_bunny_faces():
    # Mắt to tròn long lanh
    eyes_normal = Image.new("RGBA", (600, 600), (0, 0, 0, 0))
    d = ImageDraw.Draw(eyes_normal)
    # Mắt trái
    d.ellipse([225, 290, 275, 350], fill=(30, 27, 75))
    d.ellipse([235, 298, 253, 318], fill=(255, 255, 255))
    d.ellipse([255, 328, 267, 340], fill=(255, 255, 255))
    # Mắt phải
    d.ellipse([325, 290, 375, 350], fill=(30, 27, 75))
    d.ellipse([335, 298, 353, 318], fill=(255, 255, 255))
    d.ellipse([355, 328, 367, 340], fill=(255, 255, 255))
    eyes_normal.save(ASSETS_DIR / "bunny_eyes_normal.png")
    
    # Mắt nháy tinh nghịch
    eyes_wink = Image.new("RGBA", (600, 600), (0, 0, 0, 0))
    d = ImageDraw.Draw(eyes_wink)
    # Mắt trái mở
    d.ellipse([225, 290, 275, 350], fill=(30, 27, 75))
    d.ellipse([235, 298, 253, 318], fill=(255, 255, 255))
    # Mắt phải nháy
    d.arc([325, 305, 375, 335], start=0, end=180, fill=(30, 27, 75), width=7)
    eyes_wink.save(ASSETS_DIR / "bunny_eyes_wink.png")

# 3. TẠO CÁNH CỬA MA THUẬT (MAGIC DOOR - 400x550 RGBA)
def create_magic_door():
    img = Image.new("RGBA", (400, 550), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Khung cửa
    draw.rounded_rectangle([20, 20, 380, 530], radius=40, fill=(245, 158, 11), outline=(217, 119, 6), width=8)
    # Cánh cửa gỗ tím pastel
    draw.rounded_rectangle([45, 45, 355, 510], radius=30, fill=(192, 132, 252), outline=(147, 51, 234), width=6)
    # Ô cửa sổ kính phát sáng ngôi sao
    draw.rounded_rectangle([75, 80, 325, 240], radius=20, fill=(254, 240, 138), outline=(234, 179, 8), width=4)
    # Núm cửa vàng bóng loáng
    draw.ellipse([80, 280, 115, 315], fill=(253, 224, 71), outline=(161, 98, 7), width=3)
    img.save(ASSETS_DIR / "magic_door.png")
    print("Created magic_door.png")

# 4. TẠO 4 BIỂU TƯỢNG ĐỊA ĐIỂM HOẠT HÌNH RỰC RỠ (450x450 RGBA)
def create_location_badges():
    # 1. CLASSROOM (Bảng đen, phấn, bàn ghế, bút chì màu)
    im_class = Image.new("RGBA", (450, 450), (0, 0, 0, 0))
    d = ImageDraw.Draw(im_class)
    d.ellipse([15, 15, 435, 435], fill=(238, 242, 255), outline=(99, 102, 241), width=10)
    # Bảng xanh
    d.rounded_rectangle([75, 90, 375, 270], radius=15, fill=(16, 185, 129), outline=(180, 83, 9), width=8)
    # Chữ ABC và 123 trên bảng
    d.line([(100, 150), (130, 210)], fill=(255, 255, 255), width=5)
    d.line([(130, 210), (160, 150)], fill=(255, 255, 255), width=5)
    d.line([(115, 180), (145, 180)], fill=(255, 255, 255), width=4)
    # Bút chì khổng lồ đặt chéo
    d.rectangle([140, 280, 310, 330], fill=(245, 158, 11), outline=(180, 83, 9), width=4)
    d.polygon([(140, 280), (90, 305), (140, 330)], fill=(254, 202, 202))
    d.polygon([(110, 295), (90, 305), (110, 315)], fill=(30, 41, 59))
    im_class.save(ASSETS_DIR / "badge_classroom.png")
    
    # 2. LIBRARY (Tủ sách và cuốn sách mở phát sáng)
    im_lib = Image.new("RGBA", (450, 450), (0, 0, 0, 0))
    d = ImageDraw.Draw(im_lib)
    d.ellipse([15, 15, 435, 435], fill=(254, 243, 199), outline=(245, 158, 11), width=10)
    # Cuốn sách mở cánh bướm
    d.polygon([(225, 220), (90, 160), (90, 300), (225, 340)], fill=(59, 130, 246), outline=(29, 78, 216), width=6)
    d.polygon([(225, 220), (360, 160), (360, 300), (225, 340)], fill=(239, 68, 68), outline=(185, 28, 28), width=6)
    d.polygon([(225, 210), (105, 150), (105, 285), (225, 325)], fill=(255, 255, 255))
    d.polygon([(225, 210), (345, 150), (345, 285), (225, 325)], fill=(255, 255, 255))
    # Ngôi sao ma thuật bay lên
    d.ellipse([215, 100, 235, 120], fill=(250, 204, 21))
    im_lib.save(ASSETS_DIR / "badge_library.png")

    # 3. PLAYGROUND (Cầu trượt và xích đu nhún nhảy)
    im_play = Image.new("RGBA", (450, 450), (0, 0, 0, 0))
    d = ImageDraw.Draw(im_play)
    d.ellipse([15, 15, 435, 435], fill=(236, 253, 245), outline=(16, 185, 129), width=10)
    # Cầu trượt cong đỏ rực
    d.arc([80, 100, 380, 400], start=160, end=330, fill=(239, 68, 68), width=32)
    # Thang trèo vàng
    d.line([(100, 150), (100, 350)], fill=(245, 158, 11), width=8)
    d.line([(100, 200), (130, 200)], fill=(245, 158, 11), width=6)
    d.line([(100, 260), (160, 260)], fill=(245, 158, 11), width=6)
    im_play.save(ASSETS_DIR / "badge_playground.png")

    # 4. ART ROOM (Bảng màu nghệ thuật và cọ vẽ khổng lồ)
    im_art = Image.new("RGBA", (450, 450), (0, 0, 0, 0))
    d = ImageDraw.Draw(im_art)
    d.ellipse([15, 15, 435, 435], fill=(253, 242, 248), outline=(236, 72, 153), width=10)
    # Bảng pha màu oval gỗ
    d.ellipse([70, 110, 380, 330], fill=(254, 215, 170), outline=(217, 119, 6), width=6)
    # Lỗ ngón tay cái
    d.ellipse([110, 190, 160, 245], fill=(253, 242, 248), outline=(217, 119, 6), width=5)
    # 4 đốm màu rực rỡ
    d.ellipse([190, 140, 230, 180], fill=(239, 68, 68))   # Đỏ
    d.ellipse([260, 150, 300, 190], fill=(59, 130, 246))  # Xanh
    d.ellipse([310, 210, 350, 250], fill=(234, 179, 8))   # Vàng
    d.ellipse([270, 270, 310, 310], fill=(168, 85, 247))  # Tím
    # Cọ vẽ chéo
    d.line([(100, 360), (350, 100)], fill=(120, 53, 15), width=12)
    d.polygon([(340, 110), (370, 80), (390, 100), (360, 130)], fill=(239, 68, 68))
    im_art.save(ASSETS_DIR / "badge_artroom.png")
    print("Created 4 location badges successfully!")

# 5. TẠO COLOR SPLASH (VẾT MÀU BẮN TUNG TÓE - 500x500 RGBA)
def create_color_splash():
    im = Image.new("RGBA", (500, 500), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    colors = [(239, 68, 68), (59, 130, 246), (234, 179, 8), (168, 85, 247), (16, 185, 129)]
    # Vẽ các giọt màu bắn tung
    d.ellipse([180, 180, 320, 320], fill=(168, 85, 247, 220))
    d.ellipse([80, 140, 150, 210], fill=(239, 68, 68, 220))
    d.ellipse([340, 100, 420, 180], fill=(59, 130, 246, 220))
    d.ellipse([330, 310, 410, 390], fill=(234, 179, 8, 220))
    d.ellipse([100, 320, 170, 390], fill=(16, 185, 129, 220))
    im.save(ASSETS_DIR / "color_splash.png")
    print("Created color_splash.png")

if __name__ == "__main__":
    create_purple_bunny()
    create_bunny_faces()
    create_magic_door()
    create_location_badges()
    create_color_splash()
    print("ALL PURPLE VISUAL ASSETS GENERATED!")
