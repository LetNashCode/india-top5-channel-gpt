"""
Text-to-speech using edge-tts (free, Microsoft Edge neural voices,
includes good Indian-English and Hindi voices, no API key required).
"""
import asyncio
import os

import edge_tts


async def _synthesize(text: str, voice: str, rate: str, pitch: str, out_path: str):
    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    await communicate.save(out_path)


def synthesize_narration(text: str, config: dict, out_path: str) -> str:
    voice_cfg = config["voice"]
    asyncio.run(
        _synthesize(
            text=text,
            voice=voice_cfg["voice_name"],
            rate=voice_cfg.get("rate", "+0%"),
            pitch=voice_cfg.get("pitch", "+0Hz"),
            out_path=out_path,
        )
    )
    return out_path


def synthesize_script(script: dict, config: dict, workdir: str) -> list:
    """Synthesize one audio file per item, returns list of file paths in order."""
    os.makedirs(workdir, exist_ok=True)
    paths = []
    for item in script["items"]:
        out_path = os.path.join(workdir, f"item_{item['rank']}.wav")
        synthesize_narration(item["narration"], config, out_path)
        paths.append(out_path)
    return paths


if __name__ == "__main__":
    import yaml

    with open("config.yaml") as f:
        cfg = yaml.safe_load(f)
    synthesize_narration(
        "Number five. This fort has kept its secrets for three hundred years.",
        cfg,
        "test_voice.mp3",
    )
    print("Saved test_voice.mp3")
