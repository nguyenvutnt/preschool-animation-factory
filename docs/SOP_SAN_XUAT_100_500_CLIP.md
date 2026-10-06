# 🏭 HƯỚNG DẪN VẬN HÀNH SẢN XUẤT 100 – 500 CLIP HỌC LIỆU / NGÀY
*(Standard Operating Procedure - Factory Scale 100 - 500 Videos/Day)*

---

## 1. TỔNG QUAN NĂNG LỰC HẠ TẦNG

- **Máy chủ**: CPU 16 vCPUs AMD EPYC 7663, RAM 32 GB, Ổ cứng khả dụng 189 GB.
- **Chi phí biên sản xuất**: **0 VNĐ API**.
- **Chuẩn xuất bản**: 1080p CFR 25.0 fps, EBU R128 (-14.0 LUFS), Cambridge Pre-A1 & Oxford Phonics.
- **Quy mô thời lượng (1 – 5 phút/clip tùy thể loại)**:
  - Glenn Doman (Flashcard): **1.0 – 1.5 phút** (30 - 60 thẻ tráo tốc độ cao).
  - Phonics: **1.5 – 2.5 phút** (Letter sounds, CVC blending, chant).
  - Sight Words: **1.5 – 2.0 phút** (See-Say-Spell-3 Repeated Sentences).
  - Từ vựng (Vocabulary): **2.0 – 3.0 phút** (Vật thể thật, phát âm x2, TPR, đố 3s).
  - Giao tiếp (Conversation): **2.0 – 3.5 phút** (Đối thoại 2 nhân vật, 3s interactive pause).
  - Thơ vần (Rhyme): **1.5 – 2.5 phút** (Thơ vần điệu, steady beat).
  - Bài hát vận động (Song): **2.5 – 3.5 phút** (Action TPR chant theo nhạc).
  - Truyện kể tranh (Story): **3.5 – 5.0 phút** (Truyện tranh 8-10 cảnh, read-along text).

---

## 2. BA CHẾ ĐỘ VẬN HÀNH CHÍNH

### Chế độ 1: Sản xuất theo Tuần giáo trình (Khuyên dùng)
Sản xuất trọn gói các bài học cho 1 tuần của cả 6 khối tuổi (Red, Orange, Yellow, Green, Blue, Purple) gồm 150 clips:
```bash
cd /root/preschool-animation-factory
python3 pipeline/produce_batch.py --week W04 --workers 6
```

### Chế độ 2: Sản xuất theo chỉ tiêu số lượng (100 đến 500 clips)
- **Mục tiêu 100 clips (Mất ~25 – 30 phút)**:
  ```bash
  python3 pipeline/produce_batch.py --count 100 --workers 6
  ```
- **Mục tiêu 500 clips (Mất ~2.0 – 2.5 giờ)**:
  ```bash
  python3 pipeline/produce_batch.py --count 500 --workers 8
  ```
- **Tùy chỉnh chọn lọc thể loại**:
  ```bash
  python3 pipeline/produce_batch.py --count 200 --genres glenn_doman,phonics,vocabulary,conversation --workers 6
  ```
- **Tăng độ dài clip (hệ số thời lượng 1.5x để đạt 3 - 5 phút)**:
  ```bash
  python3 pipeline/produce_batch.py --count 50 --duration-scale 1.5 --workers 6
  ```

### Chế độ 3: Tự động hóa 24/7 (Daemon Auto-Production)
Chạy ngầm liên tục, tự động chia mẻ 25 clips để giải phóng bộ nhớ, tự giám sát ổ đĩa:
```bash
nohup python3 pipeline/daemon_runner.py --daily-target 500 --batch-size 25 --workers 6 > /dev/null 2>&1 &
```
Xem log tiến độ thời gian thực:
```bash
tail -f /root/preschool-animation-factory/logs/factory_daemon.log
```

---

## 3. QUẢN LÝ ĐẦU RA & KIỂM ĐỊNH TỰ ĐỘNG

- Toàn bộ video xuất xưởng nằm tại: `/root/preschool-animation-factory/dist_publish/`
- Tự động xuất 2 tệp bảng kê chất lượng sau mỗi mẻ:
  - `dist_publish/manifest_<timestamp>.json`
  - `dist_publish/manifest_<timestamp>.csv`
- Mỗi dòng thể hiện: File MP4, Thể loại, Trạng thái (PUBLISH_APPROVED), Âm lượng LUFS, Thời gian render.
