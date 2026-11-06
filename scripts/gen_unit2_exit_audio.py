#!/usr/bin/env python3
"""Generate Arabic Neural MP3 for the six Grade 8 exit-ticket lessons.

The HTML and the audio are both generated from unit2-exit-data.json.
Arabic diacritics are already proofed in that single source.
"""
import asyncio
import json
import re
from pathlib import Path

import edge_tts

VOICE = "ar-SA-HamedNeural"
RATE = "-10%"
SOURCE = Path("unit2-exit-data.json")
OUT = Path("assets/audio")
PAUSE_VOWEL = re.compile(r"[\u064B-\u0650](?=[،,:؛.!؟])")


def build_text(lesson, question, number):
    assert len(question["options"]) == 3
    choices = ("الْخِيَارُ الْأَوَّل", "الْخِيَارُ الثَّانِي", "الْخِيَارُ الثَّالِث")
    parts = ["السُّؤَالُ " + ("الْأَوَّل" if number == 1 else "الثَّانِي") + ": " + question["q"]]
    for label, option in zip(choices, question["options"]):
        parts.append(label + ": " + option)
    result = " ".join(parts)
    if PAUSE_VOWEL.search(result):
        raise ValueError("Short vowel before punctuation: " + result)
    return result


async def main():
    lessons = json.loads(SOURCE.read_text(encoding="utf-8"))
    assert len(lessons) == 6
    OUT.mkdir(parents=True, exist_ok=True)
    clips = []
    for i, lesson in enumerate(lessons, 1):
        assert len(lesson["questions"]) == 2
        for j, question in enumerate(lesson["questions"], 1):
            clips.append((OUT / f"unit2-exit-{i:02d}-{j:02d}.mp3", build_text(lesson, question, j)))
    for path, text in clips:
        for attempt in range(1, 5):
            try:
                await edge_tts.Communicate(text, voice=VOICE, rate=RATE).save(str(path))
                if path.stat().st_size < 4096:
                    raise RuntimeError(f"Audio file unexpectedly small: {path}")
                print(f"SUCCESS {path} {path.stat().st_size} bytes")
                break
            except Exception:
                if path.exists():
                    path.unlink()
                if attempt == 4:
                    raise
                await asyncio.sleep(attempt * 2)
    assert len(list(OUT.glob("unit2-exit-??-??.mp3"))) == 12


if __name__ == "__main__":
    asyncio.run(main())
