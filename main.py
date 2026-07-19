"""
Runs the full pipeline end to end: pick topic -> script -> voice ->
visuals -> assemble -> upload.

    python main.py             # full run, uploads to YouTube
    python main.py --dry-run   # builds the video but skips the upload
"""
import argparse
import os
import time

import yaml

from topics import get_next_topic
from generate_script import generate_script
from tts import synthesize_script
from visuals import fetch_visuals_for_script
from assemble import assemble_video
from upload_youtube import upload_video


def load_config(path="config.yaml") -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def build_title_and_description(script: dict, config: dict) -> tuple:
    upload_cfg = config["upload"]
    title = upload_cfg["title_template"].format(
        item_count=len(script["items"]), topic=script["topic_title"]
    )
    description = upload_cfg["description_template"].format(hook_line=script["hook_line"])
    return title, description


def run(dry_run: bool = False):
    config = load_config()

    topic = get_next_topic()
    print(f"Topic: {topic}")

    script = generate_script(topic, config)
    print(f"Script generated: {script['topic_title']} ({len(script['items'])} items)")

    run_id = str(int(time.time()))
    workdir = os.path.join("output", run_id)
    os.makedirs(workdir, exist_ok=True)

    audio_paths = synthesize_script(script, config, os.path.join(workdir, "audio"))
    print(f"Narration synthesized: {len(audio_paths)} clips")

    visual_paths = fetch_visuals_for_script(script, config, os.path.join(workdir, "visuals"))
    print(f"Visuals fetched: {len(visual_paths)} clips")

    out_path = os.path.join(workdir, "final.mp4")
    assemble_video(script, audio_paths, visual_paths, config, out_path)
    print(f"Video assembled: {out_path}")

    if dry_run or not config["upload"].get("auto_upload", True):
        print("Dry run — skipping upload.")
        return

    title, description = build_title_and_description(script, config)
    upload_video(out_path, title, description, config)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    run(dry_run=args.dry_run)
