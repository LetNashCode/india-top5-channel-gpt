"""
topics.py

Generates one unique video idea using Gemini.
Keeps track of previous ideas in used_topics.json.
"""

import json
import os

from google import genai
from google.genai import types


USED_TOPICS_PATH = "used_topics.json"


SYSTEM_PROMPT = """
You are an expert viral YouTube Shorts idea generator.

Generate ONE completely original video idea.

The idea must belong to ONE of these series:

1. Survival Simulator
2. One Wrong Choice
3. You Wake Up As
4. Last Person Alive
5. Every Minute Gets Worse
6. Impossible Challenge
7. Reality Glitch
8. Choose Your Fate

Rules

• Return ONLY ONE idea.
• Keep it under 8 words.
• Make it extremely clickable.
• Never explain.
• No numbering.
• No quotation marks.
• No punctuation at the end.
• Do not copy previous ideas.
"""


def _load_used():

    if os.path.exists(USED_TOPICS_PATH):
        with open(USED_TOPICS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    return []


def _save_used(used):

    with open(USED_TOPICS_PATH, "w", encoding="utf-8") as f:
        json.dump(used, f, indent=2, ensure_ascii=False)


def get_next_topic():

    client = genai.Client(
        api_key=os.environ["GEMINI_API_KEY"]
    )

    used = _load_used()

    previous = "\n".join(used[-200:])

    prompt = f"""
Previously used ideas:

{previous}

Generate ONE completely different idea.

Return ONLY the idea.
"""

    for _ in range(5):

        response = client.models.generate_content(
            model="gemini-flash-lite-latest",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
            ),
        )

        idea = response.text.strip()

        idea = (
            idea
            .replace('"', "")
            .replace(".", "")
            .strip()
        )

        if idea not in used:

            used.append(idea)

            _save_used(used)

            print("=" * 80)
            print("GENERATED IDEA")
            print("=" * 80)
            print(idea)
            print("=" * 80)

            return idea

    raise RuntimeError("Could not generate a unique idea.")
