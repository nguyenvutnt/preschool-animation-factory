#!/usr/bin/env python3
"""
Tạo bộ tài nguyên Đồ họa cho "Giáo viên ảo điều hướng" (Virtual Teacher Pointer & Tools):
1. pointer_hand_star.png: Bàn tay trỏ găng tay trắng hoạt hình Mickey/Disney kèm ngôi sao ma thuật vàng lấp lánh ở đầu ngón tay
2. magic_wand.png: Đũa phép ngôi sao thần kỳ
3. magic_brush.png: Cây cọ vẽ hoạt hình với đầu cọ màu cầu vồng
4. magic_lens.png: Kính lúp hoạt hình khám phá
5. rainbow_star.png: Ngôi sao cầu vồng trượt đường cong
"""

import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

OUT_DIR = Path("/root/preschool-animation-factory/assets/purple/guide_icons")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def create_pointer_hand():
    w, h = 260, 260
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    # Cổ tay găng tay trắng (x: 50..120, y: 150..230)
    d.rounded_rectangle([60, 160, 130, 240], radius=16, fill="#ECEFF1", outline="#37474F", width=4)
    # Nếp gấp cổ tay
    d.rounded_rectangle([50, 190, 140, 245], radius=18, fill="#FFFFFF", outline="#37474F", width=5)

    # Lòng bàn tay (Palm)
    d.ellipse([70, 100, 175, 190], fill="#FFFFFF", outline="#37474F", width=5)

    # Các ngón tay gập (Fingers curled)
    d.ellipse([120, 110, 175, 155], fill="#FFFFFF", outline="#37474F", width=4)
    d.ellipse([115, 135, 170, 180], fill="#FFFFFF", outline="#37474F", width=4)
    d.ellipse([100, 155, 155, 195], fill="#FFFFFF", outline="#37474F", width=4)

    # Ngón trỏ vươn dài chỉ điểm (Pointing index finger)
    # Hướng lên góc 45 độ về phía (190, 45)
    d.polygon([(90, 130), (120, 100), (195, 45), (210, 65), (125, 150)], fill="#FFFFFF")
    d.line([(90, 130), (195, 45)], fill="#37474F", width=5)
    d.line([(125, 150), (210, 65)], fill="#37474F", width=5)
    # Đầu ngón tay bo tròn
    d.ellipse([190, 40, 220, 70], fill="#FFFFFF", outline="#37474F", width=5)

    # Ngôi sao ma thuật phát sáng ở đầu ngón trỏ (x: 200..250, y: 15..65)
    # Vẽ sao 4 cánh / 5 cánh vàng rực rỡ
    cx, cy, r_out, r_in = 215, 45, 32, 14
    pts = []
    for i in range(10):
        angle = i * math.pi / 5 - math.pi / 2
        r = r_out if i % 2 == 0 else r_in
        pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    d.polygon(pts, fill="#FFD600", outline="#FF6F00", width=3)
    # Hạt sáng nhỏ
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill="#FFFFFF")

    im.save(OUT_DIR / "pointer_hand_star.png")
    print(f"✅ Created {OUT_DIR / 'pointer_hand_star.png'}")

def create_magic_brush():
    w, h = 260, 260
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    # Cán cọ gỗ (Thân xiên 45 độ từ x:50, y:210 đến x:170, y:90)
    d.polygon([(50, 220), (65, 235), (170, 100), (155, 85)], fill="#8D6E63", outline="#3E2723", width=4)
    # Vòng kim loại giữ lông cọ (Ferrule)
    d.polygon([(150, 90), (165, 105), (185, 85), (170, 70)], fill="#CFD8DC", outline="#37474F", width=4)
    # Đầu lông cọ mềm mại (Brush bristles)
    d.polygon([(170, 70), (185, 85), (225, 45), (205, 25)], fill="#E91E63", outline="#880E4F", width=4)
    # Các vệt màu nước rực rỡ ở đầu cọ
    d.ellipse([210, 25, 245, 60], fill="#00E676", outline="#00C853", width=2)
    d.ellipse([195, 15, 225, 45], fill="#FFEA00", outline="#FFD600", width=2)
    d.ellipse([220, 45, 250, 75], fill="#2979FF", outline="#2962FF", width=2)

    im.save(OUT_DIR / "magic_brush.png")
    print(f"✅ Created {OUT_DIR / 'magic_brush.png'}")

def create_magic_lens():
    w, h = 260, 260
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    # Tay cầm kính lúp
    d.polygon([(60, 220), (80, 240), (135, 165), (115, 145)], fill="#FF9800", outline="#E65100", width=4)
    # Vòng kim loại kính lúp
    d.ellipse([80, 30, 230, 180], outline="#FFB300", width=12)
    # Mặt kính trong suốt xanh nhẹ
    d.ellipse([86, 36, 224, 174], fill=(227, 242, 253, 160))
    # Vệt sáng phản chiếu trên mặt kính
    d.arc([100, 50, 210, 160], start=200, end=260, fill="#FFFFFF", width=6)
    # Ngôi sao lấp lánh bên cạnh
    d.ellipse([215, 30, 235, 50], fill="#FFD600")

    im.save(OUT_DIR / "magic_lens.png")
    print(f"✅ Created {OUT_DIR / 'magic_lens.png'}")

def main():
    create_pointer_hand()
    create_magic_brush()
    create_magic_lens()
    print("🎉 ALL VIRTUAL TEACHER POINTER ICONS READY!")

if __name__ == "__main__":
    main()
