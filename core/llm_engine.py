#!/usr/bin/env python3
"""MODULE ĐIỀU PHỐI KỊCH BẢN ĐA THỂ LOẠI & THỜI LƯỢNG LINH HOẠT (1 ĐẾN 5 PHÚT).
Hỗ trợ 8 thể loại học liệu mầm non:
  1. glenn_doman (1.0 - 2.0 phút)
  2. vocabulary (1.5 - 3.5 phút)
  3. phonics (1.5 - 3.0 phút)
  4. sight_words (1.5 - 3.0 phút)
  5. conversation (2.0 - 4.0 phút)
  6. rhyme (1.5 - 3.0 phút)
  7. story (3.0 - 5.0 phút)
  8. song (2.5 - 4.5 phút)
"""
from __future__ import annotations

import json
import subprocess
from typing import Any, Dict, List, Optional

def sinh_kich_ban_gemini(prompt: str, model: str = "gemini-3.8-flash-high") -> str:
    """Gọi Gemini Ultra/Advanced qua agy CLI (0 VNĐ)."""
    cmd = [
        "agy", "-p", prompt,
        "--model", model,
        "--output-format", "text"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return res.stdout.strip()

def tao_kich_ban_theo_thoi_luong(
    genre: str,
    topic_or_word: str,
    do_tuoi: str = "3-4",
    target_minutes: float = 1.5
) -> Dict[str, Any]:
    """Sinh kịch bản mở rộng theo thời lượng mục tiêu (1.0 đến 5.0 phút)."""
    g = genre.lower().strip()
    w = topic_or_word.strip()
    target_sec = max(60.0, min(300.0, target_minutes * 60.0))

    shots: List[Dict[str, Any]] = []

    if g in ("glenn_doman", "glenndoman", "flashcard"):
        # Glenn Doman: 1.0s/từ. Chia làm các vòng: Từ đơn -> Cụm từ 2 từ -> Câu 3 từ
        words_pool = [
            w.capitalize(), "Red " + w.capitalize(), "Big " + w.capitalize(),
            "Sweet " + w.capitalize(), "Fresh " + w.capitalize(), "Yummy " + w.capitalize(),
            "Little " + w.capitalize(), "Green " + w.capitalize(), "Round " + w.capitalize(),
            "Shiny " + w.capitalize(), "I see " + w.lower(), "I like " + w.lower(),
            "This is " + w.lower(), "Eat the " + w.lower(), "Good " + w.lower(),
            "Happy " + w.lower(), "One " + w.lower(), "Two " + w.lower() + "s"
        ]
        # Lặp lại theo thời lượng
        num_cards = int(target_sec / 1.1)
        cur_t = 0
        shot_id = 1
        while len(shots) < num_cards and cur_t < target_sec:
            idx = (shot_id - 1) % len(words_pool)
            text = words_pool[idx]
            dur = 1.0
            shots.append({"shot_id": shot_id, "card_text": text, "speech": text, "duration": dur})
            cur_t += dur
            shot_id += 1

        return {
            "genre": "glenn_doman",
            "topic": w,
            "target_duration_seconds": round(cur_t, 1),
            "age_group": do_tuoi,
            "speech_rate": "-5%",
            "shots": shots
        }

    elif g in ("phonics", "nguam"):
        letter = w[0].upper() if w else "A"
        l_low = letter.lower()
        # Chuỗi hoạt động phonics hoàn chỉnh
        modules = [
            {"card_text": f"Letter {letter}", "speech": f"Hello friends! This is the letter {letter}.", "duration": 4.0},
            {"card_text": f"Sound: /{l_low}/", "speech": f"The letter {letter} says /{l_low}/. Say /{l_low}/!", "duration": 4.0},
            {"card_text": f"/{l_low}/ - /{l_low}/ - {w.capitalize()}", "speech": f"/{l_low}/, /{l_low}/, {w}!", "duration": 4.0},
            {"card_text": f"/{l_low}/ is for {w.capitalize()}", "speech": f"{letter} is for {w}! Delicious {w}!", "duration": 4.0},
            {"card_text": f"Let's blend: /b/ - /{l_low}/ - /t/", "speech": f"Let's blend sounds: /b/ ... /{l_low}/ ... /t/!", "duration": 4.5},
            {"card_text": f"BAT! /bæt/", "speech": f"Bat! Wonderful blending!", "duration": 4.0},
            {"card_text": f"Let's blend: /c/ - /{l_low}/ - /t/", "speech": f"Next one: /c/ ... /{l_low}/ ... /t/!", "duration": 4.5},
            {"card_text": f"CAT! /kæt/", "speech": f"Cat! Meow meow, clever cat!", "duration": 4.0},
            {"card_text": f"Phonics Chant: /{l_low}/ /{l_low}/", "speech": f"Chant with me: /{l_low}/ /{l_low}/ {w}! /{l_low}/ /{l_low}/ Bat!", "duration": 5.0},
            {"card_text": f"Can you find letter {letter}?", "speech": f"Can you find the letter {letter}? Touch the screen!", "duration": 5.0},
            {"card_text": f"Super Phonics Star!", "speech": f"Super phonics star! You did it!", "duration": 4.0}
        ]
        # Nhân bản theo thời lượng
        num_modules = max(4, int(target_sec / 4.2))
        cur_t = 0
        shot_id = 1
        while len(shots) < num_modules and cur_t < target_sec:
            m = modules[(shot_id - 1) % len(modules)]
            shots.append({
                "shot_id": shot_id,
                "card_text": m["card_text"],
                "speech": m["speech"],
                "duration": m["duration"]
            })
            cur_t += m["duration"]
            shot_id += 1

        return {
            "genre": "phonics",
            "topic": w,
            "target_duration_seconds": round(cur_t, 1),
            "age_group": do_tuoi,
            "speech_rate": "-15%",
            "shots": shots
        }

    elif g in ("sight_words", "sightword", "signword"):
        sw = w.upper()
        patterns = [
            {"card_text": f"Look & Say: {sw}", "speech": f"Look and say together: {sw}!", "duration": 4.0},
            {"card_text": f"Spell: {' - '.join(list(sw))}", "speech": f"Let's spell: {' - '.join(list(sw))}! {sw}!", "duration": 4.5},
            {"card_text": f"Sentence 1: I {sw.lower()} cats.", "speech": f"Read with me: I {sw.lower()} cats.", "duration": 4.5},
            {"card_text": f"Sentence 2: I {sw.lower()} dogs.", "speech": f"Read with me: I {sw.lower()} dogs.", "duration": 4.5},
            {"card_text": f"Sentence 3: I {sw.lower()} school.", "speech": f"Read with me: I {sw.lower()} school.", "duration": 4.5},
            {"card_text": f"Flash Quiz: What word is this?", "speech": f"Look fast! What word is this? Say it out loud!", "duration": 5.0},
            {"card_text": f"Great Job: {sw}!", "speech": f"Yes! That is {sw}! Awesome!", "duration": 4.0}
        ]
        num_shots = max(5, int(target_sec / 4.4))
        cur_t = 0
        shot_id = 1
        while len(shots) < num_shots and cur_t < target_sec:
            m = patterns[(shot_id - 1) % len(patterns)]
            shots.append({"shot_id": shot_id, "card_text": m["card_text"], "speech": m["speech"], "duration": m["duration"]})
            cur_t += m["duration"]
            shot_id += 1

        return {
            "genre": "sight_words",
            "topic": sw,
            "target_duration_seconds": round(cur_t, 1),
            "age_group": do_tuoi,
            "speech_rate": "-15%",
            "shots": shots
        }

    elif g in ("conversation", "giaotiep", "dialogue"):
        dialogue_bank = [
            {"speaker": "A", "card_text": "Hello! Good morning!", "speech": "Hello little friend! Good morning to you!", "duration": 4.5},
            {"speaker": "A", "card_text": "[Interactive Pause: Say Good Morning!]", "speech": "Can you say: Good morning teacher?", "duration": 4.5},
            {"speaker": "B", "card_text": "Good morning teacher!", "speech": "Good morning teacher! Nice to see you!", "duration": 4.5},
            {"speaker": "A", "card_text": "How are you today?", "speech": "How are you feeling today?", "duration": 4.0},
            {"speaker": "A", "card_text": "[Interactive Pause: Are you happy?]", "speech": "Are you happy? Tell me!", "duration": 4.5},
            {"speaker": "B", "card_text": "I am very happy! Thank you!", "speech": "I am very happy! Thank you so much!", "duration": 4.5},
            {"speaker": "A", "card_text": "What is this? Look!", "speech": f"Look at this! Do you know what this is? It's a {w.lower()}!", "duration": 5.0},
            {"speaker": "B", "card_text": f"Yes! It is a {w.lower()}!", "speech": f"Yes teacher! It is a sweet {w.lower()}!", "duration": 4.5},
            {"speaker": "Both", "card_text": "We love learning English!", "speech": "We love learning English together! High five!", "duration": 4.5}
        ]
        num_shots = max(4, int(target_sec / 4.5))
        cur_t = 0
        shot_id = 1
        while len(shots) < num_shots and cur_t < target_sec:
            m = dialogue_bank[(shot_id - 1) % len(dialogue_bank)]
            shots.append({
                "shot_id": shot_id,
                "speaker": m["speaker"],
                "card_text": m["card_text"],
                "speech": m["speech"],
                "duration": m["duration"]
            })
            cur_t += m["duration"]
            shot_id += 1

        return {
            "genre": "conversation",
            "topic": w,
            "target_duration_seconds": round(cur_t, 1),
            "age_group": do_tuoi,
            "speech_rate": "-15%",
            "shots": shots
        }

    elif g in ("story", "storybook", "truyen"):
        story_pages = [
            {"card_text": f"Once upon a time, in a peaceful green valley...", "speech": f"Once upon a time, in a peaceful green valley, lived a little friend named {w.capitalize()}.", "duration": 6.0},
            {"card_text": f"Every morning, {w.capitalize()} loved to explore.", "speech": f"Every morning, {w.capitalize()} loved to explore the sunny woods and sing sweet tunes.", "duration": 6.0},
            {"card_text": f"One day, {w.capitalize()} saw a sad little bird.", "speech": f"One day, {w.capitalize()} saw a sad little bird sitting quietly under the big oak tree.", "duration": 6.5},
            {"card_text": f"'Don't worry, little bird! I can help you!'", "speech": "Don't worry little bird, I am your friend! I can help you find your family!", "duration": 6.0},
            {"card_text": f"They walked through the bright flower garden.", "speech": "Together, they walked through the bright flower garden, full of red and yellow roses.", "duration": 6.5},
            {"card_text": f"Soon, they found mama bird up in the nest!", "speech": "Look up high! There was mama bird, singing happily in the warm nest!", "duration": 6.0},
            {"card_text": f"'Thank you, kind friend!' chirped the bird.", "speech": "Thank you kind friend, you have a caring heart!", "duration": 5.5},
            {"card_text": f"Being kind to others makes the world bright.", "speech": "Being kind to others makes the whole world bright and happy. The end!", "duration": 6.0},
            {"card_text": f"[Reflection: Do you love helping friends?]", "speech": "Do you love helping your friends? Yes, we always help each other!", "duration": 6.0}
        ]
        num_shots = max(5, int(target_sec / 6.0))
        cur_t = 0
        shot_id = 1
        while len(shots) < num_shots and cur_t < target_sec:
            m = story_pages[(shot_id - 1) % len(story_pages)]
            shots.append({"shot_id": shot_id, "card_text": m["card_text"], "speech": m["speech"], "duration": m["duration"]})
            cur_t += m["duration"]
            shot_id += 1

        return {
            "genre": "story",
            "topic": w,
            "target_duration_seconds": round(cur_t, 1),
            "age_group": do_tuoi,
            "speech_rate": "-18%",
            "shots": shots
        }

    elif g in ("song", "movement", "baihat"):
        song_verses = [
            {"card_text": "Clap your hands! One, two, three!", "speech": "Clap your hands! One, two, three! Clap with me!", "duration": 4.5},
            {"card_text": "Stomp your feet! Happy and free!", "speech": "Stomp your feet! Happy and free! Stomp stomp stomp!", "duration": 4.5},
            {"card_text": "Jump up high! Reach for the sky!", "speech": "Jump up high! Reach for the sky! Jump jump jump!", "duration": 4.5},
            {"card_text": "Spin around! Now touch the ground!", "speech": "Spin around, round and round! Now touch the ground!", "duration": 4.5},
            {"card_text": "Wiggle your fingers! Wave hello!", "speech": "Wiggle your fingers! Wave hello to everyone!", "duration": 4.5},
            {"card_text": "Dance like a puppy! Woof woof woof!", "speech": "Dance like a happy puppy! Woof woof woof!", "duration": 4.5},
            {"card_text": "Take a deep breath. 1, 2, 3.", "speech": "Take a deep breath. In, and out. Good job!", "duration": 4.5},
            {"card_text": "You are a shining star today!", "speech": "You are a shining star today! High five!", "duration": 4.5}
        ]
        num_shots = max(4, int(target_sec / 4.5))
        cur_t = 0
        shot_id = 1
        while len(shots) < num_shots and cur_t < target_sec:
            m = song_verses[(shot_id - 1) % len(song_verses)]
            shots.append({"shot_id": shot_id, "card_text": m["card_text"], "speech": m["speech"], "duration": m["duration"]})
            cur_t += m["duration"]
            shot_id += 1

        return {
            "genre": "song",
            "topic": w,
            "target_duration_seconds": round(cur_t, 1),
            "age_group": do_tuoi,
            "speech_rate": "-10%",
            "shots": shots
        }

    elif g in ("rhyme", "poem", "tho"):
        rhyme_stanzas = [
            {"card_text": f"Little {w.lower()}, sweet and bright,", "speech": f"Little {w.lower()}, sweet and bright,", "duration": 4.0},
            {"card_text": "Shining in the morning light.", "speech": "Shining in the morning light.", "duration": 4.0},
            {"card_text": "Growing on the tree so tall,", "speech": "Growing on the tree so tall,", "duration": 4.0},
            {"card_text": "Never let the sunshine fall.", "speech": "Never let the sunshine fall.", "duration": 4.0},
            {"card_text": "Listen to the birds that sing,", "speech": "Listen to the birds that sing,", "duration": 4.0},
            {"card_text": "Joy and laughter they will bring.", "speech": "Joy and laughter they will bring.", "duration": 4.0},
            {"card_text": "Clap your hands and smile with me,", "speech": "Clap your hands and smile with me,", "duration": 4.0},
            {"card_text": "Happy as a bumblebee!", "speech": "Happy as a bumblebee! Good job!", "duration": 4.5}
        ]
        num_shots = max(4, int(target_sec / 4.0))
        cur_t = 0
        shot_id = 1
        while len(shots) < num_shots and cur_t < target_sec:
            m = rhyme_stanzas[(shot_id - 1) % len(rhyme_stanzas)]
            shots.append({"shot_id": shot_id, "card_text": m["card_text"], "speech": m["speech"], "duration": m["duration"]})
            cur_t += m["duration"]
            shot_id += 1

        return {
            "genre": "rhyme",
            "topic": w,
            "target_duration_seconds": round(cur_t, 1),
            "age_group": do_tuoi,
            "speech_rate": "-16%",
            "shots": shots
        }

    else: # Vocabulary
        vocab_items = [
            {"card_text": f"Look! What is this?", "speech": f"Hello friends! Look, what is this object?", "duration": 4.5},
            {"card_text": f"{w.capitalize()}! This is an {w.lower()}.", "speech": f"{w.capitalize()}! Say with me: {w.lower()}.", "duration": 4.5},
            {"card_text": f"The {w.lower()} is bright and colorful.", "speech": f"The {w.lower()} is bright and colorful.", "duration": 4.5},
            {"card_text": f"Touch the {w.lower()} on screen!", "speech": f"Touch the {w.lower()} on screen! One, two, touch!", "duration": 4.5},
            {"card_text": f"Can you find the {w.lower()}?", "speech": f"Where is the {w.lower()}? Is it A or B?", "duration": 5.0},
            {"card_text": f"Yes! That is the {w.lower()}!", "speech": f"Yes! That is the {w.lower()}! Excellent work!", "duration": 4.5},
            {"card_text": f"Let's review: {w.capitalize()}!", "speech": f"Let's review together: {w.capitalize()}!", "duration": 4.5}
        ]
        num_shots = max(4, int(target_sec / 4.6))
        cur_t = 0
        shot_id = 1
        while len(shots) < num_shots and cur_t < target_sec:
            m = vocab_items[(shot_id - 1) % len(vocab_items)]
            shots.append({"shot_id": shot_id, "card_text": m["card_text"], "speech": m["speech"], "duration": m["duration"]})
            cur_t += m["duration"]
            shot_id += 1

        return {
            "genre": "vocabulary",
            "topic": w,
            "target_duration_seconds": round(cur_t, 1),
            "age_group": do_tuoi,
            "speech_rate": "-16%",
            "shots": shots
        }

def tao_kich_ban_clip_theo_the_loai(
    genre: str = "vocabulary",
    topic_or_word: str = "Apple",
    do_tuoi: str = "3-4",
    target_minutes: float = 1.0,
    use_llm: bool = False
) -> Dict[str, Any]:
    """Sinh kịch bản tối ưu theo thể loại và thời lượng."""
    return tao_kich_ban_theo_thoi_luong(genre, topic_or_word, do_tuoi, target_minutes=target_minutes)

def tao_kich_ban_clip(tu_khoa: str, do_tuoi: str = "3-4") -> Dict[str, Any]:
    return tao_kich_ban_clip_theo_the_loai("vocabulary", tu_khoa, do_tuoi)
