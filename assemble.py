
"""
assemble.py
ImageMagick-free version using Pillow for text rendering.
"""
import os
import tempfile

from PIL import Image, ImageDraw, ImageFont

from moviepy.editor import (
    AudioFileClip,
    CompositeAudioClip,
    CompositeVideoClip,
    ColorClip,
    ImageClip,
    VideoFileClip,
    concatenate_videoclips,
    afx,
)

FONT_NAME = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def _fit_portrait(clip, size):
    w, h = size
    clip = clip.resize(height=h) if clip.h / clip.w < h / w else clip.resize(width=w)
    return clip.crop(x_center=clip.w/2, y_center=clip.h/2, width=w, height=h)


def _font(size):
    try:
        return ImageFont.truetype(FONT_NAME, size)
    except Exception:
        return ImageFont.load_default()


def _text_clip(text, fontsize, color, stroke_color, stroke_width,
               duration, video_size, y, max_width_ratio=0.85):
    w, h = video_size
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = _font(fontsize)

    max_w = int(w * max_width_ratio)

    lines = []
    words = text.split()
    line = ""
    for word in words:
        test = (line + " " + word).strip()
        if draw.textbbox((0,0), test, font=font)[2] <= max_w:
            line = test
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)

    line_h = draw.textbbox((0,0),"Ay",font=font)[3] + 8
    total_h = len(lines)*line_h
    cy = int(y)

    for i,l in enumerate(lines):
        bbox = draw.textbbox((0,0), l, font=font)
        tw = bbox[2]-bbox[0]
        x = (w-tw)//2
        yy = cy + i*line_h
        for dx in range(-stroke_width, stroke_width+1):
            for dy in range(-stroke_width, stroke_width+1):
                if dx or dy:
                    draw.text((x+dx,yy+dy), l, font=font, fill=stroke_color)
        draw.text((x,yy), l, font=font, fill=color)

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    img.save(tmp.name)
    clip = ImageClip(tmp.name).set_duration(duration)
    clip = clip.set_position(("center",0))
    return clip


def _build_item_clip(visual_path, audio_path, rank, name, config):
    video_size = tuple(config["video"]["resolution"])
    audio = AudioFileClip(audio_path)
    duration = audio.duration + 0.4

    if visual_path and os.path.exists(visual_path):
        base = VideoFileClip(visual_path).without_audio()
        base = base.loop(duration=duration) if base.duration < duration else base.subclip(0,duration)
        base = _fit_portrait(base, video_size)
    else:
        base = ColorClip(video_size, color=(10,10,15)).set_duration(duration)

    rank_clip = _text_clip(
        f"#{rank}",
        fontsize=110,
        color="white",
        stroke_color="black",
        stroke_width=4,
        duration=duration,
        video_size=video_size,
        y=int(video_size[1]*0.08),
        max_width_ratio=0.5,
    )

    caption_clip = _text_clip(
        name,
        fontsize=config["video"]["captions"]["font_size"],
        color="yellow",
        stroke_color="black",
        stroke_width=3,
        duration=duration,
        video_size=video_size,
        y=int(video_size[1]*0.78),
        max_width_ratio=0.85,
    )

    comp = CompositeVideoClip([base, rank_clip, caption_clip], size=video_size)
    return comp.set_audio(audio).set_duration(duration)


def assemble_video(script, audio_paths, visual_paths, config, out_path):
    clips = []
    for item,a,v in zip(script["items"], audio_paths, visual_paths):
        clips.append(_build_item_clip(v,a,item["rank"],item["name"],config))

    final = concatenate_videoclips(clips, method="compose")

    music_path = config["video"].get("background_music")
    if music_path and os.path.exists(music_path):
        music = AudioFileClip(music_path).fx(afx.audio_loop, duration=final.duration)
        music = music.volumex(config["video"].get("music_volume",0.12))
        final = final.set_audio(CompositeAudioClip([final.audio,music]))

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    final.write_videofile(
        out_path,
        fps=config["video"].get("fps",30),
        codec="libx264",
        audio_codec="aac",
        preset="medium",
        threads=4,
    )
    return out_path
