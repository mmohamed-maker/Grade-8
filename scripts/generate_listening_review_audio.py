#!/usr/bin/env python3
"""Generate six spoken-question clips for the Grade 8 Unit 2 listening review."""
import asyncio
import json
import re
from pathlib import Path
import edge_tts

SOURCE=Path('scripts/listening_review_voice_data.json')
OUT=Path('assets/audio/listening-review')
LABELS=('الْخِيَارُ الْأَوَّل','الْخِيَارُ الثَّانِي','الْخِيَارُ الثَّالِث','الْخِيَارُ الرَّابِع')
PAUSE=re.compile(r'[\u064B-\u0650](?=[،,:؛.!؟])')

async def main():
    data=json.loads(SOURCE.read_text(encoding='utf-8'))
    items=data['questions']
    assert len(items)==6
    OUT.mkdir(parents=True,exist_ok=True)
    for index,item in enumerate(items,1):
        assert len(item['options'])==4
        spoken=' '.join(['السُّؤَال: '+item['question']]+[name+': '+option for name,option in zip(LABELS,item['options'])])
        spoken=PAUSE.sub('',spoken)
        dest=OUT/f'review-q{index}.mp3'
        for attempt in range(1,5):
            try:
                await edge_tts.Communicate(spoken,voice=data['voice'],rate='-10%').save(str(dest))
                if dest.stat().st_size<4096: raise RuntimeError('Audio file is too small')
                print(dest, dest.stat().st_size)
                break
            except Exception:
                if dest.exists(): dest.unlink()
                if attempt==4: raise
                await asyncio.sleep(attempt*2)

if __name__=='__main__':
    asyncio.run(main())
