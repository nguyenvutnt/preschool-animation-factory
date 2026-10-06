# 🛡️ HỆ THỐNG AI AGENT AUDIT TOÀN TRÌNH CHUẨN QUỐC TẾ
*(Global Preschool Multi-Stage AI Audit Fleet)*

> **Tôn chỉ tối cao**: Không có bất kỳ video nào được phép phát hành ra công chúng nếu chưa vượt qua đủ **6 Cổng Kiểm Định (6-Gate Audit)** của AI Agent Giám định viên Trưởng.

---

## 1. KIẾN TRÚC 6 CỔNG KIỂM ĐỊNH (6 AUDIT GATES)

```
[1. Ý tưởng & Đề tài] ──► GATE 1: Sư phạm CEFR Pre-A1, NĐ 360/2026/NĐ-CP, COPPA, GDPR-K
            │
            ▼
[2. Kịch bản & Ngữ âm] ──► GATE 2: Zero Word Fluff, Pacing (85-105 WPM), 3s Interactive Pause
            │
            ▼
[3. Thị giác Sân khấu] ──► GATE 3: BBC CBeebies Low-Stimulation, ITU-R BT.1702, WCAG AAA (>= 7:1)
            │
            ▼
[4. Âm thanh Hậu kỳ]   ──► GATE 4: EBU R128 (-14.0 LUFS), True Peak <= -1.0 dBTP, Ducking -14dB
            │
            ▼
[5. Kỹ thuật Mã hóa]   ──► GATE 5: Broadcast Rec.709 CFR 25.0 fps, GOP 2.0s, MP4 FastStart
            │
            ▼
[6. Cổng Xuất Bản]     ──► GATE 6: Cấp chứng chỉ CERT_GLOBAL_APPROVED_<ID> & Hash SHA256
```

---

## 2. CHI TIẾT BỘ TIÊU CHUẨN KIỂM ĐỊNH TỪNG CỔNG

### GATE 1: Ý TƯỞNG & ĐỊNH VỊ SƯ PHẠM (CONCEPT & LEGAL AUDIT)
- **Chuẩn Sư phạm Quốc tế**: Bám sát khung Cambridge Young Learners (Pre-A1 Starters) và Oxford Phonics World.
- **Pháp lệnh Quản lý Giáo dục (Nghị định 360/2026/NĐ-CP)**:
  - Nghiêm cấm sử dụng các danh xưng mạo nhận ("quốc tế", "quốc gia", "số 1 Việt Nam") khi chưa được cấp phép.
  - Bảo đảm sự trong sáng của tiếng Việt và tính chuẩn xác của tiếng Anh.
- **Pháp lý Trẻ em Toàn cầu**:
  - COPPA (16 CFR Part 312): Đóng dấu Made for Kids, zero telemetry, zero PII.
  - GDPR-K: Bảo vệ quyền riêng tư trẻ em tuyệt đối.

### GATE 2: KỊCH BẢN & NGỮ ÂM (SCRIPT & LINGUISTICS AUDIT)
- **Zero Word Fluff**: Trẻ 1 - 3 tuổi tối đa 3 - 5 từ/shot; trẻ 3 - 5 tuổi tối đa 6 - 8 từ/shot.
- **Tốc độ đọc (Speech Rate)**: Bắt buộc từ **85 đến 105 WPM** (Words Per Minute).
- **Khoảng lặng tương tác (Interactive Pause)**: Bắt buộc có khoảng dừng **$\ge 3.0$ giây** để kích hoạt phản xạ tự nói của trẻ.
- **Đúng chuẩn thể loại**: Đúng chu trình của 8 thể loại (Glenn Doman tráo nhanh 1.0s, Phonics CVC Blending, Sight Words 3 câu lặp lại...).

