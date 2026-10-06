#!/usr/bin/env python3
"""ĐỘNG CƠ ĐIỀU PHỐI ĐA TIẾN TRÌNH (PARALLEL WORKER POOL).
Phân bổ khối lượng sản xuất 500 - 1.000 clip/ngày qua 4 - 8 workers song song.
Mỗi worker xử lý độc lập từ Voice -> Staging -> Render -> QC.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import sys
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.video_renderer import render_clip_hoan_chinh

def render_worker_task(task_data: Dict[str, Any], out_dir: Path) -> Dict[str, Any]:
    """Tác vụ xử lý độc lập của từng worker."""
    clip_id = task_data["clip_id"]
    shots = task_data["shots"]
    bgm = task_data.get("bgm_name")
    img_path = Path(task_data["image_path"]) if "image_path" in task_data else None
    return render_clip_hoan_chinh(clip_id, shots, out_dir, bgm_name=bgm, subject_image_path=img_path)

def chay_worker_pool(
    tasks: List[Dict[str, Any]],
    out_dir: Path,
    max_workers: int = 4
) -> List[Dict[str, Any]]:
    """Phân phối danh sách tác vụ cho Worker Pool chạy song song."""
    print(f"🚀 Kích hoạt Worker Pool: {max_workers} Workers song song cho {len(tasks)} clips.")
    t0 = time.time()
    results = []
    out_dir.mkdir(parents=True, exist_ok=True)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_task = {
            executor.submit(render_worker_task, t, out_dir): t["clip_id"]
            for t in tasks
        }
        for future in concurrent.futures.as_completed(future_to_task):
            clip_id = future_to_task[future]
            try:
                data = future.result()
                results.append(data)
                print(f"  ✅ [Xong {data['status']}] {clip_id} trong {data['render_time_seconds']}s (LUFS: {data['integrated_lufs']})")
            except Exception as exc:
                print(f"  ❌ [Lỗi] {clip_id}: {exc}")

    total_time = round(time.time() - t0, 2)
    speed = round(len(tasks) / (total_time / 60), 1)
    print(f"🏁 Hoàn thành batch {len(tasks)} clips trong {total_time}s (Tốc độ: {speed} clips/phút ~ {speed*60:.0f} clips/giờ).")
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=4, help="Số lượng worker song song")
    parser.add_argument("--count", type=int, default=5, help="Số lượng clip chạy thử")
    args = parser.parse_args()

    # Tạo batch test
    sample_words = ["Apple", "Ball", "Cat", "Dog", "Elephant", "Fish", "Giraffe", "Hat"]
    test_tasks = []
    for i in range(min(args.count, len(sample_words))):
        w = sample_words[i]
        test_tasks.append({
            "clip_id": f"batch_test_{w.lower()}",
            "shots": [
                {"card_text": f"HELLO {w.upper()}", "speech": f"Hello {w}! Welcome friend.", "duration": 4.0},
                {"card_text": f"A IS FOR {w.upper()}", "speech": f"Look! This is an {w}.", "duration": 4.0},
                {"card_text": f"CAN YOU SAY {w.upper()}?", "speech": f"Can you say {w}?", "duration": 4.5},
                {"card_text": f"GREAT! {w.upper()}", "speech": f"Good job! It is {w}.", "duration": 4.0}
            ]
        })

    out_batch = ROOT_DIR / "out_batch_test"
    chay_worker_pool(test_tasks, out_batch, max_workers=args.workers)
