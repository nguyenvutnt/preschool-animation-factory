#!/usr/bin/env python3
r"""
TẠO BỘ STICKER ICONS HOẠT HÌNH NỔI 3D (STICKER CUTOUT STYLE)
Dùng kết hợp với ảnh nền thật:
  1. sticker_classroom_book.png (Cuốn sách mở thông thái + bút chì vui nhộn)
  2. sticker_library_books.png (Chồng sách truyện cổ tích rực rỡ)
  3. sticker_playground_swing.png (Xích đu và cầu trượt năng động)
  4. sticker_art_palette.png (Bảng màu nghệ thuật + cọ vẽ sơn nước)
  5. sticker_magic_sparkle.png (Cụm sao ma thuật 3D)
"""

import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

DEST = Path("/root/preschool-animation-factory/assets/purple/stickers")
DEST.mkdir(parents=True, exist_ok=True)

def create_white_outline(img_rgba, outline_width=12):
    """Tạo viền trắng dày kiểu Sticker viền nổi (Die-cut sticker)."""
    alpha = img_rgba.getchannel("A")
    # Giãn nở alpha mask
    dilated = alpha.filter(ImageFilter.MaxFilter(outline_width * 2 + 1))
    
    # Tạo nền trắng viền
    outline_img = Image.new("RGBA", img_rgba.size, (255, 255, 255, 0))
    outline_draw = ImageDraw.Draw(outline_img)
    outline_draw.bitmap((0, 0), dilated, fill=(255, 255, 255, 255))
    
    # Bóng đổ mềm dưới sticker (Drop shadow)
    shadow_img = Image.new("RGBA", img_rgba.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_img)
    shadow_draw.bitmap((0, 8), dilated, fill=(0, 0, 0, 100))
    shadow_img = shadow_img.filter(ImageFilter.GaussianBlur(6))
    
    # Ghép: Shadow -> Outline trắng -> Hình gốc
    result = Image.new("RGBA", img_rgba.size, (0, 0, 0, 0))
    result.alpha_composite(shadow_img)
    result.alpha_composite(outline_img)
    result.alpha_composite(img_rgba)
    return result

def make_classroom_book():
    size = (500, 500)
    canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(canvas)
    
    # Bìa sách xanh ngọc & vàng
    d.polygon([(80, 200), (250, 230), (250, 420), (80, 390)], fill="#0284C7")
    d.polygon([(420, 200), (250, 230), (250, 420), (420, 390)], fill="#0369A1")
    
    # Trang sách trắng uốn cong
    d.polygon([(100, 180), (250, 210), (250, 380), (100, 350)], fill="#FFFFFF")
    d.polygon([(400, 180), (250, 210), (250, 380), (400, 350)], fill="#F8FAFC")
    
    # Dòng chữ minh hoạ cầu vồng trên sách
    for y in [240, 270, 300, 330]:
        d.line([(120, y), (230, y + 20)], fill="#38BDF8", width=8)
        d.line([(270, y + 20), (380, y)], fill="#F43F5E", width=8)
        
    # Bút chì hoạt hình đứng nghiêng
    d.polygon([(300, 80), (350, 130), (220, 260), (170, 210)], fill="#FBBF24")
    # Ngòi bút
    d.polygon([(170, 210), (220, 260), (140, 290)], fill="#FDE68A")
    d.polygon([(140, 290), (155, 275), (145, 265)], fill="#1E293B")
    # Tẩy hồng
    d.polygon([(300, 80), (350, 130), (370, 110), (320, 60)], fill="#F43F5E")
    
    # Mắt cười cho bút chì
    d.ellipse((240, 150, 255, 165), fill="#0F172A")
    d.ellipse((270, 175, 285, 190), fill="#0F172A")
    
    out = create_white_outline(canvas, 14)
    out.save(DEST / "sticker_book.png")
    print("Created sticker_book.png")

