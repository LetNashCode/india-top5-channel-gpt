"""
Topic bank for the channel. main.py picks the next unused topic each run
and records it in used_topics.json so the same topic never repeats.

Add/remove categories freely — the script generator will invent specific
Top-5 items within whichever category is chosen.
"""
import json
import os
import random

TOPIC_BANK = [
    "haunted forts and palaces across India",
    "unsolved disappearances in Indian hill stations",
    "cursed villages people abandoned overnight",
    "eerie legends from Indian Railways",
    "haunted Bollywood film sets and locations",
    "mysterious lakes and rivers with dark legends",
    "unexplained events reported by the Indian Army",
    "creepy folklore creatures from different Indian states",
    "abandoned mansions with a dark history",
    "unsolved mysteries from Indian history",
    "haunted hospitals and asylums in India",
    "strange rituals and their eerie origins",
    "ghost stories from Indian college hostels",
    "mysterious tunnels and underground passages",
    "cursed objects kept in Indian museums",
    "unexplained sightings in the Himalayas",
    "haunted highways and roads truckers avoid",
    "eerie temple legends across India",
    "unsolved deaths shrouded in mystery",
    "paranormal reports from Indian forests",
]

USED_TOPICS_PATH = os.path.join(os.path.dirname(__file__), "used_topics.json")


def _load_used():
    if os.path.exists(USED_TOPICS_PATH):
        with open(USED_TOPICS_PATH, "r") as f:
            return json.load(f)
    return []


def _save_used(used):
    with open(USED_TOPICS_PATH, "w") as f:
        json.dump(used, f, indent=2)


def get_next_topic() -> str:
    """Return a topic not used recently. Resets once the bank is exhausted."""
    used = _load_used()
    available = [t for t in TOPIC_BANK if t not in used]
    if not available:
        used = []
        available = TOPIC_BANK[:]
    topic = random.choice(available)
    used.append(topic)
    _save_used(used)
    return topic
