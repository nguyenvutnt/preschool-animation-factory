# 🏭 NHÀ MÁY HOẠT HÌNH & VIDEO HỌC LIỆU MẦM NON (PRESCHOOL ESL ANIMATION FACTORY)
> **Mục tiêu công suất**: 500 – 1.000 clip/ngày  
> **Chuẩn xuất bản toàn cầu**: Cambridge Assessment English (Pre-A1 Starters), Oxford Phonics, BBC CBeebies (Low-Stimulation), EBU R128 (-14 LUFS), COPPA Child-Safe.  
> **Chi phí biên sản xuất**: **0 VNĐ API** (Tận dụng 100% tài nguyên CPU 16 vCPUs, LLM Gemini Ultra/Advanced qua `agy` và nhạc nền Creative Commons).

---

## 1. TỔNG QUAN KIẾN TRÚC HỆ THỐNG

Dây chuyền sản xuất được thiết kế theo mô hình **Công nghiệp Đa luồng (Multi-Worker Industrial Pipeline)**:

```
[Curriculum Matrix (48 Tuần x 6 Khối)]
                │
                ▼
[1. Kịch bản & Lời bài hát] ──► 100% Gemini Ultra/Advanced (`agy` CLI) (0 VNĐ API)
                │
                ▼
[2. Giọng đọc & Âm nhạc]    ──► Edge-TTS (en-GB-SoniaNeural / en-US-AnaNeural) + BGM Library
                │
                ▼
[3. Hòa âm & Ép chuẩn EBU]  ──► FFmpeg Sidechain Ducking + EBU R128 (-14.0 LUFS, TP -1.0 dBTP)
                │
                ▼
[4. Sân khấu Visual]        ──► Zero-Collision Stage Layout (Top Stage 70-750px, Buffer 140px, Bottom 820-1080px)
                │
                ▼
[5. Động cơ Render FFmpeg]   ──► Parallel Worker Pool (4–6 Workers), Rec.709 CFR 25fps (5.3x real-time)
                │
                ▼
[6. Cổng kiểm định Auto QC] ──► Tự động thẩm định LUFS, Black frames, Resolution trước khi cấp mã PUBLISH_APPROVED
```

---

## 2. BỘ TIÊU CHUẨN XUẤT BẢN ĐẠT ĐƯỢC

1. **Chuẩn Sư phạm (Cambridge & Oxford)**:
   - Từ vựng kiểm soát nghiêm ngặt theo danh mục Pre-A1 Starters.
   - Tốc độ phát âm mầm non: **85 – 105 WPM** (không gây ngợp cho trẻ).
   - Khoảng lặng tương tác **3 giây** (Interactive Pause) kích hoạt phản xạ chủ động.
2. **Chuẩn An toàn Não bộ (Low-Stimulation / BBC CBeebies)**:
   - Thời lượng mỗi cảnh $\ge 3.5$ – 5.0 giây (cấm tuyệt đối fast-cuts).
   - Chống co giật quang học (ITU-R BT.1702).
   - Bố cục Glenn Doman không va chạm (Zero Text-Image Collision).
3. **Chuẩn Phát thanh & Truyền hình (Broadcast EBU R128)**:
   - Integrated Loudness: **-14.0 LUFS** ($\pm 0.5$ LU).
   - True Peak tối đa: $\le \mathbf{-1.0\text{ dBTP}}$.
   - Nhạc nền tự động né giọng đọc (Sidechain ducking $-14$dB).
4. **Pháp lý Trẻ em (COPPA & GDPR-K & NĐ 360/2026/NĐ-CP)**:
   - Không chứa metadata theo dõi/PII, bảo đảm thuần phong mỹ tục.

---

## 3. CẤU TRÚC THƯ MỤC DỰ ÁN