def make_library_books():
    size = (500, 500)
    canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(canvas)
    
    # Chồng 3 cuốn sách rực rỡ
    # Sách 1: Đỏ
    d.rounded_rectangle([80, 340, 420, 420], radius=15, fill="#EF4444")
    d.rounded_rectangle([90, 355, 410, 405], radius=10, fill="#FEF08A")
    d.line([(140, 340), (140, 420)], fill="#B91C1C", width=12)
    
    # Sách 2: Xanh dương
    d.rounded_rectangle([100, 260, 400, 335], radius=15, fill="#3B82F6")
    d.rounded_rectangle([110, 275, 390, 320], radius=10, fill="#FFFFFF")
    d.line([(160, 260), (160, 335)], fill="#1D4ED8", width=12)
    
    # Sách 3: Vàng cam
    d.rounded_rectangle([130, 180, 370, 255], radius=15, fill="#F59E0B")
    d.rounded_rectangle([140, 195, 360, 240], radius=10, fill="#FEF3C7")
    d.line([(180, 180), (180, 255)], fill="#B45309", width=12)
    
    # Kính lúp hoạt hình khám phá
    d.ellipse((280, 60, 400, 180), outline="#8B5CF6", width=22)
    d.ellipse((295, 75, 385, 165), fill="#E0E7FF")
    # Cán kính lúp
    d.line([(310, 165), (240, 235)], fill="#D97706", width=24)
    # Tia sáng loé trên kính
    d.arc((310, 85, 370, 145), start=210, end=300, fill="#FFFFFF", width=8)
    
    out = create_white_outline(canvas, 14)
    out.save(DEST / "sticker_library.png")
    print("Created sticker_library.png")

def make_playground_fun():
    size = (500, 500)
    canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(canvas)
    
    # Cầu trượt xoắn sắc màu
    # Thang leo
    d.line([(100, 150), (100, 420)], fill="#3B82F6", width=16)
    d.line([(150, 180), (150, 420)], fill="#3B82F6", width=16)
    for y in [220, 270, 320, 370]:
        d.line([(100, y), (150, y + 20)], fill="#F59E0B", width=12)
        
    # Máng trượt cong màu đỏ & vàng
    d.arc([130, 120, 430, 420], start=180, end=360, fill="#EF4444", width=36)
    # Lòng máng trượt
    d.arc([135, 125, 425, 415], start=180, end=360, fill="#FBBF24", width=20)
    
    # Quả bóng thể thao sọc màu
    d.ellipse((340, 320, 440, 420), fill="#10B981")
    d.arc((340, 320, 440, 420), start=30, end=210, fill="#FFFFFF", width=10)
    d.arc((340, 320, 440, 420), start=120, end=300, fill="#FBBF24", width=10)
    
    out = create_white_outline(canvas, 14)
    out.save(DEST / "sticker_playground.png")
    print("Created sticker_playground.png")

def make_art_palette():
    size = (500, 500)
    canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(canvas)
    
    # Bảng màu gỗ hình quả thận
    d.ellipse((60, 120, 440, 420), fill="#FDE68A")
    # Lỗ xỏ ngón tay
    d.ellipse((320, 300, 390, 370), fill="#00000000")
    
    # Các vệt màu nước sặc sỡ trên bảng
    colors = ["#EF4444", "#F59E0B", "#10B981", "#3B82F6", "#8B5CF6", "#EC4899"]
    angles = [170, 210, 250, 290, 330, 370]
    for c, ang in zip(colors, angles):
        rad = math.radians(ang)
        cx = 250 + 130 * math.cos(rad)
        cy = 270 + 100 * math.sin(rad)
        d.ellipse((cx - 30, cy - 30, cx + 30, cy + 30), fill=c)
        d.ellipse((cx - 15, cy - 20, cx - 5, cy - 10), fill="#FFFFFF")
        
    # Cây cọ vẽ vắt chéo
    d.line([(100, 420), (380, 80)], fill="#854D0E", width=22)
    # Khớp kim loại cọ
    d.line([(340, 130), (380, 80)], fill="#CBD5E1", width=24)
    # Đầu lông cọ dính màu đỏ tươi
    d.polygon([(380, 80), (410, 40), (430, 70)], fill="#EF4444")
    
    out = create_white_outline(canvas, 14)
    out.save(DEST / "sticker_art.png")
    print("Created sticker_art.png")

def make_stars():
    size = (400, 400)
    canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(canvas)
    
    # Ngôi sao vàng 5 cánh hoạt hình 3D
    cx, cy, r_out, r_in = 200, 200, 150, 65
    points = []
    for i in range(10):
        r = r_out if i % 2 == 0 else r_in
        ang = math.radians(i * 36 - 90)
        points.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
        
    d.polygon(points, fill="#FBBF24")
    
    # Mặt cười dễ thương cho ngôi sao
    d.ellipse((165, 175, 185, 200), fill="#78350F")
    d.ellipse((215, 175, 235, 200), fill="#78350F")
    d.arc((175, 195, 225, 230), start=0, end=180, fill="#78350F", width=6)
    
    # Má hồng
    d.ellipse((145, 200, 165, 215), fill="#F87171")
    d.ellipse((235, 200, 255, 215), fill="#F87171")
    
    out = create_white_outline(canvas, 14)
    out.save(DEST / "sticker_star.png")
    print("Created sticker_star.png")

if __name__ == "__main__":
    make_classroom_book()
    make_library_books()
    make_playground_fun()
    make_art_palette()
    make_stars()
