#!/usr/bin/env python3
"""Grade 6 original listening; fully vocalized Modern Standard Arabic; retain all vowel marks.
Generate on GitHub Actions. No credentials or private student data are used.
"""
import asyncio, json, subprocess, tempfile
from pathlib import Path
import edge_tts
TEXT = "فِي صَبَاحِ يَوْمِ الْأَحَدِ، دَخَلَتْ لَيْلَى سَاحَةَ الْمَدْرَسَةِ، فَلَاحَظَتْ أَكْوَابًا وَرَقِيَّةً كَثِيرَةً قُرْبَ الْمَقْصَفِ. قَالَتْ لِزَمِيلِهَا سَامِي: «نَشْتَرِي الْمَاءَ كُلَّ يَوْمٍ، ثُمَّ نَرْمِي الْأَكْوَابَ بَعْدَ دَقَائِقَ. أَلَا نَسْتَطِيعُ تَغْيِيرَ هَذِهِ الْعَادَةِ؟»\nأَجَابَ سَامِي بِحَمَاسٍ: «لِنَطْلُبْ مِنْ جَمِيعِ الطُّلَّابِ إِحْضَارَ زُجَاجَاتِهِمْ، وَسَتَخْتَفِي الْمُشْكِلَةُ غَدًا!» اِبْتَسَمَتِ الْمُعَلِّمَةُ، وَقَالَتْ بِنَبْرَةٍ هَادِئَةٍ: «الْفِكْرَةُ جَيِّدَةٌ، لَكِنَّنَا نَحْتَاجُ إِلَى خُطَّةٍ وَدَلِيلٍ، لَا إِلَى وَعْدٍ سَرِيعٍ».\nفِي اِجْتِمَاعِ فَرِيقِ الْبِيئَةِ، اِقْتَرَحَتْ لَيْلَى تَجْرِبَةً لِمُدَّةِ أُسْبُوعٍ وَاحِدٍ فِي الصَّفِّ السَّادِسِ. يَعُدُّ الْفَرِيقُ الْأَكْوَابَ الَّتِي يَسْتَخْدِمُهَا طُلَّابُ الصَّفِّ فِي يَوْمٍ دِرَاسِيٍّ قَبْلَ بَدْءِ التَّجْرِبَةِ، ثُمَّ يُسَجِّلُ الْعَدَدَ كُلَّ يَوْمٍ خِلَالَهَا. وَفِي نِهَايَةِ الْأُسْبُوعِ، يُقَارِنُ الْأَعْدَادَ.\nسَأَلَتْ نُورُ: «وَمَاذَا عَنِ الطَّالِبِ الَّذِي يَنْسَى زُجَاجَتَهُ؟» أَجَابَتْ لَيْلَى: «نُذَكِّرُهُ بِلُطْفٍ، وَلَا نَسْخَرُ مِنْهُ. الْهَدَفُ أَنْ نَتَعَاوَنَ، لَا أَنْ نُحْرِجَ أَحَدًا». وَأَضَافَتِ الْمُعَلِّمَةُ: «يَغْسِلُ كُلُّ طَالِبٍ زُجَاجَتَهُ، وَلَا يَتَبَادَلُهَا مَعَ زُمَلَائِهِ».\nصَمَّمَ سَامِي لَوْحَةً كَتَبَ عَلَيْهَا: «زُجَاجَتِي مَعِي؛ وَالْمَسْؤُولِيَّةُ تَبْدَأُ مِنِّي». وَضَعَ تَحْتَ الْعِبَارَةِ رَسْمًا لِزُجَاجَةٍ، ثُمَّ قَرَأَ الرِّسَالَةَ أَمَامَ زُمَلَائِهِ بِصَوْتٍ وَاضِحٍ.\nعِنْدَ نِهَايَةِ الِاجْتِمَاعِ، قَالَ سَامِي: «كُنْتُ أَظُنُّ أَنَّ الْحَمَاسَ وَحْدَهُ يَكْفِي. الْآنَ أَفْهَمُ أَنَّ الْعَادَةَ الْجَدِيدَةَ تَحْتَاجُ إِلَى تَذْكِيرٍ وَتَعَاوُنٍ وَمُتَابَعَةٍ». لَمْ يُعْلِنِ الْفَرِيقُ نَجَاحَ التَّجْرِبَةِ بَعْدُ؛ فَقَدْ كَانَ يَنْتَظِرُ مَا سَتُظْهِرُهُ الْأَعْدَادُ."
OUT=Path('assets/audio/grade6-bottle-listening.mp3')
async def main():
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        root=Path(tmp)
        segments=[]
        for i, paragraph in enumerate([s.strip() for s in __import__('re').split(r'(?<=[.؟!»])\s+|\n+', TEXT) if s.strip()]):
            if not paragraph.strip(): continue
            target=root/f'part-{i:02d}.mp3'
            for attempt in range(4):
                try:
                    await edge_tts.Communicate(paragraph,voice='ar-SA-HamedNeural',rate='-8%').save(str(target))
                    if target.stat().st_size<1024: raise RuntimeError('Empty speech')
                    break
                except Exception:
                    if attempt==3: raise
                    await asyncio.sleep(2*(attempt+1))
            wav=root/f'part-{i:02d}.wav'
            subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(target),'-ar','44100','-ac','1',str(wav)],check=True)
            segments.append(wav)
        silence=root/'pause.wav'
        subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','lavfi','-i','anullsrc=r=44100:cl=mono','-t','0.45',str(silence)],check=True)
        playlist=root/'concat.txt'
        playlist.write_text(''.join("file '"+str(p)+"'\n"+("file '"+str(silence)+"'\n" if n<len(segments)-1 else '') for n,p in enumerate(segments)))
        subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',str(playlist),'-af','loudnorm=I=-16:TP=-1.5:LRA=11','-ar','44100','-ac','1','-codec:a','libmp3lame','-b:a','128k','-metadata','title=زجاجتي معي — الاستماع للصف السادس',str(OUT)],check=True)
    meta=json.loads(subprocess.check_output(['ffprobe','-v','quiet','-print_format','json','-show_format','-show_streams',str(OUT)]))
    assert float(meta['format']['duration'])>60
    print(json.dumps({'path':str(OUT),'duration':meta['format']['duration'],'bytes':OUT.stat().st_size},ensure_ascii=False))
if __name__=='__main__': asyncio.run(main())
