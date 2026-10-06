#!/usr/bin/env python3
"""ĐỘNG CƠ DỰNG PHIM HOẠT HÌNH MẦM NON CHUẨN MASTER 5 PHÚT (MASTER ANIMATION ENGINE).
Kế thừa & Chuẩn hóa theo Pháp lệnh & Quy chuẩn Giáo dục Mầm non Quốc tế:
  1. Cấu trúc 5 Giai đoạn Sư phạm (Early Years 5-Phase Architecture):
     - Giai đoạn 1 (Scene 1-2): Khởi động & Đón trẻ đến trường (Parentese Welcome & Circle Play)
     - Giai đoạn 2 (Scene 3-4): Giảng dạy trọng tâm luân phiên (Turn-Taking & Requesting: "Please", "Thank you")
     - Giai đoạn 3 (Scene 5-6): Xây cầu khối gỗ & Đồng dao nhịp điệu (Block Building & Movement Rhythm Chant)
     - Giai đoạn 4 (Scene 7-8): Kể chuyện tương tác Syllabus Day 4 (Storybook Read-Along: Bunny & Bear)
     - Giai đoạn 5 (Scene 9-10): Tuyên dương Can-Do & Ru ngủ chuyển tiếp (Celebration & Bedtime Wind-Down)
  2. Bố cục Hoạt hình 3D & Chuyển động Điện ảnh Ken Burns:
     - 10 cảnh tranh minh họa 3D Disney/Pixar mộc mạc, giàu cảm xúc, an toàn thị giác CBeebies.
     - Chuyển động máy quay mượt mà (zoom_in, zoom_out, pan_left, pan_right) 30fps.
  3. Lồng tiếng Đa nhân vật US Motherese:
     - Mẹ (en-US-JennyNeural), Bố (en-US-GuyNeural), Cô giáo (JennyNeural)
     - Bé gái (en-US-AnaNeural +5Hz), Bé trai (en-US-AnaNeural -20Hz)
  4. Thiết kế Âm thanh Đa giác quan:
     - SFX tương tác: footsteps, harp, sparkle, pop, clapping, cheer, applause, stop_ting.
     - BGM thiếu nhi êm đềm ở mức -22dB, tôn trọn giọng đọc.
  5. Phụ đề ASS Phân vai Đổi màu (Color-Coded Character Subtitles):
     - Mẹ: Hồng pastel (&H00E19BEF)
     - Bố: Xanh ngọc (&H0058C6F9)
     - Bé gái: Vàng nắng (&H0099EEFF)
     - Bé trai: Xanh mầm non (&H0084E7B7)
     - Cô giáo: Tím nhạt (&H00FED66E)
     - Căn lề an toàn đáy MarginV=65, 100% không che hình.
"""
from __future__ import annotations

import asyncio
import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import edge_tts
from pydub import AudioSegment

CHARACTER_STYLES = {
    "Mom": {"voice": "en-US-JennyNeural", "pitch": "+0Hz", "rate": "-5%", "color": "&H00E19BEF"},
    "Dad": {"voice": "en-US-GuyNeural", "pitch": "+0Hz", "rate": "-5%", "color": "&H0058C6F9"},
    "Teacher": {"voice": "en-US-JennyNeural", "pitch": "+0Hz", "rate": "-5%", "color": "&H00FED66E"},
    "Little Girl": {"voice": "en-US-AnaNeural", "pitch": "+5Hz", "rate": "+0%", "color": "&H0099EEFF"},
    "Little Boy": {"voice": "en-US-AnaNeural", "pitch": "-20Hz", "rate": "+2%", "color": "&H0084E7B7"},
}

