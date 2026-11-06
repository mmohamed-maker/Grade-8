#!/usr/bin/env python3
"""Generate Arabic Neural audio for the questions in the three listening exit-ticket games."""
import asyncio
import json
import re
from pathlib import Path
import edge_tts

SOURCE=Path('scripts/course_games_voice_data.json')
OUTPUT=Path('assets/audio/course-games')
VOICE='ar-SA-HamedNeural'
RATE='-10%'
PAUSE_MARKS=re.compile(r'[\u064B-\u0650](?=[،,:؛.!؟])')
VOCALIZATION={
    'ميمونة':'مَيْمُونَة',
    'الصداقة':'الصَّدَاقَة',
    'الصديق':'الصَّدِيق',
    'الجسر':'الْجِسْر',
    'الوطن':'الْوَطَن',
    'الجملة':'الْجُمْلَة',
    'التعاون':'التَّعَاوُن',
    'المصالحة':'الْمُصَالَحَة',
    'العلاقة':'الْعَلَاقَة',
    'النص':'النَّصّ'
}

def prepare(sentence):
    for old,new in VOCALIZATION.items():
        sentence=re.sub(r'(?<![\u0621-\u064A\u064B-\u0652])'+old+r'(?![\u0621-\u064A\u064B-\u0652])',new,sentence)
    return PAUSE_MARKS.sub('',sentence)

async def main():
    data=json.loads(SOURCE.read_text(encoding='utf-8'))
    assert len(data)==3
    OUTPUT.mkdir(parents=True,exist_ok=True)
    labels=('الْخِيَارُ الْأَوَّل','الْخِيَارُ الثَّانِي','الْخِيَارُ الثَّالِث','الْخِيَارُ الرَّابِع')
    produced=0
    for stem,questions in data.items():
        assert len(questions)==4
        for i,q in enumerate(questions,1):
            assert len(q['options'])==4
            text=prepare(' '.join(['السُّؤَال: '+q['q']]+[label+': '+option for label,option in zip(labels,q['options'])]))
            target=OUTPUT/f'{stem}-q{i}.mp3'
            for attempt in range(1,5):
                try:
                    await edge_tts.Communicate(text,voice=VOICE,rate=RATE).save(str(target))
                    if target.stat().st_size<4096:
                        raise ValueError('Recording too small')
                    produced+=1
                    print(target,target.stat().st_size)
                    break
                except Exception:
                    if target.exists():
                        target.unlink()
                    if attempt==4:
                        raise
                    await asyncio.sleep(attempt*2)
    assert produced==12

if __name__=='__main__':
    asyncio.run(main())
