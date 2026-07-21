import os
import shutil

from moviepy.editor import AudioFileClip, concatenate_audioclips
from tiktoktts import TTS

VOICE_ID = "en_us_ghostface"
MAX_BYTES = 300


def split_text(text, limit=MAX_BYTES):
    words = text.split()
    chunks = []
    current = ""

    for word in words:
        test = word if not current else current + " " + word
        if len(test.encode("utf-8")) <= limit:
            current = test
        else:
            if current:
                chunks.append(current)
            current = word

    if current:
        chunks.append(current)

    return chunks


def synthesize_narration(text, config, out_path):
    tts = TTS()
    tts.SetVoice(VOICE_ID)

    temp = []

    for i, chunk in enumerate(split_text(text)):
        import re
        
        chunk = re.sub(r"\.{2,}", ".", chunk)
        chunk = chunk.replace("...", ".")
        chunk = chunk.replace("..", ".")
        chunk = chunk.strip()
        
        tts.New(chunk)
        part = f"tts_part_{i}.mp3"
        shutil.move("output.mp3", part)
        temp.append(part)

    clips = [AudioFileClip(x) for x in temp]
    final = concatenate_audioclips(clips)
    final.write_audiofile(out_path, codec="mp3", fps=44100, logger=None)

    final.close()
    for c in clips:
        c.close()

    for x in temp:
        os.remove(x)

    return out_path


def synthesize_script(script, config, workdir):
    os.makedirs(workdir, exist_ok=True)

    narration = " ".join([
        script["hook"],
        script["story"],
        script["twist"],
        script["ending"],
    ])

    out = os.path.join(workdir, "story.mp3")
    synthesize_narration(narration, config, out)
    return [out]
