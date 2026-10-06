#!/usr/bin/env python3
"""ĐIỀU PHỐI SẢN XUẤT HÀNG LOẠT 100 - 500 CLIP/NGÀY (BATCH PRODUCTION ORCHESTRATOR).
Tự động hóa toàn diện từ Ma trận 48 tuần True English:
  - Phân loại 8 thể loại: Glenn Doman, Từ vựng, Phonics, Sight Words, Giao tiếp, Thơ vần, Truyện kể, Bài hát.
  - Tùy biến thời lượng linh hoạt: 1.0 đến 5.0 phút theo đặc thù từng thể loại.
  - Phân luồng 4 - 8 Workers tận dụng 16 vCPUs.
  - Kiểm định tự động EBU R128 (-14.0 LUFS) và xuất Manifest chuẩn xuất bản.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.llm_engine import tao_kich_ban_theo_thoi_luong
from pipeline.worker_pool import chay_worker_pool

DATA_DIR = ROOT_DIR / "data" / "true_english_48_weeks"
MASTER_TE_FILE = DATA_DIR / "master-te.json"
DIST_DIR = ROOT_DIR / "dist_publish"

# Ma trận thời lượng chuẩn theo thể loại (phút)
GENRE_DURATION_MAP = {
    "glenn_doman": 1.0,     # Flashcard bit tráo nhanh: 1.0 - 1.5 phút
    "phonics": 2.0,         # Oxford phonics & blending: 1.5 - 2.5 phút
    "sight_words": 1.8,     # Sight words: 1.5 - 2.0 phút
    "vocabulary": 2.5,      # Từ vựng & nhận biết: 2.0 - 3.0 phút
    "conversation": 2.5,    # Giao tiếp & tình huống: 2.0 - 3.5 phút
    "rhyme": 2.0,           # Thơ vần điệu: 1.5 - 2.5 phút
    "song": 3.0,            # Bài hát & vận động: 2.5 - 3.5 phút
    "story": 4.0            # Truyện tranh kể chuyện: 3.5 - 5.0 phút
}

ALL_GENRES = list(GENRE_DURATION_MAP.keys())
GRADES = ["Red", "Orange", "Yellow", "Green", "Blue", "Purple"]

def sinh_danh_sach_tac_vu_tu_giao_trinh(
    tuan: Optional[str] = None,
    target_count: int = 100,
    genres: Optional[List[str]] = None,
    duration_factor: float = 1.0
) -> List[Dict[str, Any]]:
    """Tạo danh sách các tác vụ sản xuất dựa trên ma trận giáo trình 48 tuần."""
    active_genres = genres if genres else ALL_GENRES
    curriculum = []

    # Đọc tuần từ master-te.json
    if MASTER_TE_FILE.exists():
        try:
            with open(MASTER_TE_FILE, "r", encoding="utf-8") as f:
                d = json.load(f)
            curriculum = d.get("trang_thai_48_tuan", [])
        except Exception:
            pass

    if not curriculum:
        curriculum = [{"tuan": f"W{i:02d}", "Yellow": "School and Family"} for i in range(1, 49)]

    tasks: List[Dict[str, Any]] = []
    task_idx = 1

    # Lọc tuần nếu được chỉ định
    target_weeks = [c for c in curriculum if c.get("tuan", "").upper() == tuan.upper()] if tuan else curriculum

    for w_info in target_weeks:
        week_code = w_info.get("tuan", "W01")
        for grade in GRADES:
            topic = w_info.get(grade, w_info.get("Yellow", f"Topic of {week_code}"))
            for genre in active_genres:
                base_minutes = GENRE_DURATION_MAP.get(genre, 2.0)
                final_minutes = round(base_minutes * duration_factor, 1)

                kb = tao_kich_ban_theo_thoi_luong(genre, topic, do_tuoi="3-4", target_minutes=final_minutes)
                clip_id = f"{week_code}_{grade}_{genre}_{task_idx:04d}"

                tasks.append({
                    "clip_id": clip_id,
                    "week": week_code,
                    "grade": grade,
                    "genre": genre,
                    "topic": topic,
                    "target_minutes": final_minutes,
                    "shots": kb["shots"]
                })
                task_idx += 1
                if len(tasks) >= target_count:
                    return tasks

    return tasks

def xuat_bao_cao_manifest(results: List[Dict[str, Any]], out_dir: Path) -> Path:
    """Xuất file manifest báo cáo chất lượng và danh mục xuất bản."""
    timestamp = int(time.time())
    manifest_json = out_dir / f"manifest_{timestamp}.json"
    manifest_csv = out_dir / f"manifest_{timestamp}.csv"

    # Ghi JSON
    with open(manifest_json, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # Ghi CSV
    if results:
        fieldnames = [
            "video_file", "genre", "status", "public_release", "audit_score",
            "audit_id", "resolution", "frame_rate", "integrated_lufs",
            "render_time_seconds", "sha256_hash", "bgm_used"
        ]
        with open(manifest_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            for r in results:
                writer.writerow(r)

    print(f"📊 Đã xuất báo cáo xuất xưởng kèm Chứng chỉ Kiểm định:")
    print(f"   - JSON: {manifest_json}")
    print(f"   - CSV:  {manifest_csv}")
    return manifest_json

def chay_san_xuat_hang_loat(
    target_count: int = 100,
    week: Optional[str] = None,
    workers: int = 6,
    genres: Optional[List[str]] = None,
    duration_factor: float = 1.0,
    out_dir: Optional[Path] = None
) -> List[Dict[str, Any]]:
    """Quy trình sản xuất công nghiệp trọn gói có AI Agent Audit bảo chứng."""
    if out_dir is None:
        out_dir = DIST_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print(f"🏭 KHỞI ĐỘNG DÂY CHUYỀN SẢN XUẤT HOẠT HÌNH & HỌC LIỆU MẦM NON")
    print(f"   - Mục tiêu sản xuất: {target_count} clips")
    print(f"   - Số lượng Worker song song: {workers} luồng (Tận dụng CPU 16 vCPUs)")
    print(f"   - Phạm vi tuần: {week if week else 'Toàn bộ 48 tuần True English'}")
    print(f"   - Thời lượng clip: 1.0 – 5.0 phút tùy theo 8 thể loại")
    print("=" * 70)

    t0 = time.time()
    tasks = sinh_danh_sach_tac_vu_tu_giao_trinh(
        tuan=week,
        target_count=target_count,
        genres=genres,
        duration_factor=duration_factor
    )
    print(f"📋 Đã chuẩn bị {len(tasks)} kịch bản đạt chuẩn CEFR Pre-A1 & Oxford Phonics.")

    # 1. Chạy sản xuất qua Worker Pool
    results = chay_worker_pool(tasks, out_dir, max_workers=workers)

    # 2. Kích hoạt Cổng Giám Định AI Agent (6-Stage Audit Gate)
    print(f"\n🛡️ [CỔNG KIỂM ĐỊNH AI AGENT] Đang thẩm định chất lượng quốc tế cho {len(results)} clips...")
    from core.audit_agent import GlobalPreschoolAuditAgent
    auditor = GlobalPreschoolAuditAgent()
    certified_count = 0
    for r in results:
        v_path = Path(r["video_file"])
        if v_path.exists():
            rep = auditor.audit_full_pipeline(
                v_path,
                topic=r.get("topic", v_path.stem),
                genre=r.get("genre", "vocabulary")
            )
            r["audit_id"] = rep.audit_id
            r["audit_score"] = rep.global_score
            r["sha256_hash"] = rep.sha256_fingerprint
            r["public_release"] = rep.overall_status
            if rep.overall_status == "CERTIFIED_APPROVED":
                certified_count += 1
            else:
                r["status"] = "REJECTED_AUDIT_FAIL"

    # 3. Xuất báo cáo và chứng chỉ
    xuat_bao_cao_manifest(results, out_dir)

    total_time = round(time.time() - t0, 2)
    print("=" * 70)
    print(f"✨ HOÀN TẤT ĐỢT SẢN XUẤT:")
    print(f"   - Tổng clip xuất xưởng: {len(results)} clips")
    print(f"   - Chứng nhận Xuất bản Toàn cầu (CERTIFIED_APPROVED): {certified_count}/{len(results)} clips")
    print(f"   - Tổng thời gian: {total_time} giây ({round(total_time/60, 2)} phút)")
    print(f"   - Tốc độ trung bình: {round(len(results) / (total_time/60), 1)} clip/phút (~{round((len(results)/(total_time/60))*60)} clip/giờ)")
    print("=" * 70)
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dây chuyền sản xuất video học liệu mầm non hàng loạt")
    parser.add_argument("--count", type=int, default=10, help="Số lượng clip muốn sản xuất (10 - 500)")
    parser.add_argument("--week", default=None, help="Chỉ định tuần cụ thể (W01 - W48) nếu muốn")
    parser.add_argument("--workers", type=int, default=6, help="Số worker render song song (khuyên dùng 4 - 8)")
    parser.add_argument("--genres", default=None, help="Danh sách thể loại cách nhau bởi dấu phẩy")
    parser.add_argument("--duration-scale", type=float, default=1.0, help="Hệ số co giãn thời lượng (1.0 = chuẩn 1-5m, 0.5 = rút gọn)")
    args = parser.parse_args()

    genre_list = [g.strip() for g in args.genres.split(",")] if args.genres else None
    chay_san_xuat_hang_loat(
        target_count=args.count,
        week=args.week,
        workers=args.workers,
        genres=genre_list,
        duration_factor=args.duration_scale
    )
