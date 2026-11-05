#!/usr/bin/env python3
"""Generate consistent Arabic Neural MP3 clips for the Grade 8 listening game.

This script uses the public edge-tts Python client (rany2/edge-tts).
Run locally or from GitHub Actions. Requires internet access during generation.
"""
import asyncio
from pathlib import Path
import edge_tts

VOICE = "ar-SA-HamedNeural"
RATE = "-10%"
OUT = Path("assets/audio")
TEXTS = {
    "listening-main.mp3": "آهٍ يا رأسي! الساعة الآن العاشرة ليلًا، وأنا ما زلت في مكتبي بالمدرسة أُصَحِّحُ الدفاتر، لأنني أريد أن يفرح طلابي بدرجاتهم غدًا!",
    "radar-01.mp3": "أقرأ الأسئلة الموجودة في الورقة قبل أن يشغّل المعلم الصوت.",
    "radar-02.mp3": "سمعت كلمة صعبة لا أعرفها، فتركت القلم وتوقفت عن الاستماع!",
    "radar-03.mp3": "أثناء تشغيل الفيديو، سألت صديقي بصوت عالٍ: ماذا قال؟",
    "radar-04.mp3": "أكتب كلمات صغيرة وسريعة، كلمات مفتاحية، في دفتري وأنا أستمع.",
    "radar-05.mp3": "أنظر إلى وجه المتحدث في الفيديو لأفهم: هل هو سعيد أم غاضب؟",
}

async def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for filename, text in TEXTS.items():
        filepath = OUT / filename
        for attempt in range(3):
            try:
                await edge_tts.Communicate(text, voice=VOICE, rate=RATE).save(str(filepath))
                if filepath.stat().st_size < 1024:
                    raise RuntimeError(f"Suspiciously small audio: {filepath}")
                print(f"Generated {filepath} ({filepath.stat().st_size} bytes)")
                break
            except Exception as exc:
                if filepath.exists():
                    filepath.unlink()
                if attempt == 2:
                    raise
                print(f"Retrying {filename} after {type(exc).__name__}: {exc}")
                await asyncio.sleep((attempt + 1) * 2)

if __name__ == "__main__":
    asyncio.run(main())
