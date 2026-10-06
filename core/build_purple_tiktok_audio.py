#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

DIR = Path("/root/scratch/purple_w06_tiktok")
RAW = DIR / "raw"
BGM = Path("/root/preschool-animation-factory/res/bgm/Monkeys_Spinning_Monkeys.mp3")
SFX_DIR = Path("/root/preschool-animation-factory/res/sfx")
OUT_MP3 = DIR / "master_audio.mp3"
OUT_MANIFEST = DIR / "manifest.json"

EVENTS = [
    ("01_sarah_hook", "01_sarah_hook.mp3", "ms_sarah", 250),
    ("02_david_door1", "02_david_door1.mp3", "mr_david", 250),
    ("03_leo_classroom", "03_leo_classroom.mp3", "leo_bunny", 300),
    ("04_mia_say_classroom", "04_mia_say_classroom.mp3", "mia_kid", 400),
    ("05_david_door2", "05_david_door2.mp3", "mr_david", 250),
    ("06_sarah_library", "06_sarah_library.mp3", "ms_sarah", 250),
    ("07_leo_read_library", "07_leo_read_library.mp3", "leo_bunny", 300),
    ("08_both_library", "08_both_library.mp3", "both_kids", 400),
    ("09_david_whoosh", "09_david_whoosh.mp3", "mr_david", 250),
    ("10_mia_playground", "10_mia_playground.mp3", "mia_kid", 300),
    ("11_leo_play", "11_leo_play.mp3", "leo_bunny", 300),
    ("12_sarah_yes_playground", "12_sarah_yes_playground.mp3", "ms_sarah", 400),
    ("13_david_door4", "13_david_door4.mp3", "mr_david", 250),
    ("14_leo_artroom", "14_leo_artroom.mp3", "leo_bunny", 300),
    ("15_mia_paint", "15_mia_paint.mp3", "mia_kid", 400),
    ("16_fast_recap", "16_fast_recap.mp3", "ms_sarah", 300),
    ("17_both_yay", "17_both_yay.mp3", "both_kids", 300),
    ("18_teachers_bye", "18_teachers_bye.mp3", "teachers", 500)
]

def get_duration_ms(fpath):
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(fpath)]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, text=True, check=True)
    return float(res.stdout.strip()) * 1000.0

def main():
    current_time_ms = 400.0 # 0.4s intro whoosh
    dialogue_events = []

    for ev_id, fname, speaker, pause_ms in EVENTS:
        fpath = RAW / fname
        dur_ms = get_duration_ms(fpath)
        start_ms = current_time_ms
        end_ms = start_ms + dur_ms
        
        dialogue_events.append({
            "id": ev_id,
            "file": str(fpath),
            "speaker": speaker,
            "start_ms": start_ms,
            "end_ms": end_ms,
            "duration_ms": dur_ms,
            "type": "dialogue"
        })
        current_time_ms = end_ms + pause_ms

    total_duration_sec = (current_time_ms + 1000.0) / 1000.0
    print(f"Total audio duration: {total_duration_sec:.2f}s ({len(dialogue_events)} dialogue lines)")

    # Kiểm tra Zero Speech Overlap
    for i in range(len(dialogue_events) - 1):
        gap = dialogue_events[i+1]["start_ms"] - dialogue_events[i]["end_ms"]
        id1 = dialogue_events[i]["id"]
        id2 = dialogue_events[i+1]["id"]
        if gap < 0:
            raise RuntimeError(f"Overlap detected between {id1} and {id2}")

    print("✅ 100% Zero Speech Overlap verified!")

    sfx_events = []
    for ev in dialogue_events:
        eid = ev["id"]
        if "door" in eid or "whoosh" in eid or "hook" in eid:
            sfx_events.append({
                "id": f"sfx_whoosh_{eid}",
                "file": "/root/scratch/sfx_whoosh.wav",
                "start_ms": max(0, ev["start_ms"] - 150.0),
                "type": "sfx"
            })
        elif "say" in eid or "fast" in eid:
            sfx_events.append({
                "id": f"sfx_ting_{eid}",
                "file": str(SFX_DIR / "sfx_stop_ting.mp3"),
                "start_ms": ev["start_ms"] - 100.0,
                "type": "sfx"
            })

    ev_yay = next(e for e in dialogue_events if e["id"] == "17_both_yay")
    sfx_events.append({
        "id": "sfx_applause",
        "file": str(SFX_DIR / "sfx_applause.mp3"),
        "start_ms": ev_yay["start_ms"],
        "type": "sfx"
    })

    all_events = dialogue_events + sfx_events
    manifest = {
        "total_duration": total_duration_sec,
        "events": all_events
    }
    with open(OUT_MANIFEST, "w") as fp:
        json.dump(manifest, fp, indent=2)

    print(f"Saved manifest: {OUT_MANIFEST}")

    # Hòa âm FFmpeg
    inputs = ["-i", str(BGM)]
    for ev in all_events:
        inputs.extend(["-i", ev["file"]])

    filter_complex = []
    filter_complex.append(f"[0:a]aloop=loop=-1:size=2e+09,atrim=0:{total_duration_sec},volume=0.10,afade=t=out:st={total_duration_sec-2.0}:d=2.0[bgm];")

    delayed_labels = ["[bgm]"]
    for idx, ev in enumerate(all_events):
        delay_ms = int(ev["start_ms"])
        inp_idx = idx + 1
        vol = "1.0" if ev["type"] == "dialogue" else "0.8"
        filter_complex.append(f"[{inp_idx}:a]adelay={delay_ms}|{delay_ms},volume={vol}[a{idx}];")
        delayed_labels.append(f"[a{idx}]")

    mix_in = "".join(delayed_labels)
    total_streams = len(delayed_labels)
    filter_complex.append(f"{mix_in}amix=inputs={total_streams}:dropout_transition=0:normalize=0[mixed];")
    filter_complex.append("[mixed]loudnorm=I=-14:LRA=9:TP=-1.0[out]")

    cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", "".join(filter_complex),
        "-map", "[out]",
        "-c:a", "libmp3lame",
        "-b:a", "192k",
        str(OUT_MP3)
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"🎉 Hòa âm thành công master TikTok Upbeat audio: {OUT_MP3} ({total_duration_sec:.1f}s)")

if __name__ == "__main__":
    main()
