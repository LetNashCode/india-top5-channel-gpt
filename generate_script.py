"""
generate_script.py
Story-driven YouTube Shorts generator (English)
"""

import json
import os

from google import genai
from google.genai import types

SYSTEM_PROMPT = """
You are an elite YouTube Shorts writer.

Return ONLY valid JSON.

Schema:

{
  "title":"",
  "hook":"",
  "story":"",
  "twist":"",
  "ending":"",
  "scene_plan":[
    {
      "text":"",
      "visual":"",
      "keywords":[]
    }
  ]
}

RULES
- English only.
- No Top 5.
- No countdowns.
- 40-45 seconds.
- Structure:
  Hook
  Story
  Twist
  Ending + Open Loop
- Build suspense every sentence.
- Return only JSON.
"""

def generate_script(topic: str, config: dict) -> dict:
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    prompt = f"""
Topic:
{topic}

Target narration:
{config["script"]["target_narration_seconds"]} seconds.

Return JSON only.
"""

    response = client.models.generate_content(
        model="gemini-flash-lite-latest",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
        ),
    )

    decoder = json.JSONDecoder()
    obj, _ = decoder.raw_decode(
        response.text.replace("```json", "").replace("```", "").strip()
    )

    return obj
