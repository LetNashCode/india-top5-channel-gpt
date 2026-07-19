"""
Assembles the final 9:16 Short: visuals + narration audio + burned-in
captions + background music, synced item by item.
"""
import os

from moviepy.editor import (
    AudioFileClip,
    CompositeAudioClip,
    CompositeVideoClip,
    ColorClip,
    ImageClip,
    TextClip,
    VideoFileClip,
    concatenate_videoclips,
    afx,
)


def _fit_portrait(clip, size):
    w, h = size
    clip = clip.resize(height=h) if clip.h / clip.w < h / w else clip.resize(width=w)
    clip = clip.crop(
        x_center=clip.w / 2, y_center=clip.h / 2, width=w, height=h
    )
    return clip


def _caption_clip(text: str, duration: float, config: dict, video_size):
    font_size = config["video"]["captions"]["font_size"]
    w, h = video_size
    txt = TextClip(
        text,
        fontsize=font_size,
        color="yellow",
        font="DejaVu-Sans-Bold",
        method="caption",
        size=(int(w * 0.85), None),
        stroke_color="black",
        stroke_width=3,
        align="center",
    )
    txt = txt.set_position(("center", h * 0.78)).set_duration(duration)
    return txt


def _build_item_clip(visual_path, audio_path, rank, name, config):
    video_size = tuple(config["video"]["resolution"])
    audio = AudioFileClip(audio_path)
    duration = audio.duration + 0.4  # small pad between items

    if visual_path and os.path.exists(visual_path):
        base = VideoFileClip(visual_path).without_audio()
        if base.duration < duration:
            base = base.loop(duration=duration)
        else:
            base = base.subclip(0, duration)
        base = _fit_portrait(base, video_size)
    else:
        # Fallback: solid dark background if no stock clip was found
        base = ColorClip(video_size, color=(10, 10, 15)).set_duration(duration)

    rank_label = TextClip(
        f"#{rank}",
        fontsize=110,
        color="white",
        font="DejaVu-Sans-Bold",
        stroke_color="black",
        stroke_width=4,
    ).set_position(("center", video_size[1] * 0.08)).set_duration(duration)

    caption = _caption_clip(name, duration, config, video_size)

    composite = CompositeVideoClip([base, rank_label, caption], size=video_size)
    composite = composite.set_audio(audio.set_start(0))
    composite = composite.set_duration(duration)
    return composite


def assemble_video(script: dict, audio_paths: list, visual_paths: list, config: dict, out_path: str) -> str:
    clips = []
    for item, audio_path, visual_path in zip(script["items"], audio_paths, visual_paths):
        clip = _build_item_clip(visual_path, audio_path, item["rank"], item["name"], config)
        clips.append(clip)

    final = concatenate_videoclips(clips, method="compose")

    music_path = config["video"].get("background_music")
    if music_path and os.path.exists(music_path):
        music = AudioFileClip(music_path).fx(afx.audio_loop, duration=final.duration)
        music = music.volumex(config["video"].get("music_volume", 0.12))
        mixed = CompositeAudioClip([final.audio, music])
        final = final.set_audio(mixed)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    final.write_videofile(
        out_path,
        fps=config["video"].get("fps", 30),
        codec="libx264",
        audio_codec="aac",
        preset="medium",
        threads=4,
    )
    return out_path
