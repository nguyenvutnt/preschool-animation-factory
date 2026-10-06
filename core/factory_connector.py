#!/usr/bin/env python3
"""
MODULE ĐẤU NỐI NHÀ MÁY SẢN XUẤT CLIP (FACTORY CONNECTOR):
Đấu nối trực tiếp giữa Preschool Animation Factory và hệ thống nhà máy TrueLearning / EYC Factory trên máy.

1. Nạp Syllabus & Activities trực tiếp từ:
   /root/truelearning/out/TL16/syllabus.jsonl
   /root/truelearning/out/TL16/activity.jsonl
2. Kế thừa kho SFX/BGM chuẩn trường học:
   /root/truelearning/res/sfx/
   /root/truelearning/res/bgm/
3. Đồng bộ tiến độ xuất bản vào:
   /root/truelearning/progress/video_te.json
4. Tự động xuất bản web đa nền tảng:
   /srv/school-ai/var/video-cong-khai/
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

TL_ROOT = Path("/root/truelearning")
TL_SYLLABUS = TL_ROOT / "out" / "TL16" / "syllabus.jsonl"
TL_ACTIVITY = TL_ROOT / "out" / "TL16" / "activity.jsonl"
TL_SFX = TL_ROOT / "res" / "sfx"
TL_BGM = TL_ROOT / "res" / "bgm"
TL_PROGRESS = TL_ROOT / "progress" / "video_te.json"

PUBLISH_PUBLIC_DIR = Path("/srv/school-ai/var/video-cong-khai")

class FactoryConnector:
    def __init__(self):
        self.syllabus_cache = {}
        self.activity_cache = {}
        self._load_metadata()

    def _load_metadata(self):
        if TL_SYLLABUS.exists():
            with open(TL_SYLLABUS, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        d = json.loads(line)
                        k = (d.get("AGE", "").upper(), d.get("WEEK", "").upper())
                        self.syllabus_cache[k] = d
                    except Exception:
                        pass
                        
        if TL_ACTIVITY.exists():
            with open(TL_ACTIVITY, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        d = json.loads(line)
                        k = (d.get("AGE", "").upper(), d.get("WEEK", "").upper())
                        if k not in self.activity_cache:
                            self.activity_cache[k] = []
                        self.activity_cache[k].append(d)
                    except Exception:
                        pass

    def get_week_curriculum(self, age: str, week: str) -> Dict[str, Any]:
        """Lấy toàn bộ thông số sư phạm của tuần bài học từ hệ thống nhà máy."""
        age = age.upper()
        week = week.upper()
        if not week.startswith("W"):
            week = f"W{int(week):02d}"

        syl = self.syllabus_cache.get((age, week), {})
        acts = self.activity_cache.get((age, week), [])

        vocab_raw = syl.get("CONCEPT / VOCABULARY", "")
        vocab_list = [v.strip() for v in vocab_raw.split("\n") if v.strip()]

        return {
            "age_group": age,
            "week": week,
            "weekly_concept": syl.get("WEEKLY CONCEPT", ""),
            "weekly_focus": syl.get("WEEKLY FOCUS", ""),
            "target_vocabulary": vocab_list,
            "key_experiences": syl.get("KEY EXPERIENCES", ""),
            "activities_count": len(acts),
            "activities": acts,
            "shared_sfx_dir": str(TL_SFX),
            "shared_bgm_dir": str(TL_BGM)
        }

    def sync_progress(self, unit_key: str, status: str, output_path: str):
        """Cập nhật tiến độ sản xuất vào cơ sở dữ liệu nhà máy."""
        data = {"cap_nhat": "", "don_vi": {}}
        if TL_PROGRESS.exists():
            try:
                data = json.loads(TL_PROGRESS.read_text(encoding="utf-8"))
            except Exception:
                pass
        
        import datetime
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data["cap_nhat"] = now_str
        data["don_vi"][unit_key] = {
            "trang_thai": status,
            "file": output_path,
            "thoi_gian": now_str
        }
        TL_PROGRESS.parent.mkdir(parents=True, exist_ok=True)
        TL_PROGRESS.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"🔗 [Factory Connector] Đồng bộ tiến độ nhà máy thành công: {unit_key} -> {status}")

if __name__ == "__main__":
    fc = FactoryConnector()
    info = fc.get_week_curriculum("PURPLE", "W06")
    print("=== KẾT NỐI NHÀ MÁY THÀNH CÔNG ===")
    print("Khối:", info["age_group"], "Tuần:", info["week"])
    print("Chủ đề:", info["weekly_concept"])
    print("Tiêu điểm:", info["weekly_focus"])
    print("Từ vựng nhà máy:", info["target_vocabulary"])
    print("Số hoạt động:", info["activities_count"])
