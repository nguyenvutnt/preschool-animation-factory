#!/usr/bin/env python3
"""CLI ĐIỀU PHỐI AI AGENT AUDIT TOÀN TRÌNH TRƯỚC KHI XUẤT BẢN.
(PRE-PUBLISHING GLOBAL AUDIT CLI)

Cú pháp:
  # 1. Audit 1 video đơn lẻ
  python3 pipeline/audit_cli.py --video dist_publish/clip.mp4 --topic "A Familiar Ball" --age "1-2"

  # 2. Audit toàn bộ thư mục xuất bản (Batch Audit Gate)
  python3 pipeline/audit_cli.py --batch dist_publish/
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.audit_agent import GlobalPreschoolAuditAgent

def audit_file(video_path: Path, topic: str = "Preschool Learning", genre: str = "vocabulary", age: str = "3-4") -> bool:
    agent = GlobalPreschoolAuditAgent()
    report = agent.audit_full_pipeline(video_path, topic=topic, genre=genre, age_group=age)

    # In kết quả Markdown
    print(report.to_markdown())

    # Lưu chứng chỉ Markdown và JSON
    out_dir = video_path.parent
    cert_md = out_dir / f"CERTIFICATE_{report.audit_id}.md"
    cert_json = out_dir / f"CERTIFICATE_{report.audit_id}.json"

    with open(cert_md, "w", encoding="utf-8") as f:
        f.write(report.to_markdown())

    cert_data = {
        "audit_id": report.audit_id,
        "target_file": report.target_file,
        "genre": report.genre,
        "overall_status": report.overall_status,
        "global_score": report.global_score,
        "sha256_fingerprint": report.sha256_fingerprint,
        "timestamp": report.timestamp,
        "gates": {k: {"status": v.status, "score": v.score, "findings": v.findings} for k, v in report.gates.items()}
    }
    with open(cert_json, "w", encoding="utf-8") as f:
        json.dump(cert_data, f, indent=2, ensure_ascii=False)

    print(f"\n📜 Đã cấp Chứng chỉ Kiểm định:")
    print(f"   - Markdown: {cert_md}")
    print(f"   - JSON:     {cert_json}")
    return report.overall_status == "CERTIFIED_APPROVED"

def audit_batch(batch_dir: Path) -> None:
    videos = list(batch_dir.glob("*.mp4"))
    if not videos:
        print(f"Không tìm thấy video .mp4 nào trong: {batch_dir}")
        return

    print(f"🛡️ Bắt đầu kiểm định hàng loạt {len(videos)} videos trong {batch_dir}...")
    passed_count = 0
    for v in videos:
        print(f"\n{'='*70}\n🔍 Đang thẩm định: {v.name}...\n{'='*70}")
        ok = audit_file(v, topic=v.stem, genre="vocabulary")
        if ok:
            passed_count += 1

    print(f"\n{'='*70}\n🏁 TỔNG KẾT BATCH AUDIT: {passed_count}/{len(videos)} videos ĐẠT CHUẨN XUẤT BẢN TOÀN CẦU!\n{'='*70}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Audit Gate AI Agent trước khi xuất bản ra công chúng")
    parser.add_argument("--video", default=None, help="Đường dẫn file video đơn lẻ")
    parser.add_argument("--batch", default=None, help="Đường dẫn thư mục chứa nhiều video cần audit")
    parser.add_argument("--topic", default="A Familiar Ball", help="Chủ đề bài học")
    parser.add_argument("--genre", default="vocabulary", help="Thể loại học liệu")
    parser.add_argument("--age", default="1-2", help="Lứa tuổi mầm non (1-2, 2-3, 3-4,...)")
    args = parser.parse_args()

    if args.video:
        audit_file(Path(args.video), topic=args.topic, genre=args.genre, age=args.age)
    elif args.batch:
        audit_batch(Path(args.batch))
    else:
        parser.print_help()
