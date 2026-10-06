#!/usr/bin/env python3
"""TIẾN TRÌNH TỰ ĐỘNG HÓA SẢN XUẤT 24/7 (AUTOMATED FACTORY DAEMON).
Quản lý mục tiêu sản xuất 100 đến 500 clip/ngày:
  - Tự động quét giáo trình 48 tuần True English.
  - Phân bổ mẻ nhỏ (batches of 25 - 50 clips) tránh nghẽn I/O.
  - Giám sát dung lượng ổ cứng an toàn (tự động cảnh báo nếu disk > 85%).
  - Tự động xuất xưởng và cập nhật bảng kê nhật ký sản xuất.
"""
from __future__ import annotations

import argparse
import os
import shutil
import sys
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from pipeline.produce_batch import chay_san_xuat_hang_loat

LOG_DIR = ROOT_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
DAEMON_LOG = LOG_DIR / "factory_daemon.log"

def kiem_tra_o_dia_an_toan() -> bool:
    """Kiểm tra xem ổ đĩa còn trống trên 15% không."""
    total, used, free = shutil.disk_usage("/")
    percent_used = (used / total) * 100
    if percent_used > 85:
        print(f"⚠️ [CẢNH BÁO] Dung lượng ổ cứng đã dùng {percent_used:.1f}% > 85%. Tạm dừng nạp batch mới!")
        return False
    return True

def chay_daemon(daily_target: int = 200, batch_size: int = 25, workers: int = 6):
    """Chạy vòng lặp sản xuất tự động hàng ngày."""
    print("=" * 70)
    print(f"🤖 KHỞI ĐỘNG TIẾN TRÌNH DAEMON NHÀ MÁY HOẠT HÌNH")
    print(f"   - Chỉ tiêu ngày: {daily_target} clips")
    print(f"   - Kích thước mẻ (Batch size): {batch_size} clips/mẻ")
    print(f"   - Số luồng xử lý: {workers} workers")
    print(f"   - Log tiến trình: {DAEMON_LOG}")
    print("=" * 70)

    produced_today = 0
    batch_num = 1

    while produced_today < daily_target:
        if not kiem_tra_o_dia_an_toan():
            time.sleep(60)
            continue

        remaining = daily_target - produced_today
        current_batch_count = min(batch_size, remaining)

        print(f"\n📦 [Mẻ #{batch_num}] Đang sản xuất {current_batch_count} clips (Tiến độ: {produced_today}/{daily_target})...")
        t_batch_start = time.time()

        results = chay_san_xuat_hang_loat(
            target_count=current_batch_count,
            workers=workers
        )

        success_count = sum(1 for r in results if r.get("status") == "PUBLISH_APPROVED")
        produced_today += success_count
        batch_duration = round(time.time() - t_batch_start, 1)

        log_entry = (
            f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Batch #{batch_num}: "
            f"Thành công {success_count}/{current_batch_count} clips trong {batch_duration}s. "
            f"Lũy kế ngày: {produced_today}/{daily_target}\n"
        )
        with open(DAEMON_LOG, "a", encoding="utf-8") as f:
            f.write(log_entry)

        print(f"✅ Hoàn tất mẻ #{batch_num}. Lũy kế đạt: {produced_today}/{daily_target} clips.")
        batch_num += 1

        # Nghỉ ngắn 5 giây giữa các mẻ để giải phóng cache bộ nhớ
        if produced_today < daily_target:
            time.sleep(5)

    print("\n🎉 ĐÃ ĐẠT CHỈ TIÊU SẢN XUẤT TRONG NGÀY!")
    print(f"   Tổng xuất xưởng: {produced_today} clips.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tiến trình sản xuất tự động 24/7")
    parser.add_argument("--daily-target", type=int, default=200, help="Chỉ tiêu số clip trong ngày (100 - 500)")
    parser.add_argument("--batch-size", type=int, default=25, help="Số clip mỗi mẻ")
    parser.add_argument("--workers", type=int, default=6, help="Số worker song song")
    args = parser.parse_args()

    chay_daemon(daily_target=args.daily_target, batch_size=args.batch_size, workers=args.workers)