### GATE 3: BỐ CỤC THỊ GIÁC & AN TOÀN NÃO BỘ (VISUAL ERGONOMICS AUDIT)
- **Triết lý Low-Stimulation (BBC CBeebies Standard)**:
  - Thời lượng mỗi phân cảnh $\ge 3.5$ – 5.0 giây (cấm tuyệt đối fast-cuts và jump-cuts gây quá tải dopamine).
- **Chống co giật quang học (ITU-R BT.1702)**:
  - Tần số chớp sáng $< 3\text{Hz}$, không có chuyển cảnh nhấp nháy đỏ bão hòa.
- **Sân khấu Zero-Collision**:
  - Top Visual Stage (70 – 750px): Khung ảnh minh họa.
  - Safe Buffer Zone ($\ge 140\text{px}$): Khoảng đệm an toàn tuyệt đối không để chữ đè lên hình.
  - Bottom Flashcard Bar (820 – 1080px): Thẻ chữ đỏ Glenn Doman độc lập.
- **Độ tương phản chữ (WCAG AAA)**: Tỷ lệ tương phản $\ge 7:1$.

### GATE 4: ÂM THANH PHÁT THANH TRUYỀN HÌNH (EBU R128 AUDIO AUDIT)
- **Integrated Loudness ($I$)**: **$-14.0\text{ LUFS} \pm 0.5\text{ LU}$** (Chuẩn YouTube, Spotify, Apple Podcasts, EBU R128).
- **Maximum True Peak ($TP$)**: $\le \mathbf{-1.0\text{ dBTP}}$ (Chống hiện tượng méo tiếng inter-sample clipping trên loa điện thoại/TV).
- **Loudness Range ($LRA$)**: $\le \mathbf{7.0\text{ LU}}$ (Đảm bảo biên độ âm thanh êm dịu, không có tiếng nổ lớn làm giật mình trẻ).
- **Sidechain Ducking**: Nhạc nền tự động né giọng đọc tối thiểu $\mathbf{-14\text{dB}}$.

### GATE 5: KỸ THUẬT MÃ HÓA PHÁT HÀNH (BROADCAST VIDEO ENCODING)
- **Độ phân giải**: Full HD 1920x1080 (16:9).
- **Frame Rate Mode**: Constant Frame Rate (**CFR 25.0 fps**), không rớt khung hình.
- **Không gian màu sắc**: **ITU-R BT.709** (Rec.709 color primaries, transfer characteristics, and matrix coefficients).
- **Cấu trúc GOP**: GOP 2.0 giây (`keyint=50:min-keyint=50:no-scenecut=1`).
- **Container**: MP4 FastStart (`-movflags +faststart`) hỗ trợ xem ngay trên web không cần đợi tải hết video.

### GATE 6: CHỨNG NHẬN TOÀN CẦU & PUBLIC RELEASE GATE
- **Quy tắc cứng (Hard Gate)**: Chỉ khi cả 5 cổng trên đạt `PASS` và điểm trung bình $\ge 85/100$, Cổng Public mới mở.
- **Dấu vân tay mã hóa**: Tính toán mã hash **SHA-256** của file video thành phẩm.
- **Cấp chứng chỉ**: Xuất file `CERTIFICATE_<ID>.json` và `CERTIFICATE_<ID>.md`.

---

## 3. CÁCH SỬ DỤNG AI AGENT AUDIT

```bash
# 1. Kiểm định 1 video đơn lẻ trước khi đăng tải
python3 pipeline/audit_cli.py --video dist_publish/my_clip.mp4 --topic "Red Ball" --age "1-2" --genre "vocabulary"

# 2. Kiểm định hàng loạt toàn bộ thư mục xuất bản
python3 pipeline/audit_cli.py --batch dist_publish/

# 3. Tự động kiểm định trong dây chuyền sản xuất:
# Lệnh produce_batch.py đã tự động tích hợp Cổng Kiểm Định AI Agent:
python3 pipeline/produce_batch.py --count 100 --workers 6
```