ASS_HEADER_TEMPLATE = """[Script Info]
Title: {title}
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: None
PlayResX: 1920
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,DejaVu Sans,68,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,1,0,1,5,2,2,50,50,65,1
Style: Mom,DejaVu Sans,68,&H00E19BEF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,1,0,1,5,2,2,50,50,65,1
Style: Dad,DejaVu Sans,68,&H0058C6F9,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,1,0,1,5,2,2,50,50,65,1
Style: LittleGirl,DejaVu Sans,68,&H0099EEFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,1,0,1,5,2,2,50,50,65,1
Style: LittleBoy,DejaVu Sans,68,&H0084E7B7,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,1,0,1,5,2,2,50,50,65,1
Style: Teacher,DejaVu Sans,68,&H00FED66E,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,1,0,1,5,2,2,50,50,65,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

def format_ass_time(ms: int) -> str:
    h = ms // 3600000
    m = (ms % 3600000) // 60000
    s = (ms % 60000) // 1000
    cs = (ms % 1000) // 10
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

class MasterAnimationEngine:
    """Động cơ điều phối sản xuất phim hoạt hình mầm non 5 phút chuẩn Master."""

    def __init__(self, work_dir: Path, res_dir: Path):
        self.work_dir = Path(work_dir)
        self.res_dir = Path(res_dir)
        self.sfx_dir = self.res_dir / "sfx"
        self.bgm_dir = self.res_dir / "bgm"
        self.work_dir.mkdir(parents=True, exist_ok=True)

    async def generate_dialogue_speech(self, scenes: List[Dict[str, Any]], out_dir: Path) -> List[Dict[str, Any]]:
        """Sinh âm thanh giọng đọc đa nhân vật Motherese từ Edge-TTS."""
        out_dir.mkdir(parents=True, exist_ok=True)
        line_idx = 0
        items = []

        for sc in scenes:
            sc_num = sc["scene"]
            for line in sc["lines"]:
                char = line["char"]
                text = line["text"]
                cfg = CHARACTER_STYLES.get(char, CHARACTER_STYLES["Teacher"])
                voice = line.get("voice", cfg["voice"])
                pitch = line.get("pitch", cfg["pitch"])
                rate = line.get("rate", cfg["rate"])

                clean_name = re.sub(r'[^a-zA-Z0-9]', '_', char)
                fn = out_dir / f"sc{sc_num:02d}_line{line_idx:03d}_{clean_name}.mp3"
                comm = edge_tts.Communicate(text, voice, pitch=pitch, rate=rate)
                await comm.save(str(fn))

                items.append({
                    "scene": sc_num,
                    "char": char,
                    "text": text,
                    "file": fn,
                    "index": line_idx
                })
                line_idx += 1
        return items

    def build_timeline_and_subtitles(
        self,
        audio_items: List[Dict[str, Any]],
        title: str,
        out_ass: Path
    ) -> Tuple[Dict[int, float], AudioSegment]:
        """Tính toán trục thời gian, nhịp dừng nhận thức (cognitive pause) và xuất phụ đề ASS phân vai."""
        scene_durations = {}
        global_time_ms = 500  # 500ms lead silence
        full_speech = AudioSegment.silent(duration=500)
        dialogues = []

        # Nhóm theo scene
        by_scene: Dict[int, List[Dict[str, Any]]] = {}
        for it in audio_items:
            by_scene.setdefault(it["scene"], []).append(it)

        for sc_num in sorted(by_scene.keys()):
            sc_items = by_scene[sc_num]
            sc_audio = AudioSegment.silent(duration=300)
            current_sc_time_ms = 300

            for it in sc_items:
                clip = AudioSegment.from_file(it["file"])
                clip_len = len(clip)

                sub_start_ms = global_time_ms + current_sc_time_ms
                sub_end_ms = sub_start_ms + clip_len

                char = it["char"]
                text = it["text"]
                style = "Default"
                if "Mom" in char:
                    style = "Mom"
                elif "Dad" in char:
                    style = "Dad"
                elif "Girl" in char:
                    style = "LittleGirl"
                elif "Boy" in char:
                    style = "LittleBoy"
                elif "Teacher" in char:
                    style = "Teacher"

                clean_text = f"{{\\b1}}{char}:{{\\b0}} {text}"
                start_str = format_ass_time(sub_start_ms)
                end_str = format_ass_time(sub_end_ms)
                dialogues.append(f"Dialogue: 0,{start_str},{end_str},{style},,0,0,0,,{clean_text}")

                sc_audio += clip
                current_sc_time_ms += clip_len

                # Nhịp dừng nhận thức mầm non: 1100ms cho câu hỏi/cảm thán, 700ms cho câu thường
                pause_ms = 1100 if ('?' in text or '!' in text) else 700
                sc_audio += AudioSegment.silent(duration=pause_ms)
                current_sc_time_ms += pause_ms

            sc_audio += AudioSegment.silent(duration=600)
            current_sc_time_ms += 600

            dur_sec = len(sc_audio) / 1000.0
            scene_durations[sc_num] = dur_sec
            full_speech += sc_audio
            global_time_ms += current_sc_time_ms

        header = ASS_HEADER_TEMPLATE.format(title=title)
        out_ass.write_text(header + "\n".join(dialogues) + "\n", encoding="utf-8")
        return scene_durations, full_speech

    def mix_master_soundscape(
        self,
        full_speech: AudioSegment,
        scene_durations: Dict[int, float],
        out_master_mp3: Path,
        bgm_path: Optional[Path] = None
    ) -> Path:
        """Hòa âm chuyên nghiệp: Voiceover chuẩn phát thanh + BGM -22dB + Lớp SFX đa giác quan."""
        voice = full_speech.normalize()
        v_len = len(voice)

        # 1. BGM thiếu nhi nhẹ nhàng
        if not bgm_path or not bgm_path.exists():
            bgm_path = self.bgm_dir / "nursery_cheerful_01.mp3"
        bgm_track = AudioSegment.from_file(bgm_path)
        while len(bgm_track) < v_len:
            bgm_track += bgm_track
        bgm_cut = bgm_track[:v_len] - 22  # BGM -22dB
        bgm_faded = bgm_cut.fade_in(2500).fade_out(3500)

        # 2. SFX track
        sfx_track = AudioSegment.silent(duration=v_len)
        scene_starts = {1: 500}
        curr = 500
        for sc in range(1, len(scene_durations)):
            curr += int(scene_durations[sc] * 1000)
            scene_starts[sc + 1] = curr

        def safe_overlay(sfx_name: str, pos: int, vol_adj: float = 0.0):
            nonlocal sfx_track
            p = self.sfx_dir / sfx_name
            if p.exists() and pos < v_len:
                try:
                    seg = AudioSegment.from_file(p) + vol_adj
                    sfx_track = sfx_track.overlay(seg, position=pos)
                except Exception:
                    pass

        # Gắn hiệu ứng âm thanh khớp hành động
        safe_overlay("sfx_sparkle.mp3", scene_starts.get(1, 500) + 1500)
        safe_overlay("footsteps_pcm.wav", scene_starts.get(1, 500) + 4000, -8)
        safe_overlay("sfx_harp.mp3", scene_starts.get(2, 28000) + 1200)
        safe_overlay("pop_pcm.wav", scene_starts.get(3, 56000) + 2500, +4)
        safe_overlay("sfx_stop_ting.mp3", scene_starts.get(3, 56000) + 8000)
        safe_overlay("sfx_sparkle.mp3", scene_starts.get(4, 84000) + 8000)
        safe_overlay("pop_pcm.wav", scene_starts.get(5, 116000) + 5000, +4)
        safe_overlay("clapping_pcm.wav", scene_starts.get(6, 144000) + 2000, -6)
        safe_overlay("cheer_pcm.wav", scene_starts.get(6, 144000) + 28000, -6)
        safe_overlay("sfx_harp.mp3", scene_starts.get(7, 176000) + 2000)
        safe_overlay("sfx_sparkle.mp3", scene_starts.get(8, 206000) + 2500)
        safe_overlay("sfx_applause.mp3", scene_starts.get(9, 234000) + 1500, -4)
        safe_overlay("sfx_cheer.mp3", scene_starts.get(9, 234000) + 17000, -6)
        safe_overlay("sfx_harp.mp3", scene_starts.get(10, 264000) + 2000)

        master = voice.overlay(bgm_faded).overlay(sfx_track)
        master.export(out_master_mp3, format="mp3", bitrate="192k")
        return out_master_mp3

    def render_ken_burns_animation(
        self,
        scene_images: List[Tuple[int, Path, str]],
        scene_durations: Dict[int, float],
        master_audio: Path,
        ass_path: Path,
        out_video: Path,
        fps: int = 30
    ) -> Path:
        """Dựng các cảnh hoạt hình Ken Burns camera điện ảnh 30fps và ráp thành phẩm."""
        temp_dir = self.work_dir / "_render_temp"
        temp_dir.mkdir(parents=True, exist_ok=True)
        clip_files = []

        for sc_id, img_path, effect in scene_images:
            dur = float(scene_durations.get(sc_id, 30.0))
            total_frames = int(round(dur * fps))
            out_clip = temp_dir / f"clip_{sc_id:02d}.mp4"
            clip_files.append(out_clip)

            step = 0.15 / max(total_frames, 100)
            if effect == "zoom_in":
                zp = f"zoompan=z='min(zoom+{step:.6f},1.20)':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080:fps={fps}"
            elif effect == "zoom_out":
                zp = f"zoompan=z='if(lte(zoom,1.0),1.18,max(1.001,zoom-{step:.6f}))':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080:fps={fps}"
            elif effect == "pan_right":
                zp = f"zoompan=z=1.12:d={total_frames}:x='if(lte(on,1),(iw-iw/zoom)*0.2,(x+(iw-iw/zoom)/({total_frames}*1.5)))':y='ih/2-(ih/zoom/2)':s=1920x1080:fps={fps}"
            elif effect == "pan_left":
                zp = f"zoompan=z=1.12:d={total_frames}:x='if(lte(on,1),(iw-iw/zoom)*0.8,(x-(iw-iw/zoom)/({total_frames}*1.5)))':y='ih/2-(ih/zoom/2)':s=1920x1080:fps={fps}"
            else:
                zp = f"zoompan=z=1.05:d={total_frames}:s=1920x1080:fps={fps}"

            cmd = [
                "ffmpeg", "-y",
                "-loop", "1",
                "-i", str(img_path),
                "-vf", f"scale=3840:2160,{zp},format=yuv420p",
                "-t", f"{dur:.3f}",
                "-c:v", "libx264",
                "-preset", "ultrafast",
                "-crf", "22",
                "-r", str(fps),
                "-threads", "12",
                str(out_clip)
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

        concat_list = temp_dir / "concat.txt"
        with open(concat_list, "w", encoding="utf-8") as f:
            for c in clip_files:
                f.write(f"file '{c.resolve()}'\n")

        raw_video = temp_dir / "raw_video.mp4"
        subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list), "-c", "copy", str(raw_video)], check=True)

        # Mux âm thanh và khắc phụ đề ASS phân vai
        out_video.parent.mkdir(parents=True, exist_ok=True)
        final_cmd = [
            "ffmpeg", "-y",
            "-i", str(raw_video),
            "-i", str(master_audio),
            "-vf", f"ass={ass_path.resolve()}",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "24",
            "-c:a", "aac",
            "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            "-shortest",
            "-movflags", "+faststart",
            "-threads", "12",
            str(out_video)
        ]
        subprocess.run(final_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        shutil.rmtree(temp_dir, ignore_errors=True)
        return out_video