```
preschool-animation-factory/
├── README.md
├── docs/                     # Tài liệu kiến trúc, chuẩn quốc tế, SOP
├── core/                     # Các module cốt lõi (LLM, Voice, Audio, Layout, Render, QC)
│   ├── llm_engine.py         # Trình sinh nội dung qua Gemini agy (0 VNĐ)
│   ├── voice_engine.py       # Trình đọc chuẩn Oxford/Cambridge
│   ├── audio_master.py       # Hòa âm EBU R128 + Sidechain ducking
│   ├── visual_composer.py    # Dựng sân khấu 1080p Zero-Collision
│   ├── subtitle_generator.py # Phụ đề ASS Glenn Doman
│   ├── video_renderer.py     # Động cơ render FFmpeg siêu tốc
│   ├── qc_validator.py       # Cổng kiểm định chất lượng tự động
│   └── clone_engine.py       # Reverse-engineer link YouTube/TikTok -> True English
├── data/                     # Ngữ liệu gốc 48 tuần True English
│   ├── master-te.json        # Ma trận 48 tuần x 6 khối tuổi
│   └── tuong_tac_noi_dung.jsonl # 839 hoạt động & câu hỏi tương tác
├── pipeline/                 # Bộ điều phối sản xuất hàng loạt
│   ├── worker_pool.py        # Quản lý 4-8 worker render song song
│   ├── produce_batch.py      # Điều phối sản xuất 100 - 500 clip/ngày (thời lượng 1-5 phút)
│   └── daemon_runner.py      # Tiến trình chạy tự động 24/7
├── res/                      # Kho tài nguyên dùng chung
│   ├── bgm/                  # 10 bản nhạc nền thiếu nhi bản quyền sạch (Incompetech CC-BY 4.0)
│   └── sfx/                  # Hiệu ứng âm thanh mộc
└── config/                   # Cấu hình chuẩn xuất bản
    ├── clip_genres.json      # Định nghĩa chuẩn 8 thể loại học liệu
    └── publishing_specs.json # Chuẩn kỹ thuật EBU R128, Rec.709, Low-Stimulation
```

---

## 4. HỆ SINH THÁI 8 THỂ LOẠI HỌC LIỆU MẦM NON

Hệ thống không mặc định clip bài hát mà phân hóa thành 8 thể loại chuyên biệt:
1. **Glenn Doman (Flashcard Bit)**: 1.0 – 1.5 phút (tráo nhanh 1.0s/từ, 0 BGM, não phải chụp hình tức thì).
2. **Phonics (Oxford Phonics)**: 1.5 – 2.5 phút (Letter sounds, CVC blending, phonics chant).
3. **Sight Words**: 1.5 – 2.0 phút (See-Say-Spell-3 Repeated Sentences).
4. **Từ vựng (Vocabulary)**: 2.0 – 3.0 phút (Vật thể thật, phát âm x2, câu TPR, đố 3s).
5. **Giao tiếp (Daily Conversation)**: 2.0 – 3.5 phút (Đối thoại 2 nhân vật, có 3 lần interactive pause 3s).
6. **Thơ vần (Nursery Rhymes)**: 1.5 – 2.5 phút (Thơ 4 câu vần chân, steady beat).
7. **Bài hát vận động (Song)**: 2.5 – 3.5 phút (Action TPR chant theo nhạc).
8. **Truyện kể tranh (Read-Along Story)**: 3.5 – 5.0 phút (Truyện tranh 8-10 cảnh, read-along text).

---

## 5. BẮT ĐẦU NHANH (QUICK START)

```bash
# 1. Chạy thử nghiệm 1 clip đơn lẻ theo thể loại (glenn_doman, phonics, vocabulary, conversation,...)
python3 core/video_renderer.py --genre glenn_doman

# 2. SẢN XUẤT HÀNG LOẠT 100 – 500 CLIPS (Thời lượng 1 – 5 phút):
# Sản xuất theo tuần học (150 clips cho cả 6 khối tuổi):
python3 pipeline/produce_batch.py --week W04 --workers 6

# Sản xuất theo chỉ tiêu số lượng (100 clips trong ~25 phút):
python3 pipeline/produce_batch.py --count 100 --workers 6

# 3. Chạy tiến trình Daemon tự động hóa 24/7 (Đạt 500 clips/ngày):
nohup python3 pipeline/daemon_runner.py --daily-target 500 --batch-size 25 --workers 6 > /dev/null 2>&1 &
```

