#!/usr/bin/env python3
"""MODULE ĐIỀU PHỐI LLM CHO NHÀ MÁY HOẠT HÌNH (0 VNĐ API).
Chiến lược phân tầng:
  - 100% CỖ MÁY CHÍNH: Gemini Ultra/Advanced qua `agy -p` (Context 1M-2M tokens, hạn mức cao, không bị rate limit).
  - TIER 2 DỰ PHÒNG: ChatGPT Pro qua `codex exec` (Chỉ dùng khi gặp bài toán logic phức tạp).
"""
from __future__ import annotations

import json
import subprocess
from typing import Any, Dict, Optional

def sinh_kich_ban_gemini(prompt: str, model: str = "gemini-3.8-flash-high") -> str:
    """Gọi Gemini Ultra/Advanced qua agy CLI (0 VNĐ)."""
    cmd = [
        "agy", "-p", prompt,
        "--model", model,
        "--output-format", "text"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return res.stdout.strip()

def sinh_kich_ban_chatgpt(prompt: str) -> str:
    """Gọi ChatGPT Business Pro qua codex CLI (Dự phòng bài toán khó, bảo toàn hạn mức)."""
    cmd = [
        "codex", "exec",
        "--dangerously-bypass-approvals-and-sandbox",
        "--skip-git-repo-check",
        prompt
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return res.stdout.strip()

def tao_kich_ban_clip(tu_khoa: str, do_tuoi: str = "3-4") -> Dict[str, Any]:
    """Tự động sinh kịch bản micro-shot mầm non chuẩn CEFR Pre-A1 bằng Gemini."""
    prompt = f"""Bạn là Giám đốc Sư phạm mầm non chuẩn Cambridge Pre-A1.
Hãy viết kịch bản 1 clip học liệu ngắn (45-60 giây) gồm 4 phân cảnh (shots) về từ khóa: "{tu_khoa}" cho trẻ lứa tuổi {do_tuoi}.

Quy tắc bắt buộc:
1. Zero Word Fluff: Mỗi shot chỉ 3 - 5 từ tiếng Anh, phát âm rõ ràng, nhịp điệu chậm rãi.
2. Cấu trúc 4 shots:
   - Shot 1 (Giới thiệu): Chào hỏi + đưa ra từ khóa.
   - Shot 2 (Visual Meaning): Mô tả hành động/đặc điểm (TPR).
   - Shot 3 (Interactive Pause): Câu hỏi đố vui kèm khoảng dừng 3 giây ("What color is it?").
   - Shot 4 (Outro Củng cố): Lặp lại từ khóa + khen ngợi ("Good job!").
3. Trả về đúng định dạng JSON thuần túy (không markdown) với cấu trúc:
{{
  "keyword": "{tu_khoa}",
  "age_group": "{do_tuoi}",
  "shots": [
    {{"shot_id": 1, "card_text": "...", "speech": "...", "duration": 5.0}},
    {{"shot_id": 2, "card_text": "...", "speech": "...", "duration": 5.0}},
    {{"shot_id": 3, "card_text": "...", "speech": "...", "duration": 6.0}},
    {{"shot_id": 4, "card_text": "...", "speech": "...", "duration": 5.0}}
  ]
}}
"""
    raw_output = sinh_kich_ban_gemini(prompt)
    # Lọc chuỗi JSON
    clean_json = raw_output
    if "```json" in clean_json:
        clean_json = clean_json.split("```json")[1].split("```")[0].strip()
    elif "```" in clean_json:
        clean_json = clean_json.split("```")[1].split("```")[0].strip()
    return json.loads(clean_json)

if __name__ == "__main__":
    print("Testing LLM Engine via agy (Gemini)...")
    kb = tao_kich_ban_clip("Apple", "3-4")
    print(json.dumps(kb, indent=2, ensure_ascii=False))
