"""
Generates a structured Top-5 script using the Google Gemini API
(free tier — no billing required for this project's usage level).

Uses the current `google-genai` SDK (the older `google-generativeai`
package was retired by Google).

Output is strict JSON so downstream steps (TTS, visuals, captions,
title/description) can all consume it without any fragile text-parsing.
"""
import json
import os

from google import genai
from google.genai import types

SYSTEM_PROMPT = """
You are an elite YouTube Shorts writer.

Your job is to create highly addictive 35–45 second storytelling videos.

Return ONLY valid JSON.

Schema:

{
  "title": "",
  "hook": "",
  "story": "",
  "twist": "",
  "ending": "",
  "scene_plan": [
    {
      "text": "",
      "visual": "",
      "keywords": []
    }
  ]
}

RULES

• Never write Top 5 or countdowns.
• Never use lists.
• Tell one complete story.
• First sentence must instantly create curiosity.
• Every sentence should increase suspense.
• The twist should surprise the viewer.
• The ending should feel satisfying but leave one question unanswered.
• Write naturally.
• No introductions.
• No greetings.
• No filler.
• No emojis.
• No markdown.

HOOK

Maximum 12 words.

Examples:

"One village disappeared overnight..."

"This signal from space still has no explanation..."

"Nobody knows who built this place..."

STORY

Build curiosity.

Keep sentences short.

TWIST

Reveal the unexpected part.

ENDING

End with something people will think about after the video ends.

SCENE PLAN

Create 6-8 cinematic scenes.

Each scene must contain:

"text"

"visual"

"keywords"

Example visual:

"A dark abandoned village at night covered in heavy fog."

Example keywords:

[
"abandoned village",
"foggy street",
"cinematic night",
"old houses"
]

Return ONLY JSON.
"""


def generate_script(topic: str, config: dict) -> dict:
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    items = config["script"]["items_per_video"]
    seconds = config["script"]["target_narration_seconds"]
    language = config["script"]["language"]
    niche = config["channel"]["niche"]
    tone = config["channel"]["tone"]
    audience = config["channel"]["audience"]

    user_prompt = f"""Channel niche: {niche}
Tone: {tone}
Audience: {audience}
Language for spoken narration: {language} (write in Devanagari script for correct TTS pronunciation)
Topic for this video: {topic}
Number of countdown items: {items}
Target total narration length: about {seconds} seconds spoken aloud

Write the script now as JSON only."""

    response = client.models.generate_content(
        model="gemini-flash-lite-latest",
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
        ),
    )

    text = response.text.strip()
    text = text.replace("```json", "").replace("```", "").strip()
    # Gemini occasionally appends stray text/whitespace after the JSON object.
    # Parse only the first valid JSON value and ignore anything after it.
    decoder = json.JSONDecoder()
    obj, _ = decoder.raw_decode(text)
    return obj


if __name__ == "__main__":
    import yaml

    with open("config.yaml") as f:
        cfg = yaml.safe_load(f)
    script = generate_script("haunted forts and palaces across India", cfg)
    print(json.dumps(script, indent=2, ensure_ascii=False))
