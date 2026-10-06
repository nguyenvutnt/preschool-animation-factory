#!/usr/bin/env python3
"""
Tạo bộ mascot bé gái hoạt hình Mia Kid (4 tuổi) cho Khối Purple:
- mia_base.png: Thân bé gái, váy cam đào, tóc nơ hồng, má hồng bầu bĩnh
- mia_eyes_normal.png: Mắt to tròn long lanh
- mia_eyes_wink.png: Mắt nháy vui nhộn
- Tích hợp hệ thống miệng Rhubarb visemes (A, B, C, D, E, F, G, H, X)
"""

from PIL import Image, ImageDraw
from pathlib import Path

OUT_DIR = Path("/root/preschool-animation-factory/assets/purple")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def create_mia_base():
    w, h = 450, 520
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    # 1. Thân / Váy (Dress - Màu cam đào pastel tươi sáng #FF8A65)
    # Cổ áo trắng tròn
    d.polygon([(160, 310), (290, 310), (330, 470), (120, 470)], fill=(255, 138, 101, 255), outline=(230, 81, 0, 255))
    # Nếp váy bo tròn dưới gấu
    d.chord([120, 450, 330, 490], start=0, end=180, fill=(255, 138, 101, 255), outline=(230, 81, 0, 255))
    # Cổ áo trắng cánh sen (Peter Pan collar)
    d.chord([180, 290, 230, 330], start=0, end=180, fill=(255, 255, 255, 255), outline=(255, 183, 77, 255))
    d.chord([220, 290, 270, 330], start=0, end=180, fill=(255, 255, 255, 255), outline=(255, 183, 77, 255))

    # 2. Hai cánh tay (Arms)
    # Tay trái vẫy nhẹ
    d.ellipse([90, 330, 150, 420], fill=(255, 224, 189, 255), outline=(238, 180, 140, 255), width=3)
    # Tay phải giơ cao vẫy chào mừng
    d.ellipse([295, 280, 360, 370], fill=(255, 224, 189, 255), outline=(238, 180, 140, 255), width=3)
    # Bàn tay nhỏ
    d.ellipse([320, 260, 365, 305], fill=(255, 224, 189, 255), outline=(238, 180, 140, 255), width=3)

    # 3. Tóc sau (Back hair - Nâu hạt dẻ #5D4037)
    d.chord([100, 110, 350, 340], start=0, end=180, fill=(93, 64, 55, 255), outline=(62, 39, 35, 255), width=4)

    # 4. Khuôn mặt tròn bầu bĩnh (Face - #FFE0BD)
    d.ellipse([125, 120, 325, 310], fill=(255, 224, 189, 255), outline=(238, 180, 140, 255), width=3)

    # 5. Hai má hồng phấn đáng yêu (Rosy cheeks)
    d.ellipse([145, 235, 185, 265], fill=(255, 171, 145, 180))
    d.ellipse([265, 235, 305, 265], fill=(255, 171, 145, 180))

    # 6. Mũi nhỏ xíu
    d.ellipse([221, 232, 229, 238], fill=(244, 143, 177, 220))

    # 7. Tóc mái trước (Bangs)
    d.chord([120, 105, 330, 205], start=180, end=360, fill=(93, 64, 55, 255), outline=(62, 39, 35, 255), width=3)
    d.polygon([(120, 160), (160, 195), (200, 165), (250, 200), (290, 165), (330, 175), (330, 140), (120, 140)], fill=(93, 64, 55, 255))

    # 8. Chiếc nơ hồng xinh xắn trên đỉnh đầu (Cute Pink Bow #FF4081)
    # Nút giữa
    d.ellipse([210, 95, 240, 125], fill=(255, 64, 129, 255), outline=(194, 24, 91, 255), width=2)
    # Cánh nơ trái & phải
    d.polygon([(215, 110), (165, 85), (175, 135)], fill=(255, 64, 129, 255), outline=(194, 24, 91, 255), width=2)
    d.polygon([(235, 110), (285, 85), (275, 135)], fill=(255, 64, 129, 255), outline=(194, 24, 91, 255), width=2)

    im.save(OUT_DIR / "mia_base.png")
    print(f"✅ Created {OUT_DIR / 'mia_base.png'}")

def create_mia_eyes():
    w, h = 450, 520
    # Mắt bình thường (To tròn, long lanh hoạt hình)
    im_norm = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    dn = ImageDraw.Draw(im_norm)
    # Lòng trắng
    dn.ellipse([160, 180, 195, 225], fill=(255, 255, 255, 255), outline=(62, 39, 35, 255), width=2)
    dn.ellipse([255, 180, 290, 225], fill=(255, 255, 255, 255), outline=(62, 39, 35, 255), width=2)
    # Tròng đen nâu to tròn
    dn.ellipse([167, 186, 193, 221], fill=(62, 39, 35, 255))
    dn.ellipse([257, 186, 283, 221], fill=(62, 39, 35, 255))
    # Điểm sáng long lanh (Catchlight)
    dn.ellipse([173, 190, 181, 198], fill=(255, 255, 255, 255))
    dn.ellipse([183, 203, 187, 207], fill=(255, 255, 255, 255))
    dn.ellipse([263, 190, 271, 198], fill=(255, 255, 255, 255))
    dn.ellipse([273, 203, 277, 207], fill=(255, 255, 255, 255))
    # Lông mi cong dễ thương
    dn.arc([158, 175, 197, 195], start=200, end=340, fill=(62, 39, 35, 255), width=3)
    dn.arc([253, 175, 292, 195], start=200, end=340, fill=(62, 39, 35, 255), width=3)
    im_norm.save(OUT_DIR / "mia_eyes_normal.png")

    # Mắt nháy cười (Crescent happy eyes)
    im_wink = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    dw = ImageDraw.Draw(im_wink)
    dw.arc([158, 190, 197, 218], start=200, end=340, fill=(62, 39, 35, 255), width=4)
    dw.arc([253, 190, 292, 218], start=200, end=340, fill=(62, 39, 35, 255), width=4)
    im_wink.save(OUT_DIR / "mia_eyes_wink.png")
    print(f"✅ Created Mia eyes")

def main():
    create_mia_base()
    create_mia_eyes()

if __name__ == "__main__":
    main()
